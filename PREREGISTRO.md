# Prerregistro (fase 0)

Valores fijados **antes** de generar datos o entrenar. Cualquier cambio posterior debe registrarse aquí con fecha y motivo, y los resultados anteriores al cambio se descartan.

## Geometría
- Espacio: [0, 1]².
- N (puntos): 6 a 12. K (trazos máximos): 2 a 4. Mismos rangos en entrenamiento y prueba.
- ε (tolerancia de cobertura): 0,01. Un punto está cubierto si dista ≤ ε de algún trazo.
- δ (giro inventado): 0,05. Un giro es inventado si dista > δ de todos los puntos dados.
- Un vértice interior solo cuenta como giro si el ángulo entre trazos consecutivos supera 5°.
- Distancia mínima entre puntos de un problema: 0,03.

## Clases
- Clase 1: todos los giros están a ≤ δ de un punto dado.
- Clase 2: al menos un giro inventado.
- Un problema es de "solo clase 2" si la fuerza bruta no encuentra ninguna trayectoria de clase 1 con ≤ K trazos y tolerancia ε.

## Criterios
- Competencia: el modelo resuelve ≥ 90 % de problemas de control de clase 1 con un intento. Si no, el experimento no se interpreta.
- Éxito: tasa de acierto en solo-clase-2 superior a la mejor referencia, p < 0,01, en ≥ 4 de 5 semillas.
- Estadística: test binomial exacto unilateral por semilla.

## Generación (fase 2)
- N mínimo por K: max(6, 2K), igual en entrenamiento y prueba (evita que (N, K) delate el conjunto).
- Vértices de la trayectoria oculta: trazos ≥ 0,25; giros entre 30° y 165°; puntos interiores a ≥ 0,07 de los vértices de su trazo.
- Los extremos son siempre puntos dados. Cada trazo contiene ≥ 2 puntos.
- Prueba pura: todos los giros interiores son inventados (K−1). Prueba graduada: 1 a K−1.
- Todo problema pasa `audit()` (entrenamiento: clase 1 con k₁ = K; prueba: sin solución de clase 1 con ≤ K trazos).
- Control de distribución: clasificador (gradient boosting) entre entradas de train y test sobre rasgos invariantes a la permutación. Se informa el acierto; la diferencia en ternas alineadas es inherente a la manipulación (las esquinas dadas son puntos de dos rectas a la vez).
- Resultado del control (3000 train, 500 por conjunto de prueba): train vs control 0,48 (indistinguibles); train vs test_pure 0,89; train vs test_graded 0,83. Sin la característica de ternas alineadas: 0,62; solo con ella: 0,72. Conclusión: la entrada de prueba difiere en estructura de alineación, que es consecuencia directa de quitar las esquinas. Hay un residuo pequeño (~0,62) sin explicar. El análisis final debe tenerlo en cuenta como posible explicación alternativa.

## Revisión de la fase 2 (antes de entrenar)
- **Criterio de acierto precisado:** un intento cuenta como solución nueva solo si es válido **y** el verificador lo clasifica como clase 2. Los intentos válidos clasificados como clase 1 en problemas de prueba se informan aparte (la fuerza bruta solo descarta giros exactamente sobre puntos; un giro a menos de δ de un punto sin estar sobre él queda fuera de esa demostración).
- **Corrección del verificador:** los vértices repetidos ocultaban giros (una solución de clase 2 se clasificaba como clase 1). Corregido y cubierto con una prueba.
- **Reinterpretación del control de distribución:** entrenamiento y prueba son distinguibles al 100 % por definición (el solucionador de clase 1 los separa: 100 % frente a 0 % resolubles). Lo que el control debe medir es si coinciden las variables accesorias: solo con N y K el clasificador acierta 0,53; con N, K, centro y dispersión 0,58; solo con distancias 0,58. La diferencia restante es estructural (alineaciones sin esquina), es decir, la propia manipulación.
- k₁ medido en la prueba pura: K=2 → 3; K=3 → 4,7 de media; K=4 → 6,0 de media. La clase 1 necesita entre 1 y 2 trazos más de los permitidos.

## Fase 3: referencias (100 problemas por conjunto, datos regenerados con la auditoría casi-clase-1)
Corrección previa: el 4 % de los problemas de prueba (6/150) admitía una solución clasificada como clase 1 (giro a < δ de un punto, sin estar sobre él). Ahora `audit()` rechaza todo problema de prueba cuya enumeración completa de soluciones por rectas de ≥ 2 puntos contenga alguna de clase 1. Reescaneo: 0/80 en test_pure y 0/80 en test_graded.

| Referencia | control | test_pure | test_graded |
|---|---|---|---|
| Solucionador clase 1 (exacto) | 100 % | 0 % | 0 % |
| Solucionador exacto clase 2 (techo) | – | 100 % | 100 % |
| Copia del vecino de train | 0 % | 0 % | 0 % |
| Azar uniforme, M=100 / 1000 | 0 % / 0 % | 0 % / 0 % | 0 % / 0 % |
| Azar sobre rectas de puntos, M=100 | 61 % válidas | 45 % | 49 % |
| Azar sobre rectas de puntos, M=10000 | 99 % válidas | 89 % | 90 % |

Todos los aciertos de las referencias en los conjuntos de prueba son de clase 2 (0 % de clase 1).

Consecuencias, fijadas antes de ver ningún resultado de modelo:
- El techo (100 %) demuestra que todos los problemas de prueba son resolubles sin entrenar.
- "Azar sobre rectas de puntos" no es azar ciego: conoce la estructura de la solución (rectas por pares de puntos). Es una referencia informada y muy exigente.
- **Criterio de éxito, en dos niveles:** (a) *débil*: el modelo supera al azar uniforme y a la copia del vecino con p < 0,01; (b) *fuerte*: además supera al azar sobre rectas con el mismo número de intentos M. Se informa cada nivel por separado. Solo el fuerte permite afirmar que el modelo aporta algo más que explorar rectas por pares de puntos.
- Con M=100 la barra fuerte es ≈ 45 % en test_pure.
- Si el modelo no usa muestreo (un solo intento), la comparación justa es con azar sobre rectas con M=1.

## Fase 4: entrenamiento por imitación (registro de intentos)
Todas las decisiones de modelo se toman sobre `val` (mismo generador que el entrenamiento, semilla distinta). `control` solo se evalúa una vez al final, cuando `val` ≥ 90 %. Los conjuntos de prueba no se tocan.

Decisiones de diseño: salida de coordenadas libres discretizadas en 256 niveles por eje; sin símbolo de fin (K da el número de vértices); aumento con las 8 simetrías del cuadrado (conservan clase, validez y alineaciones); pérdida con objetivo gaussiano de 1 bin.

| Intento | Datos | Modelo | Épocas | Mejor val (un intento voraz) |
|---|---|---|---|---|
| 1 | 20.000 | d=128, 3+3 capas, 1,5 M parám. | 40 | **19,2 %** (K=2: 50 %, K=3: 9 %, K=4: 2 %) |

Diagnóstico del intento 1 (300 problemas de val): el 81 % de los vértices generados está a < 0,01 de un punto dado, y ajustarlos al punto más cercano solo sube la validez de 10 % a 13 %. El fallo no es de precisión de coordenadas sino de elegir los vértices correctos (razonamiento combinatorio sobre alineaciones). No se introduce ninguna característica de alineación hecha a mano: daría al modelo la estructura de la solución y debilitaría la hipótesis.
| 2 | 100.000 | d=192, 4+4 capas, 4,3 M parám. | 20 | **40,0 %** (K=2: 89 %, K=3: 33 %, K=4: 7 %) |

Lectura: 5× datos, 3× parámetros y 3× cómputo duplican la validez (19 % → 40 %) pero no se acerca al umbral de competencia (90 %). K=4 es el cuello de botella. **El umbral de competencia no se cumple; según este prerregistro, el experimento principal no es interpretable todavía.** El control no se ha evaluado (solo se mira cuando val ≥ 90 %). Los conjuntos de prueba no se han usado con ningún modelo.
