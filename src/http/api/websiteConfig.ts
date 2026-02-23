import http from '../request';

export const getWebsiteConfigAsync: any = () => {
  return http.request({
    url: '/huajian/common/getWebsiteConfig',
    method: 'get'
  });
};
