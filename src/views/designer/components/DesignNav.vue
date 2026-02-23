<template>
  <nav class="nav-box">
    <div class="nav-left">
      <logo-com icon-color="#74a274" font-color="#74a274" />
    </div>
    <div class="nav-center">
      <div class="left">
        <div class="nav-center-left-box">
          <el-tooltip effect="dark" content="新增任意简历模块" placement="bottom">
            <div class="icon-box" @click="openAddDrawer">
              <svg-icon icon-name="icon-database" color="#555" size="17px" />
              <span class="icon-tips">添加模块</span>
            </div>
          </el-tooltip>
          <el-tooltip effect="dark" content="切换另一个模板" placement="bottom">
            <div class="icon-box" @click="switchDrawer">
              <svg-icon icon-name="icon-shangchengmoban" color="#555" size="17px" />
              <span class="icon-tips">切换模板</span>
            </div>
          </el-tooltip>
          <el-tooltip effect="dark" content="查看JSON" placement="bottom">
            <div class="icon-box" @click="viewJSON">
              <svg-icon icon-name="icon-json1" color="#555" size="17px" />
              <span class="icon-tips">查看JSON</span>
            </div>
          </el-tooltip>
        </div>
        <div class="draft-tips-box">
          <span class="draft-tips">{{ draftTips }}</span>
        </div>
      </div>
      <div class="center">
        <p v-show="!isShowIpt">
          {{ resumeJsonNewStore.TITLE }}
          <el-icon :size="20" color="#409eff" @click="changeTitle">
            <Edit />
          </el-icon>
        </p>
        <el-input
          v-show="isShowIpt"
          ref="titleIpf"
          v-model="resumeJsonNewStore.TITLE"
          autofocus
          placeholder="请输入标题"
          @blur="blurTitle"
        />
      </div>
      <div class="right" />
    </div>
    <div class="nav-right">
      <el-tooltip effect="dark" content="下载到本地" placement="bottom">
        <div class="icon-box icon-download" @click="downloadResume">
          <svg-icon icon-name="icon-xiazai" color="#fff" size="17px" />
          <span class="icon-tips">导出</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="预览简历" placement="bottom">
        <div class="icon-box" @click="previewResume">
          <svg-icon icon-name="icon-yulan1" color="#555" size="19px" />
          <span class="icon-tips">预览</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="保存为草稿" placement="bottom">
        <div class="icon-box" @click="saveDraft">
          <svg-icon icon-name="icon-caogaoxiang1" color="#555" size="17px" />
          <span class="icon-tips">暂存</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="重置所有设置" placement="bottom">
        <div class="icon-box" @click="reset">
          <svg-icon icon-name="icon-zhongzhi" color="#555" size="17px" />
          <span class="icon-tips">重置</span>
        </div>
      </el-tooltip>
      <el-tooltip effect="dark" content="导出为JSON数据" placement="bottom">
        <div class="icon-box" @click="exportJSON">
          <svg-icon icon-name="icon-xiazai" color="#555" size="17px" />
          <span class="icon-tips">JSON</span>
        </div>
      </el-tooltip>

      <el-tooltip
        v-if="name === 'custom'"
        effect="dark"
        content="导入JSON数据"
        placement="bottom"
      >
        <div class="icon-box" @click="importJson">
          <svg-icon icon-name="icon-yunduanshangchuan" color="#fff" size="19px" />
        </div>
      </el-tooltip>
    </div>
  </nav>

  <import-json-dialog :dialog-visible="dialogVisible" @cancle="cancleJsonDialog" />

  <add-custom-model-drawer :drawer-visible="drawerVisible" @close-add-drawer="closeAddDrawer" />

  <switch-template-drawer
    :drawer-switch-visible="drawerSwitchVisible"
    @close-switch-drawer="closeSwitchDrawer"
  />

  <view-json-drawer :drawer="drawerViewJsonVisible" @close-json-drawer="closeJsonDrawer" />

  <download-dialog
    :dialog-download-visible="dialogDownloadVisible"
    @close-download-dialog="closeDownloadDialog"
    @download-file="downloadResumeFile"
  />

  <PreviewImage v-show="dialogPreviewVisible" @close="closePreview">
    <resume-preview />
  </PreviewImage>
</template>

<script lang="ts" setup>
  import appStore from '@/store';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import 'element-plus/es/components/message-box/style/index';
  import FileSaver from 'file-saver';
  import moment from 'moment';
  import { storeToRefs } from 'pinia';
  import ImportJsonDialog from '@/components/ImportJsonDialog/ImportJsonDialog.vue';
  import { cloneDeep, debounce } from 'lodash';
  import { getUuid } from '@/utils/common';
  import { updateUserresumeAsync } from '@/http/api/resume';
  import AddCustomModelDrawer from './AddCustomModelDrawer.vue';
  import SwitchTemplateDrawer from './SwitchTemplateDrawer.vue';
  import DownloadDialog from './DownloadDialog.vue';
  import ViewJsonDrawer from './ViewJsonDrawer.vue';

  const { resumeJsonNewStore } = storeToRefs(appStore.useResumeJsonNewStore);
  const emit = defineEmits(['generateReport', 'generateReportNew', 'reset', 'saveDataToLocal']);
  const route = useRoute();
  const { name } = route.query;

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
  const saveDataToLocal = async (isHandle?: boolean) => {
    const data = await updateUserresumeAsync(resumeJsonNewStore.value);
    if (data.data.status === 200) {
      const time = moment(new Date()).format('YYYY.MM.DD HH:mm:ss');
      draftTips.value = `已自动保存草稿  ${time}`;
      if (isHandle) {
        ElMessage({
          message: '保存草稿成功!',
          type: 'success'
        });
      }
      return true;
    }

    draftTips.value = '自动保存草稿失败';
    if (isHandle) {
      ElMessage.error(data.data.message || '保存失败');
    }
    return false;
  };

  const saveDraft = () => {
    saveDataToLocal(true);
  };

  const debounced = debounce(() => {
    saveDataToLocal();
  }, 5000);

  watch(
    () => resumeJsonNewStore.value,
    (newVal, oldVal) => {
      if (newVal && oldVal.ID) {
        debounced();
      }
    },
    { deep: true }
  );

  const exportJSON = () => {
    const jsonData = cloneDeep(resumeJsonNewStore.value);
    jsonData.ID = getUuid();
    const data = JSON.stringify(jsonData, null, 4);
    const blob = new Blob([data], { type: '' });
    FileSaver.saveAs(blob, `${resumeJsonNewStore.value.TITLE}.json`);
  };

  const dialogDownloadVisible = ref<boolean>(false);
  const downloadResume = () => {
    dialogDownloadVisible.value = true;
  };

  const closeDownloadDialog = () => {
    dialogDownloadVisible.value = false;
  };

  const downloadResumeFile = async (type: string) => {
    saveDataToLocal().catch(() => {});
    emit('generateReport', type);
    closeDownloadDialog();
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

  const dialogVisible = ref<boolean>(false);
  const importJson = () => {
    dialogVisible.value = true;
  };

  const cancleJsonDialog = () => {
    dialogVisible.value = false;
  };

  const drawerVisible = ref<boolean>(false);
  const openAddDrawer = () => {
    drawerVisible.value = true;
  };

  const closeAddDrawer = () => {
    drawerVisible.value = false;
  };

  const drawerSwitchVisible = ref<boolean>(false);
  const switchDrawer = () => {
    drawerSwitchVisible.value = true;
  };

  const closeSwitchDrawer = () => {
    drawerSwitchVisible.value = false;
  };

  const drawerViewJsonVisible = ref<boolean>(false);
  const viewJSON = () => {
    drawerViewJsonVisible.value = true;
  };

  const closeJsonDrawer = () => {
    drawerViewJsonVisible.value = false;
  };

  const dialogPreviewVisible = ref<boolean>(false);
  const previewResume = () => {
    dialogPreviewVisible.value = true;
  };

  const closePreview = () => {
    dialogPreviewVisible.value = false;
  };
</script>

<style lang="scss" scoped>
  .nav-box {
    height: 50px;
    width: 100%;
    background-color: #fff;
    position: sticky;
    top: 0;
    display: flex;
    box-shadow: 0 5px 21px 0 rgb(78 78 78 / 5%);
    z-index: 20;

    .nav-left {
      width: 230px;
      display: flex;
      align-items: center;
      padding-left: 20px;
    }

    .nav-center {
      flex: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .left {
        display: flex;
        align-items: center;

        .nav-center-left-box {
          display: flex;
          height: 100%;

          .icon-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #555;
            cursor: pointer;
            padding: 0 15px;
            height: 50px;
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
        }

        .draft-tips-box {
          margin-left: 10px;

          .draft-tips {
            font-size: 12px;
            color: #999;
          }
        }
      }

      .center {
        p {
          display: flex;
          align-items: center;
          margin: 0;

          .el-icon {
            margin-left: 6px;
            cursor: pointer;
          }
        }

        .el-input {
          width: 220px;
        }
      }
    }

    .nav-right {
      display: flex;
      align-items: center;
      padding-right: 40px;

      .icon-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #555;
        cursor: pointer;
        padding: 0 12px;
        height: 50px;
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
        background-color: #74a274;
        color: #fff;

        &:hover {
          background-color: rgba($color: #74a274, $alpha: 0.9);
          color: #fff;
        }
      }
    }
  }
</style>
