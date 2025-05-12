import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from skimage import io

# Renderizar imagen y título en la barra lateral
Logo = io.imread(r"./Imagenes/ITESO_Logo.png")
st.sidebar.markdown("## MENÚ DE CONFIGURACIÓN")
st.sidebar.divider()

#------------------------------------------------------------------
#----- Configuración de los Elementos del DashBoard ---------------
#------------------------------------------------------------------

#----- Renderizado de la Imagen y el Título en el Dashboard -------
st.sidebar.image(Logo, width = 200)
st.sidebar.markdown("## MENÚ DE CONFIGURACIÓN")
st.sidebar.divider()

# Selección de Año
vars_year = list(range(1996, 2024))  
default_year = vars_year.index('2020')
year_selected = st.sidebar.selectbox('Elección del Año de monitoreo:', vars_year, index = default_year)
st.sidebar.divider()

# Selección de Estación
vars_est = ['AGU','ATM','CEN','LDO','MIR','OBL','PIN','SFE','TLA','VAL']
default_est = vars_est.index('OBL')
est_selected = st.sidebar.selectbox('Elección de estación de monitoreo:', vars_est, index = default_est)
st.sidebar.divider()

# Selección de Parámetro
vars_para = ['O3', 'NO2', 'NO','NOX', 'CO', 'SO2', 'PM10', 'PM2.5', 'TMP', 'TMPI', 'RH', 'PP', 
             'WS', 'WD', 'RS', 'PBA','UV', 'UVI']
default_para = vars_year.index('2020')
para_selected = st.sidebar.selectbox('Elección del parámetro de medición:', vars_para, index = default_para)

#------------------------------------------------------------------
#----- Configuración de Texto y Elementos del Panel Central -------
#------------------------------------------------------------------

# Cargar los datos
df1 = pd.read_csv("./Archivos/Datos/datos_parte_1.csv")
df2 = pd.read_csv("./Archivos/Datos/datos_parte_2.csv")
df3 = pd.read_csv("./Archivos/Datos/datos_parte_3.csv")
df4 = pd.read_csv("./Archivos/Datos/datos_parte_4.csv")
df5 = pd.read_csv("./Archivos/Datos/datos_parte_5.csv")
df6 = pd.read_csv("./Archivos/Datos/datos_parte_6.csv")
df7 = pd.read_csv("./Archivos/Datos/datos_parte_7.csv")
df8 = pd.read_csv("./Archivos/Datos/datos_parte_8.csv")

# Concatenar los DataFrames en uno solo
df_final = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8], ignore_index=True)

# Convertir "FECHA" a datetime si es necesario
df_final['FECHA'] = pd.to_datetime(df_final['FECHA'], errors='coerce')

st.markdown(":violet[El **DataFrame** es el siguiente:]")

#----- Renderizado del DataFrame ----------------------------------
st.dataframe(df_final)
st.divider()

# Filtrar datos según selección
df_filtrado = df_final[
    (df_final['CLAVE_EST'] == est_selected) & 
    (df_final['FECHA'].dt.year == year_selected)
]

# Calcular el promedio mensual
df_filtrado['AÑO-MES'] = df_filtrado['FECHA'].dt.to_period("M")
df_promedio_mensual = df_filtrado.groupby('AÑO-MES')[para_selected].mean().reset_index()

# Crear gráfico en Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_promedio_mensual['AÑO-MES'].astype(str), df_promedio_mensual[para_selected], marker='o', linestyle='-', color='b')

# Personalizar gráfico
ax.set_title(f'Promedio mensual de {para_selected} en {est_selected} ({year_selected})')
ax.set_xlabel('Fecha (Año-Mes)')
ax.set_ylabel(f'Promedio de {para_selected}')
ax.grid()
plt.xticks(rotation=45)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)
st.divider()
