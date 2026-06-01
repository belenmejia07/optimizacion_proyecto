# =============================================================================
# MODULO 2: Planificacion de Comidas Semanal
# Tipo: Programacion Lineal (LP)
# Solver: GLPK
# Objetivo: Minimizar el costo semanal de alimentacion cumpliendo
#            requerimientos nutricionales diarios del usuario
# Formulacion:
#   min  sum(costo[a] * x[a])
#   s.a. sum(costo[a] * x[a]) <= presupuesto_semanal
#        kcal_min*7 <= sum(kcal[a]*x[a]) <= kcal_max*7
#        sum(proteina[a]*x[a]) >= proteina_min*7
#        carbs_min*7 <= sum(carbs[a]*x[a]) <= carbs_max*7
#        grasa_min*7 <= sum(grasa[a]*x[a]) <= grasa_max*7
#        fibra_min*7 <= sum(fibra[a]*x[a]) <= fibra_max*7
#        x[a] >= 0
# =============================================================================

import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition
import pandas as pd

def cargar_alimentos():
    """Carga el CSV de alimentos desde la carpeta data/."""
    return pd.read_csv("data/alimentos.csv")

def resolver_comidas(presupuesto_mensual, kcal_min, kcal_max, proteina_min,
                     carbs_min, carbs_max, grasa_min, grasa_max, fibra_min, fibra_max):
    """
    Resuelve el modelo LP de planificacion de comidas semanales.

    Parametros:
        presupuesto_mensual (float): Presupuesto de alimentacion del M1 en Bs.
        kcal_min/max (int): Rango de calorias diarias permitidas.
        proteina_min (int): Proteina minima diaria en gramos.
        carbs_min/max (int): Rango de carbohidratos diarios en gramos.
        grasa_min/max (int): Rango de grasas diarias en gramos.
        fibra_min/max (int): Rango de fibra diaria en gramos.

    Retorna:
        dict con estado, plan de alimentos, costo y totales nutricionales.
    """

    df = cargar_alimentos()
    alimentos = df["nombre"].tolist()

    # Diccionarios de datos nutricionales y costo por alimento (base 100g)
    costo    = dict(zip(df["nombre"], df["costo_bs"]))
    kcal     = dict(zip(df["nombre"], df["kcal"]))
    proteina = dict(zip(df["nombre"], df["proteina_g"]))
    carbs    = dict(zip(df["nombre"], df["carbs_g"]))
    grasa    = dict(zip(df["nombre"], df["grasa_g"]))
    fibra    = dict(zip(df["nombre"], df["fibra_g"]))

    model = pyo.ConcreteModel()

    # Variables de decision: porciones de 100g de cada alimento por semana
    model.x = pyo.Var(alimentos, domain=pyo.NonNegativeReals)

    # Funcion objetivo: minimizar costo semanal total
    model.objetivo = pyo.Objective(
        expr=sum(costo[a] * model.x[a] for a in alimentos),
        sense=pyo.minimize
    )

    # Presupuesto semanal = presupuesto mensual / 4 semanas
    presupuesto_semanal = presupuesto_mensual / 4

    model.r = pyo.ConstraintList()

    # Restriccion de presupuesto semanal
    model.r.add(sum(costo[a] * model.x[a] for a in alimentos) <= presupuesto_semanal)

    # Restricciones nutricionales (multiplicadas por 7 dias)
    model.r.add(sum(kcal[a] * model.x[a] for a in alimentos) >= kcal_min * 7)
    model.r.add(sum(kcal[a] * model.x[a] for a in alimentos) <= kcal_max * 7)
    model.r.add(sum(proteina[a] * model.x[a] for a in alimentos) >= proteina_min * 7)
    model.r.add(sum(carbs[a] * model.x[a] for a in alimentos) >= carbs_min * 7)
    model.r.add(sum(carbs[a] * model.x[a] for a in alimentos) <= carbs_max * 7)
    model.r.add(sum(grasa[a] * model.x[a] for a in alimentos) >= grasa_min * 7)
    model.r.add(sum(grasa[a] * model.x[a] for a in alimentos) <= grasa_max * 7)
    model.r.add(sum(fibra[a] * model.x[a] for a in alimentos) >= fibra_min * 7)
    model.r.add(sum(fibra[a] * model.x[a] for a in alimentos) <= fibra_max * 7)

    # Resolver con GLPK
    solver = pyo.SolverFactory("glpk")
    resultado = solver.solve(model)

    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        # Solo incluir alimentos con cantidad significativa (> 0.01 porciones)
        plan = {a: round(pyo.value(model.x[a]), 2)
                for a in alimentos if pyo.value(model.x[a]) > 0.01}

        # Calcular totales nutricionales semanales
        costo_total    = round(sum(costo[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        kcal_total     = round(sum(kcal[a]     * pyo.value(model.x[a]) for a in alimentos), 2)
        proteina_total = round(sum(proteina[a] * pyo.value(model.x[a]) for a in alimentos), 2)
        carbs_total    = round(sum(carbs[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        grasa_total    = round(sum(grasa[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        fibra_total    = round(sum(fibra[a]    * pyo.value(model.x[a]) for a in alimentos), 2)

        return {
            "estado": "optimo",
            "plan": plan,
            "costo_semanal": costo_total,
            "kcal_semanal": kcal_total,
            "proteina_semanal": proteina_total,
            "carbs_semanal": carbs_total,
            "grasa_semanal": grasa_total,
            "fibra_semanal": fibra_total,
        }
    else:
        return {"estado": "infactible"}