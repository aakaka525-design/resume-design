<template>
  <el-config-provider size="default" :locale="zhCn">
    <nav-bar
      v-if="route.meta.isShowComNav"
      :key="refreshUuid"
      bg-color="#fff"
      font-color="green"
      position="sticky"
      icon-color="green"
    />
    <div v-show="!isLoading">
      <router-view :key="refreshUuid" />
    </div>
    <loading-com-vue v-show="isLoading" />
  </el-config-provider>
</template>

<script lang="ts" setup>
  import zhCn from 'element-plus/es/locale/lang/zh-cn';
  import LoadingComVue from '@/components/Loading/LoadingCom.vue';
  import { addWebsiteViewsAsync } from '@/http/api/panel';
  import appStore from '@/store';
  import { storeToRefs } from 'pinia';

  const route = useRoute();
  const { isLoading } = storeToRefs(appStore.useLoadingStore);
  const { refreshUuid } = appStore.useRefreshStore;

  const { saveToken } = appStore.useTokenStore;
  const { token } = appStore.useTokenStore;
  const { saveUserInfo, getAndUpdateUserInfo, getUserIntegralTotal } = appStore.useUserInfoStore;

  const initUser = async () => {
    if (token) {
      await getAndUpdateUserInfo();
      await getUserIntegralTotal();
      return;
    }

    try {
      const resp = await fetch(`${import.meta.env.VITE_SERVER_ADDRESS}/huajian/auth/autoLogin`);
      const data = await resp.json();
      if (data.status === 200 && data.data) {
        saveToken(data.data.token);
        saveUserInfo(data.data.userInfo);
        await getAndUpdateUserInfo();
        await getUserIntegralTotal();
      }
    } catch (error) {
      console.warn('自动登录失败', error);
    }
  };

  const addWebsiteViews = () => {
    addWebsiteViewsAsync();
  };

  const { getWebsiteConfig } = appStore.useWebsiteConfigStore;

  onMounted(() => {
    initUser();
    addWebsiteViews();
    getWebsiteConfig();
  });
</script>
