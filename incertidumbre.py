
def laplace(matriz, maximizar=True):
    promedios = [sum(f) / len(f) for f in matriz]
    mejor = max(promedios) if maximizar else min(promedios)
    return promedios, promedios.index(mejor)

def wald(matriz, maximizar=True):
    # Maximizar: maximin | Minimizar costos: minimax
    if maximizar:
        valores = [min(f) for f in matriz]
        mejor = max(valores)
    else:
        valores = [max(f) for f in matriz]
        mejor = min(valores)
    return valores, valores.index(mejor)

def hurwicz(matriz, alfa, maximizar=True):
    if maximizar:
        valores = [alfa * max(f) + (1 - alfa) * min(f) for f in matriz]
        mejor = max(valores)
    else:
        valores = [alfa * min(f) + (1 - alfa) * max(f) for f in matriz]
        mejor = min(valores)
    return valores, valores.index(mejor)

def savage(matriz, maximizar=True):
    cols = list(zip(*matriz))
    if maximizar:
        ref = [max(c) for c in cols]
        regret = [[ref[j] - f[j] for j in range(len(f))] for f in matriz]
    else:
        ref = [min(c) for c in cols]
        regret = [[f[j] - ref[j] for j in range(len(f))] for f in matriz]
    max_regret = [max(f) for f in regret]
    mejor = min(max_regret)
    return regret, max_regret, max_regret.index(mejor)