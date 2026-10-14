
# Índice aleatorio para la razón de consistencia (n = 1..10)
RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12,
      6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def completar_reciprocos(triangulo_superior):
    """
    Recibe solo lo que está ARRIBA de la diagonal y arma la matriz completa.
    Solo se leen los valores sobre la diagonal; el resto se calcula (1/x).
    """
    n = len(triangulo_superior)
    m = [[1.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            valor = float(triangulo_superior[i][j])
            m[i][j] = valor
            m[j][i] = 1 / valor
    return m


def prioridades(matriz):
    """
    Dada una matriz de comparación por pares, calcula:
    - suma de cada columna
    - matriz normalizada
    - vector de prioridades (promedio de cada fila)
    - razón de consistencia (CR)
    """
    n = len(matriz)
    sumas = [sum(matriz[i][j] for i in range(n)) for j in range(n)]
    normalizada = [[matriz[i][j] / sumas[j] for j in range(n)] for i in range(n)]
    vector = [sum(fila) / n for fila in normalizada]

    # Consistencia
    cr = None
    lambda_max = None
    ci = None
    if n > 2:
        producto = [sum(matriz[i][j] * vector[j] for j in range(n)) for i in range(n)]
        lambda_max = sum(producto[i] / vector[i] for i in range(n)) / n
        ci = (lambda_max - n) / (n - 1)
        cr = ci / RI[n] if n in RI and RI[n] > 0 else 0.0

    return {
        "matriz": matriz,
        "sumas_columna": sumas,
        "normalizada": normalizada,
        "vector": vector,
        "lambda_max": lambda_max,
        "ci": ci,
        "cr": cr,                      # aceptable si es <= 0.10
        "consistente": (cr is None) or (cr <= 0.10),
    }


def decision_certeza(criterios, alternativas,
                     matriz_criterios, matrices_por_criterio):
    """
    criterios: lista de nombres
    alternativas: lista de nombres, ej. Proveedor A, Proveedor B]
    matriz_criterios: matriz n x n comparando criterios entre sí
    matrices_por_criterio: dict {criterio: matriz m x m comparando alternativas}
    """
    #  tabla general (pesos de los criterios)
    general = prioridades(matriz_criterios)
    pesos = general["vector"]

    # una tabla por criterio
    por_criterio = {}
    for c in criterios:
        por_criterio[c] = prioridades(matrices_por_criterio[c])

    #  tabla de decisión (prioridad x peso)
    tabla = []
    for i, alt in enumerate(alternativas):
        fila = {}
        total = 0.0
        for k, c in enumerate(criterios):
            p = por_criterio[c]["vector"][i]
            aporte = p * pesos[k]
            fila[c] = {"prioridad": p, "peso": pesos[k], "aporte": aporte}
            total += aporte
        tabla.append({"alternativa": alt, "detalle": fila, "total": total})

    ranking = sorted(tabla, key=lambda x: x["total"], reverse=True)

    return {
        "paso1_general": general,
        "paso2_por_criterio": por_criterio,
        "paso3_decision": tabla,
        "ranking": [(r["alternativa"], r["total"]) for r in ranking],
        "ganadora": ranking[0]["alternativa"],
    }