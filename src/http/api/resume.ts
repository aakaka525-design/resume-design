import http from '../request';

export const getTemplateListAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/common/getTemplateList',
    method: 'get',
    params
  });
};

export const getTemplateInfoAsync: any = (id: string) => {
  return http.request({
    url: `/huajian/resume/template/${id}`,
    method: 'get'
  });
};

export const getResetTemplateInfoAsync: any = (id: string) => {
  return http.request({
    url: `/huajian/resume/templateReset/${id}`,
    method: 'get'
  });
};

export const updateUserresumeAsync: any = (data: any) => {
  return http.request({
    url: '/huajian/userresume/template',
    method: 'post',
    data
  });
};

export const addMakeResumeCountAsync: any = () => {
  return http.request({
    url: '/huajian/pdf/addMakeResumeCount',
    method: 'get'
  });
};
