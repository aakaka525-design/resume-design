<!-- 主题色选择组件 -->
<template>
  <div class="color-picker-box">
    <div class="item-box">
      <el-popover
        popper-class="color-picker-box-popover-box"
        :teleported="teleported"
        :width="276"
        trigger="click"
      >
        <template #reference>
          <div class="custom-color-btn"> </div>
        </template>
        <div @click.prevent="">
          <color-picker
            :is-widget="true"
            :pure-color="pureColor"
            shape="circle"
            use-type="pure"
            :round-history="true"
            @pure-color-change="pureColorChange"
          />
        </div>
      </el-popover>
    </div>
    <template v-if="showList">
      <div v-for="(item, index) in colorListFilter" :key="item.hex" :class="['item-box']">
        <span
          :class="['item', { active: index === curentIndex || normalizedModelValue === item.hex }]"
          :style="{
            'background-color': item.hex
          }"
          @click="changTheme(index, item)"
        ></span>
      </div>
    </template>
  </div>
</template>
<script lang="ts" setup>
  import { ColorPicker } from 'vue3-colorpicker';
  import 'vue3-colorpicker/style.css';

  interface IColor {
    modelValue?: any;
    teleported?: boolean;
    showList?: boolean;
    listNumber?: number;
  }
  const props = withDefaults(defineProps<IColor>(), {
    modelValue: '',
    teleported: true,
    showList: true,
    listNumber: 0
  });

  const emit = defineEmits(['update:modelValue', 'change']);

  const RGB_COLOR_PATTERN = /^rgb\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/i;

  const normalizeThemeColor = (value?: string) => {
    if (!value || typeof value !== 'string') {
      return '';
    }
    const trimmedValue = value.trim();
    const matchedValue = trimmedValue.match(RGB_COLOR_PATTERN);
    if (!matchedValue) {
      return trimmedValue;
    }
    const [red, green, blue] = matchedValue.slice(1, 4).map((num) => {
      const normalized = Math.max(0, Math.min(255, Number(num) || 0));
      return normalized.toString(16).padStart(2, '0');
    });
    return `#${red}${green}${blue}`;
  };

  const pureColor = ref<string>('');

  const normalizedModelValue = computed(() => normalizeThemeColor(props.modelValue));

  watch(
    () => props.modelValue,
    (newVal) => {
      const normalizedValue = normalizeThemeColor(newVal);
      pureColor.value = normalizedValue.startsWith('#') ? normalizedValue : '';
    },
    {
      immediate: true
    }
  );

  // 颜色列表
  const colorList = reactive<Array<{ rgb: string; hex: string }>>([
    {
      rgb: 'rgb(37, 70, 101)',
      hex: '#254665'
    },
    {
      rgb: 'rgb(221, 65, 94)',
      hex: '#dd415e'
    },
    {
      rgb: 'rgb(150, 122, 91)',
      hex: '#967a5b'
    },
    {
      rgb: 'rgb(51, 144, 205)',
      hex: '#3390cd'
    },
    {
      rgb: 'rgb(245, 79, 79)',
      hex: '#f54f4f'
    },
    {
      rgb: 'rgb(77, 77, 77)',
      hex: '#4d4d4d'
    },
    {
      rgb: 'rgb(170, 132, 96)',
      hex: '#aa8460'
    },
    {
      rgb: 'rgb(118, 186, 49)',
      hex: '#76ba31'
    },
    {
      rgb: 'rgb(100, 126, 201)',
      hex: '#647ec9'
    }
  ]);

  const colorListFilter = computed(() => {
    if (props.listNumber > 0) {
      return colorList.slice(0, props.listNumber);
    } else {
      return colorList;
    }
  });

  // 更改主题色
  const curentIndex = ref<number>(-1);
  const changTheme = (index: number, item: { rgb: string; hex: string }) => {
    curentIndex.value = index;
    emit('update:modelValue', item.hex);
    emit('change', item.hex);
  };

  // 纯色改变
  const pureColorChange = (value: string) => {
    const normalizedValue = normalizeThemeColor(value);
    curentIndex.value = -1;
    emit('update:modelValue', normalizedValue);
    emit('change', normalizedValue);
  };
</script>
<style lang="scss" scoped>
  .color-picker-box {
    display: flex;
    flex-wrap: wrap;
    align-content: space-between;
    user-select: none;
    .item-box {
      width: 30px;
      height: 26px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      .custom-color-btn {
        width: 20px;
        height: 20px;
        border: 1px solid #ccc;
        cursor: pointer;
        background-color: v-bind('props.modelValue');
      }
      .item {
        display: block;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        cursor: pointer;
      }
    }

    .active {
      background-color: rgb(214, 21, 4);
      box-shadow: rgb(99, 100, 99) 0px 0px 10px;
    }
  }
</style>
<style lang="scss">
  .color-picker-box-popover-box {
    padding: 0 !important;
    width: 278px !important;
    :deep(.zs-color-picker) {
      border-radius: 50%;
      .zs-color-picker-btn {
        border-radius: 50%;
        .zs-color-picker-btn-color {
          border-radius: 50%;
        }
      }
      .zs-color-picker-panel {
        z-index: 5;
      }
    }
  }
</style>
