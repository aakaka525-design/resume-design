import http from '../request';

export const getTemplateStyleListAsync: any = () => {
  return http.request({
    url: '/huajian/common/getTemplateCategoryList',
    method: 'get'
  });
};

export const getTemplateByIdAsync: any = (id: string) => {
  return http.request({
    url: `/huajian/common/template/${id}`,
    method: 'get'
  });
};

export const templateListAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/common/templateList',
    method: 'get',
    params
  });
};

export const saveDraftAsync: any = (data: any) => {
  return http.request({
    url: '/huajian/createUserTemplate/saveDraft',
    method: 'post',
    data
  });
};

export const getUsertemplateAsync: any = (id: string) => {
  return http.request({
    url: `/huajian/createUserTemplate/getUsertemplate/${id}`,
    method: 'get'
  });
};

export const getMyResumeListAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/createUserTemplate/getMyResumeList',
    method: 'get',
    params
  });
};

export const deleteUserResumeAsync: any = (params: { id: any }) => {
  return http.request({
    url: `/huajian/createUserTemplate/deleteUserResume/${params.id}`,
    method: 'delete'
  });
};
