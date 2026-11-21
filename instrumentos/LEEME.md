# Piezas de los instrumentos

El aspecto del **compás** sale de las piezas SVG de `compas/`. DibuTec las lee,
las convierte en trazados del canvas y las coloca, gira y estira según lo
abierto que esté el compás y según se ponga de pie al trazar. Se pueden
retocar con Inkscape, Illustrator o cualquier editor de SVG.

| Pieza | Qué es | Punto de anclaje (0, 0) |
|---|---|---|
| `compas/pata-aguja.svg` | Pata de la punta seca: brazo metálico, pieza negra, tornillo, ruedecita y aguja. | La bisagra. La punta está hacia abajo. |
| `compas/pata-mina.svg` | Pata de la mina, igual pero con dos ruedecitas y la mina. | La bisagra. La punta está hacia abajo. |
| `compas/cabeza.svg` | Cabeza negra con los tornillos de las patas. | La bisagra. |
| `compas/mango.svg` | Mango estriado entre la cabeza y el asa. | Su base, sobre la cabeza. |
| `compas/taco.svg` | Taco del tornillo de ajuste (hay uno en cada pata). | El eje de la pata; la varilla va en horizontal. |
| `compas/rueda-ajuste.svg` | Rueda del centro del tornillo de ajuste. | Su centro; la varilla va en horizontal. |
| `compas/varilla.svg` | Trozo de varilla roscada que se repite a lo largo. | Su borde izquierdo; la varilla va en horizontal. |

## Reglas

- **Unidades: milímetros.** Las coordenadas del dibujo (las del `viewBox`) son
  milímetros reales del compás. El tamaño de página no importa.
- **El anclaje manda.** Cada pieza se coloca por su punto (0, 0); si mueves
  todo el dibujo, la pieza se moverá en el compás.
- **Patas:** la bisagra en (0, 0) y la punta hacia abajo (+y). Hacia **+x**
  queda el lado de **fuera** del compás (las ruedecitas van por fuera). La
  pata se estira a lo largo según lo abierto que esté el compás y se ensancha
  al ponerse de pie.
- **Marcas** (formas con un `id`, sin relleno ni borde, que no se dibujan):
  - `punta` en las patas: dónde está la punta. Fija el largo de la pata (75 mm).
  - `ajuste` en las patas: a qué altura va el tornillo de ajuste.
  - `asa` en el mango: dónde termina; el mango se estira o encoge en vertical
    para llegar hasta el asa.
- **La mina:** la forma con `id="mina"` (o `class="mina"`, o lo que haya dentro
  de un grupo así) se pinta del color elegido para el portaminas y se aclara
  cuando la mina está levantada.
- **La cabeza:** su contorno decide dónde empieza el mango y la zona donde se
  puede agarrar el compás para moverlo.
- **Varilla:** se repite cada tanto como mide el ancho de su `viewBox` (es el
  paso de la rosca).

Se admiten trazados, rectángulos, círculos, elipses, líneas y polígonos, con
grupos y transformaciones, rellenos y bordes (también con opacidad), estilos
en `style` o en clases, y degradados lineales y radiales. **Los textos no se
dibujan:** conviértelos en trazados (en Inkscape, *Trazo › Objeto a trazo*).
Tampoco se usan máscaras, recortes, filtros ni imágenes.

Los botones del compás (el asa para girar y el botón rojo de la mina) no son
piezas: los dibuja DibuTec encima.

## Después de retocar una pieza

- **Desde un servidor web** (GitHub Pages o `python3 -m http.server`): DibuTec
  lee los archivos de esta carpeta, así que basta con guardar y recargar.
- **Con doble clic en `index.html`:** el navegador no deja leer la carpeta y
  DibuTec usa las copias que guarda dentro de `index.html`. Ponlas al día con:

  ```bash
  python3 instrumentos/incrustar.py
  ```

  Conviene hacerlo siempre antes de publicar, para que las dos copias coincidan.
