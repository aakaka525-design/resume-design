import http from '../request';

export const getUserInfoAsync: any = (email: string) => {
  return http.request({
    url: `/huajian/integral/user/${email}`,
    method: 'get'
  });
};

export const updateUserAvatarAsync: any = (data: any) => {
  return http.request({
    url: '/huajian/users/updateAvatar',
    method: 'put',
    data
  });
};

export const updatePersonInfoAsync: any = (data: any) => {
  return http.request({
    url: '/huajian/users/updatePersonInfo',
    method: 'put',
    data
  });
};
