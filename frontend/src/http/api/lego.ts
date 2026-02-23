import http from '../request';

export const legoUserResumeAsync: any = (data: any) => {
  return http.request({
    url: '/huajian/lego/legoUserResume',
    method: 'post',
    data
  });
};

export const legoUserResumeListAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/lego/legoUserResumeList',
    method: 'get',
    params
  });
};

export const getLegoUserResumeByIdAsync: any = (params: { id: any }) => {
  return http.request({
    url: `/huajian/lego/legoUserResumeById/${params.id}`,
    method: 'get'
  });
};

export const deleteLegoUserResumeAsync: any = (params: { id: any }) => {
  return http.request({
    url: `/huajian/lego/deleteLegoUserResume/${params.id}`,
    method: 'delete'
  });
};

export const getLegoUserTemplateByIdAndJsonIdAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/legoTemplate/legoUserTemplateByIdAndJsonId',
    method: 'get',
    params
  });
};

export const getLegoTemplateCategoryListAsync: any = () => {
  return http.request({
    url: '/huajian/common/getLegoCategoryList',
    method: 'get'
  });
};

export const getLegoTemplateListByCategoryAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/common/getLegoTemplateListByCategory',
    method: 'get',
    params
  });
};

export const getLegoTemplateInfoByIdAsync: any = (params: { id: any }) => {
  return http.request({
    url: `/huajian/legoTemplate/legoTemplateInfoById/${params.id}`,
    method: 'get'
  });
};

export const getLegoResumePdfAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/legoPdf/getPdf',
    method: 'post',
    responseType: 'blob',
    data: params
  });
};

export const getLegoPNGAsync: any = (params: any) => {
  return http.request({
    url: '/huajian/legoPdf/getPNG',
    method: 'post',
    responseType: 'blob',
    data: params
  });
};
