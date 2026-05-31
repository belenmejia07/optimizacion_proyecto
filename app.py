import streamlit as st
from modules.modulo1_presupuesto import resolver_presupuesto, CATEGORIAS

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
            st.dataframe(resultado["asignaciones"])
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