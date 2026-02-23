#!/usr/bin/env node
import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer';

const [, , htmlPath, outputPath] = process.argv;

if (!htmlPath || !outputPath) {
  console.error('Usage: node render_html_pdf.mjs <htmlPath> <outputPath>');
  process.exit(1);
}

const ensureParentDir = async (filePath) => {
  const parent = path.dirname(filePath);
  await fs.mkdir(parent, { recursive: true });
};

const resolveChromeExecutable = () => {
  const fromEnv = process.env.PUPPETEER_EXECUTABLE_PATH;
  if (fromEnv && fsSync.existsSync(fromEnv)) {
    return fromEnv;
  }

  const candidates = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
  ];
  return candidates.find((item) => fsSync.existsSync(item));
};

const waitImagesAndFonts = async (page) => {
  await page.evaluate(async () => {
    if (document.fonts?.ready) {
      await document.fonts.ready;
    }
    const images = Array.from(document.images || []);
    await Promise.all(
      images.map((img) => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.onload = () => resolve();
          img.onerror = () => resolve();
        });
      })
    );
  });
};

const estimatePageCount = async (page) => {
  return page.evaluate(() => {
    const root = document.querySelector('#print-root') || document.body;
    const scrollHeight = (root && root.scrollHeight) || document.body.scrollHeight || 0;
    const a4HeightPx = 1122.52;
    return Math.max(1, Math.ceil(scrollHeight / a4HeightPx));
  });
};

const run = async () => {
  const html = await fs.readFile(htmlPath, 'utf-8');
  await ensureParentDir(outputPath);

  let browser;
  try {
    const executablePath = resolveChromeExecutable();
    browser = await puppeteer.launch({
      headless: 'new',
      ...(executablePath ? { executablePath } : {}),
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({
      width: 1280,
      height: 2200,
      deviceScaleFactor: 2
    });

    await page.setContent(html, {
      waitUntil: 'networkidle0',
      timeout: 90_000
    });

    await waitImagesAndFonts(page);
    const pageCount = await estimatePageCount(page);

    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: '0', right: '0', bottom: '0', left: '0' }
    });

    process.stdout.write(`${JSON.stringify({ pageCount })}\n`);
  } catch (error) {
    process.stderr.write(`${error?.stack || String(error)}\n`);
    process.exit(2);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
};

run();
