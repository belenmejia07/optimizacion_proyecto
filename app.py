import streamlit as st
from modules.modulo1_presupuesto import resolver_presupuesto, CATEGORIAS
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
    st.write("Módulo en construcción")

elif pagina == "M3 - Estudios":
    st.title("M3 - Calendario de Estudios")
    st.write("Módulo en construcción")

elif pagina == "M4 - Bienestar":
    st.title("M4 - Bienestar Estudiantil")
    st.write("Módulo en construcción")

elif pagina == "Resumen":
    st.title("Resumen del Sistema")
    st.write("Módulo en construcción")