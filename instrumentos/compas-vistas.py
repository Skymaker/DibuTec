#!/usr/bin/env python3
"""Genera, a partir de las piezas de compas/tumbado/:

- compas/tumbado/vista-tumbado.svg: el compás completo tumbado, como lo pinta DibuTec.
- compas/de-pie/*.svg: las piezas con la deformación que aplica DibuTec al poner el compás de pie.
- compas/de-pie/vista-de-pie.svg: el compás completo de pie, visto desde arriba.

Las vistas completas se montan con la misma geometría que usa DibuTec (clase Compas de index.html),
con el compás abierto 50 mm y el zoom normal. Son de referencia: DibuTec no las lee.

Uso, después de retocar las piezas tumbadas:
    python3 instrumentos/compas-vistas.py
"""
import math
import pathlib
import re

AQUI = pathlib.Path(__file__).resolve().parent
TUMBADO = AQUI / 'compas' / 'tumbado'
DE_PIE = AQUI / 'compas' / 'de-pie'
PIERNA = 75          # largo de las patas del compás de DibuTec (mm)
ABERTURA = 50        # abertura de las vistas de referencia (mm)
CABEZA_ARRIBA = 6.5  # la cabeza sobresale 6,5 mm por encima de la bisagra (su caja)
MANGO = 13.5         # largo del mango con el zoom normal (mm)


def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')


def partes(nombre):
    """viewBox y contenido (sin el comentario de la cabecera) de una pieza tumbada."""
    t = (TUMBADO / f'{nombre}.svg').read_text(encoding='utf-8')
    m = re.match(r'\s*<svg\b([^>]*)>(.*)</svg>\s*$', t, re.S)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', m.group(1)).group(1).split()]
    cuerpo = re.sub(r'\s*<!--.*?-->', '', m.group(2), count=1, flags=re.S)
    return vb, cuerpo


def marca(nombre, ident, eje, defecto):
    """Coordenada de una marca (círculo con id) de una pieza tumbada."""
    _, cuerpo = partes(nombre)
    m = re.search(rf'<circle\b[^>]*\bid="{ident}"[^>]*>', cuerpo)
    v = m and re.search(rf'\bc{eje}="([-\d.]+)"', m.group(0))
    return float(v.group(1)) if v else defecto


# ------------------------------------------------------------------ piezas de pie
def pieza_de_pie(nombre, sx, sy, explicacion):
    (x0, y0, w, h), cuerpo = partes(nombre)
    vb = [x0 * sx, y0 * sy, w * sx, h * sy]
    (DE_PIE / f'{nombre}.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(vb[2])}mm" height="{fmt(vb[3])}mm" viewBox="{' '.join(fmt(v) for v in vb)}">
  <!--
    DibuTec · compás DE PIE (visto desde arriba) · {nombre}
    Es la pieza tumbada (../tumbado/{nombre}.svg) con la deformación que le aplica DibuTec al ponerse de pie:
    {explicacion}
    Mismo anclaje, mismas marcas y mismos nombres que la pieza tumbada.
    La deformación está en el grupo «de-pie» (transform). Para editar los nodos ya deformados,
    en Inkscape: selecciona el grupo y Objeto › Desagrupar (Mayús+Ctrl+G); la transformación pasa a los trazados.
  -->
  <g id="de-pie" transform="scale({fmt(sx)} {fmt(sy)})">{cuerpo}  </g>
</svg>
''', encoding='utf-8')


# ------------------------------------------------------------------ compás completo
def montar(alzado, r=ABERTURA):
    """Grupos SVG del compás completo y su caja, con la geometría de la clase Compas de DibuTec."""
    s, f = 1 + alzado * 0.5, 1 - alzado * 0.8
    largo = {n: marca(n, 'punta', 'y', PIERNA) for n in ('pata-aguja', 'pata-mina')}
    m = r / 2
    altura = math.sqrt(max(PIERNA ** 2 - m * m, (PIERNA * 0.18) ** 2))
    b = (r / 2, -altura * (1 - alzado))
    punta, mina = (0.0, 0.0), (float(r), 0.0)
    puntos = [punta, mina, b]
    grupos = []

    def grupo(nombre, mat, pre):
        _, cuerpo = partes(nombre)
        cuerpo = re.sub(r'id="([^"]+)"', lambda x: f'id="{pre}-{x.group(1)}"', cuerpo)
        cuerpo = re.sub(r'url\(#([^)]+)\)', lambda x: f'url(#{pre}-{x.group(1)})', cuerpo)
        grupos.append(f'  <g id="{pre}" transform="matrix({" ".join(fmt(v) for v in mat)})">{cuerpo}  </g>\n')

    def lado(t, otra):
        L = math.hypot(t[0] - b[0], t[1] - b[1]) or 1e-6
        v = ((t[0] - b[0]) / L, (t[1] - b[1]) / L)
        n = (-v[1], v[0])
        if (otra[0] - t[0]) * n[0] + (otra[1] - t[1]) * n[1] > 0:
            n = (-n[0], -n[1])
        return L, v, n

    patas = {'pata-aguja': lado(punta, mina), 'pata-mina': lado(mina, punta)}
    for nombre, (L, v, n) in patas.items():
        e = L / largo[nombre]
        grupo(nombre, [n[0] * s, n[1] * s, v[0] * e, v[1] * e, b[0], b[1]], nombre)

    # Tornillo de ajuste
    def ajuste(nombre):
        L, v, _ = patas[nombre]
        d = marca(nombre, 'ajuste', 'y', 20.8) * L / largo[nombre]
        return (b[0] + v[0] * d, b[1] + v[1] * d)
    ql, qr = ajuste('pata-aguja'), ajuste('pata-mina')
    dl = math.hypot(qr[0] - ql[0], qr[1] - ql[1]) or 1e-6
    u = ((qr[0] - ql[0]) / dl, (qr[1] - ql[1]) / dl)
    w = (-u[1], u[0])
    e0 = (ql[0] - u[0] * 4 * s, ql[1] - u[1] * 4 * s)
    total = dl + 8 * s
    (vx, vy, vw, vh), cv = partes('varilla')
    trozos = ''.join(f'    <g transform="translate({fmt(i * vw - vx)} 0)">{cv}    </g>\n' for i in range(math.ceil(total / vw)))
    grupos.append(f'''  <clipPath id="corte-varilla"><rect x="0" y="{fmt(vy)}" width="{fmt(total)}" height="{fmt(vh)}"/></clipPath>
  <g id="varilla" transform="matrix({' '.join(fmt(x) for x in [u[0], u[1], w[0] * s, w[1] * s, e0[0], e0[1]])})" clip-path="url(#corte-varilla)">
{trozos}  </g>
''')
    grupo('taco', [-u[0] * s, -u[1] * s, w[0] * s, w[1] * s, ql[0], ql[1]], 'taco-aguja')
    grupo('taco', [u[0] * s, u[1] * s, w[0] * s, w[1] * s, qr[0], qr[1]], 'taco-mina')
    if dl > 6 * s:
        grupo('rueda-ajuste', [u[0] * s, u[1] * s, w[0] * s, w[1] * s, (ql[0] + qr[0]) / 2, (ql[1] + qr[1]) / 2], 'rueda-ajuste')

    # Mango (hasta el asa) y cabeza
    arriba = b[1] - CABEZA_ARRIBA * s * f
    k = b[1] - (CABEZA_ARRIBA + MANGO) * (1 - alzado * 0.85)
    if k < arriba - 1:
        alto = -marca('mango', 'asa', 'y', -13) or 13
        grupo('mango', [s, 0, 0, (arriba - k) / alto, b[0], arriba], 'mango')
        puntos.append((b[0], k - 3))
    grupo('cabeza', [s, 0, 0, s * f, b[0], b[1]], 'cabeza')
    puntos.append((b[0], arriba - 2))
    puntos.append((b[0], b[1] + 14 * s * f))
    xs, ys = [p[0] for p in puntos], [p[1] for p in puntos]
    caja = (min(xs) - 6 * s, min(ys) - 4, max(xs) - min(xs) + 12 * s, max(ys) - min(ys) + 8 + 4 * s)
    return ''.join(grupos), caja


def vista(alzado, ruta, titulo):
    cuerpo, (x, y, w, h) = montar(alzado)
    ruta.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}mm" height="{fmt(h)}mm" viewBox="{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}">
  <!--
    DibuTec · compás completo {titulo}, como lo pinta DibuTec
    (abierto {ABERTURA} mm: la punta seca en (0, 0) y la mina en ({ABERTURA}, 0); zoom normal).
    Montado con las piezas de compas/tumbado y la misma geometría que usa DibuTec. Solo de referencia:
    DibuTec no lee este archivo. Se rehace con instrumentos/compas-vistas.py.
    No incluye el asa ni el botón de la mina, que dibuja DibuTec encima.
  -->
{cuerpo}</svg>
''', encoding='utf-8')


def main():
    DE_PIE.mkdir(exist_ok=True)
    S, F = 1.5, 0.2
    pieza_de_pie('cabeza', S, S * F, '1,5 veces más ancha (está más cerca de quien mira) y aplastada a 0,3 de su altura (se ve por arriba).')
    for pata in ('pata-aguja', 'pata-mina'):
        pieza_de_pie(pata, S, 1, '1,5 veces más ancha. El largo no cambia aquí: DibuTec lo acorta según lo abierto que esté el compás, igual que en la vista tumbada.')
    pieza_de_pie('mango', S, 1, '1,5 veces más ancho. El largo lo ajusta DibuTec hasta el asa (de pie, el mango apenas asoma: unos 1 mm).')
    pieza_de_pie('taco', S, S, '1,5 veces más grande.')
    pieza_de_pie('rueda-ajuste', S, S, '1,5 veces más grande.')
    pieza_de_pie('varilla', 1, S, '1,5 veces más gruesa; el paso de la rosca (el ancho) no cambia.')
    vista(0, TUMBADO / 'vista-tumbado.svg', 'TUMBADO')
    vista(1, DE_PIE / 'vista-de-pie.svg', 'DE PIE, visto desde arriba')
    print('Generadas: compas/tumbado/vista-tumbado.svg, las piezas de compas/de-pie y compas/de-pie/vista-de-pie.svg')


if __name__ == '__main__':
    main()
