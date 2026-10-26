// Рендер HTML-страниц из manifest.json в PNG, брендбука — в PDF,
// SVG-логотипов — в PNG с прозрачным фоном.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const HTML = path.join(__dirname, 'html');

(async () => {
  const browser = await chromium.launch();
  const jobs = JSON.parse(fs.readFileSync(path.join(HTML, 'manifest.json'), 'utf8'));
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale });
    await page.goto('file://' + path.join(HTML, j.html));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(150);
    const out = path.join(ROOT, j.out);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out });
    await page.close();
    console.log('png', j.out);
  }

  const pdf = await browser.newPage();
  await pdf.goto('file://' + path.join(HTML, 'brandbook.html'));
  await pdf.evaluate(() => document.fonts.ready);
  await pdf.pdf({ path: path.join(ROOT, 'brandbook/r00ast-brandbook.pdf'), width: '1920px', height: '1080px', printBackground: true });
  console.log('pdf brandbook/r00ast-brandbook.pdf');

  const logoDir = path.join(ROOT, 'logo');
  for (const f of fs.readdirSync(logoDir).filter((f) => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(logoDir, f), 'utf8');
    const [, w, h] = svg.match(/width="(\d+)" height="(\d+)"/);
    const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
    await page.goto('file://' + path.join(logoDir, f));
    await page.screenshot({ path: path.join(logoDir, f.replace('.svg', '.png')), omitBackground: true });
    await page.close();
  }
  console.log('logo png done');
  await browser.close();
})();
