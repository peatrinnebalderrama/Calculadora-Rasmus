def _validar_probs(probs):
    if any(p < 0 for p in probs):
        raise ValueError("Las probabilidades no pueden ser negativas.")
    if abs(sum(probs) - 1) > 1e-6:
        raise ValueError(f"Las probabilidades deben sumar 1 (suman {sum(probs):.4f}).")


def valor_esperado(alternativas, estados, pagos, probs, maximizar=True):
    """
    alternativas: lista de nombres (filas)
    estados: lista de nombres de los estados de la naturaleza (columnas)
    pagos: matriz [alternativa][estado]
    probs: probabilidad de cada estado (suma 1)
    maximizar: True si los pagos son ganancias, False si son costos
    """
    _validar_probs(probs)
    pasos = []
    n_est = len(estados)
    opt = max if maximizar else min

    # valor esperado VE de cada alternativa
    ve = []
    for a, fila in zip(alternativas, pagos):
        terminos = " + ".join(f"({p}·{v})" for p, v in zip(probs, fila))
        valor = sum(p * v for p, v in zip(probs, fila))
        ve.append(valor)
        pasos.append(f"VE({a}) = {terminos} = {valor:.4f}")

    mejor_ve = opt(ve)
    idx = ve.index(mejor_ve)
    pasos.append(f"Mejor alternativa: {alternativas[idx]} con VE = {mejor_ve:.4f}")

    # mejor valor de cada estado (información perfecta)
    cols = list(zip(*pagos))
    mejores_por_estado = [opt(c) for c in cols]
    ve_ip = sum(p * m for p, m in zip(probs, mejores_por_estado))
    pasos.append("Con información perfecta: " +
                 " + ".join(f"({p}·{m})" for p, m in zip(probs, mejores_por_estado)) +
                 f" = {ve_ip:.4f}")

    #  VEIP = valor esperado de la información perfecta
    veip = (ve_ip - mejor_ve) if maximizar else (mejor_ve - ve_ip)
    pasos.append(f"VEIP = |VE con información perfecta - mejor VE| = {veip:.4f}")

    #  tabla de oportunidad perdida arrepentimiento y su valor esperado
    perdida = []
    for fila in pagos:
        if maximizar:
            perdida.append([mejores_por_estado[j] - fila[j] for j in range(n_est)])
        else:
            perdida.append([fila[j] - mejores_por_estado[j] for j in range(n_est)])
    pol = [sum(p * x for p, x in zip(probs, f)) for f in perdida]
    mejor_pol = min(pol)
    idx_pol = pol.index(mejor_pol)
    pasos.append("Pérdida de oportunidad esperada (POE): " +
                 ", ".join(f"{a} = {v:.4f}" for a, v in zip(alternativas, pol)))
    pasos.append(f"Mínima POE: {alternativas[idx_pol]} ({mejor_pol:.4f}); "
                 f"coincide con el VEIP: {abs(mejor_pol - veip) < 1e-6}")

    return {
        "ve": ve,
        "mejor": alternativas[idx],
        "mejor_ve": mejor_ve,
        "mejores_por_estado": mejores_por_estado,
        "ve_info_perfecta": ve_ip,
        "veip": veip,
        "tabla_perdida": perdida,
        "poe": pol,
        "mejor_poe": alternativas[idx_pol],
        "pasos": pasos,
    }


# ---------------------------------------------------------------------------
# ÁRBOL DE DECISIÓN (varias etapas)
#
# Nodos (diccionarios):
#   {"tipo": "final", "valor": 100}
#   {"tipo": "azar", "nombre": "Demanda",
#    "ramas": [{"etiqueta": "Alta", "prob": 0.6, "nodo": {...}}, ...]}
#   {"tipo": "decision", "nombre": "Qué hacer",
#    "ramas": [{"etiqueta": "Ampliar", "costo": 50, "nodo": {...}}, ...]}
# "costo" (opcional) es lo que cuesta tomar esa rama.
# ---------------------------------------------------------------------------

def resolver_arbol(nodo, maximizar=True):
    """Resuelve el árbol de derecha a izquierda (hacia atrás). Devuelve el árbol
    anotado con 'valor' en cada nodo, y la lista de pasos."""
    pasos = []
    opt = max if maximizar else min

    def evaluar(n):
        tipo = n["tipo"]
        nombre = n.get("nombre", tipo)

        if tipo == "final":
            n["valor"] = float(n["valor"])
            return n["valor"]

        if tipo == "azar":
            _validar_probs([r["prob"] for r in n["ramas"]])
            total = 0.0
            partes = []
            for r in n["ramas"]:
                v = evaluar(r["nodo"])
                r["valor"] = v
                total += r["prob"] * v
                partes.append(f"({r['prob']}·{v:.2f})")
            n["valor"] = total
            pasos.append(f"Nodo de azar «{nombre}»: " + " + ".join(partes) + f" = {total:.4f}")
            return total

        if tipo == "decision":
            netos = []
            for r in n["ramas"]:
                v = evaluar(r["nodo"])
                costo = float(r.get("costo", 0))
                neto = v - costo if maximizar else v + costo
                r["valor"] = v
                r["neto"] = neto
                netos.append(neto)
                if costo:
                    pasos.append(f"  Rama «{r['etiqueta']}»: {v:.2f} "
                                 f"{'-' if maximizar else '+'} {costo:.2f} = {neto:.2f}")
                else:
                    pasos.append(f"  Rama «{r['etiqueta']}»: {neto:.2f}")
            mejor = opt(netos)
            for r in n["ramas"]:
                r["elegida"] = (r["neto"] == mejor)
            n["valor"] = mejor
            elegida = next(r["etiqueta"] for r in n["ramas"] if r["elegida"])
            pasos.append(f"Nodo de decisión «{nombre}»: se elige «{elegida}» con valor {mejor:.4f}")
            return mejor

        raise ValueError(f"Tipo de nodo desconocido: {tipo}")

    valor = evaluar(nodo)
    return {"arbol": nodo, "valor": valor, "pasos": pasos}


if __name__ == "__main__":
    # Tienda de autopartes: cuántos lotes de baterías pedir según la demanda
    alts = ["Pedir 10", "Pedir 20", "Pedir 30"]
    est = ["Demanda baja", "Demanda media", "Demanda alta"]
    pagos = [[100, 100, 100], [60, 200, 200], [20, 160, 300]]
    r = valor_esperado(alts, est, pagos, [0.3, 0.5, 0.2])
    print("\n".join(r["pasos"]))

    arbol = {"tipo": "decision", "nombre": "Ampliar tienda", "ramas": [
        {"etiqueta": "Ampliar", "costo": 80, "nodo": {
            "tipo": "azar", "nombre": "Demanda", "ramas": [
                {"etiqueta": "Alta", "prob": 0.6, "nodo": {"tipo": "final", "valor": 300}},
                {"etiqueta": "Baja", "prob": 0.4, "nodo": {"tipo": "final", "valor": 100}}]}},
        {"etiqueta": "No ampliar", "nodo": {"tipo": "final", "valor": 150}}]}
    print()
    print("\n".join(resolver_arbol(arbol)["pasos"]))