# Experimento 2 — Polígonos: generalización al número de puntos

Experimento independiente del de los nueve puntos (raíz del repositorio). Comparten repositorio y utilidades de geometría, nada más.

## 1. Pregunta

Un modelo entrenado solo con **4 puntos → cuadrilátero** (Dataset 1) y **7 puntos → heptágono** (Dataset 2), ¿dibuja un polígono válido cuando recibe **10 o 12 puntos**, cantidades con las que nunca se entrenó?

**Qué demostraría un resultado positivo:** que el modelo aprendió la regla "une todos los puntos en un contorno cerrado" y no "dibuja 4 o 7 lados". La salida (un decágono) no existe en el entrenamiento. Es generalización al tamaño; no es una clase de solución nueva en el sentido del experimento 1, y el informe lo dirá así.

## 2. Definiciones

- **Entrada:** N puntos en [0, 1]², en orden aleatorio.
- **Salida:** el orden en que se recorren, cerrando al primero.
- **Polígono válido:** visita cada punto exactamente una vez y ningún lado cruza a otro.
- **Coincidencia exacta:** el orden coincide con el de referencia, sin importar el punto de inicio ni el sentido de giro.

Azar: con N puntos hay (N−1)!/2 recorridos distintos. Con N=10 son 181.440 y con N=12 casi 20 millones, así que acertar por casualidad es descartable. Con N=3 solo hay uno: ese caso no informa y se excluye.

## 3. Datos

Los puntos son los vértices de un polígono regular deformado: ruido en el radio y en el ángulo, más rotación, escala y posición aleatorias. Después se barajan.

| Conjunto | N | Uso |
|---|---|---|
| Dataset 1 | 4 | Entrenamiento |
| Dataset 2 | 7 | Entrenamiento |
| Control | 4 y 7 (problemas nuevos) | Comprobar que aprendió la tarea (≥ 95 %) |
| Interpolación | 5 y 6 | Tamaños entre los entrenados |
| **Extrapolación** | 8, 9, **10, 12**, 16 | Pregunta principal |

- Tres niveles de irregularidad: casi regular, irregular convexo, no convexo. Se entrena con los dos primeros.
- En los convexos la respuesta es única. En los no convexos hay varias válidas, y ahí se mide validez, no coincidencia.
- Mismo rango de coordenadas y de tamaño de figura para todos los N. Lo que cambia inevitablemente es la separación angular entre vecinos (90° con 4, 51° con 7, 36° con 10); se informa como factor de dificultad.

## 4. Modelos

El número de vértices de salida crece con N, y eso condiciona la arquitectura: un modelo con posiciones de salida fijas no puede emitir un décimo vértice si solo entrenó hasta siete.

| Modelo | Salida | Para qué |
|---|---|---|
| **A. Puntero** (principal) | Elige el siguiente punto entre los dados; termina cuando no quedan | Responde a la pregunta: ¿aprendió la regla? No usa el número de paso, así que el tamaño no le afecta por construcción |
| **B. Coordenadas libres** (secundario) | Genera vértices libremente y un símbolo de fin | Ver qué hace sin restricciones: ¿se detiene en 7?, ¿cierra antes?, ¿omite puntos? |

Lección del experimento 1: el modelo de coordenadas libres ya tuvo dificultades dentro de su distribución. Por eso A es el principal y B se aborda solo después.

## 5. Referencias

| Referencia | Papel |
|---|---|
| Orden angular alrededor del centroide | Techo (≈ 100 % en convexos) |
| Vecino más cercano | Atajo que el modelo podría haber aprendido |
| Orden aleatorio | Suelo |

Comparar los fallos del modelo con los del vecino más cercano indica qué regla aprendió.

## 6. Visualizaciones (entregable central)

1. **Galería de Dataset 1 y Dataset 2:** puntos de entrada y trayectoria objetivo, una rejilla por dataset y nivel de irregularidad.
2. **Galería de predicciones con N=10 y N=12:** puntos y polígono dibujado por el modelo, verde si es válido y rojo si no.
3. **Curva de acierto frente a N:** de 4 a 16, con los tamaños entrenados marcados y las referencias superpuestas.
4. **Galería de fallos:** cruces, cierres prematuros, puntos omitidos.

Se guardan como PNG en `polygons/results/` y se reúnen en una página para verlas juntas.

## 7. Fases

| Fase | Contenido | Entregable |
|---|---|---|
| 0 | Fijar definiciones, niveles de ruido y umbrales | `polygons/PREREGISTRO.md` |
| 1 | Generador y galería de los datasets | `generate.py`, visualización 1 |
| 2 | Métricas (validez, cruces, coincidencia) y referencias | `metrics.py`, `baselines.py`, pruebas |
| 3 | Modelo A y entrenamiento; control ≥ 95 % | `model_pointer.py`, `train.py` |
| 4 | Evaluación en todos los N y visualizaciones 2–4 | `evaluate.py`, figuras |
| 5 | Modelo B (opcional) y su catálogo de comportamientos | `model_free.py` |
| 6 | Variantes e informe | `INFORME.md` |

Variantes de la fase 6: entrenar solo con N=4, solo con N=7 o con ambos; con y sin el nivel no convexo.

Las fases 0 a 4 son pequeñas: la tarea es mucho más fácil que la del experimento 1 y cabe en esta CPU.

## 8. Criterio de éxito (se fija en la fase 0)

- **Éxito:** ≥ 90 % de polígonos válidos con N=10 y N=12 en datos convexos, en al menos 4 de 5 semillas.
- **Éxito parcial:** muy por encima del vecino más cercano y del azar, sin llegar al 90 %.
- **Fracaso informativo:** acierta en 4 y 7 y cae fuera; se documenta cómo falla.

## 9. Estructura

```
Beyond-Patterns/
├── beyond/ …            # experimento 1 (nueve puntos), sin cambios
└── polygons/            # experimento 2
    ├── PLAN.md
    ├── PREREGISTRO.md
    ├── generate.py  metrics.py  baselines.py
    ├── model_pointer.py  model_free.py
    ├── train.py  evaluate.py  visualize.py
    ├── tests/
    └── results/
```
