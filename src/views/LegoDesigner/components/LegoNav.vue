<template>
  <div class="lego-nav-box">
    <div class="nav-left">
      <logo-com icon-color="#74a274" font-color="#74a274" />
    </div>
    <div class="nav-right">
      <el-tooltip effect="dark" content="下载到本地" placement="bottom">
        <div class="icon-box icon-download" @click="downloadResume">
          <svg-icon icon-name="icon-xiazai" color="#fff" size="17px" />
          <span class="icon-tips">导出</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="预览" placement="bottom">
        <div class="icon-box" @click="previewResume">
          <svg-icon icon-name="icon-yulan1" color="#555" size="19px" />
          <span class="icon-tips">预览</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="保存草稿" placement="bottom">
        <div class="icon-box" @click="saveDraft">
          <svg-icon icon-name="icon-caogaoxiang1" color="#555" size="17px" />
          <span class="icon-tips">保存</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="重置" placement="bottom">
        <div class="icon-box" @click="reset">
          <svg-icon icon-name="icon-zhongzhi" color="#555" size="17px" />
          <span class="icon-tips">重置</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="导出为JSON" placement="bottom">
        <div class="icon-box" @click="exportJSON">
          <svg-icon icon-name="icon-xiazai" color="#555" size="17px" />
          <span class="icon-tips">JSON</span>
        </div>
      </el-tooltip>
    </div>
  </div>

  <download-dialog
    :dialog-download-visible="dialogDownloadVisible"
    @close-download-dialog="closeDownloadDialog"
    @download-file="downloadResumeFile"
  />

  <preview-image v-show="dialogPreviewVisible" @close="closePreview">
    <render-page />
  </preview-image>

  <process-bar-dialog
    :dialog-visible="dialogVisible"
    :percentage-num="percentage"
    @cancle="cancleProgress"
  />
</template>

<script lang="ts" setup>
  import appStore from '@/store';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import FileSaver from 'file-saver';
  import { cloneDeep } from 'lodash';
  import { storeToRefs } from 'pinia';
  import DownloadDialog from './DownloadDialog/DownloadDialog.vue';
  import PreviewImage from '../render/PreviewImage/PreviewImage.vue';
  import RenderPage from '../render/index.vue';
  import { CONFIG } from '../config/lego';
  import moment from 'moment';
  import { getImgBase64URL } from '../utils/html2img';
  import { legoUserResumeAsync } from '@/http/api/lego';
  import { exportLegoPNG, exportLegoPdf } from '../utils/pdf';
  import ProcessBarDialog from '@/components/ProcessBarDialog/ProcessBarDialog.vue';
  import { onBeforeRouteLeave } from 'vue-router';

  const { HJSchemaJsonStore, draftTips } = storeToRefs(appStore.useLegoJsonStore);
  const { resetHJSchemaJsonData } = appStore.useLegoJsonStore;
  const { setUuid } = appStore.useRefreshStore;
  const { resetSelectWidget } = appStore.useLegoSelectWidgetStore;
  const { id, category } = useRoute().query;

  const props = defineProps<{
    pagesRefs: any;
    postWorkInfo: any;
    templateInfo: any;
  }>();

  const exportJSON = () => {
    const jsonData = cloneDeep(HJSchemaJsonStore.value);
    const data = JSON.stringify(jsonData, null, 4);
    const blob = new Blob([data], { type: '' });
    FileSaver.saveAs(blob, `${HJSchemaJsonStore.value.config.title}.json`);
  };

  const dialogDownloadVisible = ref<boolean>(false);
  const downloadResume = () => {
    dialogDownloadVisible.value = true;
  };

  const closeDownloadDialog = () => {
    dialogDownloadVisible.value = false;
  };

  const downloadResumeFile = async (type: string) => {
    await saveDraft();
    closeDownloadDialog();
    await generateReport(type);
  };

  const dialogVisible = ref<boolean>(false);
  const percentage = ref<number>(10);

  const generateReport = async (type: string) => {
    dialogVisible.value = true;
    percentage.value = 10;

    const progressTimer = setInterval(() => {
      if (percentage.value < 90) {
        percentage.value += 8;
      } else {
        clearInterval(progressTimer);
      }
    }, 180);

    try {
      if (type === 'pdf') {
        await exportLegoPdf(_id.value);
      } else {
        await exportLegoPNG(_id.value);
      }

      percentage.value = 100;
      setTimeout(() => {
        cancleProgress();
      }, 650);
    } catch (error) {
      console.error('导出失败', error);
      ElMessage.error('导出失败，请重试');
      cancleProgress();
    } finally {
      clearInterval(progressTimer);
    }
  };

  const cancleProgress = () => {
    dialogVisible.value = false;
    percentage.value = 10;
  };

  const dialogPreviewVisible = ref<boolean>(false);
  const previewResume = () => {
    dialogPreviewVisible.value = true;
  };

  const closePreview = () => {
    dialogPreviewVisible.value = false;
  };

  const imgUrl = ref<string>('');
  const isCanSave = ref<boolean>(true);
  const _id = ref<string>(id as string);

  const saveDraft = async () => {
    if (CONFIG.SAVE_LOCAL) {
      const local = localStorage.getItem('LegoLogo');
      if (local) {
        const temp = JSON.parse(local);
        temp[HJSchemaJsonStore.value.id] = HJSchemaJsonStore.value;
        localStorage.setItem('LegoLogo', JSON.stringify(temp));
      } else {
        const temp: { [propName: string]: any } = {};
        temp[HJSchemaJsonStore.value.id] = HJSchemaJsonStore.value;
        localStorage.setItem('LegoLogo', JSON.stringify(temp));
      }
      const time = moment(new Date()).format('YYYY.MM.DD HH:mm:ss');
      draftTips.value = `已保存草稿  ${time}`;
      ElMessage.success('保存成功');
      return;
    }

    if (!isCanSave.value) {
      return;
    }

    isCanSave.value = false;
    draftTips.value = '保存中......';
    imgUrl.value = await getImgBase64URL(props.pagesRefs[0]);
    const params = {
      id: _id.value,
      previewUrl: imgUrl.value,
      category,
      lego_json: HJSchemaJsonStore.value
    };

    const data = await legoUserResumeAsync(params);
    if (data.data.status === 200) {
      const time = moment(new Date()).format('YYYY.MM.DD HH:mm:ss');
      draftTips.value = `已保存草稿  ${time}`;
      _id.value = data.data.data._id;
      ElMessage.success('保存成功');
    } else {
      ElMessage.error(data.data.message);
    }

    isCanSave.value = true;
  };

  const reset = () => {
    ElMessageBox.confirm('此操作会重置画布至初始状态，是否继续?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        const jsonId = HJSchemaJsonStore.value.id;
        resetHJSchemaJsonData(jsonId);
        resetSelectWidget();
        setUuid();
      })
      .catch(() => {});
  };

  onBeforeUnmount(async () => {
    draftTips.value = '';
    resetHJSchemaJsonData();
    resetSelectWidget();
    setUuid();
  });

  onBeforeRouteLeave((to, from, next) => {
    ElMessageBox.confirm('离开前请确保您编辑的内容已保存草稿！', '警告', {
      confirmButtonText: '保存草稿并离开',
      cancelButtonText: '直接离开',
      showCancelButton: true,
      closeOnClickModal: false,
      closeOnPressEscape: false,
      distinguishCancelAndClose: true,
      type: 'warning',
      beforeClose: async (action, instance, done) => {
        if (action === 'confirm') {
          instance.confirmButtonLoading = true;
          await saveDraft();
          instance.confirmButtonLoading = false;
          done();
        } else if (action === 'close') {
          done();
          return;
        } else {
          done();
          next();
        }
      }
    })
      .then(() => {
        next();
      })
      .catch(() => {});
  });
</script>

<style lang="scss" scoped>
  .lego-nav-box {
    background-color: #fff;
    height: 60px;
    width: 100%;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    .nav-left {
      width: 300px;
      height: 100%;
      display: flex;
      align-items: center;
      user-select: none;
      padding: 0 0 0 40px;
    }
    .nav-right {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 30px;
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
