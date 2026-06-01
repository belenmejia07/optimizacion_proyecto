import streamlit as st
from modules.modulo1_presupuesto import resolver_presupuesto, CATEGORIAS
from modules.modulo2_comidas import resolver_comidas
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="OptiVida", layout="wide")

# Navegación en el sidebar
st.sidebar.title("OptiVida")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Módulos",
    ["Inicio", "M1 - Presupuesto", "M2 - Comidas", "M3 - Estudios", "M4 - Bienestar", "Resumen"]
)

# Mostrar página según selección
if pagina == "Inicio":
    st.title("Sistema de Optimización de Vida Estudiantil")
    st.write("Selecciona un módulo en el menú lateral para comenzar.")

elif pagina == "M1 - Presupuesto":
    st.title("M1 - Presupuesto Mensual")
    st.markdown("**Tipo:** Programación Lineal (LP) | **Solver:** GLPK")
    st.markdown("---")

    # Entradas
    ingreso = st.number_input("Ingreso mensual (Bs)", min_value=500.0, value=3000.0, step=100.0)

    st.markdown("**Prioridades por categoría** (0 = baja, 1 = alta)")
    prioridades = {}
    for cat in CATEGORIAS:
        prioridades[cat] = st.slider(cat, 0.0, 1.0, 0.5, step=0.05)

    if st.button("Resolver"):
        resultado = resolver_presupuesto(ingreso, prioridades)

        if resultado["estado"] == "optimo":
            st.success("¡Solución óptima encontrada!")
    
            # Tabla de resultados
            df = pd.DataFrame({
                "Categoría": list(resultado["asignaciones"].keys()),
                "Monto (Bs)": list(resultado["asignaciones"].values()),
            })
            df["% del ingreso"] = (df["Monto (Bs)"] / ingreso * 100).round(1)
            st.dataframe(df, hide_index=True)

            # Gráfico de torta
            fig = px.pie(
                df,
                values="Monto (Bs)",
                names="Categoría",
                title="Distribución del presupuesto"
            )
            st.plotly_chart(fig)

            # Guardar datos para módulos siguientes
            st.session_state["presupuesto_alimentacion"] = resultado["alimentacion"]
            st.session_state["presupuesto_bienestar"] = resultado["bienestar"]
            st.info(f"Alimentación disponible para M2: Bs {resultado['alimentacion']}")
        else:
            st.error("El modelo no tiene solución.")

elif pagina == "M2 - Comidas":
    st.title("M2 - Planificación de Comidas")
    st.markdown("**Tipo:** Programación Lineal (LP) | **Solver:** GLPK")
    st.markdown("---")

    if "presupuesto_alimentacion" not in st.session_state:
        st.warning("Primero debes resolver el M1 para obtener el presupuesto de alimentación.")
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
            resultado = resolver_comidas(
            presupuesto, kcal_min, kcal_max,
            proteina_min, carbs_min, carbs_max,
            grasa_min, grasa_max, fibra_min, fibra_max
            )

            if resultado["estado"] == "optimo":
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

                st.session_state["kcal_cubierta"] = resultado["kcal_semanal"] / 7
                st.session_state["proteina_cubierta"] = resultado["proteina_semanal"] / 7

            else:
                st.error("No se encontró solución. Ajusta los requerimientos nutricionales.")

elif pagina == "M3 - Estudios":
    st.title("M3 - Calendario de Estudios")
    st.write("Módulo en construcción")

elif pagina == "M4 - Bienestar":
    st.title("M4 - Bienestar Estudiantil")
    st.write("Módulo en construcción")

elif pagina == "Resumen":
    st.title("Resumen del Sistema")
    st.write("Módulo en construcción")