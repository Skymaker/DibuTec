# DibuTec

Simulador de dibujo técnico para la ESO. Funciona en el navegador, con ratón o
en tablet, con portaminas, regla, escuadra, cartabón, compás y transportador.

Pruébalo: https://skymaker.github.io/DibuTec/

## Cómo abrirlo

- **Con doble clic** en `index.html`: funciona todo menos la lista de
  ejercicios guiados (el navegador no deja leer la carpeta). Los ejercicios se
  pueden cargar con «Cargar un ejercicio (.json)» o arrastrándolos sobre la hoja.
- **Desde un servidor web** (GitHub Pages, o `python3 -m http.server` en esta
  carpeta y abrir `http://localhost:8000`): funciona todo, también la lista de
  ejercicios.

## Archivos

| Archivo | Contenido |
|---|---|
| `index.html` | La aplicación completa (HTML, CSS y JavaScript en un único archivo). |
| `editor.html` | Editor gráfico de ejercicios guiados (también en un único archivo). |
| `compas3d.html` | Prueba de un compás en 3D con funcionamiento mecánico (modelo en `instrumentos/compas/3d/`). |
| `compas3d.js` | Modelo y mecánica del compás 3D, que usan `compas3d.html` y la opción «Compás en 3D» de la aplicación. |
| `vendor/three-r147/` | Three.js (licencia MIT), para el compás 3D. La aplicación solo lo carga si se activa «Compás en 3D». |
| `ejercicios/` | Ejercicios guiados, uno por archivo JSON. |
| `ejercicios/indice.json` | Temas y ejercicios que aparecen en la aplicación, en orden. |
| `ejercicios/LEEME.md` | Formato de los ejercicios y cómo añadir otros nuevos. |
| `instrumentos/` | Piezas SVG del compás: alzado (`compas/tumbado/`) y planta (`compas/de-pie/`), para retocar su aspecto (ver `instrumentos/LEEME.md`). |
| `iconos/` | Icono de la aplicación (`icono.svg` es el original; los PNG se generan a partir de él). |
| `manifest.webmanifest` | Datos para instalar la aplicación en la pantalla de inicio. |
| `PLAN.md` | Plan de desarrollo. |

## Añadir ejercicios

La forma más cómoda es el **editor de ejercicios** (`editor.html`, también desde
el panel «Ejercicios guiados» de la aplicación): se dibuja el enunciado sobre la
hoja, se escriben los pasos con sus objetivos, se ve la construcción esperada de
cada paso, se revisan los errores y se prueba en DibuTec con un botón. «Guardar»
descarga el `.json`.

A mano: Copia el archivo `.json` del ejercicio en `ejercicios/` y añade su nombre a
uno de los temas de `ejercicios/indice.json`. El formato está explicado en `ejercicios/LEEME.md`.
