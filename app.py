import streamlit as st
from modules.modulo1_presupuesto import resolver_presupuesto, CATEGORIAS
from modules.modulo2_comidas import resolver_comidas
from modules.modulo3_estudios import resolver_estudios, MATERIAS, DIAS, BLOQUES
from modules.modulo4_bienestar import resolver_bienestar, ITEMS
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="OptiVida", layout="wide")

st.sidebar.title("OptiVida")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Módulos",
    ["Inicio", "M1 - Presupuesto", "M2 - Comidas", "M3 - Estudios", "M4 - Bienestar", "Resumen"]
)

# ── INICIO ─────────────────────────────────────────────────────────────────
if pagina == "Inicio":
    st.title("Sistema de Optimización de Vida Estudiantil")
    st.write("Selecciona un módulo en el menú lateral para comenzar.")
    st.markdown("""
    | Módulo | Tipo | Descripción |
    |--------|------|-------------|
    | M1 | LP | Distribuye tu presupuesto mensual |
    | M2 | LP | Planifica tus comidas semanales |
    | M3 | MILP | Organiza tu calendario de estudios |
    | M4 | MINLP | Optimiza tu bienestar estudiantil |
    """)

elif pagina == "M1 - Presupuesto":
    st.title("M1 - Presupuesto Mensual")
    st.markdown("**Tipo:** Programación Lineal (LP) | **Solver:** GLPK")
    st.markdown("---")

    ingreso = st.number_input("Ingreso mensual (Bs)", min_value=0.0, value=3000.0, step=100.0)

    st.markdown("**Prioridades por categoría** (0 = baja, 1 = alta)")
    prioridades = {}
    for cat in CATEGORIAS:
        prioridades[cat] = st.slider(cat, 0.0, 1.0, 0.5, step=0.05)

    if st.button("Resolver"):
        if ingreso <= 0:
            st.error("El ingreso debe ser mayor a 0.")
            st.session_state.pop("resultado_m1", None)
            st.session_state.pop("presupuesto_alimentacion", None)
            st.session_state.pop("presupuesto_bienestar", None)
        else:
            resultado = resolver_presupuesto(ingreso, prioridades)
            if resultado["estado"] == "optimo":
                st.session_state["resultado_m1"] = resultado
                st.session_state["ingreso_m1"] = ingreso
                st.session_state["presupuesto_alimentacion"] = resultado["alimentacion"]
                st.session_state["presupuesto_bienestar"] = resultado["bienestar"]
            else:
                st.error("El modelo no tiene solución.")

    # Mostrar resultado guardado
    if "resultado_m1" in st.session_state:
        resultado = st.session_state["resultado_m1"]
        ingreso_guardado = st.session_state["ingreso_m1"]
        st.success("¡Solución óptima encontrada!")

        df = pd.DataFrame({
            "Categoría": list(resultado["asignaciones"].keys()),
            "Monto (Bs)": list(resultado["asignaciones"].values()),
        })
        df["% del ingreso"] = (df["Monto (Bs)"] / ingreso_guardado * 100).round(1)
        st.dataframe(df, hide_index=True)

        fig = px.pie(df, values="Monto (Bs)", names="Categoría", title="Distribución del presupuesto")
        st.plotly_chart(fig)
        st.info(f"Alimentación disponible para M2: Bs {resultado['alimentacion']}")

# ── MÓDULO 2 ───────────────────────────────────────────────────────────────
elif pagina == "M2 - Comidas":
    st.title("M2 - Planificación de Comidas")
    st.markdown("**Tipo:** Programación Lineal (LP) | **Solver:** GLPK")
    st.markdown("---")

    if "presupuesto_alimentacion" not in st.session_state:
        st.warning("Primero debes resolver el M1.")
    else:
        presupuesto = st.session_state["presupuesto_alimentacion"]
        st.info(f"Presupuesto recibido del M1: Bs {presupuesto}")

        kcal_min     = st.number_input("Calorías mínimas/día", value=1800)
        kcal_max     = st.number_input("Calorías máximas/día", value=2000)
        proteina_min = st.number_input("Proteína mínima/día (g)", value=56)
        carbs_min    = st.number_input("Carbohidratos mínimos/día (g)", value=225)
        carbs_max    = st.number_input("Carbohidratos máximos/día (g)", value=290)
        grasa_min    = st.number_input("Grasas mínimas/día (g)", value=50)
        grasa_max    = st.number_input("Grasas máximas/día (g)", value=77)
        fibra_min    = st.number_input("Fibra mínima/día (g)", value=25)
        fibra_max    = st.number_input("Fibra máxima/día (g)", value=35)

        if st.button("Resolver"):
            if kcal_min >= kcal_max:
                st.error("Las calorías mínimas deben ser menores que las máximas.")
            elif carbs_min >= carbs_max:
                st.error("Los carbohidratos mínimos deben ser menores que los máximos.")
            elif grasa_min >= grasa_max:
                st.error("Las grasas mínimas deben ser menores que las máximas.")
            elif fibra_min >= fibra_max:
                st.error("La fibra mínima debe ser menor que la máxima.")
            else:
                resultado = resolver_comidas(
                    presupuesto, kcal_min, kcal_max,
                    proteina_min, carbs_min, carbs_max,
                    grasa_min, grasa_max, fibra_min, fibra_max
                )
                if resultado["estado"] == "optimo":
                    st.session_state["resultado_m2"] = resultado
                    st.session_state["kcal_cubierta"] = resultado["kcal_semanal"] / 7
                    st.session_state["proteina_cubierta"] = resultado["proteina_semanal"] / 7
                else:
                    st.error("No se encontró solución. Ajusta los requerimientos nutricionales.")

        # Mostrar resultado guardado
        if "resultado_m2" in st.session_state:
            resultado = st.session_state["resultado_m2"]
            st.success("¡Plan de comidas óptimo encontrado!")

            df = pd.DataFrame({
                "Alimento": list(resultado["plan"].keys()),
                "Porciones/semana (100g)": list(resultado["plan"].values()),
                "Gramos/semana": [round(v * 100, 0) for v in resultado["plan"].values()],
                "Gramos/día": [round(v * 100 / 7, 1) for v in resultado["plan"].values()],
            })
            st.dataframe(df, hide_index=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Costo semanal", f"Bs {resultado['costo_semanal']}")
            col2.metric("Calorías/semana", f"{resultado['kcal_semanal']} kcal")
            col3.metric("Proteína/semana", f"{resultado['proteina_semanal']} g")

            col4, col5, col6 = st.columns(3)
            col4.metric("Carbs/semana", f"{resultado['carbs_semanal']} g")
            col5.metric("Grasas/semana", f"{resultado['grasa_semanal']} g")
            col6.metric("Fibra/semana", f"{resultado['fibra_semanal']} g")

# ── MÓDULO 3 ───────────────────────────────────────────────────────────────
elif pagina == "M3 - Estudios":
    st.title("M3 - Calendario de Estudios")
    st.markdown("**Tipo:** Programación Entera Mixta (MILP) | **Solver:** GLPK")
    st.markdown("---")

    st.markdown("**Prioridades por materia** (0 = baja, 1 = alta)")
    prioridades = {}
    for m in MATERIAS:
        prioridades[m] = st.slider(m, 0.0, 1.0, 0.5, step=0.05, key=f"prio_{m}")

    st.markdown("**Bloques bloqueados** (clases, compromisos fijos)")
    st.caption("Selecciona los bloques en los que NO puedes estudiar")

    bloques_bloqueados = []
    for d in DIAS:
        cols = st.columns(4)
        for i, b in enumerate(BLOQUES):
            with cols[i]:
                if st.checkbox(f"{d} B{b}", key=f"block_{d}_{b}"):
                    bloques_bloqueados.append((d, b))

    max_bloques_dia = st.slider("Máximo de bloques de estudio por día", 1, 4, 3)

    if st.button("Resolver", key="resolver_m3"):
        # Validando que no se bloqueen todos lo bloques
        if len(bloques_bloqueados) >= len(DIAS) * len(BLOQUES):
            st.error("No puedes bloquear todos los bloques.")
            st.stop()
        else: 
            resultado = resolver_estudios(bloques_bloqueados, prioridades, max_bloques_dia=max_bloques_dia)
            if resultado["estado"] == "optimo":
                st.session_state["resultado_m3"] = resultado
                st.session_state["bloques_libres"] = resultado["bloques_libres"]
            else:
                st.error("No se encontró solución. Reduce los bloques bloqueados o el mínimo de horas.")

    # Mostrar resultado guardado
    if "resultado_m3" in st.session_state:
        resultado = st.session_state["resultado_m3"]
        st.success("¡Calendario óptimo generado!")

        st.markdown("### Calendario semanal")
        filas = []
        for d in DIAS:
            fila = {"Día": d}
            for b in BLOQUES:
                materia = resultado["calendario"][d][b]
                fila[f"Bloque {b}"] = materia if materia else "—"
            filas.append(fila)
        df_cal = pd.DataFrame(filas)
        st.dataframe(df_cal, hide_index=True, use_container_width=True)

        st.markdown("### Horas por materia")
        df_horas = pd.DataFrame({
            "Materia": list(resultado["horas_por_materia"].keys()),
            "Horas/semana": list(resultado["horas_por_materia"].values()),
        })
        st.dataframe(df_horas, hide_index=True)
        st.info("Bloques libres guardados para el M4.")

# ── MÓDULO 4 ───────────────────────────────────────────────────────────────
elif pagina == "M4 - Bienestar":
    st.title("M4 - Bienestar Estudiantil")
    st.markdown("**Tipo:** Programación No Lineal Entera Mixta (MINLP) | **Solver:** IPOPT")
    st.markdown("---")

    if "presupuesto_bienestar" not in st.session_state:
        st.warning("Primero debes resolver el M1.")
    elif "bloques_libres" not in st.session_state:
        st.warning("Primero debes resolver el M3.")
    else:
        presupuesto = st.session_state["presupuesto_bienestar"]
        bloques_libres = st.session_state["bloques_libres"]
        horas_libres = sum(bloques_libres.values()) * 2

        st.info(f"Presupuesto de bienestar del M1: Bs {presupuesto}")
        st.info(f"Horas libres disponibles del M3: {horas_libres} horas")

        st.markdown("**Importancia de cada ítem** (0 = baja, 1 = alta)")
        pesos = {}
        for item in ITEMS:
            pesos[item] = st.slider(item, 0.0, 1.0, 0.5, step=0.05, key=f"peso_{item}")

        if st.button("Resolver", key="resolver_m4"):
            # Validando que el presupuesto para el bienestar no sea menor o igual a cero
            if presupuesto <= 0:
                st.error("El presupuesto de bienestar es 0. Ajusta las prioridades en el M1.")
                st.stop()
            else:
                resultado = resolver_bienestar(presupuesto, bloques_libres, pesos)
                if resultado["estado"] == "optimo":
                    st.session_state["resultado_m4"] = resultado
                else:
                    st.error("No se encontró solución. Verifica el presupuesto disponible.")

        # Mostrar resultado guardado
        if "resultado_m4" in st.session_state:
            resultado = st.session_state["resultado_m4"]
            st.success("¡Plan de bienestar óptimo encontrado!")

            filas = []
            for item, datos in resultado["seleccionados"].items():
                filas.append({
                    "Ítem": item,
                    "Gasto (Bs)": datos["gasto_bs"],
                    "Utilidad": datos["utilidad"],
                })
            df = pd.DataFrame(filas)
            st.dataframe(df, hide_index=True)

            col1, col2 = st.columns(2)
            col1.metric("Gasto total", f"Bs {resultado['gasto_total']}")
            col2.metric("Utilidad total", resultado["utilidad_total"])

# ── RESUMEN ────────────────────────────────────────────────────────────────
elif pagina == "Resumen":
    st.title("📊 Resumen del Sistema")
    st.markdown("---")

    m1_listo = "resultado_m1" in st.session_state
    m2_listo = "resultado_m2" in st.session_state
    m3_listo = "resultado_m3" in st.session_state
    m4_listo = "resultado_m4" in st.session_state

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("M1 Presupuesto", "✅ Resuelto" if m1_listo else "⬜ Pendiente")
    col2.metric("M2 Comidas", "✅ Resuelto" if m2_listo else "⬜ Pendiente")
    col3.metric("M3 Estudios", "✅ Resuelto" if m3_listo else "⬜ Pendiente")
    col4.metric("M4 Bienestar", "✅ Resuelto" if m4_listo else "⬜ Pendiente")

    st.markdown("---")

    if not any([m1_listo, m2_listo, m3_listo, m4_listo]):
        st.warning("Resuelve los módulos en orden para ver el resumen aquí.")
    else:
        if m1_listo:
            st.markdown("### M1 — Presupuesto Mensual")
            r1 = st.session_state["resultado_m1"]
            df1 = pd.DataFrame({
                "Categoría": list(r1["asignaciones"].keys()),
                "Monto (Bs)": list(r1["asignaciones"].values()),
            })
            st.dataframe(df1, hide_index=True)

        if m2_listo:
            st.markdown("### M2 — Plan de Comidas")
            r2 = st.session_state["resultado_m2"]
            col1, col2, col3 = st.columns(3)
            col1.metric("Costo semanal", f"Bs {r2['costo_semanal']}")
            col2.metric("Calorías/semana", f"{r2['kcal_semanal']} kcal")
            col3.metric("Proteína/semana", f"{r2['proteina_semanal']} g")

        if m3_listo:
            st.markdown("### M3 — Calendario de Estudios")
            r3 = st.session_state["resultado_m3"]
            df3 = pd.DataFrame({
                "Materia": list(r3["horas_por_materia"].keys()),
                "Horas/semana": list(r3["horas_por_materia"].values()),
            })
            st.dataframe(df3, hide_index=True)

        if m4_listo:
            st.markdown("### M4 — Plan de Bienestar")
            r4 = st.session_state["resultado_m4"]
            col1, col2 = st.columns(2)
            col1.metric("Gasto total", f"Bs {r4['gasto_total']}")
            col2.metric("Utilidad total", r4["utilidad_total"])