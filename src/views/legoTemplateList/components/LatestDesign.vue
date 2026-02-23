<template>
  <div class="latest-title">
    <h1>最近的设计</h1>
  </div>
  <div class="latest-card-box">
    <div class="card-box-item space-design" @mouseover="mouseover" @mouseleave="mouseleave">
      <svg-icon
        icon-name="icon-jiahao"
        color="#9c9c9c"
        size="48px"
        class-name="catalog-icon"
      />
      <div ref="maskLayerRef" class="mask-layer">
        <div class="design-button" @click="toSpaceDesign">空白制作</div>
      </div>
    </div>
    <div v-for="(item, index) in legoPersonList" :key="index" class="card-box-item">
      <person-template-card
        :card-data="item"
        :width="cardWidth"
        :height="cardHeight"
        @to-design="toDesignDetail"
        @delete-person-template="deletePersonTemplate"
      />
    </div>
  </div>
</template>
<script lang="ts" setup>
  import PersonTemplateCard from './PersonTemplateCard.vue';

  const emit = defineEmits(['deletePersonTemplate']);

  const props = defineProps<{
    legoPersonList: any;
    cardWidth: any;
    cardHeight: any;
    category: string;
  }>();

  const router = useRouter();
  const toDesignDetail = (cardData: { _id: any; category: any }) => {
    router.push({
      path: '/legoDesigner',
      query: {
        id: cardData._id,
        category: cardData.category
      }
    });
  };

  const maskLayerRef = ref<any>(null);
  const mouseover = () => {
    maskLayerRef.value.style.opacity = 1;
  };

  const mouseleave = () => {
    maskLayerRef.value.style.opacity = 0;
  };

  const toSpaceDesign = () => {
    router.push({
      path: '/legoDesigner',
      query: {
        category: props.category
      }
    });
  };

  const deletePersonTemplate = (id: string) => {
    emit('deletePersonTemplate', id);
  };
</script>
<style lang="scss" scoped>
  .latest-title {
    height: 70px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #dfdfdf;
    margin-top: 20px;
    h1 {
      color: #0d1216;
      font-size: 16px;
      letter-spacing: 3px;
      font-weight: 600;
    }
  }
  .latest-card-box {
    display: flex;
    padding: 30px 0 0 0;
    flex-wrap: wrap;
    .space-design {
      width: v-bind('cardWidth');
      height: calc(v-bind('cardHeight'));
      background-color: #fff;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      &:hover {
        box-shadow: 0px 16px 22px 2px rgb(0 37 58 / 24%);
        transform: translateY(2%) scale(1.03);
      }
      .mask-layer {
        height: 100%;
        width: 100%;
        border-radius: 5px 5px 0 0;
        position: absolute;
        left: 0;
        top: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        opacity: 0;
        transition: all 0.3s;
        .design-button {
          width: 100px;
          height: 30px;
          font-size: 13px;
          background-color: #2cbd99;
          border-radius: 6px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #ffffff;
          transition: all 0.3s;
          &:hover {
            background-color: rgba(#42aa90, 0.7);
          }
        }
      }
    }
    .card-box-item {
      &:not(:nth-child(4n)) {
        margin-right: 33px;
      }
    }
  }
</style>
