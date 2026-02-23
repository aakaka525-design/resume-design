<template>
  <header :class="['nav-bar-box', { 'background-nav': Boolean(props.bgColor) }]" :style="headerStyle">
    <logo-com />
    <div class="center">
      <el-menu
        :default-active="route.path"
        class="menu"
        mode="horizontal"
        :ellipsis="false"
        router
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          {{ item.name }}
        </el-menu-item>
      </el-menu>
    </div>
    <div class="right">
      <el-button type="primary" @click="toResume">简历模板</el-button>
      <el-button plain @click="toLego">积木模板</el-button>
    </div>
  </header>
</template>

<script setup lang="ts">
  import appStore from '@/store';
  import { storeToRefs } from 'pinia';
  import type { CSSProperties } from 'vue';

  interface IBgcColor {
    bgColor?: string;
    fontColor?: string;
    position?: string;
    iconColor?: string;
  }

  const props = withDefaults(defineProps<IBgcColor>(), {
    bgColor: '',
    fontColor: '',
    iconColor: '#74a274',
    position: 'sticky'
  });

  const router = useRouter();
  const route = useRoute();

  const { getIndexMenuList } = appStore.useIndexMenuStore;
  const { indexMenuList } = storeToRefs(appStore.useIndexMenuStore);

  onMounted(() => {
    getIndexMenuList();
  });

  const menuItems = computed(() => {
    const enabled = indexMenuList.value
      .filter((item: any) => item.status === 1 && item.path)
      .map((item: any) => ({
        name: item.name,
        path: item.path
      }));

    if (enabled.length) {
      return enabled;
    }

    return [
      { name: '首页', path: '/' },
      { name: '简历模板', path: '/resume' },
      { name: '积木模板', path: '/legoTemplateList' }
    ];
  });

  const headerStyle = computed<CSSProperties>(() => ({
    backgroundColor: props.bgColor || '#fff',
    position: props.position as CSSProperties['position']
  }));

  const toResume = () => {
    router.push('/resume');
  };

  const toLego = () => {
    router.push('/legoTemplateList');
  };
</script>

<style scoped lang="scss">
  .nav-bar-box {
    width: 100%;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    box-sizing: border-box;
    z-index: 20;
    box-shadow: 0 2px 10px rgb(0 0 0 / 6%);

    .center {
      flex: 1;
      display: flex;
      justify-content: center;
      margin: 0 24px;

      .menu {
        border-bottom: none;
      }
    }

    .right {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }
</style>
