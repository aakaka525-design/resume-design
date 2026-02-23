import { getWebsiteConfigAsync } from '@/http/api/websiteConfig';
import { defineStore } from 'pinia';
import { title } from '@/config/seo';

export const useWebsiteConfigStore = defineStore('websiteConfig', () => {
  const websiteConfig = reactive<{
    all_free: boolean;
    open_comment: boolean;
    website_title: string;
  }>({
    all_free: true,
    open_comment: false,
    website_title: title
  });

  function saveWebsiteConfig(websiteConfigData: any) {
    websiteConfig.open_comment = Boolean(websiteConfigData.open_comment);
    websiteConfig.all_free = Boolean(websiteConfigData.all_free);
    websiteConfig.website_title = websiteConfigData.website_title || title;
    document.title = websiteConfig.website_title;
  }
  // 查询网站配置信息
  async function getWebsiteConfig() {
    const data = await getWebsiteConfigAsync();
    if (data.status === 200) {
      saveWebsiteConfig(data.data);
    } else {
      ElMessage.error(data.message);
    }
  }
  return {
    getWebsiteConfig,
    websiteConfig
  };
});
