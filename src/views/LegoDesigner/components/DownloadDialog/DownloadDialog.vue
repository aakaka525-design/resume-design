<template>
  <el-dialog
    class="download-resume-select"
    :model-value="dialogDownloadVisible"
    title="下载作品"
    width="500px"
    append-to-body
    @close="handleClose"
  >
    <div class="content-box">
      <div class="content-down-btn">
        <div class="download-item" @click="download('img')">
          <div class="download-com-box img-box">
            <svg-icon icon-name="icon-tupian" color="#fff" size="26px" />
            <span>下载图片</span>
          </div>
          <p>适合微信、QQ发送</p>
        </div>

        <div class="download-item" @click="download('pdf')">
          <div class="download-com-box pdf-box">
            <svg-icon icon-name="icon-pdf" color="#fff" size="26px" />
            <span>下载 PDF</span>
          </div>
          <p>适合打印与投递（推荐）</p>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script lang="ts" setup>
  const emit = defineEmits(['closeDownloadDialog', 'downloadFile']);

  withDefaults(
    defineProps<{
      dialogDownloadVisible: boolean;
    }>(),
    {
      dialogDownloadVisible: false
    }
  );

  const download = (type: string) => {
    emit('downloadFile', type);
  };

  const handleClose = () => {
    emit('closeDownloadDialog');
  };
</script>

<style lang="scss" scoped>
  .download-resume-select {
    .content-box {
      .content-down-btn {
        display: flex;
        justify-content: center;
        gap: 20px;

        .download-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;

          .download-com-box {
            width: 110px;
            height: 110px;
            border-radius: 5px;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #fff;

            span {
              margin-top: 10px;
            }

            &:hover {
              transform: translateY(-2px);
              opacity: 0.9;
            }
          }

          p {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
          }

          .img-box {
            background: linear-gradient(90deg, #a986ff 0, #9861ff 100%);
          }

          .pdf-box {
            background: linear-gradient(149deg, #ffa98f 0, #ff6464 100%);
          }
        }
      }
    }
  }
</style>
