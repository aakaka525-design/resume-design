import axios, { AxiosResponse, AxiosError, AxiosRequestConfig, AxiosInstance } from 'axios';
import type { RequestConfig, RequestInterceptors } from './types/types';
import qs from 'qs';

const isEnvelopeResponse = (
  value: unknown
): value is { status: number; data: any; message: string } => {
  return (
    typeof value === 'object' &&
    value !== null &&
    Object.prototype.hasOwnProperty.call(value, 'status') &&
    Object.prototype.hasOwnProperty.call(value, 'data') &&
    Object.prototype.hasOwnProperty.call(value, 'message')
  );
};

const normalizeEnvelope = (payload: any) => {
  if (!isEnvelopeResponse(payload)) {
    return payload;
  }

  const originData = payload.data;

  // 兼容旧代码：允许 data.data.status / data.data.data 访问方式
  if (Array.isArray(originData)) {
    const arrData: any = originData;
    arrData.status = payload.status;
    arrData.message = payload.message;
    arrData.data = originData.slice();
    payload.data = arrData;
    return payload;
  }

  if (originData && typeof originData === 'object') {
    payload.data = {
      ...(originData as Record<string, any>),
      status: payload.status,
      message: payload.message,
      data: originData
    };
  }

  return payload;
};

class Request {
  instance: AxiosInstance;
  interceptorsObj?: RequestInterceptors<AxiosResponse>;
  cancelRequestSourceList: Map<string, AbortController> = new Map();
  requestUrlList: Set<string> = new Set();

  constructor(config: RequestConfig) {
    this.instance = axios.create(config);
    this.interceptorsObj = config.interceptors;

    this.instance.interceptors.request.use(
      (config) => {
        // 在此处添加请求拦截逻辑
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    if (this.interceptorsObj) {
      this.instance.interceptors.request.use(
        (config) =>
          this.interceptorsObj?.requestInterceptors
            ? (this.interceptorsObj.requestInterceptors(config as AxiosRequestConfig) as any)
            : config,
        this.interceptorsObj.requestInterceptorsCatch
      );
      this.instance.interceptors.response.use(
        this.interceptorsObj.responseInterceptors,
        this.interceptorsObj.responseInterceptorsCatch
      );
    }

    this.instance.interceptors.response.use(
      (response: AxiosResponse) => normalizeEnvelope(response.data),
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );
  }

  private getSourceIndex(url: string): number {
    return Array.from(this.cancelRequestSourceList.keys()).indexOf(url);
  }

  private delUrl(url: string) {
    this.requestUrlList.delete(url);
    this.cancelRequestSourceList.delete(url);
  }

  request<T>(config: RequestConfig<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      if (config.interceptors?.requestInterceptors) {
        config = config.interceptors.requestInterceptors(config);
      }

      const url = config.url;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort(); // 超时取消请求
      }, 60000 * 5); // 60秒

      if (url) {
        this.requestUrlList.add(url);
        this.cancelRequestSourceList.set(url, controller);
      }

      config.signal = controller.signal;

      if (!config.headers) {
        config.headers = {};
        config.headers['Content-Type'] = 'application/json';
      }

      if (config.method === 'post' && config.headers['Content-Type'] !== 'application/json') {
        config.data = qs.stringify(config.data);
      }

      if (localStorage.getItem('token')) {
        config.headers.Authorization = localStorage.getItem('token') as string;
      }

      this.instance
        .request<any, T>(config)
        .then((res) => {
          clearTimeout(timeoutId); // 请求成功，清除定时器
          if (config.interceptors?.responseInterceptors) {
            res = config.interceptors.responseInterceptors(res);
          }
          resolve(res);
        })
        .catch((error: AxiosError) => {
          clearTimeout(timeoutId); // 请求失败，清除定时器
          reject(error);
        })
        .finally(() => {
          if (url) this.delUrl(url);
        });
    });
  }

  cancelRequest(url: string | string[]) {
    if (typeof url === 'string') {
      const controller = this.cancelRequestSourceList.get(url);
      controller?.abort();
    } else {
      url.forEach((u) => {
        const controller = this.cancelRequestSourceList.get(u);
        controller?.abort();
      });
    }
  }

  cancelAllRequest() {
    this.cancelRequestSourceList.forEach((controller) => {
      controller.abort();
    });
  }
}

export default Request;
export { RequestConfig, RequestInterceptors };
