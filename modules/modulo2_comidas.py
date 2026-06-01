import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition
import pandas as pd

def cargar_alimentos():
    return pd.read_csv("data/alimentos.csv")

def resolver_comidas(presupuesto_mensual, kcal_min, kcal_max, proteina_min, carbs_min, carbs_max, grasa_min, grasa_max, fibra_min, fibra_max):
    
    df = cargar_alimentos()
    alimentos = df["nombre"].tolist()
    
    costo    = dict(zip(df["nombre"], df["costo_bs"]))
    kcal     = dict(zip(df["nombre"], df["kcal"]))
    proteina = dict(zip(df["nombre"], df["proteina_g"]))
    carbs    = dict(zip(df["nombre"], df["carbs_g"]))
    grasa    = dict(zip(df["nombre"], df["grasa_g"]))
    fibra    = dict(zip(df["nombre"], df["fibra_g"]))

    model = pyo.ConcreteModel()
    model.x = pyo.Var(alimentos, domain=pyo.NonNegativeReals)

    model.objetivo = pyo.Objective(
        expr=sum(costo[a] * model.x[a] for a in alimentos),
        sense=pyo.minimize
    )

    presupuesto_semanal = presupuesto_mensual / 4

    model.r = pyo.ConstraintList()

    model.r.add(sum(costo[a] * model.x[a] for a in alimentos) <= presupuesto_semanal)
    model.r.add(sum(kcal[a] * model.x[a] for a in alimentos) >= kcal_min * 7)
    model.r.add(sum(kcal[a] * model.x[a] for a in alimentos) <= kcal_max * 7)
    model.r.add(sum(proteina[a] * model.x[a] for a in alimentos) >= proteina_min * 7)
    model.r.add(sum(carbs[a] * model.x[a] for a in alimentos) >= carbs_min * 7)
    model.r.add(sum(carbs[a] * model.x[a] for a in alimentos) <= carbs_max * 7)
    model.r.add(sum(grasa[a] * model.x[a] for a in alimentos) >= grasa_min * 7)
    model.r.add(sum(grasa[a] * model.x[a] for a in alimentos) <= grasa_max * 7)
    model.r.add(sum(fibra[a] * model.x[a] for a in alimentos) >= fibra_min * 7)
    model.r.add(sum(fibra[a] * model.x[a] for a in alimentos) <= fibra_max * 7)

    solver = pyo.SolverFactory("glpk")
    resultado = solver.solve(model)

    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        plan = {a: round(pyo.value(model.x[a]), 2) for a in alimentos if pyo.value(model.x[a]) > 0.01}
        costo_total    = round(sum(costo[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        kcal_total     = round(sum(kcal[a]     * pyo.value(model.x[a]) for a in alimentos), 2)
        proteina_total = round(sum(proteina[a] * pyo.value(model.x[a]) for a in alimentos), 2)
        carbs_total    = round(sum(carbs[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        grasa_total    = round(sum(grasa[a]    * pyo.value(model.x[a]) for a in alimentos), 2)
        fibra_total    = round(sum(fibra[a] * pyo.value(model.x[a]) for a in alimentos), 2)

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