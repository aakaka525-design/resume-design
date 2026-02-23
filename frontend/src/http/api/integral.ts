import http from '../request';

export const getUserIntegralTotalAsync: any = () => {
  return http.request({
    url: '/huajian/integral/getUserIntegralTotal',
    method: 'get'
  });
};
