import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

ITEMS = {
    "Vitaminas":                   {"costo_min": 50,  "costo_max": 200, "tiempo_horas": 0},
    "Libros":                      {"costo_min": 80,  "costo_max": 300, "tiempo_horas": 2},
    "Materiales de estudio":       {"costo_min": 50,  "costo_max": 250, "tiempo_horas": 1},
    "Materiales de entrenamiento": {"costo_min": 100, "costo_max": 400, "tiempo_horas": 3},
}

def resolver_bienestar(presupuesto_bienestar, bloques_libres, pesos):

    items = list(ITEMS.keys())
    gamma = 0.5
    horas_libres = sum(bloques_libres.values()) * 2

    model = pyo.ConcreteModel()

    # Solo variables continuas con límites min/max por ítem
    model.z = pyo.Var(items, domain=pyo.NonNegativeReals)

    # Valor inicial
    for i in items:
        model.z[i].set_value(ITEMS[i]["costo_min"])

    # Función objetivo no lineal: max Σ peso[i] * z[i]^gamma
    model.objetivo = pyo.Objective(
    expr=sum(pesos[i] * (model.z[i] + 1e-6)**gamma for i in items),
    sense=pyo.maximize
    )

    model.r = pyo.ConstraintList()

    # 1. No exceder presupuesto total
    model.r.add(sum(model.z[i] for i in items) <= presupuesto_bienestar)

    # 2. Límites por ítem
    for i in items:
        model.r.add(model.z[i] <= ITEMS[i]["costo_max"])
        model.r.add(model.z[i] >= 0)

    # 3. Tiempo disponible del M3
    # Cada ítem con gasto > 0 consume tiempo — aproximamos con proporción
    model.r.add(
        sum((ITEMS[i]["tiempo_horas"] / ITEMS[i]["costo_max"]) * model.z[i] for i in items) <= horas_libres
    )

    solver = pyo.SolverFactory("ipopt")
    resultado = solver.solve(model)

    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        seleccionados = {
            i: {
                "gasto_bs": round(pyo.value(model.z[i]), 2),
                "utilidad": round(pesos[i] * max(pyo.value(model.z[i]), 0)**gamma, 3),
            }
            for i in items
        }

        utilidad_total = round(pyo.value(model.objetivo), 3)
        gasto_total = round(sum(pyo.value(model.z[i]) for i in items), 2)

        return {
            "estado": "optimo",
            "seleccionados": seleccionados,
            "utilidad_total": utilidad_total,
            "gasto_total": gasto_total,
        }
    else:
        return {"estado": "infactible"}