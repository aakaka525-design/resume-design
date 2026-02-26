import assert from 'node:assert/strict';
import { assertPdfBlob } from '../src/utils/exportGuards';

const run = async () => {
  const validPdf = new Blob(['%PDF-1.4\nhello'], { type: 'application/pdf' });
  await assert.doesNotReject(assertPdfBlob(validPdf, 'application/pdf'));

  const htmlBlob = new Blob(['<!doctype html><html><body>fallback</body></html>'], {
    type: 'text/html'
  });
  await assert.rejects(assertPdfBlob(htmlBlob, 'text/html'));

  const octetPdf = new Blob(['%PDF-1.7\nmock'], { type: 'application/octet-stream' });
  await assert.doesNotReject(assertPdfBlob(octetPdf, 'application/octet-stream'));

  const jsonBlob = new Blob(['{"status":500,"message":"error"}'], {
    type: 'application/json'
  });
  await assert.rejects(assertPdfBlob(jsonBlob, 'application/json'));

  console.log('pdf_blob_guard_check passed');
};

run().catch((error) => {
  console.error('pdf_blob_guard_check failed');
  console.error(error);
  process.exit(1);
});
