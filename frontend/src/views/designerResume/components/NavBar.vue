<template>
  <nav class="nav-box">
    <div class="design-nav-left">
      <div class="return-icon" @click="returnPage">
        <el-icon><ArrowLeftBold /></el-icon>
      </div>
      <div class="resume-title">
        <p v-show="!isShowIpt">
          {{ HJNewJsonStore.config.title }}
          <el-icon :size="20" color="#74a274" @click="changeTitle">
            <Edit />
          </el-icon>
        </p>
        <el-input
          v-show="isShowIpt"
          ref="titleIpf"
          v-model="HJNewJsonStore.config.title"
          autofocus
          placeholder="请输入标题"
          @blur="blurTitle"
        />
      </div>
      <div v-if="draftTips" class="draft-tips-box">
        <span class="draft-tips">{{ draftTips }}</span>
        <svg-icon icon-name="icon-shijian1" color="#999999" size="14px" />
      </div>
    </div>
    <div class="nav-center"></div>
    <div class="nav-right">
      <el-tooltip effect="dark" content="下载到本地" placement="bottom">
        <div class="icon-box icon-download" @click="downloadResume">
          <svg-icon icon-name="icon-xiazai" color="#fff" size="17px" />
          <span class="icon-tips">导出</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="保存为草稿" placement="bottom">
        <div class="icon-box" @click="saveDraft">
          <svg-icon icon-name="icon-caogaoxiang1" color="#555" size="17px" />
          <span class="icon-tips">暂存</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="预览简历" placement="bottom">
        <div class="icon-box" @click="previewResume">
          <svg-icon icon-name="icon-yulan1" color="#555" size="19px" />
          <span class="icon-tips">预览</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="重置所有设置" placement="bottom">
        <div class="icon-box" @click="reset">
          <svg-icon icon-name="icon-zhongzhi" color="#555" size="17px" />
          <span class="icon-tips">重置</span>
        </div>
      </el-tooltip>
    </div>
  </nav>

  <download-dialog
    :dialog-download-visible="dialogDownloadVisible"
    @close-download-dialog="closeDownloadDialog"
    @download-file="downloadResumeFile"
  />
</template>

<script lang="ts" setup>
  import appStore from '@/store';
  import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
  import 'element-plus/es/components/message-box/style/index';
  import { storeToRefs } from 'pinia';
  import DownloadDialog from '../../designer/components/DownloadDialog.vue';
  import { debounce } from 'lodash';
  import { saveDraftAsync } from '@/http/api/createTemplate';
  import { formatListDate } from '@/utils/common';

  const { HJNewJsonStore } = storeToRefs(appStore.useCreateTemplateStore);
  const emit = defineEmits(['generateReport', 'reset', 'previewResume']);
  const route = useRoute();
  const id = route.params.id;

  const router = useRouter();
  const returnPage = () => {
    router.go(-1);
  };

  const titleIpf = ref<any>(null);
  const isShowIpt = ref<boolean>(false);
  const changeTitle = () => {
    isShowIpt.value = true;
    titleIpf.value.focus();
  };

  const blurTitle = () => {
    isShowIpt.value = false;
  };

  const draftTips = ref<string>('');
  const saveDataToLocal = () => {
    return new Promise(async (resolve) => {
      const data = {
        templateId: id,
        templateJson: HJNewJsonStore.value
      };
      const result = await saveDraftAsync(data);
      if (result.data.status === 200) {
        draftTips.value = `已保存：${formatListDate(result.data.data.updateDate)}`;
        resolve('保存草稿成功');
      } else {
        ElNotification({
          title: '保存失败',
          message: result.data.message,
          type: 'error'
        });
        resolve(null);
      }
    });
  };

  const saveDraft = () => {
    saveDataToLocal();
  };

  const debounced = debounce(() => {
    saveDataToLocal();
  }, 5000);

  watch(
    () => HJNewJsonStore.value,
    (newVal, oldVal) => {
      if (newVal && oldVal.id) {
        debounced();
      }
    },
    {
      deep: true
    }
  );

  const previewResume = () => {
    emit('previewResume');
  };

  const dialogDownloadVisible = ref<boolean>(false);
  const downloadResume = () => {
    dialogDownloadVisible.value = true;
  };

  const closeDownloadDialog = () => {
    dialogDownloadVisible.value = false;
  };

  const isDownloading = ref(false);
  const downloadResumeFile = async (type: string) => {
    if (isDownloading.value) {
      ElNotification({
        title: '提示',
        message: '正在处理下载请求，请稍候...',
        type: 'warning',
        duration: 2000
      });
      return;
    }

    isDownloading.value = true;

    try {
      const data = await saveDataToLocal();
      if (data) {
        emit('generateReport', type);
        closeDownloadDialog();
      }
    } finally {
      isDownloading.value = false;
    }
  };

  const reset = () => {
    ElMessageBox.confirm('此操作会重置简历至初始状态，是否继续?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        emit('reset');
        draftTips.value = '';
      })
      .catch(() => {});
  };

  defineExpose({
    saveDataToLocal
  });
</script>

<style lang="scss" scopeds>
  .nav-box {
    height: 50px;
    width: 100%;
    background-color: #fff;
    position: sticky;
    top: 0;
    display: flex;
    box-shadow: 0 5px 21px 0 rgb(78 78 78 / 5%);
    z-index: 20;
    .design-nav-left {
      display: flex;
      align-items: center;
      user-select: none;
      padding: 0 0 0 20px;
      .return-icon {
        width: 30px;
        height: 30px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        transition: all 0.3s;
        &:hover {
          opacity: 0.8;
        }
      }
      .resume-title {
        flex-shrink: 0;
        p {
          display: flex;
          align-items: center;
          font-size: 16px;
          .el-icon {
            margin-left: 5px;
            cursor: pointer;
            margin-top: 1px;
          }
        }
        .el-input {
          width: 200px;
        }
      }
      .draft-tips-box {
        height: 100%;
        display: flex;
        align-items: center;
        margin-left: 15px;
        flex-shrink: 0;
        .draft-tips {
          margin-right: 7px;
          font-size: 12px;
          color: #999999;
        }
      }
    }
    .nav-center {
      flex: 1;
    }
    .nav-right {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 50px;
      .icon-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #555;
        cursor: pointer;
        padding: 0 15px;
        height: 100%;
        transition: all 0.3s;
        &:hover {
          background-color: rgba($color: #74a274, $alpha: 0.1);
          color: #74a274;
        }
        .icon-tips {
          font-size: 12px;
          margin-top: 8px;
        }
      }
      .icon-download {
        background-color: rgba($color: #74a274, $alpha: 1);
        color: #fff;
        &:hover {
          background-color: rgba($color: #74a274, $alpha: 0.9);
          color: #fff;
        }
      }
    }
  }
</style>
