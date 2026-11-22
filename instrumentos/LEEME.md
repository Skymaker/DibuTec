# Piezas de los instrumentos

El aspecto del **compás** sale de piezas SVG. DibuTec las lee, las convierte
en trazados del canvas y las coloca, gira y estira según lo abierto que esté
el compás. Hay dos juegos de piezas:

- `compas/tumbado/`: el **alzado**, el compás tumbado sobre el papel (como se
  ve casi siempre).
- `compas/de-pie/`: la **planta**, el compás de pie visto desde arriba (como se
  ve mientras se traza un arco).

Al empezar a trazar, el compás se levanta y el alzado da paso a la planta con
un fundido; al soltar, vuelve. Las piezas salen del dibujo
`compas/original/compas-alzado-planta.svg` (alzado arriba y planta abajo).

En `compas/3d/` está el modelo 3D del compás para la prueba `compas3d.html`
(ver `compas/3d/LEEME.md`).

## Piezas

| Pieza | Tumbado (alzado) | De pie (planta) | Punto de anclaje (0, 0) |
|---|---|---|---|
| `pata-aguja.svg` | Brazo, pieza negra, ruedecita y aguja. | La pata vista desde arriba. | La bisagra; la punta hacia +y. |
| `pata-mina.svg` | Igual, con la mina. | Igual, con la mina. | La bisagra; la punta hacia +y. |
| `cabeza.svg` | Cabeza negra con sus tornillos. | La cabeza y el mango vistos desde arriba. | La bisagra. |
| `mango.svg` | Mango estriado. | — (lo tapa la cabeza) | Su base, sobre la cabeza. |
| `taco.svg` | Pinza del tornillo de ajuste, con el extremo de la varilla. | Igual, desde arriba. | El eje de la pata a la altura de la varilla. |
| `rueda-ajuste.svg` | Rueda del tornillo de ajuste. | Igual, desde arriba. | Su centro, en la varilla. |
| `varilla.svg` | Trozo de varilla que se repite a lo largo. | — (queda bajo las patas) | Su borde izquierdo. |

Si falta una pieza en una carpeta, DibuTec no la dibuja en esa vista.

## Reglas

- **Unidades: milímetros.** Las coordenadas del dibujo (las del `viewBox`) son
  milímetros reales del compás (las patas miden 75 mm). El tamaño de página no
  importa.
- **El anclaje manda.** Cada pieza se coloca por su punto (0, 0); si mueves
  todo el dibujo, la pieza se moverá en el compás.
- **Patas tumbadas:** el eje de la pata baja desde (0, 0) hacia +y, hasta la
  punta. Hacia **+x** queda el lado de **fuera** del compás (la ruedecita va
  por fuera). Cada pata **gira en su tornillo** de la cabeza: la marca `eje`
  de la pata se coloca sobre la marca `eje-aguja` o `eje-mina` de la cabeza, y
  la pata llega hasta la punta.
- **Patas de pie:** también bajan desde (0, 0) hacia +y, pero hacia **+x**
  queda el lado que en la pantalla está **por encima** de la línea de las
  puntas. Desde arriba, cada pata va de su tornillo (marca `eje`, a un lado
  del centro) a la punta, así que DibuTec la encoge según la abertura.
- **Pinzas, rueda y varilla:** la varilla va en horizontal (+x, de la pata de
  la aguja a la de la mina); en las pinzas, +x es el lado de fuera (la misma
  pieza, en espejo, sirve para las dos patas).
- **Marcas** (círculos con un `id`, sin relleno ni borde, que no se dibujan):
  - `punta` en las patas: dónde está la punta. Fija el largo de la pata.
  - `ajuste` en las patas: a qué distancia de la bisagra va el tornillo de
    ajuste.
  - `eje` en las patas y `eje-aguja` / `eje-mina` en la cabeza tumbada: el
    tornillo en el que gira cada pata.
  - `asa` en el mango: dónde termina; ahí va el asa para girar.
- **La mina:** la forma con `id="mina"` (o `class="mina"`, o lo que haya dentro
  de un grupo así) se pinta del color elegido para el portaminas y se aclara
  cuando la mina está levantada.
- **La cabeza tumbada:** su contorno decide dónde empieza el mango y la zona
  donde se puede agarrar el compás para moverlo.
- **Varilla:** se repite cada tanto como mide el ancho de su `viewBox`.

Se admiten trazados, rectángulos, círculos, elipses, líneas y polígonos, con
grupos y transformaciones, rellenos y bordes (también con opacidad), estilos
en `style` o en clases, y degradados lineales y radiales (también con
`gradientTransform` y enlaces `href`). **Los textos no se dibujan:**
conviértelos en trazados. Tampoco se usan máscaras, recortes, filtros ni
imágenes.

Los botones del compás (el asa para girar y el botón rojo de la mina) no son
piezas: los dibuja DibuTec encima.

## Abertura mínima y máxima

El compás se abre entre **12 y 110 mm de radio** (`rMin` y `rMax` en la clase
`Compas` de `index.html`). Por debajo de 12 mm, las pinzas del tornillo de
ajuste chocarían con la rueda; por encima de 110 mm, el compás estaría
demasiado abierto. Si cambias las piezas (sobre todo las pinzas, la rueda o
la separación de los tornillos), revisa el mínimo.

## Vistas completas

`compas/tumbado/vista-tumbado.svg` y `compas/de-pie/vista-de-pie.svg` son el
compás completo montado con estas piezas, como lo pinta DibuTec (abierto
51,1 mm). Son solo de referencia: DibuTec no las lee. Si retocas piezas,
rehazlas con:

```bash
python3 instrumentos/compas-vistas.py
```

## Después de retocar una pieza

- **Desde un servidor web** (GitHub Pages o `python3 -m http.server`): DibuTec
  lee los archivos de esta carpeta, así que basta con guardar y recargar.
- **Con doble clic en `index.html`:** el navegador no deja leer la carpeta y
  DibuTec usa las copias que guarda dentro de `index.html`. Ponlas al día con:

  ```bash
  python3 instrumentos/incrustar.py
  ```

  Conviene hacerlo siempre antes de publicar, para que las dos copias coincidan.
