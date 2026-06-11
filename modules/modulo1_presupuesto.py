# =============================================================================
# MODULO 1: Presupuesto Mensual Inteligente
# Tipo: Programacion Lineal (LP)
# Solver: GLPK
# Objetivo: Maximizar utilidad ponderada al distribuir el ingreso mensual
#            entre categorias de gasto respetando limites minimos y maximos
# Formulacion:
#   max  sum(prioridades[c] * x[c])
#   s.a. sum(x[c]) = ingreso
#        min[c] * ingreso <= x[c] <= max[c] * ingreso  para todo c
#        x[c] >= 0
# =============================================================================

import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

# Categorias de gasto con sus limites como porcentaje del ingreso mensual
CATEGORIAS = {
    "Alimentacion":    {"min": 0.15, "max": 0.35},
    "Transporte":      {"min": 0.05, "max": 0.10},
    "Estudios":        {"min": 0.10, "max": 0.20},
    "Salud/Bienestar": {"min": 0.05, "max": 0.15},
    "Ocio":            {"min": 0.02, "max": 0.10},
    "Ahorro":          {"min": 0.05, "max": 0.10},
}

def resolver_presupuesto(ingreso, prioridades):
    """
    Resuelve el modelo LP de distribucion de presupuesto mensual.

    Parametros:
        ingreso (float): Ingreso mensual disponible en Bs.
        prioridades (dict): Peso de importancia por categoria.

    Retorna:
        dict con estado, asignaciones por categoria, y presupuestos
        para alimentacion (->M2) y bienestar (->M4).
    """

    model = pyo.ConcreteModel()
    categorias = list(CATEGORIAS.keys()) # Se toma solo los nombres de las categorias

    # Variables de decision: monto asignado a cada categoria (continuas, >= 0)
    model.x = pyo.Var(categorias, domain=pyo.NonNegativeReals)

    # Funcion objetivo: maximizar utilidad ponderada por prioridades del usuario
    model.objetivo = pyo.Objective(
        expr=sum(prioridades[c] * model.x[c] for c in categorias),
        sense=pyo.maximize
    )

    # Restriccion 1: todo el ingreso debe ser asignado (balance exacto)
    model.balance = pyo.Constraint(
        expr=sum(model.x[c] for c in categorias) == ingreso
    )

    # Restriccion 2: cada categoria respeta su rango minimo y maximo
    model.limites = pyo.ConstraintList() # Se crea una lista de restricciones por cada categoria
    for c in categorias: # Se itera por categoria
        model.limites.add(model.x[c] >= CATEGORIAS[c]["min"] * ingreso) # A cada categoria no se le asigna menos que el minimo
        model.limites.add(model.x[c] <= CATEGORIAS[c]["max"] * ingreso) # A cada categoria no se le asigna mas que el maximo

    # Resolver con GLPK
    solver = pyo.SolverFactory("glpk")
    resultado = solver.solve(model)

    # Verificar si se encontro solucion optima
    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        asignaciones = {c: round(pyo.value(model.x[c]), 2) for c in categorias}

        return {
            "estado": "optimo",
            "asignaciones": asignaciones,
            "alimentacion": asignaciones["Alimentacion"],  # pasa al M2
            "bienestar": asignaciones["Salud/Bienestar"],  # pasa al M4
        }
    else:
        return {"estado": "infactible"}