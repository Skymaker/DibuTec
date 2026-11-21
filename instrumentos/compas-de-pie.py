#!/usr/bin/env python3
"""Genera en compas/de-pie/ las piezas del compás de pie (visto desde arriba) a partir de las
tumbadas de compas/, con las mismas deformaciones que aplica DibuTec al ponerse de pie, y el
compás completo de pie (vista-de-pie.svg) como referencia.

Uso, después de retocar las piezas tumbadas:
    python3 instrumentos/compas-de-pie.py
"""
import re, pathlib, math
BASE = pathlib.Path(__file__).resolve().parent / 'compas'
OUT = BASE / 'de-pie'
S, F = 1.5, 0.2          # de pie: 50 % más ancho; la cabeza, aplastada al 20 % (en altura, × 1,5 × 0,2 = 0,3)

def partes(nombre):
    t = (BASE / f'{nombre}.svg').read_text(encoding='utf-8')
    m = re.match(r'\s*<svg\b([^>]*)>(.*)</svg>\s*$', t, re.S)
    attrs, cuerpo = m.group(1), m.group(2)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', attrs).group(1).split()]
    cuerpo = re.sub(r'\s*<!--.*?-->', '', cuerpo, count=1, flags=re.S)   # el comentario de la cabecera
    return vb, cuerpo

def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')

def pieza(nombre, sx, sy, explicacion):
    vb, cuerpo = partes(nombre)
    x0, y0, w, h = vb
    nvb = [x0 * sx, y0 * sy, w * sx, h * sy]
    texto = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(nvb[2])}mm" height="{fmt(nvb[3])}mm" viewBox="{' '.join(fmt(v) for v in nvb)}">
  <!--
    DibuTec · compás DE PIE (visto desde arriba) · {nombre}
    Es la pieza tumbada ({nombre}.svg) con la deformación que le aplica DibuTec al ponerse de pie:
    {explicacion}
    Mismo anclaje, mismas marcas y mismos nombres que la pieza tumbada.
    La deformación está en el grupo «de-pie» (transform). Para editar los nodos ya deformados,
    en Inkscape: selecciona el grupo y Objeto › Desagrupar (Mayús+Ctrl+G); la transformación pasa a los trazados.
  -->
  <g id="de-pie" transform="scale({fmt(sx)} {fmt(sy)})">{cuerpo}  </g>
</svg>
'''
    (OUT / f'{nombre}.svg').write_text(texto, encoding='utf-8')

pieza('cabeza', S, S * F, '1,5 veces más ancha (está más cerca de quien mira) y aplastada a 0,3 de su altura (se ve por arriba).')
pieza('pata-aguja', S, 1, '1,5 veces más ancha. El largo no cambia aquí: DibuTec lo acorta según lo abierto que esté el compás, igual que en la vista tumbada.')
pieza('pata-mina', S, 1, '1,5 veces más ancha. El largo no cambia aquí: DibuTec lo acorta según lo abierto que esté el compás, igual que en la vista tumbada.')
pieza('mango', S, 1, '1,5 veces más ancho. El largo lo ajusta DibuTec hasta el asa (de pie, el mango apenas asoma: unos 1 mm).')
pieza('taco', S, S, '1,5 veces más grande.')
pieza('rueda-ajuste', S, S, '1,5 veces más grande.')
pieza('varilla', 1, S, '1,5 veces más gruesa; el paso de la rosca (el ancho) no cambia.')

# ---- Compás completo de pie, montado como en DibuTec (abertura r = 50 mm, zoom normal) ----
r = 50.0
b = (r / 2, 0.0)
def pieza_g(nombre, mat, pre, extra=''):
    _, cuerpo = partes(nombre)
    cuerpo = re.sub(r'id="([^"]+)"', lambda m: f'id="{pre}-{m.group(1)}"', cuerpo)
    cuerpo = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{pre}-{m.group(1)})', cuerpo)
    return f'  <g id="{pre}" transform="matrix({" ".join(fmt(v) for v in mat)})"{extra}>{cuerpo}  </g>\n'
def lado(t, otra):
    L = math.hypot(t[0] - b[0], t[1] - b[1]); v = ((t[0] - b[0]) / L, (t[1] - b[1]) / L); n = (-v[1], v[0])
    if (otra[0] - t[0]) * n[0] + (otra[1] - t[1]) * n[1] > 0: n = (-n[0], -n[1])
    return L, v, n
punta, mina = (0.0, 0.0), (r, 0.0)
partes_svg = []
for nombre, t, o, pre in (('pata-aguja', punta, mina, 'pata-aguja'), ('pata-mina', mina, punta, 'pata-mina')):
    L, v, n = lado(t, o); e = L / 75
    partes_svg.append(pieza_g(nombre, [n[0] * S, n[1] * S, v[0] * e, v[1] * e, b[0], b[1]], pre))
Li, vi, _ = lado(punta, mina); Ld, vd, _ = lado(mina, punta)
ql = (b[0] + vi[0] * 20.8 * Li / 75, b[1] + vi[1] * 20.8 * Li / 75); qr = (b[0] + vd[0] * 20.8 * Ld / 75, b[1] + vd[1] * 20.8 * Ld / 75)
dl = math.hypot(qr[0] - ql[0], qr[1] - ql[1]); u = ((qr[0] - ql[0]) / dl, (qr[1] - ql[1]) / dl); w = (-u[1], u[0])
e0 = (ql[0] - u[0] * 4 * S, ql[1] - u[1] * 4 * S); largo = dl + 8 * S
vtiles = ''
_, cv = partes('varilla')
n_t = math.ceil(largo / 0.7)
vtiles = ''.join(f'    <g transform="translate({fmt(i * 0.7)} 0)">{cv}    </g>\n' for i in range(n_t))
partes_svg.append(f'''  <clipPath id="corte-varilla"><rect x="0" y="-0.6" width="{fmt(largo)}" height="1.2"/></clipPath>
  <g id="varilla" transform="matrix({' '.join(fmt(x) for x in [u[0], u[1], w[0] * S, w[1] * S, e0[0], e0[1]])})" clip-path="url(#corte-varilla)">
{vtiles}  </g>
''')
partes_svg.append(pieza_g('taco', [-u[0] * S, -u[1] * S, w[0] * S, w[1] * S, ql[0], ql[1]], 'taco-izquierdo'))
partes_svg.append(pieza_g('taco', [u[0] * S, u[1] * S, w[0] * S, w[1] * S, qr[0], qr[1]], 'taco-derecho'))
if dl > 6 * S:
    partes_svg.append(pieza_g('rueda-ajuste', [u[0] * S, u[1] * S, w[0] * S, w[1] * S, (ql[0] + qr[0]) / 2, (ql[1] + qr[1]) / 2], 'rueda-ajuste'))
# mango: asa a (6,5 + 13,5) × 0,15 = 3 mm de la bisagra; la cabeza empieza a 6,5 × 1,5 × 0,2 = 1,95 mm
arriba = b[1] - 6.5 * S * F; k = b[1] - 20 * 0.15
if k < arriba - 1:
    partes_svg.append(pieza_g('mango', [S, 0, 0, (arriba - k) / 13, b[0], arriba], 'mango'))
partes_svg.append(pieza_g('cabeza', [S, 0, 0, S * F, b[0], b[1]], 'cabeza'))
xs = (-6, r + 6); ys = (-12, 12)
(OUT / 'vista-de-pie.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(xs[1]-xs[0])}mm" height="{fmt(ys[1]-ys[0])}mm" viewBox="{fmt(xs[0])} {fmt(ys[0])} {fmt(xs[1]-xs[0])} {fmt(ys[1]-ys[0])}">
  <!--
    DibuTec · compás DE PIE completo, visto desde arriba, como lo pinta DibuTec al trazar
    (abertura de 50 mm; la punta seca en (0, 0) y la mina en (50, 0)). Solo de referencia: DibuTec no lo lee.
    Está montado con las piezas tumbadas y las mismas matrices que usa DibuTec, así que coincide con ellas.
    No incluye el asa ni el botón de la mina, que dibuja DibuTec encima.
  -->
{''.join(partes_svg)}</svg>
''', encoding='utf-8')
print('Piezas de pie y vista-de-pie.svg generadas en', OUT)
