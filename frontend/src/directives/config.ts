// directives/config.ts
import { App, DirectiveBinding } from 'vue';
import appStore from '@/store';

const configDirectives = {
  install(app: App) {
    app.directive('config', {
      mounted(el, binding: DirectiveBinding) {
        const configStore: any = appStore.useWebsiteConfigStore.websiteConfig;
        const configKey = binding.arg;
        if (!configKey || !configStore[configKey]) {
          el.style.display = 'none';
        }
      },
      updated(el, binding: DirectiveBinding) {
        // 同步检查，不使用 nextTick 避免触发 ElDropdown 等组件的递归更新
        const configStore: any = appStore.useWebsiteConfigStore.websiteConfig;
        const configKey = binding.arg;
        const shouldHide = !configKey || !configStore[configKey];
        const newDisplay = shouldHide ? 'none' : '';
        if (el.style.display !== newDisplay) {
          el.style.display = newDisplay;
        }
      }
    });
  }
};

export default configDirectives;
