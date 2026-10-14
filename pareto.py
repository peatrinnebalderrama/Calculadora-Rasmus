
# Regla 80/20: separa los productos prioritarios
def pareto(productos, limite=80):
    """
    productos: lista de diccionarios con "nombre" y
      - "valor" (ventas, cantidad vendida o valor anual), o bien
      - "demanda" y "precio" (o "costo"): valor = demanda * precio
    limite: % acumulado hasta donde llegan los prioritarios (80 por defecto)
    """
    if not 0 < limite < 100:
        raise ValueError("El límite debe estar entre 0 y 100.")
    if len(productos) < 2:
        raise ValueError("Agrega al menos 2 productos.")

    por_demanda = any("valor" not in p for p in productos)

    # valor de cada producto
    items = []
    for p in productos:
        if "valor" in p:
            valor = p["valor"]
        else:
            precio = p["precio"] if "precio" in p else p["costo"]
            valor = p["demanda"] * precio
        if valor < 0:
            raise ValueError(f"«{p['nombre']}» tiene un valor negativo.")
        items.append({"nombre": p["nombre"], "valor": float(valor)})

    total = sum(i["valor"] for i in items)
    if total <= 0:
        raise ValueError("El total debe ser mayor que cero.")

    #ordenar de mayor a menor
    items.sort(key=lambda x: x["valor"], reverse=True)

    # % de cada producto y % acumulado
    acumulado = 0.0
    tabla = []
    for pos, i in enumerate(items, start=1):
        pct = i["valor"] / total * 100
        acumulado += pct
        tabla.append({
            "posicion": pos,
            "nombre": i["nombre"],
            "valor": i["valor"],
            "pct": pct,
            "pct_acumulado": acumulado,
            "pct_productos_acum": pos / len(items) * 100,
            # PASO 4: prioritario si su acumulado llega al límite o menos
            "prioritario": acumulado <= limite + 1e-9,
        })

    nota = None
    if not any(t["prioritario"] for t in tabla):
        # El primer producto ya pasa del límite por sí solo: es el único prioritario
        tabla[0]["prioritario"] = True
        nota = (f"«{tabla[0]['nombre']}» ya supera el {limite} % por sí solo "
                f"({tabla[0]['pct']:.2f} %), así que es el único prioritario.")

    prio = [t for t in tabla if t["prioritario"]]
    resto = [t for t in tabla if not t["prioritario"]]

    def resumen(grupo):
        return {
            "num_productos": len(grupo),
            "pct_productos": len(grupo) / len(tabla) * 100,
            "valor": sum(t["valor"] for t in grupo),
            "pct_valor": sum(t["pct"] for t in grupo),
        }

    r_prio, r_resto = resumen(prio), resumen(resto)

    # Procedimiento en texto
    p1 = tabla[0]
    pasos = [
        (f"Valor de cada producto = demanda × precio. Total = {total:,.2f}."
         if por_demanda else f"Se toman las ventas de cada producto. Total = {total:,.2f}."),
        "Se ordenan los productos de mayor a menor.",
        f"% de cada producto = valor / total × 100. Ejemplo: {p1['nombre']} = "
        f"{p1['valor']:,.2f} / {total:,.2f} = {p1['pct']:.2f} %.",
        "% acumulado = se suma el % de cada producto al de los anteriores: " +
        ", ".join(f"{t['nombre']} {t['pct_acumulado']:.2f} %"
                  for t in tabla[:len(prio) + 1]) + (" …" if len(resto) > 1 else "."),
        f"Prioritarios: los productos cuyo acumulado llega a {limite} % o menos "
        f"({', '.join(t['nombre'] for t in prio)}).",
        f"Conclusión: {len(prio)} de {len(tabla)} productos "
        f"({r_prio['pct_productos']:.0f} %) generan el {r_prio['pct_valor']:.1f} % de las ventas.",
    ]
    if nota:
        pasos.insert(5, nota)

    return {
        "total": total,
        "limite": limite,
        "tabla": tabla,
        "prioritarios": r_prio,
        "resto": r_resto,
        "pasos": pasos,
        "grafica": {
            "etiquetas": [t["nombre"] for t in tabla],
            "pct": [t["pct"] for t in tabla],
            "acumulado": [t["pct_acumulado"] for t in tabla],
            "prioritario": [t["prioritario"] for t in tabla],
        },
    }