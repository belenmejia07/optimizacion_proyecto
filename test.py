# En esta archivo se probo que el solver ipopt funcione correctamente
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.x = pyo.Var(domain=pyo.NonNegativeReals)
m.obj = pyo.Objective(expr=m.x**2, sense=pyo.minimize)
m.c = pyo.Constraint(expr=m.x >= 2)

solver = pyo.SolverFactory("ipopt")
r = solver.solve(m)

print("Estado:", r.solver.status)
print("x =", pyo.value(m.x))