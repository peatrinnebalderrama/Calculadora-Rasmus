
from flask import Flask, jsonify, request, render_template, abort
from jinja2 import TemplateNotFound


import importlib
import inventarios
import riesgo


def cargar(nombre):
    
    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError:
        return None


def requerir(modulo, nombre):
    if modulo is None:
        raise ValueError(f"Falta el archivo {nombre}.py en la carpeta del proyecto.")


incertidumbre = cargar("incertidumbre")
certeza = cargar("certeza")
pareto_mod = cargar("pareto")

app = Flask(__name__)


def api(funcion):
    """atrapa errores y los devuelve como JSON con código 400."""
    def envoltura():
        try:
            datos = request.get_json(force=True)
            return jsonify(funcion(datos))
        except (ValueError, KeyError, TypeError, ZeroDivisionError) as e:
            return jsonify({"error": f"Datos inválidos: {e}"}), 400
    envoltura.__name__ = funcion.__name__
    return envoltura



TEMAS = {
    "certeza": {"titulo": "Decisión bajo certeza", "icono": "bi-table", "grupo": "Decisiones",
                "descripcion": "Compara alternativas según criterios con tablas por pares."},
    "riesgo": {"titulo": "Decisión bajo riesgo", "icono": "bi-diagram-3", "grupo": "Decisiones",
               "descripcion": "Valor esperado, VEIP y árbol de decisión con probabilidades."},
    "incertidumbre": {"titulo": "Información escasa", "icono": "bi-question-diamond", "grupo": "Decisiones",
                      "descripcion": "Laplace, Wald, Hurwicz y Savage: criterios optimista y pesimista."},
    "pareto": {"titulo": "Pareto (ABC)", "icono": "bi-bar-chart-line", "grupo": "Inventarios",
               "descripcion": "Regla 80/20 para clasificar los productos en A, B y C."},
    "eoq": {"titulo": "EOQ", "icono": "bi-box-seam", "grupo": "Inventarios",
            "descripcion": "Cantidad económica de pedido, con y sin faltantes."},
}


@app.context_processor
def inyectar_temas():
    return {"TEMAS": TEMAS}


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/<nombre>")
def tema(nombre):
    if nombre not in TEMAS:
        abort(404)
    try:
        return render_template(f"{nombre}.html", info=TEMAS[nombre])
    except TemplateNotFound:
        return render_template("pendiente.html", info=TEMAS[nombre])


# ---------- 1. CERTEZA ----------
@app.route("/api/certeza", methods=["POST"])
@api
def api_certeza(d):
    requerir(certeza, "certeza")
    # triángulos superiores
    m_crit = certeza.completar_reciprocos(d["matriz_criterios"])
    m_alt = {c: certeza.completar_reciprocos(m)
             for c, m in d["matrices_por_criterio"].items()}
    return certeza.decision_certeza(d["criterios"], d["alternativas"], m_crit, m_alt)


# ---------- 2. RIESGO ----------
@app.route("/api/riesgo", methods=["POST"])
@api
def api_riesgo(d):
    return riesgo.valor_esperado(d["alternativas"], d["estados"], d["pagos"],
                                 d["probs"], d.get("maximizar", True))


@app.route("/api/riesgo/arbol", methods=["POST"])
@api
def api_arbol(d):
    return riesgo.resolver_arbol(d["arbol"], d.get("maximizar", True))


# ---------- 3. INCERTIDUMBRE ----------
@app.route("/api/incertidumbre", methods=["POST"])
@api
def api_incertidumbre(d):
    requerir(incertidumbre, "incertidumbre")
    m = d["matriz"]
    alts = d["alternativas"]
    mx = d.get("maximizar", True)
    alfa = float(d.get("alfa", 0.5))
    if not 0 <= alfa <= 1:
        raise ValueError("α debe estar entre 0 y 1.")
    if len(m) != len(alts):
        raise ValueError("Cada alternativa necesita una fila de pagos.")
    if len({len(f) for f in m}) != 1:
        raise ValueError("Todas las filas deben tener el mismo número de estados.")

    mejor = "mayor" if mx else "menor"
    out = {}

    # Laplace
    v, i = incertidumbre.laplace(m, mx)
    pasos = [f"{a}: ({' + '.join(str(x) for x in f)}) / {len(f)} = {val:.4f}"
             for a, f, val in zip(alts, m, v)]
    pasos.append(f"Se elige el {mejor} promedio: {alts[i]}")
    out["laplace"] = {"valores": v, "indice": i, "mejor": alts[i], "pasos": pasos}

    # Wald
    v, i = incertidumbre.wald(m, mx)
    if mx:
        pasos = [f"{a}: peor resultado = mínimo de {f} = {val}" for a, f, val in zip(alts, m, v)]
        pasos.append(f"Se elige el mayor de los mínimos (maximin): {alts[i]}")
    else:
        pasos = [f"{a}: peor resultado = máximo de {f} = {val}" for a, f, val in zip(alts, m, v)]
        pasos.append(f"Se elige el menor de los máximos (minimax): {alts[i]}")
    out["wald"] = {"valores": v, "indice": i, "mejor": alts[i], "pasos": pasos}

    # Hurwicz (α = coeficiente de optimismo, peso del mejor resultado)
    v, i = incertidumbre.hurwicz(m, alfa, mx)
    pasos = []
    for a, f, val in zip(alts, m, v):
        b, w = (max(f), min(f)) if mx else (min(f), max(f))
        pasos.append(f"{a}: α·{b} + (1-α)·{w} = {alfa}·{b} + {round(1 - alfa, 4)}·{w} = {val:.4f}")
    pasos.append(f"Se elige el {mejor} valor: {alts[i]}")
    out["hurwicz"] = {"valores": v, "indice": i, "mejor": alts[i], "alfa": alfa, "pasos": pasos}

    # Savage
    regret, maxr, i = incertidumbre.savage(m, mx)
    ref = [max(c) if mx else min(c) for c in zip(*m)]
    pasos = [f"Mejor valor de cada estado ({'máximo' if mx else 'mínimo'} de cada columna): {ref}"]
    for a, r, mr in zip(alts, regret, maxr):
        pasos.append(f"{a}: arrepentimientos {r} → máximo = {mr}")
    pasos.append(f"Se elige el menor de los arrepentimientos máximos: {alts[i]}")
    out["savage"] = {"tabla_arrepentimiento": regret, "maximos": maxr, "referencia": ref,
                     "indice": i, "mejor": alts[i], "pasos": pasos}
    return out


# ---------- 4. INVENTARIOS ----------
@app.route("/api/pareto", methods=["POST"])
@api
def api_pareto(d):
    requerir(pareto_mod, "pareto")
    return pareto_mod.pareto(d["productos"], d.get("limite", 80))


@app.route("/api/eoq", methods=["POST"])
@api
def api_eoq(d):
    return inventarios.eoq_clasico(d["D"], d["S"], d.get("H"), d.get("i"),
                                   d.get("C", 0), d.get("L", 0), d.get("dias", 365))


@app.route("/api/eoq-faltantes", methods=["POST"])
@api
def api_eoq_faltantes(d):
    return inventarios.eoq_faltantes(d["D"], d["S"], d["B"], d.get("H"), d.get("i"),
                                     d.get("C", 0), d.get("L", 0), d.get("dias", 365))


if __name__ == "__main__":
    app.run(debug=True)