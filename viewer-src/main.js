// Amy's Ring viewer: three.js + ray-traced diamond shader (three-mesh-bvh).
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { MeshBVH, MeshBVHUniformStruct, BVHShaderGLSL } from 'three-mesh-bvh';

// ---------------------------------------------------------------- studio environment
// Mostly dark room with a few very bright softboxes: dark facets + white flashes.
function buildStudio(bright = false) {
  const scene = new THREE.Scene();
  scene.background = bright ? new THREE.Color(0.22, 0.22, 0.22) : new THREE.Color(0.05, 0.05, 0.05);
  const box = (w, h, intensity, pos, look, tint = [1, 1, 1]) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(...tint).multiplyScalar(intensity), side: THREE.DoubleSide }));
    m.position.set(...pos); m.lookAt(...look); scene.add(m);
  };
  // big soft overhead + key/fill/rim strips
  box(6, 6, 6, [0, 7, 0], [0, 0, 0]);
  box(2.2, 7, 14, [-6, 2.5, 3], [0, 0, 0]);
  box(2.2, 7, 11, [6, 2.5, 2], [0, 0, 0]);
  box(8, 1.2, 9, [0, 3, -6], [0, 0, 0]);
  box(1.0, 5, 18, [2.5, 4, 6], [0, 0, 0]);
  box(1.0, 5, 16, [-3, 4, -5], [0, 0, 0]);
  box(3, 3, 4, [0, -6, 0], [0, 0, 0]);
  // ring of narrow strips around the horizon: lots of small facet flashes
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * Math.PI * 2 + 0.2, r = 6.5;
    box(0.6, 3.2, i % 2 ? 7 : 12, [Math.cos(a) * r, 0.6, Math.sin(a) * r], [0, 0, 0]);
  }
  // a light gray floor sweep so the band never reflects pure black
  const floor = new THREE.Mesh(new THREE.CircleGeometry(9, 48), new THREE.MeshBasicMaterial({ color: bright ? new THREE.Color(0.45, 0.45, 0.45) : new THREE.Color(0.18, 0.18, 0.18) }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -3.5; scene.add(floor);
  return scene;
}

// ---------------------------------------------------------------- diamond material
function diamondMaterial(bvh, envMap, opts) {
  const uniforms = {
    bvh: { value: new MeshBVHUniformStruct() },
    envMap: { value: envMap },
    ior: { value: 2.42 },
    dispersion: { value: opts.dispersion },
    fireAmount: { value: 0.5 },
    envIntensity: { value: 1.0 },
    tint: { value: new THREE.Color(1, 1, 1) },
    modelInv: { value: new THREE.Matrix4() },
    modelMat: { value: new THREE.Matrix4() },
  };
  uniforms.bvh.value.updateFrom(bvh);
  const mat = new THREE.ShaderMaterial({
    uniforms,
    defines: { BOUNCES: opts.bounces, CHROMA: opts.chroma ? 1 : 0 },
    vertexShader: /* glsl */`
      varying vec3 vWorld;
      void main() {
        vec4 w = modelMatrix * vec4(position, 1.0);
        vWorld = w.xyz;
        gl_Position = projectionMatrix * viewMatrix * w;
      }`,
    fragmentShader: /* glsl */`
      precision highp isampler2D;
      precision highp usampler2D;
      ${BVHShaderGLSL.common_functions}
      ${BVHShaderGLSL.bvh_struct_definitions}
      ${BVHShaderGLSL.bvh_ray_functions}
      uniform BVH bvh;
      uniform samplerCube envMap;
      uniform float ior, dispersion, envIntensity, fireAmount;
      uniform vec3 tint;
      uniform mat4 modelInv;
      uniform mat4 modelMat;
      varying vec3 vWorld;

      vec3 env(vec3 d) { return textureLod(envMap, d, 0.0).rgb * envIntensity; }
      float fresnel(float cosi, float n1, float n2) {
        float r0 = (n1 - n2) / (n1 + n2); r0 *= r0;
        return r0 + (1.0 - r0) * pow(1.0 - clamp(cosi, 0.0, 1.0), 5.0);
      }
      // trace one wavelength through the stone, return radiance
      vec3 traceInside(vec3 roL, vec3 rdL, float n) {
        vec3 acc = vec3(0.0); float thr = 1.0;
        for (int i = 0; i < BOUNCES; i++) {
          uvec4 fi; vec3 fn; vec3 bc; float side = 1.0; float dist = 0.0;
          bool hit = bvhIntersectFirstHit(bvh, roL + rdL * 1e-4, rdL, fi, fn, bc, side, dist);
          if (!hit) { acc += thr * env(normalize((modelMat * vec4(rdL, 0.0)).xyz)); return acc; }
          vec3 p = roL + rdL * (dist + 1e-4);
          vec3 nrm = normalize(fn);
          if (dot(nrm, rdL) < 0.0) nrm = -nrm;          // outward, along the ray
          vec3 outD = refract(rdL, -nrm, n);           // diamond -> air
          float cosi = dot(rdL, nrm);
          if (dot(outD, outD) < 1e-6) {                 // total internal reflection
            rdL = reflect(rdL, -nrm); roL = p - nrm * 2e-4; continue;
          }
          float F = fresnel(cosi, n, 1.0);
          acc += thr * (1.0 - F) * env(normalize((modelMat * vec4(outD, 0.0)).xyz));
          thr *= F;
          rdL = reflect(rdL, -nrm); roL = p - nrm * 2e-4;
        }
        // remaining energy leaves along the last direction
        acc += thr * env(normalize((modelMat * vec4(rdL, 0.0)).xyz));
        return acc;
      }
      void main() {
        vec3 n = normalize(cross(dFdx(vWorld), dFdy(vWorld)));   // flat facet normal
        vec3 v = normalize(vWorld - cameraPosition);
        if (dot(n, v) > 0.0) n = -n;
        float cosi = dot(-v, n);
        float F = fresnel(cosi, 1.0, ior);
        vec3 refl = env(reflect(v, n));
        vec3 roL = (modelInv * vec4(vWorld, 1.0)).xyz;
        vec3 nL = normalize((transpose(mat3(modelInv)) * n));
        vec3 vL = normalize((modelInv * vec4(v, 0.0)).xyz);
        vec3 col;
        // white (single-IOR) path gives the facet pattern; dispersion only adds sparse
        // colored sparks: R/B traced with slightly offset IOR, blended in weakly and
        // kept luminance-neutral so the stone never takes on an overall tint.
        col = traceInside(roL, refract(vL, nL, 1.0 / ior), ior);
      #if CHROMA
        float iorR = ior - dispersion, iorB = ior + dispersion;
        float r = traceInside(roL, refract(vL, nL, 1.0 / iorR), iorR).r;
        float b = traceInside(roL, refract(vL, nL, 1.0 / iorB), iorB).b;
        vec3 fire = vec3(r, col.g, b);
        float lw = dot(col, vec3(0.2126, 0.7152, 0.0722));
        float lf = dot(fire, vec3(0.2126, 0.7152, 0.0722));
        fire *= lw / max(lf, 1e-4);                       // same brightness as the white path
        float spark = smoothstep(0.7, 1.8, lw);           // color only in the brightest flashes
        col = mix(col, fire, fireAmount * spark);
      #endif
        col = col * (1.0 - F) * tint + refl * F;
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  mat.onBeforeRender = (r, s, c, g, obj) => { uniforms.modelMat.value.copy(obj.matrixWorld); uniforms.modelInv.value.copy(obj.matrixWorld).invert(); };
  return mat;
}

// ---------------------------------------------------------------- app
// Quality tiers. "full" = desktop; "lite" = phones/iOS (fewer bounces, no fire);
// "basic" = no ray tracing at all (mirror-facet material) if the shader fails or
// the device is too slow. If WebGL itself fails, onFail() lets the page fall back
// to photos.
const TIERS = {
  full: { big: 6, small: 4, chroma: true, pr: 1.75, cube: 512 },
  lite: { big: 4, small: 2, chroma: false, pr: 2, cube: 256 },
  basic: { big: 0, small: 0, chroma: false, pr: 1.5, cube: 256 },
};

export function startViewer({ container, src, onProgress, onLoad, onInteract, onFail, onQuality }) {
  const qs = new URLSearchParams(location.search);
  // debug/QA flags: ?still (no auto-rotate), ?mask (flat diamond mask), ?q=full|lite|basic, ?fail=webgl|load|shader
  const STILL = qs.has('still') || qs.has('mask'), MASK = qs.has('mask');
  const isIOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const isPhone = isIOS || Math.min(screen.width, screen.height) < 600 || matchMedia('(pointer: coarse)').matches;
  let tier = TIERS[qs.get('q')] ? qs.get('q') : (isPhone ? 'lite' : 'full');
  let failed = false;
  const fail = (reason, err) => {
    if (failed) return; failed = true;
    console.warn('3D viewer unavailable:', reason, err || '');
    try { renderer && renderer.setAnimationLoop(null); } catch (e) { /* ignore */ }
    onFail && onFail(reason);
  };

  let renderer;
  try {
    if (qs.get('fail') === 'webgl') throw new Error('forced');
    const probe = document.createElement('canvas');
    if (!probe.getContext('webgl2')) throw new Error('WebGL2 not available');
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance', failIfMajorPerformanceCaveat: false });
  } catch (e) {
    fail('webgl', e);
    return { reset() {}, pause() {}, failed: true };
  }
  const canvas = renderer.domElement;
  canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); fail('context-lost'); });

  // shader compile/link problems (e.g. a GPU that can't handle the ray tracer): drop to basic
  let shaderBroken = qs.get('fail') === 'shader';
  renderer.debug.onShaderError = (gl, program, vs, fs) => {
    shaderBroken = true;
    console.warn('diamond shader failed to compile; using basic material', gl.getProgramInfoLog(program));
  };

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, TIERS[tier].pr));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x000000, 0);
  container.appendChild(canvas);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(22, 1, 0.001, 10);

  // environment: sharp cube for the diamonds, PMREM for the metal
  const hdrOK = renderer.extensions.has('EXT_color_buffer_half_float') || renderer.extensions.has('EXT_color_buffer_float');
  const cubeRT = new THREE.WebGLCubeRenderTarget(TIERS[tier].cube, { type: hdrOK ? THREE.HalfFloatType : THREE.UnsignedByteType, generateMipmaps: false });
  new THREE.CubeCamera(0.1, 50, cubeRT).update(renderer, buildStudio());
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(buildStudio(true), 0.02).texture;
  pmrem.dispose();

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = 0.08;
  controls.enablePan = true; controls.screenSpacePanning = true;
  controls.autoRotate = !STILL; controls.autoRotateSpeed = 16 / 6; // ~16deg/s
  controls.rotateSpeed = 0.8;

  let home = null;
  controls.addEventListener('start', () => { controls.autoRotate = false; onInteract && onInteract(); });

  // soft contact shadow (cheap radial gradient)
  const sc = document.createElement('canvas'); sc.width = sc.height = 128;
  const g = sc.getContext('2d'); const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0, 'rgba(0,0,0,0.16)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false, toneMapped: false }));
  shadow.rotation.x = -Math.PI / 2; if (!MASK) scene.add(shadow);

  // ---- diamond materials per tier
  const stones = []; // { mesh, bvh, big }
  // no ray tracing: flat mirror facets against the brighter (metal) studio, so stones stay white
  const basicDiamond = new THREE.MeshStandardMaterial({
    color: 0xffffff, metalness: 1, roughness: 0.02, flatShading: true, envMapIntensity: 2.2,
  });
  function applyTier(name) {
    tier = name; const T = TIERS[name];
    document.body.dataset.quality = name; onQuality && onQuality(name);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, T.pr)); resize();
    for (const st of stones) {
      if (st.mesh.material && st.mesh.material !== basicDiamond) st.mesh.material.dispose();
      if (name === 'basic') { st.mesh.material = basicDiamond; continue; }
      if (!st.bvh) st.bvh = new MeshBVH(st.mesh.geometry);
      const m = diamondMaterial(st.bvh, cubeRT.texture, { bounces: st.big ? T.big : T.small, chroma: st.big && T.chroma, dispersion: 0.02 });
      m.uniforms.envIntensity.value = st.big ? 1.3 : 1.7;
      st.mesh.material = m;
    }
  }

  const GLB_BYTES = 2656952; // fallback when the server gzips and sends no Content-Length
  const loader = new GLTFLoader();
  const url = qs.get('fail') === 'load' ? src + '.missing' : src;
  loader.load(url, async (gltf) => {
    const root = gltf.scene;
    root.updateMatrixWorld(true);
    root.traverse((o) => {
      if (!o.isMesh) return;
      const name = o.material && o.material.name;
      if (MASK) {
        o.material = new THREE.MeshBasicMaterial({ color: name === 'Diamond' ? 0xff00ff : 0x000000, toneMapped: false });
      } else if (name === 'Diamond') {
        o.geometry.deleteAttribute('normal');
        stones.push({ mesh: o, bvh: null, big: /Center|Heart/.test(o.name) });
      } else {
        o.material = new THREE.MeshPhysicalMaterial({
          // bright polished 18K white gold: high albedo, slightly soft highlights so it never mirrors black
          color: new THREE.Color(0.93, 0.93, 0.92), metalness: 1, roughness: 0.12,
          envMapIntensity: 1.6, clearcoat: 0.3, clearcoatRoughness: 0.04,
        });
      }
    });
    try { applyTier(shaderBroken ? 'basic' : tier); } catch (e) { console.warn(e); applyTier('basic'); }
    scene.add(root);
    const bb = new THREE.Box3().setFromObject(root);
    const ctr = bb.getCenter(new THREE.Vector3()); const size = bb.getSize(new THREE.Vector3());
    const radius = size.length() / 2;
    shadow.position.set(ctr.x, bb.min.y - radius * 0.02, ctr.z);
    shadow.scale.setScalar(Math.max(size.x, size.z) * 1.15);
    controls.target.copy(ctr);
    const dist = radius / Math.sin(THREE.MathUtils.degToRad(22) / 2) * (window.innerWidth > window.innerHeight ? 0.88 : 1.02);
    // default framing: azimuth -40deg, polar 70deg
    const th = THREE.MathUtils.degToRad(-40), ph = THREE.MathUtils.degToRad(70);
    const pos = new THREE.Vector3(Math.sin(ph) * Math.sin(th), Math.cos(ph), Math.sin(ph) * Math.cos(th)).multiplyScalar(dist).add(ctr);
    home = { pos, target: ctr.clone(), dist };
    camera.position.copy(pos); camera.near = dist / 50; camera.far = dist * 10; camera.updateProjectionMatrix();
    controls.minDistance = dist * 0.35; controls.maxDistance = dist * 2.2;
    controls.update();
    // compile shaders without blocking the page (KHR_parallel_shader_compile where available)
    try {
      if (renderer.extensions.has('KHR_parallel_shader_compile')) await renderer.compileAsync(scene, camera);
      else renderer.compile(scene, camera);
    } catch (e) { shaderBroken = true; }
    if (shaderBroken && tier !== 'basic') applyTier('basic');
    if (failed) return;
    ready = true;
    onLoad && onLoad();
  }, (e) => {
    const total = e.total || GLB_BYTES;
    onProgress && onProgress(Math.min(0.98, e.loaded / total));
  }, (err) => fail('load', err));

  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // keep the ring fully in frame on tall phones
    camera.fov = w < h ? 22 * Math.min(1.6, (h / w) * 0.72) : 22;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container); resize();

  // frame-time watchdog: if the device can't keep up, step down a tier (full -> lite -> basic)
  let ready = false, running = true, frames = [], last = 0, slowChecks = 0;
  renderer.setAnimationLoop((t) => {
    if (!running || failed) return;
    controls.update();
    renderer.render(scene, camera);
    if (shaderBroken && tier !== 'basic' && ready) { applyTier('basic'); return; }
    if (!ready || qs.has('q')) return;
    if (last) frames.push(t - last);
    last = t;
    if (frames.length >= 45) {
      frames.sort((a, b) => a - b);
      const med = frames[frames.length >> 1];
      frames = [];
      if (med > 55 && tier !== 'basic' && ++slowChecks >= 1) {
        applyTier(tier === 'full' ? 'lite' : 'basic'); slowChecks = 0;
      }
    }
  });

  return {
    reset() {
      if (!home) return;
      camera.position.copy(home.pos); controls.target.copy(home.target); controls.update();
      controls.autoRotate = !STILL;
    },
    pause(p) { running = !p; last = 0; frames = []; },
    get quality() { return tier; },
  };
}
