import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import { ElMessage } from 'element-plus';
import { jsPDF } from 'jspdf';
import { addMakeResumeCountAsync } from '@/http/api/resume';
import appStore from '@/store';
import { assertPdfBlob } from '@/utils/exportGuards';

const FALLBACK_SANS_STACK =
  '"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Noto Sans CJK SC","Source Han Sans SC",sans-serif';
const PDF_EDITOR_STATE_CLASSES = [
  'module-active',
  'module-select',
  'page-ghost',
  'sortable-chosen',
  'sortable-ghost',
  'sortable-drag'
] as const;

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
 * 获取简历内容 DOM 元素（.design-content / createTemplate 预览区）
 */
const getResumeElement = (): HTMLElement | null => {
  const selectors = [
    '#resume-container .components-wrapper',
    '#resume-container .page-wrapper',
    '.resume-container .page-wrapper',
    '.design-content',
    '#print'
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector) as HTMLElement | null;
    if (element) {
      return element;
    }
  }

  return null;
};

const getResumeExportRoot = (element: HTMLElement): HTMLElement => {
  return (element.closest('.page-wrapper') as HTMLElement | null) || element;
};

const escapeHtml = (value: string): string => {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const getServerBaseUrl = (): string => {
  const envBase = (import.meta.env.VITE_SERVER_ADDRESS || '').trim();
  if (envBase) {
    return envBase.replace(/\/$/, '');
  }
  return window.location.origin.replace(/\/$/, '');
};

/**
 * 下一帧执行，确保样式更新后再截图
 */
const waitNextFrame = (): Promise<void> => {
  return new Promise((resolve) => {
    requestAnimationFrame(() => resolve());
  });
};

/**
 * 导出前临时归一化预览样式，避免缩放与辅助线污染导出结果
 */
const prepareExportContext = (element: HTMLElement): (() => void) => {
  const cleanups: Array<() => void> = [];

  const zoomContainer = element.closest('.resume-container') as HTMLElement | null;
  if (zoomContainer) {
    const prevZoom = zoomContainer.style.zoom;
    if (prevZoom && prevZoom !== '1') {
      zoomContainer.style.zoom = '1';
      cleanups.push(() => {
        zoomContainer.style.zoom = prevZoom;
      });
    }
  }

  const helperLines = Array.from(
    document.querySelectorAll('.lines, .page-tips-one, .el-loading-mask')
  ) as HTMLElement[];
  const prevDisplay = helperLines.map((line) => line.style.display);
  helperLines.forEach((line) => {
    line.style.display = 'none';
  });
  cleanups.push(() => {
    helperLines.forEach((line, index) => {
      line.style.display = prevDisplay[index];
    });
  });

  // 临时剥离编辑态 class，避免截图/导出混入交互样式
  const editorStateSelector = PDF_EDITOR_STATE_CLASSES.map((name) => `.${name}`).join(', ');
  const editorStateElements = Array.from(
    document.querySelectorAll(editorStateSelector)
  ) as HTMLElement[];
  const removedEditorStateClasses = editorStateElements.map((node) => ({
    node,
    classes: PDF_EDITOR_STATE_CLASSES.filter((className) => node.classList.contains(className))
  }));
  removedEditorStateClasses.forEach(({ node, classes }) => {
    classes.forEach((className) => node.classList.remove(className));
  });
  cleanups.push(() => {
    removedEditorStateClasses.forEach(({ node, classes }) => {
      classes.forEach((className) => node.classList.add(className));
    });
  });

  // 统一字体回退，避免导出时退化到 serif 导致整体挤压
  const prevFontFamily = element.style.fontFamily;
  const computedFont = window.getComputedStyle(element).fontFamily || '';
  if (computedFont) {
    element.style.fontFamily = `${computedFont},${FALLBACK_SANS_STACK}`;
    cleanups.push(() => {
      element.style.fontFamily = prevFontFamily;
    });
  }

  return () => {
    for (let i = cleanups.length - 1; i >= 0; i -= 1) {
      cleanups[i]();
    }
  };
};

/**
 * html2canvas 渲染 DOM → Canvas
 */
const renderToCanvas = async (
  element: HTMLElement,
  foreignObjectRendering = false
): Promise<HTMLCanvasElement> => {
  return html2canvas(element, {
    scale: Math.max(2, window.devicePixelRatio || 1),
    useCORS: true,
    allowTaint: false,
    foreignObjectRendering,
    backgroundColor: '#ffffff',
    logging: false,
    ignoreElements: (node: Element) => {
      if (!(node instanceof HTMLElement)) return false;
      return (
        node.classList.contains('lines') ||
        node.classList.contains('page-tips-one') ||
        node.classList.contains('el-loading-mask')
      );
    }
  });
};

/**
 * 判断 canvas 是否几乎空白（用于导出回退）
 */
const isCanvasNearlyBlank = (canvas: HTMLCanvasElement): boolean => {
  const ctx = canvas.getContext('2d');
  if (!ctx || canvas.width === 0 || canvas.height === 0) {
    return true;
  }

  const sampleCols = 12;
  const sampleRows = 12;
  let nonBlank = 0;

  for (let y = 0; y < sampleRows; y += 1) {
    const py = Math.floor((canvas.height - 1) * (y / (sampleRows - 1)));
    for (let x = 0; x < sampleCols; x += 1) {
      const px = Math.floor((canvas.width - 1) * (x / (sampleCols - 1)));
      const [r, g, b, a] = ctx.getImageData(px, py, 1, 1).data;
      const isWhite = r > 248 && g > 248 && b > 248;
      if (a > 0 && !isWhite) {
        nonBlank += 1;
      }
    }
  }

  return nonBlank <= 2;
};

/**
 * 导出抓图：统一做样式归一化
 */
const captureResumeCanvas = async (element: HTMLElement): Promise<HTMLCanvasElement> => {
  const restore = prepareExportContext(element);
  try {
    await waitNextFrame();
    try {
      const highFidelityCanvas = await renderToCanvas(element, true);
      if (!isCanvasNearlyBlank(highFidelityCanvas)) {
        return highFidelityCanvas;
      }
    } catch {
      // ignore and fallback to stable mode
    }
    return await renderToCanvas(element, false);
  } finally {
    restore();
  }
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
    format: 'a4',
    precision: 16
  });

  const imgData = canvas.toDataURL('image/png');
  const pageWidth = 210;
  const pageHeight = 297;
  const imgHeight = (canvas.height * pageWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 0;
  let pageCount = 0;

  pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
  pageCount += 1;
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
    pageCount += 1;
    heightLeft -= pageHeight;
  }

  return {
    blob: pdf.output('blob'),
    pageCount
  };
};

const waitAssetsReady = async (element: HTMLElement): Promise<void> => {
  if ((document as any).fonts?.ready) {
    try {
      await (document as any).fonts.ready;
    } catch {
      // ignore
    }
  }

  const images = Array.from(element.querySelectorAll('img')) as HTMLImageElement[];
  await Promise.all(
    images.map((img) => {
      if (img.complete) {
        return Promise.resolve();
      }
      return new Promise<void>((resolve) => {
        const done = () => {
          img.removeEventListener('load', done);
          img.removeEventListener('error', done);
          resolve();
        };
        img.addEventListener('load', done);
        img.addEventListener('error', done);
      });
    })
  );
};

const collectStyleMarkup = (): string => {
  const nodes = Array.from(document.querySelectorAll('style, link[rel="stylesheet"]')) as Array<
    HTMLStyleElement | HTMLLinkElement
  >;
  const chunks: string[] = [];

  for (const node of nodes) {
    if (node.tagName.toLowerCase() === 'link') {
      const href = (node as HTMLLinkElement).href;
      if (!href) continue;
      chunks.push(`<link rel="stylesheet" href="${escapeHtml(href)}">`);
      continue;
    }
    chunks.push(node.outerHTML);
  }

  return chunks.join('\n');
};

const buildPrintableHtml = async (element: HTMLElement, title: string): Promise<string> => {
  const restore = prepareExportContext(element);
  try {
    await waitNextFrame();
    await waitAssetsReady(element);

    const exportRoot = getResumeExportRoot(element);
    const clonedRoot = exportRoot.cloneNode(true) as HTMLElement;
    clonedRoot
      .querySelectorAll('.lines, .page-tips-one, .el-loading-mask')
      .forEach((node) => node.remove());

    // 去除编辑态 class，避免导出结果出现虚线边框/拖拽态样式
    for (const className of PDF_EDITOR_STATE_CLASSES) {
      if (clonedRoot.classList.contains(className)) {
        clonedRoot.classList.remove(className);
      }
      clonedRoot.querySelectorAll(`.${className}`).forEach((node) => {
        node.classList.remove(className);
      });
    }

    const styleMarkup = collectStyleMarkup();
    const escapedTitle = escapeHtml(title || '我的简历');
    const baseHref = `${window.location.origin.replace(/\/$/, '')}/`;

    return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <base href="${escapeHtml(baseHref)}" />
  <title>${escapedTitle}</title>
  ${styleMarkup}
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: #ffffff;
      font-family: ${FALLBACK_SANS_STACK};
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    #print-root {
      width: 820px;
      margin: 0 auto;
      background: #ffffff;
      overflow: hidden;
    }
    #print-root .lines,
    #print-root .page-tips-one,
    #print-root .el-loading-mask {
      display: none !important;
    }
    #print-root .module-active,
    #print-root .module-select,
    #print-root .module-box,
    #print-root .module-box:hover,
    #print-root .sortable-chosen,
    #print-root .sortable-ghost,
    #print-root .sortable-drag,
    #print-root .page-ghost {
      border: none !important;
      box-shadow: none !important;
      outline: none !important;
    }
    #print-root .module-component,
    #print-root .module-preview {
      cursor: default !important;
    }
    @page {
      size: A4;
      margin: 0;
    }
  </style>
</head>
<body>
  <div id="print-root">${clonedRoot.outerHTML}</div>
</body>
</html>`;
  } finally {
    restore();
  }
};

const requestHighFidelityPdf = async (
  html: string,
  title: string
): Promise<{
  blob: Blob;
  pageCount: number;
}> => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${getServerBaseUrl()}/huajian/pdf/getPdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: token } : {})
    },
    body: JSON.stringify({
      html,
      title
    })
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(`高保真PDF服务失败(${response.status})${errorText ? `: ${errorText}` : ''}`);
  }

  const blob = await response.blob();
  await assertPdfBlob(blob, response.headers.get('content-type'));

  const rawPageCount = Number(response.headers.get('X-Page-Count') || '1');
  const pageCount = Number.isFinite(rawPageCount) && rawPageCount > 0 ? rawPageCount : 1;
  return { blob, pageCount };
};

const buildLocalPdfFromElement = async (
  element: HTMLElement
): Promise<{
  blob: Blob;
  pageCount: number;
}> => {
  const canvas = await captureResumeCanvas(element);
  return buildPdfBlob(canvas);
};

const recordExportCount = () => {
  addMakeResumeCountAsync().catch(() => {
    // ignore
  });
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

  const canvas = await captureResumeCanvas(element);

  return new Promise<void>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        const fileName = getResumeTitle();
        saveAs(blob, `${fileName}.png`);
        recordExportCount();
        resolve();
      } else {
        reject(new Error('图片生成失败'));
      }
    }, 'image/png');
  });
};

/**
 * 导出 PDF：优先后端高保真渲染，失败时回退客户端导出
 */
export const exportPdf = async (id?: string, height?: string): Promise<void> => {
  void id;
  void height;
  const element = getResumeElement();
  if (!element) {
    ElMessage.error('找不到简历内容，请确认页面已加载');
    return;
  }

  const fileName = getResumeTitle();

  try {
    const html = await buildPrintableHtml(element, fileName);
    const { blob } = await requestHighFidelityPdf(html, fileName);
    saveAs(blob, `${fileName}.pdf`);
  } catch (error) {
    console.error('高保真PDF导出失败，回退本地导出:', error);
    const { blob } = await buildLocalPdfFromElement(element);
    saveAs(blob, `${fileName}.pdf`);
    ElMessage.warning('已回退为兼容导出模式，建议确保前后端均已启动以获得最佳一致性');
  } finally {
    recordExportCount();
  }
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

  const fileName = getResumeTitle();
  try {
    const html = await buildPrintableHtml(element, fileName);
    return await requestHighFidelityPdf(html, fileName);
  } catch (error) {
    console.error('高保真PDF预览失败，回退本地预览:', error);
    return await buildLocalPdfFromElement(element);
  }
};
