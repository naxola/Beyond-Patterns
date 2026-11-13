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
