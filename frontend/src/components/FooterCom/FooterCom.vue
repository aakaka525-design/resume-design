<template>
  <footer class="global-footer">
    <div class="content">
      <div class="brand">
        <h3>猫步简历（本地版）</h3>
        <p>个人项目最小功能：简历编辑 + 积木编辑。</p>
      </div>
      <div class="links">
        <a @click.prevent="toResume" href="/resume">简历模板</a>
        <a @click.prevent="toLego" href="/legoTemplateList">积木模板</a>
      </div>
    </div>
    <div class="copyright">Copyright © 2026 Local Resume Editor</div>
  </footer>
</template>

<script setup lang="ts">
  const router = useRouter();

  const toResume = () => {
    router.push('/resume');
  };

  const toLego = () => {
    router.push('/legoTemplateList');
  };
</script>

<style lang="scss" scoped>
  .global-footer {
    margin-top: 30px;
    background: #1f2937;
    color: #e5e7eb;
    padding: 24px 20px;

    .content {
      max-width: 1080px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;

      .brand h3 {
        margin: 0 0 6px;
      }

      .brand p {
        margin: 0;
        color: #9ca3af;
      }

      .links {
        display: flex;
        gap: 16px;

        a {
          color: #d1fae5;
          text-decoration: none;
          cursor: pointer;
        }
      }
    }

    .copyright {
      max-width: 1080px;
      margin: 14px auto 0;
      color: #9ca3af;
      font-size: 13px;
    }
  }
</style>
