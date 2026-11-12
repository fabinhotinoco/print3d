// Render fotorrealista simples de um STL via three.js + Chromium headless.
// Uso: node render.mjs <saida.png> <a.stl>:<#cor> [<b.stl>:<#cor> ...]
// Vistas: topo (ápice), base e perspectiva.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const [out, ...parts] = process.argv.slice(2);
const models = parts.map(p => { const i = p.lastIndexOf(":"); return { file: path.resolve(p.slice(0, i)), color: p.slice(i + 1) }; });

const html = `<!doctype html><html><body style="margin:0;background:#e9e9ec">
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script>
<script type="module">
import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
const W = 640, H = 640, views = [[0.001, -0.001, 1], [0.001, 0.001, -1], [1.0, -0.6, 0.45]];
const colors = ${JSON.stringify(models.map(m => m.color))};
const geos = []; for (let i = 0; i < colors.length; i++) geos.push(new STLLoader().parse(await (await fetch("/m" + i + ".stl")).arrayBuffer()));
geos[0].computeBoundingBox(); const c = new THREE.Vector3(); geos[0].boundingBox.getCenter(c);
geos.forEach(g => g.translate(-c.x, -c.y, -c.z)); geos[0].computeBoundingBox();
const r = geos[0].boundingBox.getSize(new THREE.Vector3()).length() / 2;
const canvas = document.createElement("canvas"); document.body.appendChild(canvas);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W * views.length, H); renderer.setScissorTest(true);
const scene = new THREE.Scene();
geos.forEach((g, i) => scene.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: colors[i], roughness: 0.55, metalness: 0.05, polygonOffset: i > 0, polygonOffsetFactor: -1 }))));
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 2.2); scene.add(key);
views.forEach((v, i) => {
  const cam = new THREE.PerspectiveCamera(30, 1, 1, 1000);
  const d = new THREE.Vector3(...v).normalize().multiplyScalar(r / Math.sin(Math.PI * 15 / 180) * 1.05);
  cam.position.copy(d); cam.up.set(0, 0, 1); if (Math.abs(v[2]) > 0.95) cam.up.set(0, 1, 0); cam.lookAt(0, 0, 0);
  key.position.copy(d.clone().add(new THREE.Vector3(r, -r, r)));
  renderer.setViewport(i * W, 0, W, H); renderer.setScissor(i * W, 0, W, H);
  renderer.setClearColor(0xe9e9ec); renderer.render(scene, cam);
});
window.done = true;
</script></body></html>`;

const server = http.createServer((req, res) => {
  if (req.url === "/") return res.end(html);
  const mm = req.url.match(/^\/m(\d+)\.stl$/); if (mm) return res.end(fs.readFileSync(models[+mm[1]].file));
  if (req.url.startsWith("/three/")) {
    const f = path.join(here, "node_modules", req.url);
    res.setHeader("Content-Type", "text/javascript");
    return res.end(fs.readFileSync(f));
  }
  res.statusCode = 404; res.end();
}).listen(0);
const port = server.address().port;
const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1920, height: 640 } });
page.on("pageerror", e => console.error(e));
await page.goto(`http://localhost:${port}/`);
await page.waitForFunction(() => window.done, null, { timeout: 60000 });
await page.locator("canvas").screenshot({ path: out });
await browser.close(); server.close();
console.log("ok", out);
