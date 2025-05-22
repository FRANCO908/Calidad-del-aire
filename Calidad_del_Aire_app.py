import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from skimage import io
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point

# Renderizar imagen y título en la barra lateral
Logo = io.imread(r"./Imagenes/ITESO_Logo.png")

#----- Renderizado del Texto --------------------------------------
st.title("Histórico de monitoreo de contaminantes atmosféricos en la ZMG  (1996 a 2023)")
st.markdown(":blue[La presente aplicación interactiva permite explorar bases de datos sobre "
                    "parámetros de contaminación atmosférica en la **Zona Metropolitana de Guadalajara** (Jalisco, México), abarcando "
                    "el periodo de 1996 a 2023. Mediante el uso de la **librería Pandas**, los registros históricos "
                    "fueron homogeneizados y unificados, lo que facilita su procesamiento y análisis eficiente. "
                    "Es importante señalar que los datos no han sido verificados, por lo que deben interpretarse "
                    "con precaución. Sin embargo, el objetivo principal es optimizar el acceso y manejo de información clave, "
                    "contribuyendo a la toma de decisiones fundamentadas y al diseño de políticas de calidad del aire "
                    "basadas en datos organizados y estructurados.]")

st.divider()

#------------------------------------------------------------------
#----- Configuración de los Elementos del DashBoard ---------------
#------------------------------------------------------------------

#----- Renderizado de la Imagen y el Título en el Dashboard -------
st.sidebar.image(Logo, width = 200)
st.sidebar.markdown("## MENÚ DE CONFIGURACIÓN")
st.sidebar.divider()

# Selección de Año
vars_year = ['1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007',
             '2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019',
             '2020','2021','2022','2023']
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
default_para = vars_para.index('PM10')
para_selected = st.sidebar.selectbox('Elección del parámetro de medición:', vars_para, index = default_para)

#------------------------------------------------------------------
#----- Configuración de elementos del Panel Central ---------------
#------------------------------------------------------------------

#Definición de las columnas
colum_1, colum_2 = st.columns(2)

# Cargar el CSV con las estaciones
data = pd.read_csv("./Datos/Estaciones.csv")

# Crear GeoDataFrame con puntos
gdf = gpd.GeoDataFrame(
      data,
      geometry=gpd.points_from_xy(data["Longitud"], data["Latitud"]),
      crs="EPSG:4326"
      )

# Convertir a proyección métrica para calcular buffer en metros
gdf_meters = gdf.to_crs(epsg=6372)
gdf["buffer"] = gdf_meters.buffer(gdf["Representatividad (km)"] * 1000).to_crs(epsg=4326)

# Crear mapa base
center = [gdf["Latitud"].mean(), gdf["Longitud"].mean()]
m = folium.Map(location=center, zoom_start=11)

# Dibujar círculos de representatividad
for _, row in gdf.iterrows():
  folium.GeoJson(
    row["buffer"],
    style_function=lambda x: {
      "fillColor": "blue",
      "color": "blue",
                "weight": 1,
                "fillOpacity": 0.1,
                            }
                            ).add_to(m)

# Marcadores con popup de información
for _, row in gdf.iterrows():
    popup_text = (
        f"<b>Estación:</b> {row['Estación']}<br>"
        f"<b>Clave:</b> {row['CLAVE_EST']}<br>"
        f"<b>Altitud:</b> {row['Altitud (msnm)']} msnm<br>"
        f"<b>Año de instalación:</b> {row['Año de instalación']}"
    )
    folium.Marker(
        location=[row["Latitud"], row["Longitud"]],
        popup=popup_text,
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)

colum_1.subheader('Mapa de Estaciones de Monitoreo:')

# Mostrar mapa en Streamlit
st_data = st_folium(m, width=600, height=400)
st.divider()

# Cargar los datos
df1 = pd.read_csv("./Datos/datos_parte_1.csv")
df2 = pd.read_csv("./Datos/datos_parte_2.csv")
df3 = pd.read_csv("./Datos/datos_parte_3.csv")
df4 = pd.read_csv("./Datos/datos_parte_4.csv")
df5 = pd.read_csv("./Datos/datos_parte_5.csv")
df6 = pd.read_csv("./Datos/datos_parte_6.csv")
df7 = pd.read_csv("./Datos/datos_parte_7.csv")
df8 = pd.read_csv("./Datos/datos_parte_8.csv")

# Concatenar los DataFrames en uno solo
df_final = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8], ignore_index=True)

# Convertir "FECHA" a datetime si es necesario
df_final['FECHA'] = pd.to_datetime(df_final['FECHA'], errors='coerce')

st.markdown(":blue[El **DataFrame** es el siguiente:]")

#----- Renderizado del DataFrame ----------------------------------
st.dataframe(df_final.head(5000))
st.divider()

# Filtrar datos según selección
df_filtrado = df_final[
    (df_final['CLAVE_EST'] == est_selected) & 
    (df_final['FECHA'].dt.year == int(year_selected))
].copy()

# st.dataframe(df_filtrado)
# st.divider()

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

st.markdown(":blue[Utilice el siguiente gráfico modificable para explorar los datos fácilmente, " 
                  "seleccionando estación de monitoreo, año y contaminante o parámetro de interés desde el Menú de configuración.]")

# Mostrar el gráfico en Streamlit
st.pyplot(fig)
st.divider()
