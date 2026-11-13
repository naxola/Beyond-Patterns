# Prerregistro — Experimento 2 (polígonos)

Valores fijados antes de entrenar. Cualquier cambio posterior se anota aquí con su motivo.

## Tarea
- Entrada: N puntos en [0, 1]², barajados. Salida: orden de recorrido, cerrando al primero.
- Polígono válido: cada punto exactamente una vez y ningún par de lados no adyacentes se cruza.
- Coincidencia exacta: mismo ciclo que la referencia, sin importar inicio ni sentido.
- Forma canónica de la referencia: empieza en el punto de menor x (desempate por y) y gira en sentido antihorario.

## Generación
Vértices de un polígono regular de N lados, con rotación aleatoria, radio entre 0,20 y 0,40 y centro tal que todo cabe en [0,05, 0,95]². Distancia mínima entre puntos: 0,04.

| Nivel | Ángulo | Radio | Forma |
|---|---|---|---|
| `regular` | ±5 % de la separación angular | ±3 % | Casi regular, convexo |
| `irregular` | ±35 % de la separación | constante, con estiramiento de un eje a 0,6–1,0 | Convexo garantizado (puntos sobre una elipse) |
| `noconvexo` | ±35 % de la separación | factor entre 0,55 y 1,0 por punto | Estrellado respecto al centro: el orden angular es un polígono válido |

## Conjuntos
- Dataset 1: N=4. Dataset 2: N=7. 20.000 problemas cada uno, mitad `regular` y mitad `irregular`.
- Control: N=4 y N=7, problemas nuevos. Umbral de competencia: ≥ 95 % de polígonos válidos.
- Interpolación: N=5, 6. Extrapolación: N=8, 9, 10, 12, 16. 1.000 problemas por N y nivel.
- `noconvexo` solo se usa en prueba (y en la variante de la fase 6).
- N=3 se excluye: solo existe un recorrido posible.

## Criterio de éxito
- Éxito: ≥ 90 % de polígonos válidos con N=10 y con N=12 en los niveles convexos, en ≥ 4 de 5 semillas.
- Éxito parcial: por encima del vecino más cercano y del azar con p < 0,01, sin llegar al 90 %.
- Fracaso informativo: cumple el control y cae fuera de él.

## Alcance de la afirmación
Un éxito demuestra generalización al número de puntos (la misma regla aplicada a más puntos). No demuestra una clase de solución nueva.

## Enmienda 1 (antes de entrenar ningún modelo)
Al ejecutar las referencias, el vecino más cercano acertaba el 97–98 % con N=10 y 12 en los tres niveles iniciales (orden angular 100 %, azar 0 %). Con esos datos, un modelo que solo hubiera aprendido "ir al punto más cercano" habría superado el criterio de éxito. Se añade el nivel **`estrecho`**: elipse convexa con eje menor entre 0,12 y 0,30 del mayor, donde vecinos de lados opuestos están más cerca que los siguientes en el contorno.

| Vecino más cercano, válidos | N=4 | N=7 | N=10 | N=12 | N=16 |
|---|---|---|---|---|---|
| `regular` | 100 % | 100 % | 100 % | 100 % | 100 % |
| `irregular` | 92 % | 96 % | 97 % | 96 % | 99 % |
| `estrecho` | 24 % | 0 % | 3 % | 12 % | 35 % |

- `estrecho` entra en el entrenamiento (con `regular` e `irregular`) y en todas las pruebas. `noconvexo` sigue solo en prueba.
- **Criterio de éxito corregido:** ≥ 90 % de válidos con N=10 y N=12 en **cada** nivel convexo, `estrecho` incluido, en ≥ 4 de 5 semillas. Pasar solo `regular`/`irregular` no cuenta, porque lo logra el vecino más cercano.
- El control (≥ 95 %) se evalúa también por nivel.

## Resultados (fase 3-4)
Ver `INFORME.md`. Criterio de éxito cumplido en 5/5 semillas (mínimo 98,1 % con N=10 y 12 en niveles convexos). El criterio y los datos no se modificaron tras ver resultados de modelo; la única enmienda (nivel `estrecho`) se hizo antes de entrenar y se registró arriba.

## Modelo B: coordenadas libres (fijado antes de entrenarlo)
**Pregunta:** si el modelo puede escribir cualquier coordenada y decidir cuándo parar, ¿qué hace con N=10 o 12 puntos? ¿Para en 7, cierra antes, omite puntos, repite, inventa vértices?

- **Salida:** vértices como pares (x, y) discretizados en 256 niveles por eje, más un símbolo FIN. Sin máscara de puntos ya visitados ni número de vértices dado. Es el mismo problema, mismos datos y mismo entrenamiento (N=4 y N=7) que el modelo de puntero.
- **Posición de salida:** codificación sinusoidal del índice de vértice (definida para cualquier índice, también los no entrenados) más un embedding de "x o y". Se elige así para no fijar de antemano un máximo de 7 vértices por tener parámetros sin entrenar.
- **Decodificación:** voraz, hasta FIN o 24 vértices.
- **Emparejado de vértices:** un vértice de salida corresponde a un punto de entrada si dista ≤ 0,012 (≈ 3 niveles de cuantización; los puntos distan ≥ 0,04, así que no hay ambigüedad).

**Categorías de resultado (excluyentes, en este orden de prioridad):**
1. *Vértice inventado:* algún vértice no corresponde a ningún punto.
2. *No termina:* llega a 24 vértices sin emitir FIN.
3. *Para antes:* emite FIN con menos vértices que N, sin repetir puntos (omite puntos).
4. *Repite o se pasa:* repite algún punto o emite más de N vértices.
5. *Cruces:* visita cada punto una vez pero el polígono se cruza.
6. *Correcto:* polígono válido que pasa por todos los puntos una vez.

Se informa además cuántos vértices emite según N, y en particular si emite exactamente 4 o 7 cuando N no lo es.

**Hipótesis previa (no un criterio de éxito):** con N=10 y 12 es probable que pare en 7 o que repita puntos, porque 4 y 7 son las únicas longitudes que vio. Si en cambio acierta ≥ 90 % en ambos N, el modelo habrá aprendido "para cuando has visitado todos". Cualquiera de los dos resultados se publica.
Criterio comparable al del modelo de puntero: ≥ 90 % de *Correcto* con N=10 y 12 en niveles convexos, en ≥ 2 de 3 semillas.

### Modelo B: condición de control de variedad (fijada tras ver la semilla 0 del modelo B y antes de entrenarla)
Semilla 0 del modelo B (4 y 7 puntos): correcto 99,9 % con N=4 y 99,6 % con N=7; con N≥8 emite siempre 7 vértices y para (93–99 % "Para antes"); con N=5 emite 4 (79 %) y con N=6 emite 7 (88 %). Solo emite longitudes 4 o 7.

Esto admite dos lecturas: (a) con solo dos tamaños el modelo no tiene datos para distinguir "para tras 4 o 7" de "para cuando has visitado todos"; (b) aunque haya variedad, el modelo de coordenadas libres no extrapola la longitud de la salida. Para separarlas se entrena **una variante con N ∈ {4, 5, 6, 7}** (20.000 problemas por tamaño, mismos niveles) y se prueba en N = 8, 9, 10, 12, 16, que siguen sin verse.
- Si emite N vértices con N ≥ 8 y acierta ≥ 90 %: el fallo anterior era falta de variedad.
- Si sigue emitiendo 7: el fallo no se explica por falta de variedad dentro de 4–7.
Se evalúa con los problemas ya generados de `test_n5` y `test_n6` (semillas distintas de las de entrenamiento).
