// node render.js <cfg.json> <out_video.mp4> [fps] [--still t1,t2,...  out_prefix]
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [cfgPath, out] = process.argv.slice(2);
  const fps = 30;
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  const stillIdx = process.argv.indexOf('--still');
  const b = await chromium.launch();
  const pg = await b.newPage({viewport: {width: 1080, height: 1920}});
  await pg.goto('file://' + path.join(__dirname, 'page.html'));
  await pg.evaluate(c => window.setup(c), cfg);
  await pg.evaluate(() => document.fonts.ready);
  await pg.evaluate(() => window.frame(0.5));
  await pg.waitForTimeout(600);
  if (stillIdx > 0) {
    const ts = process.argv[stillIdx + 1].split(',').map(Number), pre = process.argv[stillIdx + 2];
    for (const t of ts) { await pg.evaluate(t => window.frame(t), t); await pg.screenshot({path: `${pre}-${t}.png`}); }
    await b.close(); return;
  }
  const N = Math.ceil(cfg.dur * fps);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], {stdio: ['pipe', 'inherit', 'inherit']});
  for (let i = 0; i < N; i++) {
    await pg.evaluate(t => window.frame(t), i / fps);
    const buf = await pg.screenshot({type: 'jpeg', quality: 90});
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.error(`frame ${i}/${N}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
})();
