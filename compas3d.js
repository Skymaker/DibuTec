/* =====================================================================
   Motor del compás 3D de DibuTec: modelo y mecánica
   Lo usan compas3d.html (la prueba) e index.html (la opción «Compás en 3D»).
   Necesita Three.js r147 (vendor/three-r147: three.min.js, GLTFLoader.js y
   SVGLoader.js).

   Unidades: milímetros. El modelo está en el plano del alzado: X a la derecha
   (de la aguja a la mina), Y hacia arriba (hacia la cabeza) y Z hacia delante;
   la aguja, en (0, 0, 0). Ver instrumentos/compas/3d/LEEME.md.
   ===================================================================== */
window.DibuTecCompas3D = (() => {
'use strict';
const NOMBRES = ['cabeza', 'mango', 'pata-aguja', 'pata-mina', 'pinza-aguja', 'pinza-mina', 'varilla', 'rueda',
                 'punta-aguja', 'punta-mina', 'ajuste-aguja', 'ajuste-mina', 'asa', 'mina'];
const COLOR_MINA = '#757575';
const COLOR_AGUJA = '#1e3a6e';   // aguja de la punta seca: metálica, azul oscuro

// ------------------------------------------------------------------ ruedecitas de las patas
// Ruedecita de apriete: un cilindro con el canto estriado, con el eje a lo largo de X (hacia fuera de la
// pata), y su tornillo, otro cilindro en el mismo eje que va de «a» a «b» (respecto al centro de la rueda)
const Ruedecita = {
  unir(geos) {
    const pos = [], nor = [];
    for (const g0 of geos) {
      const g = g0.index ? g0.toNonIndexed() : g0;
      pos.push(...g.attributes.position.array); nor.push(...g.attributes.normal.array);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    return g;
  },
  crear({ nombre, R, grosor, rTornillo, a, b, mats }) {
    const g = new THREE.Group(); g.name = nombre;
    const cuerpo = new THREE.Mesh(new THREE.CylinderGeometry(R, R, grosor, 48).rotateZ(-Math.PI / 2), mats.cuerpo);
    cuerpo.name = nombre + '-cuerpo';
    const estrias = [], n = 28, e = Math.max(0.1, R * 0.07);
    for (let i = 0; i < n; i++) {
      estrias.push(new THREE.BoxGeometry(grosor * 0.98, e, e).translate(0, R, 0).rotateX(i / n * Math.PI * 2));
    }
    const est = new THREE.Mesh(this.unir(estrias), mats.estrias); est.name = nombre + '-estrias';
    const tor = new THREE.Mesh(new THREE.CylinderGeometry(rTornillo, rTornillo, b - a, 24).rotateZ(-Math.PI / 2).translate((a + b) / 2, 0, 0), mats.tornillo);
    tor.name = 'tornillo-' + nombre;
    for (const m of [cuerpo, est, tor]) { m.castShadow = true; g.add(m); }
    return g;
  },
  // Mallas con la transformación ya aplicada a la geometría (para mezclarlas con las piezas extruidas)
  hornear(grupo) {
    grupo.updateMatrixWorld(true);
    const out = [];
    grupo.traverse(o => { if (o.isMesh) { const m = new THREE.Mesh(o.geometry.clone().applyMatrix4(o.matrixWorld), o.material); m.name = o.name; m.castShadow = true; out.push(m); } });
    return out;
  },
};

// ------------------------------------------------------------------ construcción del modelo desde los SVG
const Construir = {
  // Grosores (mm) sacados de la planta del dibujo
  GROSOR: { cabeza: 5.4, mango: 3.1, pata: 2.7, pinza: 4.2 },
  CAPA: 0.012,   // cada capa del SVG sobresale un poco más que la anterior (sin parpadeos)
  // Un material por color: las piezas del mismo color lo comparten (y así se exporta al .glb)
  materiales: new Map(),
  material(color, nombre) {
    const k = String(color).toLowerCase() + '|' + (nombre || '');
    if (!this.materiales.has(k)) this.materiales.set(k, this.materialNuevo(color, nombre));
    return this.materiales.get(k);
  },
  materialAguja() {
    if (!this.materiales.has('aguja')) this.materiales.set('aguja', new THREE.MeshStandardMaterial({
      color: new THREE.Color(COLOR_AGUJA), metalness: 0.9, roughness: 0.28, envMapIntensity: 0.8, side: THREE.DoubleSide, name: 'aguja-metal-azul' }));
    return this.materiales.get('aguja');
  },
  materialNuevo(color, nombre) {
    const c = new THREE.Color(color);
    const hsl = {}; c.getHSL(hsl);
    const metal = hsl.s < 0.12 && hsl.l > 0.45;   // grises claros: metal
    return new THREE.MeshStandardMaterial({ color: c, metalness: metal ? 0.8 : 0.1, roughness: metal ? 0.38 : 0.55, envMapIntensity: metal ? 0.55 : 0.25, side: THREE.DoubleSide, name: nombre || '' });
  },
  // Color de un relleno: los degradados se sustituyen por su color central
  color(valor, doc) {
    if (!valor || valor === 'none') return null;
    const m = /url\(\s*["']?#([^"')]+)["']?\s*\)/.exec(valor);
    if (!m) return valor;
    let g = doc.getElementById(m[1]);
    for (let i = 0; i < 5 && g && !g.querySelector('stop'); i++) {
      const h = g.getAttribute('href') || g.getAttribute('xlink:href');
      g = h ? doc.getElementById(h.slice(1)) : null;
    }
    if (!g) return '#888888';
    const stops = [...g.querySelectorAll('stop')].map(s => {
      const st = s.getAttribute('style') || '', c = /stop-color:\s*([^;]+)/.exec(st);
      return { o: parseFloat(s.getAttribute('offset')) || 0, c: (c && c[1]) || s.getAttribute('stop-color') || '#888' };
    });
    if (!stops.length) return '#888888';
    stops.sort((a, b) => Math.abs(a.o - 0.5) - Math.abs(b.o - 0.5));
    return stops[0].c.trim();
  },
  // Escala de las transformaciones de un elemento y sus grupos (el grosor de los trazos no la lleva)
  escala(nodo) {
    let k = 1;
    for (let e = nodo; e && e.getAttribute; e = e.parentNode) {
      const t = e.getAttribute('transform') || '';
      for (const m of t.matchAll(/(matrix|scale)\s*\(([^)]*)\)/g)) {
        const v = m[2].split(/[\s,]+/).filter(Boolean).map(Number);
        if (m[1] === 'matrix') k *= Math.sqrt(Math.abs(v[0] * v[3] - v[1] * v[2]));
        else k *= Math.sqrt(Math.abs(v[0] * (v.length > 1 ? v[1] : v[0])));
      }
    }
    return k;
  },
  // Forma con y hacia arriba (el SVG la tiene hacia abajo)
  voltear(shape, espejoX) {
    const sx = espejoX ? -1 : 1;
    const pts = shape.extractPoints(8);
    const s = new THREE.Shape(pts.shape.map(p => new THREE.Vector2(p.x * sx, -p.y)));
    s.holes = pts.holes.map(h => new THREE.Path(h.map(p => new THREE.Vector2(p.x * sx, -p.y))));
    return s;
  },
  // Pieza en relieve: cada relleno del SVG se extruye; cada trazo, una lámina delante y detrás
  pieza(texto, grosor, espejoX = false) {
    const doc = new DOMParser().parseFromString(texto, 'image/svg+xml');
    // Los degradados pasan a su color central (Three.js no los lee)
    texto = texto.replace(/url\(\s*["']?#([^"')]+)["']?\s*\)/g, m => this.color(m, doc) || 'none');
    const datos = new THREE.SVGLoader().parse(texto);
    const grupo = new THREE.Group();
    let capa = 0, minaMesh = null;
    const rellenos = [], trazos = [], rueda = {};
    for (const p of datos.paths) {
      const st = p.userData.style || {}, nodo = p.userData.node;
      if (nodo && nodo.closest && nodo.closest('defs')) continue;
      const esMina = !!(nodo && nodo.closest && nodo.closest('#mina, .mina'));
      const esAguja = !!(nodo && nodo.closest && nodo.closest('#aguja, .aguja'));
      // La ruedecita y su tornillo se hacen con cilindros: aquí solo se miden
      const parte = nodo && nodo.closest && nodo.closest('#ruedecita, #ruedecita-estrias, #ruedecita-tornillo');
      if (parte) {
        const caja = new THREE.Box2();
        for (const sp of p.subPaths) for (const q of sp.getPoints(4)) caja.expandByPoint(q);
        const r = rueda[parte.id] || (rueda[parte.id] = { caja: new THREE.Box2(), color: null });
        r.caja.union(caja);
        r.color = r.color || this.color(parte.id === 'ruedecita-estrias' ? st.stroke : st.fill, doc);
        continue;
      }
      const relleno = this.color(st.fill, doc), borde = this.color(st.stroke, doc);
      if (relleno && st.fillOpacity !== 0) rellenos.push({ p, relleno, esMina, esAguja, op: st.fillOpacity });
      if (borde && st.strokeWidth > 0 && st.strokeOpacity !== 0) trazos.push({ p, borde, st: Object.assign({}, st, { strokeWidth: st.strokeWidth * (nodo ? this.escala(nodo) : 1) }) });
    }
    for (const r of rellenos) {
      const shapes = THREE.SVGLoader.createShapes(r.p).map(s => this.voltear(s, espejoX));
      if (!shapes.length) continue;
      const g = grosor + 2 * capa * this.CAPA;
      const geo = new THREE.ExtrudeGeometry(shapes, { depth: g, bevelEnabled: false, curveSegments: 8 });
      geo.translate(0, 0, -g / 2);
      const mat = r.esMina ? this.materialNuevo(COLOR_MINA, 'mina') : r.esAguja ? this.materialAguja() : r.op < 1 ? this.materialNuevo(r.relleno) : this.material(r.relleno);
      if (r.op < 1) { mat.transparent = true; mat.opacity = r.op; }
      const mesh = new THREE.Mesh(geo, mat);
      mesh.castShadow = true;
      if (r.esMina) { mesh.name = 'mina'; minaMesh = mesh; }
      if (r.esAguja) mesh.name = 'aguja';
      grupo.add(mesh);
      capa++;
    }
    let k = 0;
    for (const t of trazos) {
      for (const sp of t.p.subPaths) {
        const pts = sp.getPoints(8);
        if (pts.length < 2) continue;
        const geo = THREE.SVGLoader.pointsToStroke(pts, t.st);
        if (!geo) continue;
        geo.applyMatrix4(new THREE.Matrix4().makeScale(espejoX ? -1 : 1, -1, 1));
        const z = grosor / 2 + capa * this.CAPA + (k + 1) * 0.004;
        for (const lado of [1, -1]) {
          const m = new THREE.Mesh(geo.clone().translate(0, 0, z * lado), this.material(t.borde));
          grupo.add(m);
        }
        k++;
      }
    }
    // Ruedecita: cilindro con el eje hacia fuera (x de la pieza) y su tornillo, de la pata a la cara de fuera
    if (rueda.ruedecita && rueda['ruedecita-tornillo']) {
      const c = rueda.ruedecita.caja, t = rueda['ruedecita-tornillo'].caja, sx = espejoX ? -1 : 1;
      const u0 = c.min.x, u1 = c.max.x, uc = (u0 + u1) / 2, tc = (c.min.y + c.max.y) / 2;
      const r = Ruedecita.crear({
        nombre: 'ruedecita', R: (c.max.y - c.min.y) / 2, grosor: u1 - u0, rTornillo: (t.max.y - t.min.y) / 2,
        a: t.min.x - uc, b: u1 - uc + 0.25,
        mats: { cuerpo: this.material(rueda.ruedecita.color || '#1b1d22'), estrias: this.material((rueda['ruedecita-estrias'] || {}).color || '#4c5056'),
                tornillo: this.material(rueda['ruedecita-tornillo'].color || '#c4c8cd') },
      });
      r.position.set(uc * sx, -tc, 0);
      if (espejoX) r.scale.x = -1;
      for (const m of Ruedecita.hornear(r)) grupo.add(m);
    }
    return { grupo, minaMesh };
  },
  // Marca (círculo con id) de un SVG, en coordenadas del SVG (y hacia abajo)
  marca(texto, id) {
    const doc = new DOMParser().parseFromString(texto, 'image/svg+xml');
    const c = doc.getElementById(id);
    return c ? { x: parseFloat(c.getAttribute('cx')), y: parseFloat(c.getAttribute('cy')) } : null;
  },
  // Pone la geometría de un grupo en otro sistema: x → ejeX, y → ejeY, origen en «o» (todo en el plano XY)
  colocar(grupo, ejeX, ejeY, o) {
    const det = ejeX.x * ejeY.y - ejeX.y * ejeY.x;
    const m = new THREE.Matrix4().set(ejeX.x, ejeY.x, 0, o.x, ejeX.y, ejeY.y, 0, o.y, 0, 0, det < 0 ? -1 : 1, 0, 0, 0, 0, 1);
    grupo.traverse(o3 => { if (o3.isMesh) o3.geometry.applyMatrix4(m); });
  },
  // Modelo completo en su posición de reposo (la del dibujo). fuente(nombre) da el texto de cada pieza SVG
  modelo(fuente) {
    const T = n => fuente(`compas/tumbado/${n}`);
    const raiz = new THREE.Group(); raiz.name = 'compas';
    const V2 = THREE.Vector2;
    const ejeA = this.marca(T('cabeza'), 'eje-aguja'), ejeM = this.marca(T('cabeza'), 'eje-mina');
    const lp = n => ({ punta: this.marca(T(n), 'punta').y, eje: this.marca(T(n), 'eje').y, ajuste: this.marca(T(n), 'ajuste').y });
    const pa = lp('pata-aguja'), pm = lp('pata-mina');
    const L = ((pa.punta - pa.eje) + (pm.punta - pm.eje)) / 2, ex = (ejeM.x - ejeA.x) / 2, ey = (ejeA.y + ejeM.y) / 2;
    const r0 = 51.1;   // abertura del dibujo original
    const altura = ey + Math.sqrt(L * L - (r0 / 2 - ex) ** 2);
    const b = new V2(r0 / 2, altura);
    const S = { aguja: new V2(b.x + ejeA.x, b.y - ejeA.y), mina: new V2(b.x + ejeM.x, b.y - ejeM.y) };
    const tips = { aguja: new V2(0, 0), mina: new V2(r0, 0) };
    // Cabeza (origen en la bisagra) y mango (origen en el borde de arriba de la cabeza)
    const cab = this.pieza(T('cabeza'), this.GROSOR.cabeza).grupo;
    cab.name = 'cabeza';
    cab.position.set(b.x, b.y, 0);
    raiz.add(cab);
    const caja = new THREE.Box3().setFromObject(cab);
    const man = this.pieza(T('mango'), this.GROSOR.mango).grupo;
    man.name = 'mango';
    man.position.set(0, caja.max.y - b.y, 0);
    cab.add(man);
    const asaM = this.marca(T('mango'), 'asa');
    const asa = new THREE.Object3D(); asa.name = 'asa'; asa.position.set(0, -asaM.y, 0); man.add(asa);
    // Patas: origen en su tornillo, el eje de la pieza hacia la punta
    for (const [lado, nombre, info, signo] of [['aguja', 'pata-aguja', pa, -1], ['mina', 'pata-mina', pm, 1]]) {
      const { grupo } = this.pieza(T(nombre), this.GROSOR.pata);
      const s = S[lado], t = tips[lado], v = t.clone().sub(s).normalize();
      let n = new V2(-v.y, v.x); if (Math.sign(n.x) !== signo) n.negate();
      // punto de la pieza (px, py↓) → s + n·px + v·(py − eje); en la geometría y va hacia arriba: (px, −py)
      this.colocar(grupo, n, v.clone().negate(), v.clone().multiplyScalar(-info.eje));
      grupo.name = nombre;
      grupo.position.set(s.x, s.y, 0);
      raiz.add(grupo);
      const punta = new THREE.Object3D(); punta.name = `punta-${lado}`;
      punta.position.set(v.x * (info.punta - info.eje), v.y * (info.punta - info.eje), 0); grupo.add(punta);
      const aj = new THREE.Object3D(); aj.name = `ajuste-${lado}`;
      aj.position.set(v.x * (info.ajuste - info.eje), v.y * (info.ajuste - info.eje), 0); grupo.add(aj);
    }
    // Pinzas (origen en el punto de ajuste de cada pata), horizontales
    raiz.updateMatrixWorld(true);
    for (const [lado, signo] of [['aguja', -1], ['mina', 1]]) {
      const { grupo } = this.pieza(T('taco'), this.GROSOR.pinza);
      this.colocar(grupo, new V2(signo, 0), new V2(0, 1), new V2(0, 0));
      grupo.name = `pinza-${lado}`;
      const q = raiz.getObjectByName(`ajuste-${lado}`).getWorldPosition(new THREE.Vector3());
      grupo.position.copy(q);
      raiz.add(grupo);
    }
    // Varilla roscada y rueda (cilindros, en horizontal a lo largo de X)
    const qa = raiz.getObjectByName('ajuste-aguja').getWorldPosition(new THREE.Vector3());
    const qm = raiz.getObjectByName('ajuste-mina').getWorldPosition(new THREE.Vector3());
    const medio = qa.clone().add(qm).multiplyScalar(0.5);
    const varilla = new THREE.Group(); varilla.name = 'varilla';
    const largoVarilla = 40;
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.58, 0.58, largoVarilla, 20).rotateZ(Math.PI / 2), this.material('#c4c8cd', 'metal'));
    rod.castShadow = true;
    varilla.add(rod);
    for (let x = -largoVarilla / 2 + 0.35; x < largoVarilla / 2; x += 0.7) {   // rosca
      const anillo = new THREE.Mesh(new THREE.TorusGeometry(0.58, 0.07, 4, 16).rotateY(Math.PI / 2), this.material('#8d939a'));
      anillo.position.x = x; varilla.add(anillo);
    }
    varilla.position.copy(medio);
    raiz.add(varilla);
    const rueda = new THREE.Group(); rueda.name = 'rueda';
    const R = 3.45, ancho = 1.55;
    const disco = new THREE.Mesh(new THREE.CylinderGeometry(R, R, ancho, 40).rotateZ(Math.PI / 2), this.material('#1b1c1f'));
    disco.castShadow = true;
    rueda.add(disco);
    for (let i = 0; i < 24; i++) {   // estrías
      const e = new THREE.Mesh(new THREE.BoxGeometry(ancho * 1.02, 0.28, 0.28), this.material('#3a3d42'));
      const a = i / 24 * Math.PI * 2;
      e.position.set(0, Math.cos(a) * R, Math.sin(a) * R);
      e.rotation.x = -a;
      rueda.add(e);
    }
    rueda.position.copy(medio);
    raiz.add(rueda);
    return raiz;
  },
};

// ------------------------------------------------------------------ mecánica
// Se apoya solo en los nombres y en las posiciones de reposo de las piezas (vale para el modelo de Blender)
const Mecanica = {
  init(modelo) {
    this.m = modelo;
    const g = n => modelo.getObjectByName(n);
    this.p = {};
    for (const n of NOMBRES) this.p[n] = g(n);
    const faltan = NOMBRES.filter(n => !this.p[n]);
    if (faltan.length) throw new Error('Faltan piezas en el modelo: ' + faltan.join(', '));
    modelo.updateMatrixWorld(true);
    const W = o => o.getWorldPosition(new THREE.Vector3());
    const reposo = this.reposo = {};
    for (const n of ['cabeza', 'pata-aguja', 'pata-mina', 'pinza-aguja', 'pinza-mina', 'varilla', 'rueda'])
      reposo[n] = { pos: this.p[n].position.clone(), quat: this.p[n].quaternion.clone() };
    // Geometría que no cambia: tornillos respecto a la bisagra, largo de las patas, puntos de ajuste
    const b = W(this.p.cabeza), Sa = W(this.p['pata-aguja']), Sm = W(this.p['pata-mina']);
    const Ta = W(this.p['punta-aguja']), Tm = W(this.p['punta-mina']);
    this.r0 = Ta.distanceTo(Tm);
    this.ejes = { aguja: Sa.clone().sub(b), mina: Sm.clone().sub(b) };
    this.largo = { aguja: Sa.distanceTo(Ta), mina: Sm.distanceTo(Tm) };
    this.ang0 = { aguja: Math.atan2(Ta.y - Sa.y, Ta.x - Sa.x), mina: Math.atan2(Tm.y - Sm.y, Tm.x - Sm.x) };
    // Puntos de ajuste en el sistema de cada pata (girar la pata los lleva consigo)
    this.ajuste = {
      aguja: W(this.p['ajuste-aguja']).sub(Sa), mina: W(this.p['ajuste-mina']).sub(Sm),
    };
    // Topes del tornillo de ajuste: las pinzas chocan con la rueda (cerrado) o se salen de la varilla (abierto)
    const caja = o => new THREE.Box3().setFromObject(o);
    const cP = caja(this.p['pinza-mina']), qm = W(this.p['pinza-mina']);
    const dentro = qm.x - cP.min.x, fuera = cP.max.x - qm.x;
    const cR = caja(this.p.rueda), cV = caja(this.p.varilla);
    this.dlMin = 2 * dentro + (cR.max.x - cR.min.x) + 0.2;
    this.dlMax = (cV.max.x - cV.min.x) - 2 * fuera - 0.4;
    this.paso = 0.7;   // mm que se separan las pinzas por vuelta de rueda (cada una, 0,35)
    // Codos (opcionales): la parte negra de cada pata gira en el tornillo que la une al brazo metálico
    this.codo = { aguja: g('codo-aguja'), mina: g('codo-mina') };
    this.conCodos = !!(this.codo.aguja && this.codo.mina);
    if (this.conCodos) {
      for (const lado of ['aguja', 'mina']) reposo[`codo-${lado}`] = { quat: this.codo[lado].quaternion.clone() };
      const Ka = W(this.codo.aguja), Km = W(this.codo.mina);
      this.rodilla = { aguja: Ka.clone().sub(Sa), mina: Km.clone().sub(Sm) };
      this.dk = { aguja: Ka.distanceTo(Ta), mina: Km.distanceTo(Tm) };
      // Eje de giro de los codos (el Z del modelo) visto desde cada pata
      this.ejeCodo = {};
      for (const lado of ['aguja', 'mina']) {
        const q = this.p[`pata-${lado}`].getWorldQuaternion(new THREE.Quaternion()).invert();
        this.ejeCodo[lado] = new THREE.Vector3(0, 0, 1).applyQuaternion(q).normalize();
      }
    }
    this.rBrazos = this.radioDe(this.dlMin);   // abertura mínima de los brazos (las pinzas tocan la rueda)
    this.rMin = this.conCodos ? Math.min(5, this.rBrazos) : this.rBrazos;
    this.rMax = Math.min(this.radioDe(this.dlMax), 2 * (Math.abs(this.ejes.mina.x) + Math.min(this.largo.aguja, this.largo.mina) * 0.97));
    this.dl0 = this.separacion(this.r0);
    this.r = this.r0;
    this.aplicar();
  },
  // Postura para una abertura r (plano del alzado; aguja en el origen). Por debajo de rBrazos, los brazos
  // se quedan en rBrazos y las partes negras giran en el codo hacia dentro hasta llegar a las puntas
  postura(r) {
    const rb = this.rBrazos;
    if (!this.conCodos || rb === undefined || r >= rb) return this.posturaRecta(r);
    const p = this.posturaRecta(rb), dx = (rb - r) / 2, z = new THREE.Vector3(0, 0, 1);
    const mover = v => { v.x -= dx; };
    mover(p.b);
    let sube = 0;
    for (const lado of ['aguja', 'mina']) {
      const l = p[lado];
      mover(l.S); mover(l.q);
      l.K = this.rodilla[lado].clone().applyAxisAngle(z, l.giro).add(l.S);
      l.Tv = new THREE.Vector3(lado === 'aguja' ? -dx : r + dx, 0, 0);
      const x = lado === 'aguja' ? 0 : r, hx = x - l.K.x, dk = this.dk[lado];
      l.T = new THREE.Vector3(x, l.K.y - Math.sqrt(Math.max(0, dk * dk - hx * hx)), 0);
      sube += l.T.y / 2;
    }
    p.b.y -= sube;
    for (const lado of ['aguja', 'mina']) {
      const l = p[lado];
      for (const v of [l.S, l.q, l.K, l.Tv, l.T]) v.y -= sube;
      l.codo = Math.atan2(l.T.y - l.K.y, l.T.x - l.K.x) - Math.atan2(l.Tv.y - l.K.y, l.Tv.x - l.K.x);
    }
    return p;
  },
  posturaRecta(r) {
    const ex = (this.ejes.mina.x - this.ejes.aguja.x) / 2, ey = -(this.ejes.aguja.y + this.ejes.mina.y) / 2;
    const L = (this.largo.aguja + this.largo.mina) / 2, h = r / 2 - ex;
    const b = new THREE.Vector3(r / 2, ey + Math.sqrt(Math.max(L * L - h * h, 0)), 0);
    const out = { b };
    for (const lado of ['aguja', 'mina']) {
      const S = b.clone().add(this.ejes[lado]), T = new THREE.Vector3(lado === 'aguja' ? 0 : r, 0, 0);
      const ang = Math.atan2(T.y - S.y, T.x - S.x), giro = ang - this.ang0[lado];
      const q = this.ajuste[lado].clone().applyAxisAngle(new THREE.Vector3(0, 0, 1), giro).add(S);
      out[lado] = { S, giro, q, codo: 0 };
    }
    return out;
  },
  separacion(r) { const p = this.postura(r); return p.mina.q.x - p.aguja.q.x; },
  // Abertura que da una separación de pinzas (la separación crece con la abertura)
  radioDe(dl) {
    let a = 1, z = 200;
    for (let i = 0; i < 60; i++) { const m = (a + z) / 2; if (this.separacion(m) < dl) a = m; else z = m; }
    return (a + z) / 2;
  },
  // Vueltas de la rueda respecto a la abertura del dibujo
  vueltas() { return (this.separacion(this.r) - this.dl0) / this.paso; },
  ponerRadio(r) { this.r = THREE.MathUtils.clamp(r, this.rMin, this.rMax); this.aplicar(); return this.r; },
  // Con las partes negras giradas (por debajo de rBrazos), la rueda mueve los brazos y las puntas a la vez
  girarRueda(dv) {
    const rb = this.rBrazos, base = Math.max(this.r, rb), doblado = this.r - base;
    const brazos = THREE.MathUtils.clamp(this.radioDe(this.separacion(base) + dv * this.paso), rb, this.rMax);
    return this.ponerRadio(brazos + doblado);
  },
  aplicar() {
    const p = this.postura(this.r), R = this.reposo, z = new THREE.Vector3(0, 0, 1);
    this.p.cabeza.position.copy(p.b);
    for (const lado of ['aguja', 'mina']) {
      const o = this.p[`pata-${lado}`];
      o.position.copy(p[lado].S);
      o.quaternion.copy(R[`pata-${lado}`].quat).premultiply(new THREE.Quaternion().setFromAxisAngle(z, p[lado].giro));
      this.p[`pinza-${lado}`].position.copy(p[lado].q);
      if (this.conCodos) {
        const c = this.codo[lado];
        c.quaternion.copy(R[`codo-${lado}`].quat).premultiply(new THREE.Quaternion().setFromAxisAngle(this.ejeCodo[lado], p[lado].codo));
      }
    }
    const medio = p.aguja.q.clone().add(p.mina.q).multiplyScalar(0.5);
    this.p.varilla.position.copy(medio);
    this.p.rueda.position.copy(medio);
    this.p.rueda.quaternion.copy(R.rueda.quat).premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), this.vueltas() * Math.PI * 2));
  },
  reposar() { this.ponerRadio(this.r0); },
};

// ------------------------------------------------------------------ carga del modelo
// Modelo de Blender (compas.glb) si se puede leer y tiene todas las piezas; si no, el que se construye
// desde las piezas SVG del alzado. Devuelve { modelo, origen }.
function cargarModelo(url, fuente, { soloSVG = false } = {}) {
  const desdeSVG = () => ({ modelo: Construir.modelo(fuente), origen: 'svg' });
  if (soloSVG || location.protocol === 'file:') return Promise.resolve(desdeSVG());
  // «no-cache»: el navegador pregunta siempre si el modelo ha cambiado (si no, usaría uno guardado y antiguo)
  return fetch(url, { cache: 'no-cache' })
    .then(r => { if (!r.ok) throw new Error('sin modelo'); return r.arrayBuffer(); })
    .then(buf => new Promise((ok, mal) => new THREE.GLTFLoader().parse(buf, '', ok, mal)))
    .then(g => {
      const faltan = NOMBRES.filter(n => !g.scene.getObjectByName(n));
      if (faltan.length) throw new Error('Faltan piezas en el modelo: ' + faltan.join(', '));
      return { modelo: g.scene, origen: 'glb' };
    })
    .catch(err => { if (err && err.message !== 'sin modelo') console.warn('Compás 3D:', err); return desdeSVG(); });
}

return { NOMBRES, COLOR_MINA, COLOR_AGUJA, Ruedecita, Construir, Mecanica, cargarModelo };
})();
