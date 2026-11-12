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
