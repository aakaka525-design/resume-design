import { getLegoPNGAsync, getLegoResumePdfAsync } from '@/http/api/lego';
import appStore from '@/store';
import { saveAs } from 'file-saver';
import { assertPdfBlob, assertPngBlob } from '@/utils/exportGuards';

const toBlob = (value: unknown): Blob => {
  if (value instanceof Blob) {
    return value;
  }
  return new Blob([value as BlobPart], { type: 'application/octet-stream' });
};

// 生成pdf方法
export const exportLegoPdf = async (id?: string) => {
  const { HJSchemaJsonStore } = appStore.useLegoJsonStore;
  const fileName = HJSchemaJsonStore.config.title;
  const params = {
    url: `${location.origin}/legoPrintPdfPreview?id=${id}`,
    printBackground: true,
    timezone: '',
    margin: '',
    filename: '',
    width: HJSchemaJsonStore.css.width + 'px',
    height: HJSchemaJsonStore.css.height + 'px',
    integralPayGoodsId: id
  };
  const pdfData = await getLegoResumePdfAsync(params);
  const blob = toBlob(pdfData);
  await assertPdfBlob(blob, blob.type);
  saveAs(blob, `${fileName}.pdf`);
};

// 生成PNG方法
export const exportLegoPNG = async (id?: string) => {
  const { HJSchemaJsonStore } = appStore.useLegoJsonStore;
  const fileName = HJSchemaJsonStore.config.title;
  const params = {
    url: `${location.origin}/legoPrintPdfPreview?id=${id}`,
    selector: '#lego-preview-designer',
    integralPayGoodsId: id
  };
  const pngData = await getLegoPNGAsync(params);
  const blob = toBlob(pngData);
  await assertPngBlob(blob, blob.type);
  saveAs(blob, `${fileName}.png`);
};

export const getLegoPdfUrl = (id?: string) => {
  return `${location.origin}/legoPrintPdfPreview?id=${id}`;
};
