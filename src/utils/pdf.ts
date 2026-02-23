import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import { ElMessage } from 'element-plus';
import { jsPDF } from 'jspdf';
import { addMakeResumeCountAsync } from '@/http/api/resume';
import appStore from '@/store';

/**
 * 获取简历标题
 */
const getResumeTitle = (): string => {
  try {
    const { HJNewJsonStore } = appStore.useCreateTemplateStore;
    const titleFromDesignerResume = HJNewJsonStore?.config?.title;
    if (titleFromDesignerResume) {
      return titleFromDesignerResume;
    }
  } catch {
    // ignore
  }

  try {
    const { resumeJsonNewStore } = appStore.useResumeJsonNewStore;
    return resumeJsonNewStore.TITLE || '我的简历';
  } catch {
    return '我的简历';
  }
};

/**
 * 获取简历内容 DOM 元素（.design-content）
 */
const getResumeElement = (): HTMLElement | null => {
  const selectors = [
    '.design-content',
    '#print',
    '#resume-container .page-wrapper',
    '.resume-container .page-wrapper'
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector) as HTMLElement | null;
    if (element) {
      return element;
    }
  }

  return null;
};

/**
 * html2canvas 渲染 DOM → Canvas
 */
const renderToCanvas = async (element: HTMLElement): Promise<HTMLCanvasElement> => {
  return html2canvas(element, {
    scale: 2,
    useCORS: true,
    allowTaint: false,
    backgroundColor: '#ffffff',
    logging: false
  });
};

const buildPdfBlob = (
  canvas: HTMLCanvasElement
): {
  blob: Blob;
  pageCount: number;
} => {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const imgData = canvas.toDataURL('image/jpeg', 1);
  const pageWidth = 210;
  const pageHeight = 297;
  const imgHeight = (canvas.height * pageWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 0;
  let pageCount = 0;

  pdf.addImage(imgData, 'JPEG', 0, position, pageWidth, imgHeight);
  pageCount += 1;
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight;
    pdf.addPage();
    pdf.addImage(imgData, 'JPEG', 0, position, pageWidth, imgHeight);
    pageCount += 1;
    heightLeft -= pageHeight;
  }

  return {
    blob: pdf.output('blob'),
    pageCount
  };
};

/**
 * 导出 PNG — 纯客户端
 * 返回 Promise 在文件真正触发下载后 resolve
 */
export const exportPNG = async (id?: string, height?: string): Promise<void> => {
  void id;
  void height;
  const element = getResumeElement();
  if (!element) {
    ElMessage.error('找不到简历内容，请确认页面已加载');
    return;
  }

  const canvas = await renderToCanvas(element);

  // 使用 Promise 包装 toBlob 回调，确保下载完成后再 resolve
  return new Promise<void>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        const fileName = getResumeTitle();
        saveAs(blob, `${fileName}.png`);
        addMakeResumeCountAsync();
        resolve();
      } else {
        reject(new Error('图片生成失败'));
      }
    }, 'image/png');
  });
};

/**
 * 导出 PDF — 纯客户端（直接下载）
 */
export const exportPdf = async (id?: string, height?: string): Promise<void> => {
  void id;
  void height;
  const element = getResumeElement();
  if (!element) {
    ElMessage.error('找不到简历内容，请确认页面已加载');
    return;
  }

  const canvas = await renderToCanvas(element);
  const fileName = getResumeTitle();
  const { blob } = buildPdfBlob(canvas);
  saveAs(blob, `${fileName}.pdf`);
  addMakeResumeCountAsync();
};

// 兼容 LegoDesigner
export const exportPdfNew = exportPdf;
export const exportPNGNew = exportPNG;
export const exportPdfPreview = async (
  id?: string
): Promise<{
  blob: Blob;
  pageCount: number;
}> => {
  void id;
  const element = getResumeElement();
  if (!element) {
    throw new Error('找不到简历内容，请确认页面已加载');
  }
  const canvas = await renderToCanvas(element);
  return buildPdfBlob(canvas);
};
