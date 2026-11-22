# Compás en 3D (prueba)

`compas.glb` es el modelo 3D del compás que usa `compas3d.html`, la prueba del
compás tridimensional con funcionamiento mecánico. Se ha construido a partir
de las piezas SVG del alzado (`../tumbado/`), dándoles el grosor de la planta,
y se puede retocar en **Blender** (o cualquier programa que abra glTF).

## Abrirlo en Blender

1. *Archivo › Importar › glTF 2.0 (.glb/.gltf)* y elige `compas.glb`.
2. **Unidades:** en el modelo, 1 unidad = 1 mm (las patas miden 75). Para ver
   las medidas en milímetros: *Propiedades de la escena › Unidades*, con
   *Escala de unidad* 0,001 y *Longitud* en milímetros. No escales el modelo.

## Lo que la mecánica necesita

La prueba mueve las piezas por su **nombre** y su **origen** (el punto de
pivote del objeto), así que se pueden cambiar sus formas, materiales y
detalles libremente, pero hay que conservar:

| Objeto | Qué es | Origen |
|---|---|---|
| `compas` | Todo el compás (padre de lo demás). | La aguja, en (0, 0, 0). |
| `cabeza` | Cabeza. Hijo: `mango`. | La bisagra (entre los dos tornillos). |
| `mango` | Mango. Hijo: `asa` (vacío). | El borde de arriba de la cabeza. |
| `pata-aguja`, `pata-mina` | Patas. Hijos: `punta-…` y `ajuste-…` (vacíos). | El **tornillo** en el que gira la pata. |
| `mina` | La mina (dentro de `pata-mina`): toma el color del portaminas. | — |
| `pinza-aguja`, `pinza-mina` | Pinzas del tornillo de ajuste. | Donde se enganchan a su pata (el vacío `ajuste-…`). |
| `varilla` | Varilla roscada, a lo largo de X. | Su centro. |
| `rueda` | Rueda del tornillo de ajuste: gira alrededor de X. | Su centro. |

Dentro de cada pata está su **ruedecita** de apriete (`ruedecita-aguja`,
`ruedecita-mina`): un cilindro estriado con el eje hacia fuera de la pata y su
tornillo (`tornillo-ruedecita-…`), otro cilindro en el mismo eje. Son solo
decorativas: se pueden retocar o cambiar sin que la mecánica se entere.

Vacíos (*empties*): `punta-aguja` y `punta-mina` marcan las puntas;
`ajuste-aguja` y `ajuste-mina`, dónde se enganchan las pinzas; `asa`, dónde
está el asa para girar.

**Postura:** el modelo está en reposo, abierto como en el dibujo (51,1 mm). En
el sistema del glTF, X va de la aguja a la mina, Y hacia la cabeza y Z hacia
delante (en Blender, al importar, Y pasa a ser Z). Las patas tienen que seguir
en el mismo plano.

**Topes:** la prueba calcula la abertura mínima y máxima con las piezas: se
cierra hasta que las pinzas tocan la rueda y se abre hasta que la varilla se
acaba. Alargar la varilla deja abrir más; adelgazar las pinzas o la rueda deja
cerrar más.

**Materiales:** las piezas del mismo color comparten material, con nombres
como `metal-gris-claro-bebebe` o `plastico-negro-111111` (tipo, tono y color).
Cambiar uno cambia todas las piezas que lo usan; para cambiar solo una, dale
un material propio. La mina tiene el suyo (`mina`): la prueba le pone el
color del portaminas y la aclara cuando está levantada. La aguja de la punta
seca (objeto `aguja`) tiene `aguja-metal-azul`, metálico y azul oscuro.

## Guardarlo

*Archivo › Exportar › glTF 2.0*, formato **glTF Binary (.glb)**, con *+Y Up*
marcado, y guárdalo encima de `instrumentos/compas/3d/compas.glb`.
`compas3d.html` lo carga al abrirla desde un servidor web. Con doble clic
(`file://`) el navegador no deja leerlo y la prueba construye el modelo desde
las piezas SVG.

Si se pierde el modelo, `compas3d.html` lo vuelve a generar desde los SVG con
el botón **Descargar modelo (.glb)** (abriendo `compas3d.html?svg`).
