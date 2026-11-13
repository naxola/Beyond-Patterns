# Experimento 2 — Informe: ¿generaliza el modelo a más puntos de los entrenados?

## Resultado en una frase
Entrenado solo con 4 y 7 puntos, el modelo de puntero dibuja polígonos válidos (todos los puntos, sin cruces) con 8, 9, **10, 12** y 16 puntos con una tasa de acierto del 98–100 % en las 5 semillas, incluso en los casos donde el atajo "ir al punto más cercano" falla.

## Qué se midió
- **Tarea:** N puntos barajados → orden de recorrido que forma un polígono cerrado sin cruces. Datos y criterios fijados en `PREREGISTRO.md` antes de entrenar.
- **Modelo:** Transformer con salida de tipo puntero (elige el siguiente punto entre los dados). Ninguna parte usa el número de paso ni N. 763.000 parámetros, 30 épocas, unos 6 minutos por semilla en CPU.
- **Entrenamiento:** 20.000 problemas con 4 puntos + 20.000 con 7 puntos (niveles casi regular, irregular y estrecho, todos convexos).
- **Prueba:** N = 5, 6, 8, 9, 10, 12, 16, con un nivel más (no convexo) que no se vio nunca. Se usaron los primeros 1.500 problemas de cada conjunto.

## Resultados
Control (competencia, umbral 95 %): 100 % con N=4 y con N=7 en todas las semillas.

Criterio de éxito (≥ 90 % de válidos con N=10 y N=12 en cada nivel convexo, en ≥ 4 de 5 semillas): **se cumple en las 5 semillas**. El mínimo observado fue 98,1 %.

| N | regular | irregular | estrecho | no convexo | Vecino más cercano en `estrecho` |
|---|---|---|---|---|---|
| 10 | 100 % | 100 % | 99,5–100 % | 99,7–100 % | 2 % |
| 12 | 99,2–100 % | 99,7–100 % | 98,1–100 % | 99,7–100 % | 10 % |

(Rangos entre las 5 semillas. Orden angular: 100 %; azar: 0 %.) Figuras: `results/acierto_vs_n.png`, `results/predicciones_10_12.png`.

### Los fallos
Aparecen sobre todo con N=16. De 269 fallos entre las 5 semillas (N = 10, 12, 16), el 80 % se corrige intercambiando dos puntos vecinos del recorrido. Con N=10 y N=12 son 34 de 34. No hay recorridos caóticos. Figura: `results/fallos.png`.

### ¿Hacen falta dos tamaños de entrenamiento? (una semilla por variante)
| Entrenado con | N=8 | N=10 | N=12 | N=16 |
|---|---|---|---|---|
| Solo 4 puntos (irregular) | 83 % | 42 % | 12 % | 0 % |
| Solo 7 puntos (irregular) | 100 % | 100 % | 100 % | 99 % |
| 4 y 7 puntos (irregular) | 100 % | 100 % | 100 % | 100 % |

Con solo 4 puntos el modelo no llega a aprender la regla: con 4 puntos solo hay 3 recorridos posibles y casi cualquier atajo sirve. Con 7 puntos sí. Figura: `results/variantes.png`.

## Lo que se puede y no se puede afirmar
**Se puede afirmar:**
- Con estos datos, el modelo aplica correctamente la regla "une todos los puntos en un contorno sin cruces" a cantidades de puntos que nunca vio (hasta 16), y no lo hace con un atajo local: supera ampliamente al vecino más cercano donde este falla.
- Basta un tamaño de entrenamiento si tiene estructura suficiente (7 sí, 4 no).

**No se puede afirmar:**
- *Que sea una solución nueva en el sentido fuerte.* El decágono sale de aplicar la misma regla a más puntos. Es generalización al tamaño, no una clase de solución distinta como la que busca el experimento de los nueve puntos.
- *Que valga para cualquier arquitectura.* El modelo de puntero obliga a visitar cada punto una vez y no depende de N por construcción; eso hace posible la generalización. No se probó el modelo de coordenadas libres (fase 5 del plan), que es el que podría "inventar" vértices o parar en 7.
- *Que valga para formas arbitrarias.* Los datos son convexos o estrellados respecto al centro; hay recorridos válidos para los que el orden angular no sirve y no se probaron.
- Las variantes tienen una sola semilla.

## Siguientes pasos posibles
1. Modelo de coordenadas libres: ¿se detiene en 7 lados con 10 puntos?
2. Formas donde el orden angular no es válido (espirales, formas en U).
3. Generalizar a más puntos aún (32, 64) y a otras densidades.
