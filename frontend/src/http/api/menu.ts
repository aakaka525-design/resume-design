import http from '../request';

export const getIndexMenuListAsync: any = () => {
  return http.request({
    url: '/huajian/common/getIndexMenuList',
    method: 'get'
  });
};
