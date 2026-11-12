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
