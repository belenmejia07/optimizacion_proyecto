import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

# Categorías con sus límites mínimos y máximos (porcentaje del ingreso)
CATEGORIAS = {
    "Alimentación":    {"min": 0.15, "max": 0.40},
    "Transporte":      {"min": 0.05, "max": 0.20},
    "Estudios":        {"min": 0.05, "max": 0.20},
    "Salud/Bienestar": {"min": 0.05, "max": 0.15},
    "Ocio":            {"min": 0.02, "max": 0.15},
    "Ahorro":          {"min": 0.10, "max": 0.30},
}

def resolver_presupuesto(ingreso, prioridades):
    model = pyo.ConcreteModel()

    categorias = list(CATEGORIAS.keys())

    # Variables de decisión
    model.x = pyo.Var(categorias, domain=pyo.NonNegativeReals)

    # Función objetivo
    model.objetivo = pyo.Objective(
        expr=sum(prioridades[c] * model.x[c] for c in categorias),
        sense=pyo.maximize
    )

    # Restricción 1: todo el ingreso debe ser asignado
    model.balance = pyo.Constraint(
        expr=sum(model.x[c] for c in categorias) == ingreso
    )

    # Restricción 2: límites por categoría
    model.limites = pyo.ConstraintList()
    for c in categorias:
        model.limites.add(model.x[c] >= CATEGORIAS[c]["min"] * ingreso)
        model.limites.add(model.x[c] <= CATEGORIAS[c]["max"] * ingreso)

    # Resolver
    solver = pyo.SolverFactory("glpk")
    resultado = solver.solve(model)

    # Verificar resultado
    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):
        
        asignaciones = {c: round(pyo.value(model.x[c]), 2) for c in categorias}
        
        return {
            "estado": "optimo",
            "asignaciones": asignaciones,
            "alimentacion": asignaciones["Alimentación"],
            "bienestar": asignaciones["Salud/Bienestar"],
        }
    else:
        return {"estado": "infactible"}