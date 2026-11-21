#!/usr/bin/env python3
"""Copia las piezas SVG de esta carpeta dentro de index.html.

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
    for f in sorted(AQUI.glob('*/*.svg')):
        piezas[f'{f.parent.name}/{f.stem}'] = f.read_text(encoding='utf-8')
    if not piezas:
        sys.exit('No hay piezas SVG en ' + str(AQUI))
    lineas = ['  incrustadas: {']
    for nombre, texto in piezas.items():
        # «</» cortaría el <script> de index.html
        cadena = json.dumps(texto, ensure_ascii=False).replace('</', '<\\/')
        lineas.append(f'    {json.dumps(nombre)}: {cadena},')
    lineas.append('  },')
    html = INDEX.read_text(encoding='utf-8')
    i, j = html.find(INICIO), html.find(FIN)
    if i < 0 or j < i:
        sys.exit('No encuentro las marcas PIEZAS-SVG en index.html')
    nuevo = html[:i + len(INICIO)] + '\n' + '\n'.join(lineas) + '\n  ' + html[j:]
    if nuevo == html:
        print('index.html ya tenía estas piezas.')
        return
    INDEX.write_text(nuevo, encoding='utf-8')
    print(f'{len(piezas)} piezas copiadas en index.html: ' + ', '.join(piezas))


if __name__ == '__main__':
    main()
