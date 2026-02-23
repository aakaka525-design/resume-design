<!-- 数据配置、头像上传组件 -->
<template>
  <el-upload
    class="avatar-uploader"
    :action="uploadAddress()"
    :headers="{ Authorization: appStore.useTokenStore.token }"
    :show-file-list="false"
    :on-success="handleAvatarSuccess"
    :before-upload="beforeAvatarUpload"
  >
    <img v-if="imageUrl" :src="imageUrl" class="avatar" />
    <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
  </el-upload>
</template>
<script setup lang="ts">
  import { ElMessage } from 'element-plus';
  import CONFIG from '@/config';
  import type { UploadProps } from 'element-plus';
  import useDesignSelectModelItem from '@/hooks/material/useDesignSelectModelItem';
  import appStore from '@/store';
  import { resolveUploadFileUrl } from '@/utils/upload';

  // 选中的模块
  const { modelItem } = useDesignSelectModelItem();
  console.log('头像上传', modelItem);
  const imageUrl = ref(modelItem.data.avatar);
  // 上传文件地址
  const uploadAddress = () => {
    return CONFIG.serverAddress + '/huajian/upload/file/avatar';
  };

  const handleAvatarSuccess: UploadProps['onSuccess'] = (response) => {
    const fileUrl = resolveUploadFileUrl(response);
    if (!fileUrl) {
      ElMessage.error('上传成功但未拿到图片地址');
      return;
    }
    imageUrl.value = fileUrl;
    modelItem.data.avatar = fileUrl;
  };

  const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
    if (rawFile.size / 1024 / 1024 > 5) {
      ElMessage.error('头像不能大于5M');
      return false;
    }
    return true;
  };
</script>
