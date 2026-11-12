# Beyond Patterns — Plan de desarrollo

## 1. Pregunta e hipótesis

**Pregunta:** ¿puede un modelo producir una solución válida de una clase que nunca vio en su entrenamiento, cuando lo aprendido no puede resolver el problema?

**Tarea:** dado un conjunto de N puntos en el plano y un máximo de K trazos, dibujar una línea quebrada continua de como mucho K trazos rectos que pase por todos los puntos. Es la generalización del problema de los nueve puntos.

**Clases de solución:**

- **Clase 1:** todos los giros ocurren sobre puntos dados.
- **Clase 2:** al menos un giro ocurre en un lugar donde no hay punto (giro inventado).

**Hipótesis (H1):** un modelo entrenado solo con soluciones de clase 1 resuelve problemas que solo admiten soluciones de clase 2 con una frecuencia significativamente mayor que las referencias.

**Hipótesis nula (H0):** su tasa de acierto en esos problemas no supera a la de las referencias.

Una solución cuenta como nueva solo si cumple las tres condiciones:

| Condición | Comprobación |
|---|---|
| Válida | Verificador geométrico: como mucho K trazos y todos los puntos a distancia ≤ ε de la trayectoria. |
| Cualitativamente distinta | Para ese problema está demostrado por fuerza bruta que no existe solución de clase 1, y el entrenamiento contiene cero ejemplos de clase 2. |
| No atribuible al azar | Tasa de acierto superior a las tres referencias con significación estadística. |

## 2. Definiciones que se fijan antes de entrenar

Estas decisiones se escriben en `PREREGISTRO.md` y no se tocan después de ver resultados.

- **Espacio:** coordenadas en [0, 1]².
- **Rangos:** N entre 6 y 12, K entre 2 y 4. Son los mismos en entrenamiento y prueba.
- **Tolerancia de cobertura ε:** distancia máxima de un punto a la trayectoria para darlo por cubierto.
- **Umbral de giro inventado δ:** un giro es inventado si está a más de δ de todos los puntos. Se exige δ mucho mayor que ε.
- **Forma canónica:** los extremos de la trayectoria se recortan al primer y último punto cubierto, y se empieza por el extremo de menor x. Así cada problema tiene una única respuesta de referencia.
- **Umbral de competencia:** el modelo debe resolver al menos el 90 % de problemas nuevos de clase 1. Si no llega, el experimento no es interpretable.
- **Criterio de éxito:** tasa de acierto en la prueba de clase 2 superior a la mejor referencia, con p < 0,01 y en al menos 4 de 5 semillas.

## 3. Datos

### Generación

Todos los problemas se construyen a partir de una trayectoria oculta de K trazos.

| Conjunto | Dónde se colocan los puntos | Uso |
|---|---|---|
| Entrenamiento | En todos los giros y extremos, más puntos intermedios en los trazos | Imitación |
| Control (clase 1 nuevo) | Igual que el entrenamiento, problemas no vistos | Medir competencia |
| Prueba (solo clase 2) | Solo en el interior de los trazos, al menos 2 por trazo y a más de δ de cualquier giro | Experimento principal |
| Prueba graduada | Mezcla: algunos giros con punto y otros sin él | Medir dificultad según el número de giros inventados (1, 2, 3) |

### Garantías automáticas

1. **Auditoría del entrenamiento:** se comprueba que ninguna solución de entrenamiento tiene un giro inventado.
2. **Prueba de imposibilidad:** para cada problema de prueba se enumeran todas las trayectorias de clase 1 de K trazos (como mucho 12⁵ secuencias) con el mismo verificador y la misma ε. Se descarta el problema si alguna lo resuelve.
3. **Solubilidad:** la trayectoria oculta demuestra que cada problema de prueba tiene solución de clase 2.
4. **Control de distribución:** se entrena un clasificador para distinguir entradas de entrenamiento y de prueba. Su acierto se informa como medida de cuánto se parecen.

Caso de prueba fijo: la cuadrícula 3×3 del acertijo original, que necesita 5 trazos en clase 1 y 4 en clase 2 (comprobado por fuerza bruta).

## 4. Modelo

- **Entrada:** conjunto de puntos y valor de K.
- **Codificador:** Transformer sin codificación posicional, para que el orden de los puntos no importe.
- **Decodificador:** autorregresivo, genera los K+1 vértices como coordenadas discretizadas (256 niveles por eje) y un símbolo de fin.
- **Requisito:** la salida son coordenadas libres. El modelo nunca elige entre los puntos dados, porque eso haría imposible la clase 2 por construcción.
- **Tamaño:** pequeño (menos de 5 millones de parámetros), entrenable en una sola GPU.

## 5. Referencias de comparación

| Referencia | Qué descarta |
|---|---|
| Salida del modelo con ruido añadido | Que el acierto sea imprecisión afortunada |
| Copiar la solución del problema de entrenamiento más parecido | Que sea memorización |
| Búsqueda aleatoria de trayectorias con el mismo número de intentos | Que sea azar |
| Algoritmo exacto (agrupa puntos alineados y corta las rectas) | Nada: marca el techo alcanzable |

## 6. Niveles del experimento

| Nivel | Entrenamiento | Evaluación |
|---|---|---|
| 1 | Imitación de soluciones de clase 1 | Un solo intento por problema |
| 2 | El mismo modelo del nivel 1 | M intentos por muestreo; el verificador filtra. Se compara con búsqueda aleatoria con el mismo M |
| 3 | Aprendizaje por refuerzo con el verificador como recompensa, solo en problemas de tipo clase 1 | Un intento y M intentos |

En el nivel 2 el modelo no aprende de sus fallos: solo se mide si entre sus intentos aparece la solución nueva más a menudo que por azar.

## 7. Fases

| Fase | Contenido | Entregable | Estimación |
|---|---|---|---|
| 0 | Prerregistro de definiciones y umbrales | `PREREGISTRO.md` | 0,5 días |
| 1 | Geometría, verificador, clasificador de clase, solucionador de fuerza bruta, pruebas unitarias | `beyond/geometry.py`, `beyond/verify.py`, `tests/` | 2 días |
| 2 | Generadores, conjuntos de datos, auditorías y control de distribución | `beyond/generate.py`, `data/` | 2 días |
| 3 | Referencias y algoritmo exacto | `beyond/baselines.py` | 1–2 días |
| 4 | Modelo y entrenamiento por imitación; comprobación del umbral de competencia | `beyond/model.py`, `train.py` | 3–4 días |
| 5 | Evaluación de niveles 1 y 2 | `evaluate.py`, tablas de resultados | 2 días |
| 6 | Nivel 3 (refuerzo) | `train_rl.py` | 3–4 días |
| 7 | Variantes | Resultados por variante | 3 días |
| 8 | Análisis e informe | `INFORME.md`, figuras | 2 días |

Las estimaciones son orientativas.

### Variantes de la fase 7

- Añadir al entrenamiento problemas con puntos sin alinear, donde girar en los puntos es la única regla posible.
- Coordenadas continuas en lugar de discretizadas.
- Tamaño del modelo y cantidad de datos.
- Resultado en la prueba graduada según el número de giros inventados.

## 8. Cómo se interpretan los resultados

| Resultado | Lectura |
|---|---|
| Falla en los tres niveles | La imitación y el objetivo no bastan para salir de la clase aprendida. H0 se mantiene. |
| Falla en el nivel 1, acierta en el 2 | La solución nueva está en la distribución del modelo pero no es su respuesta preferida. |
| Acierta solo en el nivel 3 | La novedad viene del objetivo, no de los datos. |
| Acierta en el nivel 1 | El modelo no aprendió "gira en los puntos" sino una regla más profunda. Ver la limitación siguiente. |

## 9. Limitación principal

Los datos de entrenamiento son compatibles con dos reglas:

- **Regla superficial:** "gira sobre un punto".
- **Regla profunda:** "gira donde se cortan dos rectas de puntos alineados".

En el entrenamiento ambas dan la misma respuesta. Si el modelo acierta en la prueba, un crítico puede decir que aprendió la regla profunda y que eso es generalización de una regla, no una solución nueva.

El experimento no elimina esa objeción; la acota:

- La primera variante de la fase 7 refuerza la regla superficial y permite ver si el resultado cambia.
- La prueba graduada muestra si el modelo coloca giros inventados solo cuando hacen falta.
- El análisis de dónde coloca los giros en los fallos indica qué regla sigue.

Lo que el experimento sí demuestra sin ambigüedad es que la salida es válida, pertenece a una clase con cero ejemplos de entrenamiento y no es obtenible con la estrategia entrenada.

## 10. Estructura del repositorio

```
Beyond-Patterns/
├── PLAN.md
├── PREREGISTRO.md
├── beyond/
│   ├── geometry.py
│   ├── verify.py
│   ├── generate.py
│   ├── baselines.py
│   └── model.py
├── train.py
├── train_rl.py
├── evaluate.py
├── configs/
├── tests/
├── data/
└── results/
```

**Herramientas:** Python, PyTorch, NumPy, Matplotlib, pytest.
