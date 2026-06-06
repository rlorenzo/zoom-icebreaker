// Records the README "app in action" clip (docs/demo.webm) by driving the live
// demo mode in a real browser, so the capture includes the actual animations:
// the FLIP row-slide as someone moves into the introduced group, the checkmark
// drawing itself, and the clay completion flash. Playwright records VP8 WebM;
// we then transcode to VP9, which is the preferred WebM codec and compresses
// the screen capture far smaller at the same quality.
//
//   uv run tracker.py --no-ax --port 3939    # in one terminal
//   npm run record:demo                      # in another
//
// The transcode needs an ffmpeg with libvpx-vp9. It is resolved in order:
//   FFMPEG=/path/to/ffmpeg env var  ->  the `ffmpeg-static` package  ->  ffmpeg on PATH
// so `npm i ffmpeg-static` (or `brew install ffmpeg`) is enough. Override the
// target page with URL=... npm run record:demo
import { execFileSync } from "node:child_process";
import { rmSync } from "node:fs";
import { chromium } from "playwright";

const URL = process.env.URL || "http://localhost:3939/";
const TMP_DIR = ".rec-tmp";
const RAW = `${TMP_DIR}/raw.webm`;
const OUT = "docs/demo.webm";
// 880px content column + a little air; tall enough for all six rows once the
// demo bar is hidden. Kept modest so the committed clip stays small.
const SIZE = { width: 1000, height: 820 };

async function resolveFfmpeg() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  try {
    return (await import("ffmpeg-static")).default;
  } catch {
    return "ffmpeg"; // assume it is on PATH
  }
}

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: SIZE,
  deviceScaleFactor: 2, // render at 2x, encode to SIZE -> crisp text
  reducedMotion: "no-preference", // we are specifically showcasing motion
  recordVideo: { dir: TMP_DIR, size: SIZE },
});
const page = await context.newPage();

// The SSE stream never goes idle, so wait on a rendered element, not networkidle.
await page.goto(URL, { waitUntil: "domcontentloaded" });
await page.evaluate(() => localStorage.removeItem("icebreaker.firstrun.seen"));
await page.reload({ waitUntil: "domcontentloaded" });

// First-run welcome -> open the sample meeting.
await page.getByRole("button", { name: "Try a demo" }).click();

// Clean "real app" framing: drop the demo banner (it's just a recording aid),
// the footer, and the external sponsor so the clip is all live roster.
await page.evaluate(() => {
  document.getElementById("demoBar")?.style.setProperty("display", "none");
  document.querySelector("footer")?.style.setProperty("display", "none");
  document.querySelector(".sponsor-bar")?.style.setProperty("display", "none");
});

await page.waitForTimeout(1200); // hold on the full roster so viewers read it

// Mark the top three waiting people, one at a time, pacing each so the flash,
// checkmark draw, and reorder slide all play out on camera.
for (let i = 0; i < 3; i++) {
  await page.locator(".row:not(.introduced) .toggle").first().click();
  await page.waitForTimeout(2300);
}

await page.waitForTimeout(1000); // end hold before the loop restarts

const video = page.video();
await context.close(); // finalizes the raw VP8 .webm
await video.saveAs(RAW);
await video.delete();
await browser.close();

// Transcode VP8 -> VP9 (constant-quality, no audio track).
const ffmpeg = await resolveFfmpeg();
// biome-ignore format: keep the ffmpeg flags grouped as flag/value pairs
const args = [
  "-y", "-i", RAW,
  "-c:v", "libvpx-vp9",
  "-crf", "37", "-b:v", "0",
  "-pix_fmt", "yuv420p",
  "-row-mt", "1",
  "-an",
  OUT,
];
execFileSync(ffmpeg, args, { stdio: "inherit" });
rmSync(TMP_DIR, { recursive: true, force: true });

console.log(`wrote ${OUT} (VP9)`);
