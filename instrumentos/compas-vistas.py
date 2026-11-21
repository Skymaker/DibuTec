#!/usr/bin/env python3
"""Monta el compás completo con las piezas de compas/, con la misma geometría que usa DibuTec
(clase Compas de index.html), abierto como en el dibujo original y con el zoom normal:

- compas/tumbado/vista-tumbado.svg: tumbado sobre el papel (alzado).
- compas/de-pie/vista-de-pie.svg: de pie, visto desde arriba (planta).

Son de referencia: DibuTec no las lee. Uso, después de retocar piezas:
    python3 instrumentos/compas-vistas.py
"""
import math
import pathlib
import re

AQUI = pathlib.Path(__file__).resolve().parent / 'compas'
ABERTURA = 51.1      # mm entre la punta seca y la mina
PIERNA = 75          # largo de las patas en DibuTec (mm)


def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')


def leer(vista, nombre):
    f = AQUI / vista / f'{nombre}.svg'
    if not f.exists():
        return None
    t = f.read_text(encoding='utf-8')
    m = re.match(r'\s*(?:<\?xml[^>]*>\s*)?<svg\b([^>]*)>(.*)</svg>\s*$', t, re.S)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', m.group(1)).group(1).split()]
    cuerpo = re.sub(r'\s*<!--.*?-->', '', m.group(2), count=1, flags=re.S)
    return vb, cuerpo


def marca(vista, nombre, ident, eje, defecto):
    p = leer(vista, nombre)
    m = p and re.search(rf'<circle\b[^>]*\bid="{ident}"[^>]*>', p[1])
    v = m and re.search(rf'\bc{eje}="([-\d.]+)"', m.group(0))
    return float(v.group(1)) if v else defecto


def caja_cabeza(vista):
    """Caja aproximada de la cabeza a partir de su viewBox (la pieza se guarda con un margen de 0,6 mm)."""
    vb, _ = leer(vista, 'cabeza')
    return vb[0] + 0.6, vb[1] + 0.6, vb[2] - 1.2, vb[3] - 1.2


class Montaje:
    def __init__(self):
        self.grupos, self.n = [], 0

    def pieza(self, vista, nombre, mat, pre=None):
        p = leer(vista, nombre)
        if not p:
            return
        self.n += 1
        pre = pre or f'{nombre}-{self.n}'
        cuerpo = re.sub(r'id="([^"]+)"', lambda x: f'id="{pre}-{x.group(1)}"', p[1])
        cuerpo = re.sub(r'(url\(#|href="#)([^)"]+)', lambda x: f'{x.group(1)}{pre}-{x.group(2)}', cuerpo)
        self.grupos.append(f'  <g id="{pre}" transform="matrix({" ".join(fmt(v) for v in mat)})">{cuerpo}  </g>\n')

    def varilla(self, vista, mat, largo):
        p = leer(vista, 'varilla')
        if not p:
            return
        (vx, vy, vw, vh), cv = p
        trozos = ''.join(f'    <g transform="translate({fmt(i * vw - vx)} 0)">{cv}    </g>\n' for i in range(math.ceil(largo / vw)))
        self.grupos.append(f'''  <clipPath id="corte-varilla-{vista}"><rect x="0" y="{fmt(vy)}" width="{fmt(largo)}" height="{fmt(vh)}"/></clipPath>
  <g id="varilla" transform="matrix({' '.join(fmt(x) for x in mat)})" clip-path="url(#corte-varilla-{vista})">
{trozos}  </g>
''')

    def ajuste(self, vista, ql, qr):
        dl = math.hypot(qr[0] - ql[0], qr[1] - ql[1]) or 1e-6
        u = ((qr[0] - ql[0]) / dl, (qr[1] - ql[1]) / dl)
        w = (-u[1], u[0])
        self.varilla(vista, [u[0], u[1], w[0], w[1], ql[0] - u[0] * 4, ql[1] - u[1] * 4], dl + 8)
        self.pieza(vista, 'taco', [-u[0], -u[1], w[0], w[1], ql[0], ql[1]], 'taco-aguja')
        self.pieza(vista, 'taco', [u[0], u[1], w[0], w[1], qr[0], qr[1]], 'taco-mina')
        self.pieza(vista, 'rueda-ajuste', [u[0], u[1], w[0], w[1], (ql[0] + qr[0]) / 2, (ql[1] + qr[1]) / 2], 'rueda-ajuste')


def tumbado(r=ABERTURA):
    M, V = Montaje(), 'tumbado'
    # Cada pata gira en su tornillo de la cabeza (marcas «eje-aguja» y «eje-mina»)
    ejes = {'pata-aguja': (marca(V, 'cabeza', 'eje-aguja', 'x', -2.5), marca(V, 'cabeza', 'eje-aguja', 'y', 7.3)),
            'pata-mina': (marca(V, 'cabeza', 'eje-mina', 'x', 2.5), marca(V, 'cabeza', 'eje-mina', 'y', 7.3))}
    largo = {n: marca(V, n, 'punta', 'y', PIERNA) - marca(V, n, 'eje', 'y', 7.7) for n in ejes}
    ex = (ejes['pata-mina'][0] - ejes['pata-aguja'][0]) / 2
    ey = (ejes['pata-mina'][1] + ejes['pata-aguja'][1]) / 2
    L = (largo['pata-aguja'] + largo['pata-mina']) / 2
    h = max(0, r / 2 - ex)
    b = (r / 2, -(ey + math.sqrt(max(L * L - h * h, (L * 0.18) ** 2))))
    q = {}
    for nombre, t, otra in (('pata-aguja', (0, 0), (r, 0)), ('pata-mina', (r, 0), (0, 0))):
        S = (b[0] + ejes[nombre][0], b[1] + ejes[nombre][1])
        Ls = math.dist(S, t)
        v = ((t[0] - S[0]) / Ls, (t[1] - S[1]) / Ls)
        n = (-v[1], v[0])
        if (otra[0] - t[0]) * n[0] + (otra[1] - t[1]) * n[1] > 0:
            n = (-n[0], -n[1])
        e = Ls / largo[nombre]
        eje = marca(V, nombre, 'eje', 'y', 7.7)
        O = (S[0] - v[0] * eje * e, S[1] - v[1] * eje * e)
        M.pieza(V, nombre, [n[0], n[1], v[0] * e, v[1] * e, O[0], O[1]], nombre)
        d = marca(V, nombre, 'ajuste', 'y', 24) * e
        q[nombre] = (O[0] + v[0] * d, O[1] + v[1] * d)
    M.ajuste(V, q['pata-aguja'], q['pata-mina'])
    cx, cy, cw, ch = caja_cabeza(V)
    arriba = b[1] + cy
    largo = -marca(V, 'mango', 'asa', 'y', -8)
    M.pieza(V, 'mango', [1, 0, 0, 1, b[0], arriba], 'mango')
    M.pieza(V, 'cabeza', [1, 0, 0, 1, b[0], b[1]], 'cabeza')
    return M, (-8, arriba - largo - 4, r + 16, -(arriba - largo - 4) + 4)


def de_pie(r=ABERTURA):
    M, V = Montaje(), 'de-pie'
    b = (r / 2, 0)
    q = {}
    for nombre, t in (('pata-aguja', (0, 0)), ('pata-mina', (r, 0))):
        L0 = math.dist(b, t)
        v = ((t[0] - b[0]) / L0, (t[1] - b[1]) / L0)
        eje, punta = marca(V, nombre, 'eje', 'y', 2.5), marca(V, nombre, 'punta', 'y', 25)
        e = (L0 - eje) / (punta - eje)                 # desde arriba, la pata va de su tornillo a la punta
        O = (b[0] + v[0] * eje * (1 - e), b[1] + v[1] * eje * (1 - e))
        M.pieza(V, nombre, [0, -1, v[0] * e, v[1] * e, O[0], O[1]], nombre)   # +x de la pieza: hacia arriba
        d = marca(V, nombre, 'ajuste', 'y', 8) * e
        q[nombre] = (O[0] + v[0] * d, O[1] + v[1] * d)
    M.ajuste(V, q['pata-aguja'], q['pata-mina'])
    M.pieza(V, 'cabeza', [1, 0, 0, 1, b[0], b[1]], 'cabeza')
    return M, (-6, -8, r + 12, 16)


def escribir(ruta, titulo, montaje):
    M, (x, y, w, h) = montaje
    ruta.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{fmt(w)}mm" height="{fmt(h)}mm" viewBox="{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}">
  <!--
    DibuTec · compás completo {titulo}, como lo pinta DibuTec
    (abierto {fmt(ABERTURA)} mm: la punta seca en (0, 0) y la mina en ({fmt(ABERTURA)}, 0); zoom normal).
    Montado con las piezas de esta carpeta y la misma geometría que usa DibuTec. Solo de referencia:
    DibuTec no lee este archivo. Se rehace con instrumentos/compas-vistas.py.
    No incluye el asa ni el botón de la mina, que dibuja DibuTec encima.
  -->
{''.join(M.grupos)}</svg>
''', encoding='utf-8')


if __name__ == '__main__':
    escribir(AQUI / 'tumbado' / 'vista-tumbado.svg', 'TUMBADO (alzado)', tumbado())
    escribir(AQUI / 'de-pie' / 'vista-de-pie.svg', 'DE PIE, visto desde arriba (planta)', de_pie())
    print('Generadas compas/tumbado/vista-tumbado.svg y compas/de-pie/vista-de-pie.svg')
