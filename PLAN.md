# DibuTec — Plan de desarrollo

Simulador 2D de dibujo técnico infantil. Aplicación web en **un único `index.html`**
con CSS y JS incrustados, sin dependencias externas, funcional sin conexión.
Optimizada para **ordenador con ratón** y **tablet táctil**.

## Estado

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Base: estructura, CSS adaptable, iconos SVG, canvas en capas, mm↔px, zoom y desplazamiento | ✅ Hecha |
| 1b | Papel configurable + panel de configuración | ✅ Hecha |
| 2 | Portaminas, puntos magnéticos, goma y deshacer/rehacer | ✅ Hecha |
| 3 | Regla | ⏳ Pendiente |
| 4 | Escuadra, cartabón y deslizamiento | ⏳ Pendiente |
| 5 | Compás | ⏳ Pendiente |
| 6 | Transportador | ⏳ Pendiente |
| 7 | Pulido | ⏳ Pendiente |
| 8 | Ejercicios guiados (opcional) | ⏳ Pendiente |

---

## 1. Arquitectura

- **Un solo `index.html`** con `<style>` y `<script>` incrustados.
- **Unidades reales:** todo el modelo trabaja en **milímetros**; la vista convierte mm→px
  con zoom (`escala` = px/mm) y desplazamiento (`ox`, `oy`). Hoja A4 apaisada
  (297 × 210 mm) por defecto.
- **Tres `<canvas>` superpuestos**, ajustados a `devicePixelRatio`:
  1. **Papel**: mesa, hoja, margen y fondo elegido. Solo se repinta al cambiar zoom,
     desplazamiento o configuración.
  2. **Dibujo**: puntos, rectas, arcos y circunferencias con grosor real de mina (0,5 mm).
  3. **Instrumentos**: regla, escuadra, cartabón, compás y transportador, translúcidos.
- **Pointer Events** únicamente, con `touch-action: none` sobre el lienzo.
- **Módulos** (objetos dentro del mismo `<script>`):
  `Iconos`, `Config`, `Geom`, `Vista`, `Capas`, `Render`, `Escena`, `Snap`,
  `Instrumentos` (clase base `Instrumento` + subclases), `Entrada`, `Historial`, `UI`.
- **`Config`**: preferencias en `localStorage` con valores por defecto
  (lectura/escritura protegidas con `try/catch`).
- **`Iconos`**: todos los SVG como cadenas dentro del JS.

## 2. Modelo de datos

```js
punto:       { id, x, y, etiqueta }          // A, B, C… automáticas
recta:       { id, p1:{x,y}, p2:{x,y} }
arco:        { id, cx, cy, r, a0, a1 }       // circunferencia si |a1-a0| ≥ 2π
instrumento: { tipo, x, y, rot, visible, bloqueado, ...propios }
```

La escena se serializa a JSON → guardado en `localStorage`, exportar/importar e
historial de deshacer/rehacer por instantáneas.

## 3. Instrumentos

| Instrumento | Geometría | Interacción |
|---|---|---|
| **Portaminas 0,5 mm** | Cursor punta | Clic/toque → marca punto (cruz + etiqueta). Arrastrar junto al canto de regla/escuadra/cartabón → traza recta proyectada sobre el canto. Sin canto no traza. |
| **Regla** | 300 × 30 mm, graduada en mm/cm | Arrastrar cuerpo = mover. Asa en extremo = girar (Shift: saltos de 15°). Dos cantos útiles. |
| **Escuadra** | Triángulo 45°-45°-90°, cateto graduado | Igual que la regla; tres cantos útiles. |
| **Cartabón** | Triángulo 30°-60°-90° | Igual. |
| **Compás** | Punta seca + mina | 1) Punta seca → se pega a un punto. 2) Mina → apertura, muestra radio en mm, toma distancia si cae en un punto. 3) Asa superior → gira y traza arco; 360° = circunferencia. |
| **Transportador** | Semicírculo 180°, doble escala | Centro se pega a un punto, base se alinea con una recta. Toque en la escala → punto en el grado exacto (redondeo a 1°). |

## 4. Magnetismo de los puntos

- Objetivos por prioridad: puntos, extremos de rectas, centros de arcos,
  intersecciones (fase 7) y, opcionalmente, nodos de la cuadrícula del papel (prioridad mínima).
- Radio de captura fijo en **píxeles de pantalla** (~12 px ratón, ~20 px táctil),
  ajustable (débil/medio/fuerte).
- Halo de color sobre el objetivo y sonido opcional.
- Lo usan: punta seca y mina del compás, centro del transportador, cantos de
  regla/escuadra/cartabón (se alinean con dos puntos cercanos) y el lápiz.

## 5. Deslizamiento entre instrumentos

1. **Contacto**: canto del instrumento arrastrado casi paralelo (< 3°) y cercano (< 2 mm)
   a un canto de otro → se encaja (mismo ángulo, colineal).
2. **Guía**: mientras hay contacto, el movimiento se proyecta sobre la dirección del canto
   guía; giro bloqueado.
3. **Soltar**: alejar > 8 mm o pulsar Alt.
4. **Candado** para fijar el instrumento guía.
5. Canto en contacto resaltado en verde.

## 6. Interfaz

### 6.1 Panel de configuración (botón engranaje)

Panel lateral deslizante (pantalla completa en móviles/tablets pequeñas).

**Papel**

| Tipo | Dibujo |
|---|---|
| En blanco | Solo color de papel y margen |
| Cuadriculado | Líneas cada 4, 5 o 10 mm |
| Milimetrado | Finas cada 1 mm, medias cada 5 mm, gruesas cada 10 mm |
| Isométrico | Tres familias a 30°, 90° y 150°, separación elegible |

- Vista previa SVG de cada tipo.
- Color de líneas (azul claro / gris / verde), color de papel (blanco / crema),
  tamaño de hoja (A4/A3, horizontal/vertical), margen sí/no.
- **Imán a la cuadrícula** (desactivado por defecto); en isométrico, vértices de los triángulos.

**Dibujo**: grosor de mina 0,3 / 0,5 / 0,7 mm, color del grafito, etiquetado automático.

**Ayudas**: fuerza del imán, sonidos, mensajes de ayuda, tamaño de interfaz.

Se guarda y aplica al instante; botón «Restaurar valores por defecto».

### 6.2 Iconos SVG

- Set propio en línea: portaminas, mover, regla, escuadra, cartabón, compás,
  transportador, goma, deshacer, rehacer, zoom ±, ajustar, candado, engranaje,
  guardar, abrir, exportar, papelera, cerrar.
- `viewBox 0 0 24 24`, trazo 2 px redondeado, color por `currentColor`
  y relleno de acento (clase `.a`) para un aire infantil.
- Cada botón con `aria-label` y `title` con nombre y atajo.

### 6.3 Ratón y táctil

**Común**: Pointer Events, `touch-action: none`, canvas nítido con `devicePixelRatio`,
adaptación automática con `@media (pointer: coarse)` y `pointerType`.

**Ratón**
- Botones de 40 px; rueda = zoom centrado en el cursor; botón central o
  espacio + arrastrar = desplazar.
- Cursor contextual (punta, mano, giro, diana).
- Shift = giro en saltos de 15°, Alt = soltar guía, atajos de teclado.
- Resaltado de cantos y asas al pasar por encima.

**Táctil**
- Botones y asas ≥ 48 px; zonas de toque mayores que el dibujo.
- Un dedo = acción de la herramienta; dos dedos en el papel = zoom + desplazamiento;
  dos dedos en un instrumento = mover + girar.
- Rechazo de palma: si hay un lápiz digital (`pen`) activo se ignoran los dedos.
- Lupa de precisión desplazada sobre el dedo al arrastrar puntas.
- Sin menús contextuales; barra lateral en horizontal, inferior en vertical.
- Sin selección de texto, sin menú por pulsación larga, sin zoom por doble toque.

### 6.4 Atajos de teclado

| Tecla | Acción |
|---|---|
| P | Portaminas |
| M / H | Mover vista |
| R | Regla |
| E | Escuadra |
| T | Cartabón |
| C | Compás |
| A | Transportador |
| B | Goma |
| Ctrl+Z / Ctrl+Y | Deshacer / rehacer |
| + / − / 0 | Acercar / alejar / ajustar hoja |
| Espacio (mantener) | Desplazar vista |
| Esc | Cerrar panel / cancelar |

## 7. Fases

| Fase | Contenido | Resultado comprobable |
|---|---|---|
| **1. Base** | HTML/CSS adaptable, iconos SVG, canvas en capas con DPR, mm↔px, zoom y desplazamiento con ratón y gestos | Hoja visible, zoom y desplazamiento en ratón y táctil |
| **1b. Papel y configuración** | 4 tipos de papel, panel con vistas previas, `localStorage` | Cambiar fondo y que se recuerde |
| **2. Lápiz y puntos** | Marcar puntos, etiquetas, magnetismo, goma, deshacer/rehacer | Marcar y borrar puntos |
| **3. Regla** | Dibujo, mover, girar, cantos, trazado de rectas | Unir dos puntos |
| **4. Escuadra y cartabón** | Clase triángulo genérica, deslizamiento | Trazar paralela y perpendicular |
| **5. Compás** | Pinchar, abrir, girar; arcos y circunferencias | Construir una mediatriz |
| **6. Transportador** | Escala, alineación, marcado de ángulos | Dibujar un ángulo de 60° |
| **7. Pulido** | Lupa táctil, rechazo de palma, imán a cuadrícula, intersecciones, guardar/exportar PNG (con o sin fondo), sonidos, ayuda | Uso completo en tablet |
| **8. Opcional** | Ejercicios guiados (mediatriz, bisectriz, hexágono, cubo isométrico) | Modo tutorial |

Cada fase se prueba con ratón y con táctil.

## 8. Pruebas

- Tests unitarios de `Geom` (proyección, intersecciones, ángulos) en `index.html?test`.
- Playwright en dos perfiles: escritorio con ratón y tablet emulada (iPad, `hasTouch`).
- Capturas de referencia por cada tipo de papel.
- Prueba manual en tablet real.

## 9. Riesgos y decisiones

- **Conflicto de gestos** (¿arrastrar sobre la regla mueve o dibuja?): el lápiz dibuja
  solo si está activo; los instrumentos se mueven arrastrando su cuerpo con la
  herramienta mover o fuera del canto.
- **Precisión vs. facilidad**: fuerza del imán configurable según la edad.
- **Rendimiento**: capa de papel cacheada; capa de dibujo solo se repinta al cambiar.
