# =============================================================================
# MODULO 3: Calendario de Estudios Semanal
# Tipo: Programacion Entera Mixta (MILP)
# Solver: GLPK
# Objetivo: Maximizar bloques de estudio ponderados por prioridad,
#            asignando materias a bloques de tiempo con variables binarias
# Formulacion:
#   max  sum(prioridades[m] * x[d,b,m])
#   s.a. sum_m(x[d,b,m]) <= 1                          para todo d,b
#        sum_{d,b}(x[d,b,m]) >= bloques_minimos         para todo m
#        sum_{d,b}(x[d,b,m]) <= bloques_maximos         para todo m
#        sum_{b,m}(x[d,b,m]) <= max_bloques_dia         para todo d
#        sum_m(x[d,b,m]) = 0   si (d,b) bloqueado
#        x[d,b,m] en {0,1}
# =============================================================================

import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

# Lista de materias del semestre
MATERIAS = [
    "Adquisicion y Analisis de Datos",
    "Estructuras de Datos",
    "Metodologias de la Investigacion",
    "Metodologias Agiles",
    "Conocimiento y Razonamiento Automatico",
    "Optimizacion",
]

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
BLOQUES = [1, 2, 3, 4]  # 4 bloques de 2 horas por dia

def resolver_estudios(bloques_bloqueados, prioridades, min_horas=6, max_bloques_dia=3):
    """
    Resuelve el modelo MILP de asignacion de bloques de estudio.

    Parametros:
        bloques_bloqueados (list): Lista de tuplas (dia, bloque) no disponibles.
        prioridades (dict): Peso de importancia por materia, entre 0 y 1.
        min_horas (int): Horas minimas de estudio por materia por semana.
        max_bloques_dia (int): Maximo de bloques de estudio por dia.

    Retorna:
        dict con estado, calendario semanal, horas por materia
        y bloques libres por dia (->M4).
    """

    model = pyo.ConcreteModel()

    # Variables binarias: x[dia, bloque, materia] = 1 si se estudia esa materia
    model.x = pyo.Var(DIAS, BLOQUES, MATERIAS, domain=pyo.Binary)

    # Funcion objetivo: maximizar bloques ponderados por prioridad del usuario
    model.objetivo = pyo.Objective(
        expr=sum(
            prioridades[m] * model.x[d, b, m]
            for d in DIAS for b in BLOQUES for m in MATERIAS
        ),
        sense=pyo.maximize
    )

    model.r = pyo.ConstraintList()

    # Restriccion 1: en cada bloque solo se puede estudiar una materia a la vez
    for d in DIAS:
        for b in BLOQUES:
            model.r.add(sum(model.x[d, b, m] for m in MATERIAS) <= 1)

    # Restriccion 2: cada materia debe cumplir el minimo de bloques semanales
    bloques_minimos = min_horas // 2  # 6 horas / 2 horas por bloque = 3 bloques
    for m in MATERIAS:
        model.r.add(
            sum(model.x[d, b, m] for d in DIAS for b in BLOQUES) >= bloques_minimos
        )

    # Restriccion 3: bloques bloqueados no pueden ser usados
    for (d, b) in bloques_bloqueados:
        model.r.add(sum(model.x[d, b, m] for m in MATERIAS) == 0)

    # Restriccion 4: limite de bloques de estudio por dia para evitar sobrecarga
    for d in DIAS:
        model.r.add(
            sum(model.x[d, b, m] for b in BLOQUES for m in MATERIAS) <= max_bloques_dia
        )

    # Restriccion 5: limite maximo por materia para distribucion equitativa
    bloques_maximos = bloques_minimos * 2
    for m in MATERIAS:
        model.r.add(
            sum(model.x[d, b, m] for d in DIAS for b in BLOQUES) <= bloques_maximos
        )

    # Resolver con GLPK
    solver = pyo.SolverFactory("glpk")
    resultado = solver.solve(model)

    if (resultado.solver.status == SolverStatus.ok and
            resultado.solver.termination_condition == TerminationCondition.optimal):

        # Construir calendario: dia -> bloque -> materia asignada
        calendario = {}
        for d in DIAS:
            calendario[d] = {}
            for b in BLOQUES:
                asignado = None
                for m in MATERIAS:
                    if pyo.value(model.x[d, b, m]) > 0.5:
                        asignado = m
                calendario[d][b] = asignado

        # Calcular horas totales por materia (bloques * 2 horas)
        horas_por_materia = {}
        for m in MATERIAS:
            bloques_asignados = sum(
                pyo.value(model.x[d, b, m]) for d in DIAS for b in BLOQUES
            )
            horas_por_materia[m] = round(bloques_asignados * 2, 1)

        # Calcular bloques libres por dia -> pasan al M4
        bloques_libres = {}
        for d in DIAS:
            libres = sum(
                1 for b in BLOQUES
                if calendario[d][b] is None and (d, b) not in bloques_bloqueados
            )
            bloques_libres[d] = libres

        return {
            "estado": "optimo",
            "calendario": calendario,
            "horas_por_materia": horas_por_materia,
            "bloques_libres": bloques_libres,
        }
    else:
        return {"estado": "infactible"}