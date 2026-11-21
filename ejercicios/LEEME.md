# Ejercicios guiados de DibuTec

Cada ejercicio es **un archivo JSON** en esta carpeta. DibuTec lee
`indice.json` y carga cada ejercicio de su propio archivo, así que un archivo
con errores no impide usar los demás.

## Añadir un ejercicio

1. Crea `mi-ejercicio.json` en esta carpeta (puedes copiar uno existente).
2. Añade su nombre a uno de los temas de `indice.json` (ver abajo).

3. Abre DibuTec desde un servidor web (por ejemplo, GitHub Pages o
   `python3 -m http.server`) y pulsa el botón **Ejercicios guiados**.

Si abres DibuTec con doble clic (`file://`), el navegador no deja leer la
carpeta. En ese caso, carga el ejercicio con **Cargar un ejercicio (.json)**
o arrastra el archivo sobre la hoja. También se puede abrir directamente con
la dirección `index.html?ejercicio=ejercicios/mi-ejercicio.json`.

Si un archivo tiene un error, la lista de ejercicios lo muestra en rojo con el
motivo (por ejemplo, «paso 3: tipo de objetivo desconocido «arcoo»»).

## Temas: `indice.json`

Los ejercicios se agrupan por temas. Cada tema es un grupo desplegable en la
lista de ejercicios; los temas y los ejercicios de cada tema aparecen **en el
orden en que se escriben** en el índice:

```json
{
  "grupos": [
    {
      "id": "trazados-fundamentales",
      "titulo": "Trazados fundamentales",
      "descripcion": "Mediatriz, bisectriz, perpendiculares y paralelas.",
      "ejercicios": ["mediatriz.json", "bisectriz.json"]
    },
    {
      "id": "perspectiva",
      "titulo": "Perspectiva",
      "abierto": false,
      "ejercicios": ["cubo-isometrico.json"]
    }
  ]
}
```

| Campo del tema | Obligatorio | Significado |
|---|---|---|
| `titulo` | sí | Nombre del tema. |
| `ejercicios` | sí | Archivos del tema, en orden. Un mismo archivo puede estar en varios temas. |
| `id` | no | Identificador fijo (letras, números y guiones). Sirve para recordar el orden y lo desplegado de cada persona aunque cambie el título; si falta, se saca del título. |
| `descripcion` | no | Texto corto bajo el título. |
| `abierto` | no | `false` para que el tema empiece plegado (por defecto, desplegado). |

Cada persona puede, además, **reordenar los temas** con el botón «Ordenar
temas» de la lista (flechas ↑ ↓) y plegarlos o desplegarlos. Su navegador lo
recuerda; «Orden original» vuelve al orden del índice. Los temas nuevos que se
añadan al índice aparecen al final de su orden.

El formato antiguo, `{ "ejercicios": [...] }` sin temas, sigue funcionando:
se muestra como un único tema «Ejercicios».

## Estructura

```json
{
  "formato": "dibutec-ejercicio",
  "version": 1,
  "id": "mediatriz",
  "titulo": "Mediatriz de un segmento",
  "nivel": "1.º ESO",
  "descripcion": "Texto corto para la lista de ejercicios.",
  "papel": { "papel": "blanco", "hoja": "A4-h" },
  "inicial": { "puntos": [], "rectas": [], "arcos": [] },
  "instrumentos": { "regla": { "x": 40, "y": 150, "giro": 0 } },
  "textos": { "AB": "el segmento AB" },
  "pasos": [ { "texto": "…", "objetivo": { "tipo": "…" } } ],
  "final": "Mensaje al terminar."
}
```

| Campo | Obligatorio | Significado |
|---|---|---|
| `formato` | sí | Siempre `"dibutec-ejercicio"`. |
| `titulo` | sí | Nombre del ejercicio. |
| `pasos` | sí | Lista de pasos (ver abajo). |
| `nivel`, `descripcion` | no | Se muestran en la lista de ejercicios. |
| `papel` | no | Papel del ejercicio: `papel` (`blanco`, `cuadriculado`, `milimetrado`, `isometrico`), `cuadro` (4, 5, 10), `triangulo` (5, 10), `colorLineas`, `colorPapel`, `hoja` (`A4-h`, `A4-v`, `A3-h`, `A3-v`), `margen`, `imanCuadricula`. Al salir del ejercicio se recupera el papel anterior. |
| `inicial` | no | El enunciado: puntos, rectas y arcos que ya están dibujados (en azul y sin poder borrarse). |
| `instrumentos` | no | Instrumentos que aparecen al empezar, con `x`, `y` (mm), `giro` (grados), para el compás `radio` y, para la escuadra y el cartabón, `"volteado": true` si deben empezar dados la vuelta. Los demás se guardan. |
| `textos` | no | Cómo llamar a cada nombre en los mensajes de ayuda («el primer arco» en vez de «arcoA»). |
| `final` | no | Mensaje de felicitación. |

### Coordenadas

Todo se mide en **milímetros** desde la esquina superior izquierda de la hoja
(x hacia la derecha, y hacia abajo). Un A4 horizontal mide 297 × 210 mm y el
margen está a 10 mm del borde. Los ángulos se miden en grados, en sentido
contrario a las agujas del reloj, como en el transportador.

### Enunciado (`inicial`)

```json
"inicial": {
  "puntos": [ { "nombre": "A", "x": 90, "y": 110 } ],
  "rectas": [
    { "nombre": "AB", "desde": "A", "hasta": "B" },
    { "nombre": "r", "x1": 40, "y1": 160, "x2": 250, "y2": 130 }
  ],
  "arcos": [ { "nombre": "c", "centro": "O", "radio": 40, "desde": 0, "hasta": 360 } ]
}
```

El `nombre` de un punto es también su etiqueta en la hoja.

### Referencias

En los objetivos, un punto se indica con su **nombre** (`"A"`, o un nombre
puesto por un paso anterior con `nombrar`) o con **coordenadas**
(`{ "x": 148.5, "y": 105 }`). Una línea (recta, arco o circunferencia) se
indica siempre con su nombre.

## Pasos

```json
{
  "texto": "Pincha el compás en A y traza un arco grande.",
  "pista": "Arrastra la mina para abrir el compás.",
  "herramientas": ["compas"],
  "objetivo": { "tipo": "arco", "centro": "A", "nombrar": "arcoA" }
}
```

- `texto`: la instrucción del paso.
- `pista` (opcional): se muestra al pulsar **Pista**.
- `herramientas` (opcional): botones de la barra que se resaltan: `lapiz`,
  `mover`, `goma`, `regla`, `escuadra`, `cartabon`, `compas`, `transportador`.
- `objetivo` u `objetivos` (lista): lo que hay que conseguir. El paso se
  completa solo cuando se cumplen todos.

DibuTec comprueba los objetivos cada vez que algo cambia. Si lo último que se
dibujó no cumple el objetivo, explica el motivo en la barra de estado. Si se
deshace o se borra algo que se consiguió en un paso anterior, el ejercicio
vuelve a ese paso.

### Opciones comunes de los objetivos

| Opción | Significado |
|---|---|
| `nombrar` | Pone nombre a lo que cumple el objetivo para usarlo en pasos siguientes. Una cadena o una lista (para varios puntos). |
| `rotular` | Solo para puntos: les pone una etiqueta en la hoja. `true` usa el nombre de `nombrar`; también vale una etiqueta (`"M"`) o una lista (`["1", "2"]`). Así el texto de los pasos puede decir «pincha en M». Si otro punto tenía esa etiqueta, recibe una letra libre. |
| `posteriorA` | Solo vale lo dibujado después de ese elemento (`"posteriorA": "M"`). Sirve para pedir un arco nuevo con centro en un punto que ya se usó antes. |
| `tolerancia` | Margen en mm (por defecto 1). |
| `toleranciaGrados` | Margen en grados (por defecto 1). |
| `permitirDados` | Si es `true`, también valen los elementos del enunciado. |

### `punto`

Un punto marcado con el portaminas.

| Condición | Ejemplo |
|---|---|
| `cerca` | `"cerca": { "x": 100, "y": 50 }` |
| `sobre` | `"sobre": "c"` (sobre una recta o arco) |
| `cruce` | `"cruce": ["arcoA", "arcoB"]` (donde se cortan dos líneas) |
| `angulo` | `"angulo": { "vertice": "V", "desde": "B", "grados": 60 }`; con `"sentido": "antihorario"` u `"horario"` solo vale un lado |
| `distancia` | `"distancia": { "de": "A", "mm": 35 }` |
| `cantidad` | Número de puntos distintos que hacen falta (en un `cruce`, cada uno en un corte distinto). |

### `recta`

Una recta trazada con el portaminas a lo largo de un instrumento.

| Condición | Ejemplo |
|---|---|
| `desde`, `hasta` | Extremos (en cualquier orden). |
| `pasaPor` | `"pasaPor": ["C", "D"]` |
| `paralelaA`, `perpendicularA` | `"paralelaA": "r"` |
| `angulo` | `"angulo": { "con": "r", "grados": 30 }` |
| `longitudMin` | Longitud mínima en mm. |

### `arco`

Un arco o circunferencia trazado con el compás.

| Condición | Ejemplo |
|---|---|
| `centro` | `"centro": "A"` |
| `radio` | `"radio": 50` o `"radio": { "min": 60, "max": 140 }` |
| `radioComo` | Mismo radio que otro arco (`"radioComo": "arcoA"`) o abertura igual a la distancia entre dos puntos (`"radioComo": ["A1", "A2"]`, para llevar una medida con el compás). |
| `completo` | `true` si tiene que ser una circunferencia entera. |
| `barridoMin` | Grados mínimos del arco. |
| `pasaPor` | Puntos por los que pasa. |
| `cortaA` | `["r"]` o `[{ "elemento": "arcoA", "cortes": 2 }]` |

### `rectas`

Varias rectas a la vez. Cada segmento se da por bueno si una recta trazada
pasa por sus dos extremos.

```json
{ "tipo": "rectas", "segmentos": [["A", "B"], ["B", { "x": 50, "y": 60 }]] }
{ "tipo": "rectas", "poligono": ["V1", "V2", "V3", "V4"], "cerrado": true }
```

### `vertices`

Los vértices de un polígono regular inscrito en una circunferencia, a partir
de uno de ellos.

```json
{ "tipo": "vertices", "circunferencia": "c", "desde": "P1", "lados": 6,
  "nombrar": ["V1", "V2", "V3", "V4", "V5", "V6"] }
```

### `instrumento`

La posición de un instrumento (`regla`, `escuadra`, `cartabon`, `compas`,
`transportador`). Solo con el `instrumento` exige que esté a la vista.

| Condición | Significado |
|---|---|
| `cantoSobre` | Un canto encima de una recta. |
| `cantoPasaPor` | Un canto pasa por un punto o por varios (`["A", "B"]`). Se puede combinar con `paraleloA` o `perpendicularA`. |
| `apoyadoEn` | Apoyado en el canto de otro instrumento. |
| `bloqueado` | Fijado (`true`) o suelto (`false`) con el candado. |
| `origenEn` | El centro del transportador o la punta seca del compás en un punto. |

### `continuar`

Paso de lectura: se completa al pulsar **Siguiente** en la tarjeta.

```json
{ "texto": "Fíjate: la mediatriz es perpendicular a AB.", "objetivo": { "tipo": "continuar" } }
```
