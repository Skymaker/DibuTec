#!/usr/bin/env python3
"""Copia las piezas SVG de esta carpeta dentro de index.html (y de compas3d.html).

DibuTec lee las piezas de sus archivos cuando se abre desde un servidor web
(GitHub Pages, python3 -m http.server…). Al abrir index.html con doble clic,
el navegador no deja leer la carpeta y usa las copias que guarda dentro de
index.html: este script las pone al día.

Uso (desde la carpeta de DibuTec o desde esta):
    python3 instrumentos/incrustar.py
"""
import json
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent
INDEX = AQUI.parent / 'index.html'
INICIO = '/* PIEZAS-SVG:INICIO (lo escribe instrumentos/incrustar.py; no editar a mano) */'
FIN = '/* PIEZAS-SVG:FIN */'


def main():
    piezas = {}
    # <instrumento>/<vista>/<pieza>.svg (las vistas completas, vista-*.svg, y el dibujo original son solo de referencia)
    for f in sorted(AQUI.glob('*/*/*.svg')):
        if f.stem.startswith('vista-') or f.parent.name == 'original':
            continue
        piezas[f'{f.parent.parent.name}/{f.parent.name}/{f.stem}'] = f.read_text(encoding='utf-8')
    if not piezas:
        sys.exit('No hay piezas SVG en ' + str(AQUI))
    lineas = ['  incrustadas: {']
    for nombre, texto in piezas.items():
        # «</» cortaría el <script> de index.html
        cadena = json.dumps(texto, ensure_ascii=False).replace('</', '<\\/')
        lineas.append(f'    {json.dumps(nombre)}: {cadena},')
    lineas.append('  },')
    # index.html (la aplicación) y compas3d.html (la prueba del compás en 3D, que se construye desde ellas)
    for destino in (INDEX, AQUI.parent / 'compas3d.html'):
        if not destino.exists():
            continue
        html = destino.read_text(encoding='utf-8')
        i, j = html.find(INICIO), html.find(FIN)
        if i < 0 or j < i:
            sys.exit(f'No encuentro las marcas PIEZAS-SVG en {destino.name}')
        nuevo = html[:i + len(INICIO)] + '\n' + '\n'.join(lineas) + '\n  ' + html[j:]
        if nuevo == html:
            print(f'{destino.name} ya tenía estas piezas.')
            continue
        destino.write_text(nuevo, encoding='utf-8')
        print(f'{len(piezas)} piezas copiadas en {destino.name}: ' + ', '.join(piezas))


if __name__ == '__main__':
    main()
