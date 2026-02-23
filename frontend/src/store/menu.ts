import { getIndexMenuListAsync } from '@/http/api/menu';
import { buildTree } from '@/utils/common';
import { defineStore } from 'pinia';

export const useIndexMenuStore = defineStore('indexMenuStore', () => {
  const indexMenuList = ref<any>([]);

  function saveIndexMenu(indexMenu: any) {
    indexMenuList.value = indexMenu;
  }

  async function getIndexMenuList() {
    const data = await getIndexMenuListAsync();
    if (data.status === 200) {
      saveIndexMenu(buildTree(data.data));
    } else {
      ElMessage({
        message: data.message,
        type: 'error'
      });
    }
  }

  return {
    indexMenuList,
    saveIndexMenu,
    getIndexMenuList
  };
});
