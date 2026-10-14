
# EOQ clásico y EOQ con faltantes 
from math import sqrt
def _costo_mantener(H, i, C):
    """H puede darse directo, o calcularse como i * C."""
    if H is not None:
        return float(H)
    if i is not None and C is not None:
        return float(i) * float(C)
    raise ValueError("Da H, o bien i y C.")


def eoq_clasico(D, S, H=None, i=None, C=0.0, L=0, dias=365):
    """
    D: demanda anual | S: costo de ordenar por pedido
    H: costo de mantener 1 unidad/año (o i * C)
    C: costo unitario | L: tiempo de entrega (en días) | dias: días del año
    """
    H = _costo_mantener(H, i, C)
    pasos = []

    Q = sqrt(2 * D * S / H)
    pasos.append(f"Q* = raíz(2·D·S / H) = raíz(2·{D}·{S} / {H}) = {Q:.2f}")

    N = D / Q
    pasos.append(f"N = D / Q* = {D} / {Q:.2f} = {N:.2f} pedidos/año")

    T = dias / N
    pasos.append(f"T = {dias} / N = {T:.2f} días entre pedidos")

    d = D / dias
    ROP = d * L
    pasos.append(f"d = D / {dias} = {d:.2f}/día;  R = d·L = {d:.2f}·{L} = {ROP:.2f} unidades")

    c_ordenar = N * S
    c_mantener = (Q / 2) * H
    c_compra = D * C
    total = c_ordenar + c_mantener + c_compra
    pasos.append(f"Costo ordenar = N·S = {c_ordenar:.2f}")
    pasos.append(f"Costo mantener = (Q/2)·H = {c_mantener:.2f}")
    if C:
        pasos.append(f"Costo compra = D·C = {c_compra:.2f}")
    pasos.append(f"Costo total = {total:.2f}")

    # Datos para graficar costos vs Q
    qs = [Q * k / 10 for k in range(2, 21)]
    grafica = {
        "q": qs,
        "ordenar": [D / q * S for q in qs],
        "mantener": [q / 2 * H for q in qs],
        "total": [D / q * S + q / 2 * H for q in qs],
    }

    return {"Q": Q, "N": N, "T": T, "ROP": ROP, "costo_ordenar": c_ordenar,
            "costo_mantener": c_mantener, "costo_compra": c_compra,
            "costo_total": total, "pasos": pasos, "grafica": grafica}


def eoq_faltantes(D, S, B, H=None, i=None, C=0.0, L=0, dias=365):
    """
    Igual que el clásico, más:
    B: costo de faltante por unidad/año (pedidos pendientes permitidos)
    """
    H = _costo_mantener(H, i, C)
    pasos = []

    factor = sqrt((H + B) / B)
    Q = sqrt(2 * D * S / H) * factor
    pasos.append(f"Q* = raíz(2DS/H)·raíz((H+B)/B) = {Q:.2f}")

    
    Smax = Q * B / (H + B)
    pasos.append(f"Faltante máximo =  Q*·B/(H+B) = {Smax:.2f}")

    faltante = Q - Smax
    pasos.append(f"Inventario máximo I* = Q* - S* = {faltante:.2f}")


    N = D / Q
    T = dias / N
    pasos.append(f"N = D/Q* = {N:.2f} pedidos/año;  T = {T:.2f} días")

    d = D / dias
    t1 = Smax / d   # días con inventario
    t2 = faltante / d  # días con faltante
    pasos.append(f"Días con inventario t1 = S*/d = {t1:.2f};  días con faltante t2 = {t2:.2f}")

    ROP = d * L - faltante
    pasos.append(f"Punto de reorden R = d·L - faltante máx = {ROP:.2f} (negativo = pedir con faltante ya acumulado)")

    c_ordenar =  S*(D/Q)
    c_mantener = ((Q-faltante) ** 2) * H / (2 * Q)
    c_faltante =  faltante** 2 * B / (2 * Q)
    c_compra = D * C
    total = c_ordenar + c_mantener + c_faltante + c_compra
    pasos.append(f"Costo ordenar = {c_ordenar:.2f}")
    pasos.append(f"Costo mantener = (Q*-S*)²·H/(2Q*) = {c_mantener:.2f}")
    pasos.append(f"Costo faltante = S*²·P/(2Q*) = {c_faltante:.2f}")
    pasos.append(f"Costo total = {total:.2f}")

    return {"Q": Q, "S_max": Smax, "faltante_max": faltante, "N": N, "T": T,
            "t1": t1, "t2": t2, "ROP": ROP, "costo_ordenar": c_ordenar,
            "costo_mantener": c_mantener, "costo_faltante": c_faltante,
            "costo_compra": c_compra, "costo_total": total, "pasos": pasos}


if __name__ == "__main__":
    r = eoq_clasico(D=1000, S=10, H=2.5, L=7)
    print("\n".join(r["pasos"]))
    print()
    r = eoq_faltantes(D=1000, S=10, H=2.5, B=5, L=7)
    print("\n".join(r["pasos"]))