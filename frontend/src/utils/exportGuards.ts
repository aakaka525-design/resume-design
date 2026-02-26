const PDF_MAGIC_BYTES = [0x25, 0x50, 0x44, 0x46, 0x2d];
const PNG_MAGIC_BYTES = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const BINARY_MIME_TYPES = new Set(['application/octet-stream', 'binary/octet-stream']);

const normalizeMime = (value?: string | null): string => {
  return (value || '').split(';')[0].trim().toLowerCase();
};

const readBlobBytes = async (blob: Blob, length: number): Promise<Uint8Array> => {
  const buffer = await blob.slice(0, length).arrayBuffer();
  return new Uint8Array(buffer);
};

const startsWith = (source: Uint8Array, prefix: number[]): boolean => {
  if (source.length < prefix.length) {
    return false;
  }
  for (let i = 0; i < prefix.length; i += 1) {
    if (source[i] !== prefix[i]) {
      return false;
    }
  }
  return true;
};

const readTextPreview = async (blob: Blob, length = 120): Promise<string> => {
  try {
    const raw = await blob.slice(0, length).text();
    return raw.replace(/\s+/g, ' ').trim().slice(0, length);
  } catch {
    return '';
  }
};

const isPdfMime = (mime: string): boolean => {
  const normalized = normalizeMime(mime);
  return (
    normalized === '' ||
    normalized === 'application/pdf' ||
    normalized === 'application/x-pdf' ||
    BINARY_MIME_TYPES.has(normalized)
  );
};

const isPngMime = (mime: string): boolean => {
  const normalized = normalizeMime(mime);
  return normalized === '' || normalized === 'image/png' || BINARY_MIME_TYPES.has(normalized);
};

const resolveMime = (blob: Blob, hintedMime?: string | null): string => {
  return normalizeMime(hintedMime || blob.type);
};

export const assertPdfBlob = async (blob: Blob, hintedMime?: string | null): Promise<void> => {
  if (!blob || blob.size <= 0) {
    throw new Error('导出失败：返回文件为空');
  }

  const mime = resolveMime(blob, hintedMime);
  if (!isPdfMime(mime)) {
    const preview = await readTextPreview(blob);
    throw new Error(
      `导出失败：服务返回了非 PDF 内容（${mime || 'unknown'}）${
        preview ? `，内容片段：${preview}` : ''
      }`
    );
  }

  const bytes = await readBlobBytes(blob, PDF_MAGIC_BYTES.length);
  if (!startsWith(bytes, PDF_MAGIC_BYTES)) {
    const preview = await readTextPreview(blob);
    throw new Error(
      `导出失败：文件头不是 PDF（${mime || 'unknown'}）${preview ? `，内容片段：${preview}` : ''}`
    );
  }
};

export const assertPngBlob = async (blob: Blob, hintedMime?: string | null): Promise<void> => {
  if (!blob || blob.size <= 0) {
    throw new Error('导出失败：返回文件为空');
  }

  const mime = resolveMime(blob, hintedMime);
  if (!isPngMime(mime)) {
    const preview = await readTextPreview(blob);
    throw new Error(
      `导出失败：服务返回了非 PNG 内容（${mime || 'unknown'}）${
        preview ? `，内容片段：${preview}` : ''
      }`
    );
  }

  const bytes = await readBlobBytes(blob, PNG_MAGIC_BYTES.length);
  if (!startsWith(bytes, PNG_MAGIC_BYTES)) {
    const preview = await readTextPreview(blob);
    throw new Error(
      `导出失败：文件头不是 PNG（${mime || 'unknown'}）${preview ? `，内容片段：${preview}` : ''}`
    );
  }
};
