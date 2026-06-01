# =============================================================================
# MODULO 4: Bienestar Estudiantil
# Tipo: Programacion No Lineal (NLP) - aproximacion de MINLP
# Solver: IPOPT
# Objetivo: Maximizar la utilidad total de items de bienestar bajo
#            el principio de utilidad marginal decreciente
# Formulacion:
#   max  sum(pesos[i] * (z[i] + eps)^gamma)   donde gamma = 0.5
#   s.a. sum(z[i]) <= presupuesto_bienestar
#        0 <= z[i] <= costo_max[i]             para todo i
#        sum(tiempo[i]/costo_max[i] * z[i]) <= horas_libres
# Nota: gamma = 0.5 (raiz cuadrada) modela rendimiento decreciente:
#       cada boliviano adicional aporta menos utilidad que el anterior
# =============================================================================

import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

# Items de bienestar con sus rangos de costo y tiempo requerido en horas
ITEMS = {
    "Vitaminas":                   {"costo_min": 50,  "costo_max": 200, "tiempo_horas": 0},
    "Libros":                      {"costo_min": 80,  "costo_max": 300, "tiempo_horas": 2},
    "Materiales de estudio":       {"costo_min": 50,  "costo_max": 250, "tiempo_horas": 1},
    "Materiales de entrenamiento": {"costo_min": 100, "costo_max": 400, "tiempo_horas": 3},
}

def resolver_bienestar(presupuesto_bienestar, bloques_libres, pesos):
    """
    Resuelve el modelo NLP de optimizacion de bienestar estudiantil.

    Parametros:
        presupuesto_bienestar (float): Presupuesto disponible del M1 en Bs.
        bloques_libres (dict): Bloques libres por dia del M3.
        pesos (dict): Importancia de cada item, entre 0 y 1.

    Retorna:
        dict con estado, gasto por item, utilidad por item y totales.
    """

    items = list(ITEMS.keys())
    gamma = 0.5  # exponente de utilidad marginal decreciente

    # Total de horas libres disponibles semanales (del M3)
    horas_libres = sum(bloques_libres.values()) * 2

    model = pyo.ConcreteModel()

    # Variables continuas: cuanto gastar en cada item (en Bs)
    model.z = pyo.Var(items, domain=pyo.NonNegativeReals)

    # Valor inicial para ayudar a IPOPT a converger
    for i in items:
        model.z[i].set_value(ITEMS[i]["costo_min"])

    # Funcion objetivo no lineal: max sum(peso[i] * z[i]^gamma)
    # eps=1e-6 evita derivada infinita cuando z[i] = 0
    model.objetivo = pyo.Objective(
        expr=sum(pesos[i] * (model.z[i] + 1e-6)**gamma for i in items),
        sense=pyo.maximize
    )

    model.r = pyo.ConstraintList()

    # Restriccion 1: no exceder presupuesto total de bienestar (del M1)
    model.r.add(sum(model.z[i] for i in items) <= presupuesto_bienestar)

    # Restriccion 2: limite maximo de gasto por item
    for i in items:
        model.r.add(model.z[i] <= ITEMS[i]["costo_max"])
        model.r.add(model.z[i] >= 0)

    # Restriccion 3: tiempo disponible del M3
    # Proporcion de tiempo consumido por cada item segun su gasto
    model.r.add(
        sum((ITEMS[i]["tiempo_horas"] / ITEMS[i]["costo_max"]) * model.z[i]
            for i in items) <= horas_libres
    )

    # Resolver con IPOPT (solver NLP)
    solver = pyo.SolverFactory("ipopt")
    resultado = solver.solve(model)

    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        seleccionados = {
            i: {
                "gasto_bs": round(pyo.value(model.z[i]), 2),
                # Utilidad calculada con la misma formula del objetivo
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