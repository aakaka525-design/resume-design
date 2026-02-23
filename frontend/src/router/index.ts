import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { title, description, keywords } from '@/config/seo';
import { useHead } from '@vueuse/head';

const Index = () => import('@/views/index/index.vue');
const Resume = () => import('@/views/resumeList/index.vue');
const ResumeContent = () => import('@/views/resumeContent/index.vue');
const Designer = () => import('@/views/designer/index.vue');
const DesignResume = () => import('@/views/designerResume/index.vue');
const PdfPreview = () => import('@/views/PdfPreview/index.vue');
const ResumePreview = () => import('@/views/createTemplate/previewer/index.vue');
const LegoDesigner = () => import('@/views/LegoDesigner/index.vue');
const LegoTemplateList = () => import('@/views/legoTemplateList/index.vue');
const LegoPrintPdfPreview = () =>
  import('@/views/LegoDesigner/render/LegoPrintPdfPreview/index.vue');
const NotFoundPage = () => import('@/views/404/index.vue');

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Index',
    meta: {
      title,
      keepAlive: true,
      isShowComNav: true
    },
    component: Index
  },
  {
    path: '/resume',
    name: 'Resume',
    meta: {
      title: '简历模板',
      keepAlive: true,
      isShowComNav: true
    },
    component: Resume
  },
  {
    path: '/resumedetail/:id',
    name: 'ResumeContent',
    meta: {
      title: '模板详情',
      keepAlive: true,
      isShowComNav: false
    },
    component: ResumeContent
  },
  {
    path: '/designer',
    name: 'Designer',
    meta: {
      title: '简历编辑',
      keepAlive: true,
      isShowComNav: false
    },
    component: Designer
  },
  {
    path: '/designResume/:id',
    name: 'DesignResume',
    meta: {
      title: '编辑简历',
      keepAlive: true,
      isShowComNav: false
    },
    component: DesignResume
  },
  {
    path: '/pdfPreview',
    name: 'PdfPreview',
    meta: {
      title: 'PDF预览',
      keepAlive: false,
      isShowComNav: false
    },
    component: PdfPreview
  },
  {
    path: '/resumePreview',
    name: 'ResumePreview',
    meta: {
      title: '简历预览',
      keepAlive: false,
      isShowComNav: false
    },
    component: ResumePreview
  },
  {
    path: '/legoDesigner',
    name: 'LegoDesigner',
    meta: {
      title: '积木编辑',
      keepAlive: true,
      isShowComNav: false
    },
    component: LegoDesigner
  },
  {
    path: '/legoTemplateList',
    name: 'LegoTemplateList',
    meta: {
      title: '积木模板',
      keepAlive: true,
      isShowComNav: true
    },
    component: LegoTemplateList
  },
  {
    path: '/legoPrintPdfPreview',
    name: 'LegoPrintPdfPreview',
    meta: {
      title: '积木预览',
      keepAlive: false,
      isShowComNav: false
    },
    component: LegoPrintPdfPreview
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  }
});

router.beforeEach((to, from, next) => {
  const isTemplatePage = location.pathname.endsWith('.html');
  if (!isTemplatePage) {
    useHead({
      title: `猫步简历 - ${String(to.meta.title || title)}`,
      meta: [
        {
          name: 'description',
          content: String(to.meta?.description || description)
        },
        {
          name: 'keywords',
          content: String(to.meta?.keywords || keywords)
        }
      ]
    });
  }
  next();
});

export default router;
