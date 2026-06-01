# OptiVida - Sistema de Optimizacion de Vida Estudiantil

Proyecto Final | Materia: Optimizacion | UCB - Semestre 3

## Descripcion

OptiVida es un sistema de 4 modulos de optimizacion interconectados
que optimizan la vida estudiantil mensual de forma integral.
Cada modulo recibe datos del anterior formando un flujo coherente de decisiones optimizadas

## Que problema resuelve esto?

En vista de que a muchos estudiantes les cuesta organizarse para estudiar, hacer tareas, comer saludable y con los nutrientes que se necesitan para rendir de manera optima en los etudios, como tambien tener un tiempo para recrearse, relajarse y tener bien claras sus prioridades, se creo este proyecto con el proposito de ayudar a esos estudiantes.

## Modulos

| Modulo | Tipo | Solver | Descripcion |
|--------|------|--------|-------------|
| M1 - Presupuesto | LP | GLPK | Maximiza utilidad al distribuir ingreso mensual |
| M2 - Comidas | LP | GLPK | Minimiza costo semanal respetando nutricion |
| M3 - Estudios | MILP | GLPK | Asigna bloques de estudio con variables binarias |
| M4 - Bienestar | NLP | IPOPT | Maximiza utilidad con rendimiento marginal decreciente |

## Flujo de datos

M1 --> presupuesto_alimentacion --> M2

M1 --> presupuesto_bienestar    --> M4

M3 --> bloques_libres           --> M4

## Requisitos

- Python 3.11
- Conda (Miniconda o Anaconda)

## Instalacion

1. Clonar el repositorio:
git clone https://github.com/belenmejia07/optimizacion_proyecto.git

2. Crear y activar el entorno conda:
conda create -n pro_fin_ev_op python=3.11
conda activate pro_fin_ev_op

3. Instalar dependencias:
conda install -c conda-forge pyomo glpk ipopt streamlit pandas plotly

## Ejecucion

Con el entorno activo, ejecutar: streamlit run app.py

La app abre en http://localhost:8501

## Uso

1. Ejecutar M1 - ingresar ingreso mensual y prioridades
2. Ejecutar M2 - ajustar requerimientos nutricionales
3. Ejecutar M3 - configurar materias y bloques bloqueados
4. Ejecutar M4 - ajustar importancia de items de bienestar
5. Ver Resumen - ver resultados integrados de todos los modulos

## Estructura del proyecto
```
pro_final/
├── app.py                      # App principal Streamlit
├── README.md
├── requirements.txt
├── data/
│   └── alimentos.csv           # 20 alimentos con macros y precios en Bs
├── modules/
│   ├── modulo1_presupuesto.py  # LP
│   ├── modulo2_comidas.py      # LP
│   ├── modulo3_estudios.py     # MILP
│   └── modulo4_bienestar.py    # NLP
```
## Tecnologias

- Pyomo: modelado de optimizacion
- GLPK: solver LP y MILP
- IPOPT: solver NLP
- Streamlit: interfaz web
- Pandas: manejo de datos
- Plotly: visualizaciones