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
| `ejercicios/` | Ejercicios guiados, uno por archivo JSON. |
| `ejercicios/indice.json` | Lista de ejercicios que aparecen en la aplicación. |
| `ejercicios/LEEME.md` | Formato de los ejercicios y cómo añadir otros nuevos. |
| `iconos/` | Icono de la aplicación (`icono.svg` es el original; los PNG se generan a partir de él). |
| `manifest.webmanifest` | Datos para instalar la aplicación en la pantalla de inicio. |
| `PLAN.md` | Plan de desarrollo. |

## Añadir ejercicios

Copia el archivo `.json` del ejercicio en `ejercicios/` y añade su nombre a
`ejercicios/indice.json`. El formato está explicado en `ejercicios/LEEME.md`.
