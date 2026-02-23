<template>
  <div class="index-box">
    <section class="hero">
      <h1>本地简历编辑器</h1>
      <p>仅保留个人项目所需的最小功能：简历编辑、积木编辑与本地导出。</p>
      <div class="actions">
        <el-button type="primary" size="large" @click="toResume">开始编辑简历</el-button>
        <el-button size="large" @click="toLego">进入积木编辑</el-button>
      </div>
    </section>

    <section class="section">
      <h2>核心入口</h2>
      <div class="cards">
        <div class="card" @click="toResume">
          <h3>简历模板</h3>
          <p>选择模板并进入 `designResume` 编辑链路。</p>
        </div>
        <div class="card" @click="toLegoTemplates">
          <h3>积木模板</h3>
          <p>选择模板或空白页面，进入 `legoDesigner` 编辑链路。</p>
        </div>
      </div>
    </section>

    <footer-com />
  </div>
</template>

<script setup lang="ts">
  import FooterCom from '@/components/FooterCom/FooterCom.vue';
  import { useHead } from '@vueuse/head';

  const router = useRouter();

  useHead({
    title: '猫步简历 - 本地简历编辑器',
    meta: [
      {
        name: 'description',
        content: '本地个人简历编辑器，支持简历编辑与积木编辑最小链路。'
      }
    ]
  });

  const toResume = () => {
    router.push('/resume');
  };

  const toLego = () => {
    router.push('/legoDesigner');
  };

  const toLegoTemplates = () => {
    router.push('/legoTemplateList');
  };
</script>

<style scoped lang="scss">
  .index-box {
    min-height: calc(100vh - 64px);
    background: linear-gradient(180deg, #f5f9f5 0%, #fff 45%);

    .hero {
      max-width: 1080px;
      margin: 0 auto;
      padding: 72px 24px 36px;

      h1 {
        margin: 0;
        font-size: 42px;
        color: #1f2937;
      }

      p {
        margin: 14px 0 28px;
        color: #4b5563;
        font-size: 16px;
      }

      .actions {
        display: flex;
        gap: 12px;
      }
    }

    .section {
      max-width: 1080px;
      margin: 0 auto;
      padding: 24px;

      h2 {
        margin-bottom: 16px;
      }

      .cards {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }

      .card {
        cursor: pointer;
        background: #fff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.2s ease;

        &:hover {
          border-color: #74a274;
          transform: translateY(-2px);
        }

        h3 {
          margin: 0 0 8px;
        }

        p {
          margin: 0;
          color: #6b7280;
        }
      }
    }
  }

  @media (max-width: 768px) {
    .index-box .section .cards {
      grid-template-columns: 1fr;
    }

    .index-box .hero h1 {
      font-size: 34px;
    }
  }
</style>
