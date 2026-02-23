import http from '../request';

export const addWebsiteViewsAsync: any = () => {
  return http.request({
    url: '/huajian/common/addWebsiteViews',
    method: 'get'
  });
};
