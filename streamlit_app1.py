import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chile Map Dashboard", page_icon="🌎", layout="wide")

# Cargar los datos de GeoJSON para el mapa de las regiones de Chile
geojson_url = 'https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson'
chile_geojson = requests.get(geojson_url).json()

# Cargar los datos del archivo Excel
df = pd.read_excel(r'D:\Users\u_sociales\Documents\GitHub\Streamlit---Dashboard\data CHILE\dta\region_summary.xlsx')

# Reemplazar '.' por NaN y ',' por nada en la columna 'num. obsev.' y luego convertir a flotante
df['num. obsev.'] = df['num. obsev.'].replace({',': '', '.': 'NaN'}, regex=True)
df['num. obsev.'] = pd.to_numeric(df['num. obsev.'], errors='coerce')

# Sidebar - Selección de tipo de test y variable a visualizar
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type = st.selectbox('Select Test Type', df['test_type'].unique())
    variable = st.selectbox('Select Variable', ['beta_robust', 'p-value', 'num. obsev.'])

# Filtrar los datos basados en el tipo de test seleccionado
df_filtered = df[df['test_type'] == test_type]

# Crear dos columnas para los gráficos
col1, col2 = st.columns([3, 2])  # Ajustar las proporciones para dar más espacio a la columna del mapa

# Visualizar el mapa coroplético en la columna de la izquierda
with col1:
    st.title('Mapa de las Regiones de Chile')
    fig_chile = px.choropleth(
        df_filtered,
        geojson=chile_geojson,
        locations='codregion',  # Asegúrate de que esta columna exista en df y coincida con los códigos de región
        color=variable,  # La variable seleccionada para visualizar
        featureidkey="properties.codregion"
    )
    fig_chile.update_geos(
        fitbounds="locations",
        visible=False,
        center={"lat": -38, "lon": -71},  # Centrar en Chile
        projection_scale=5  # Ajustar la escala si es necesario para mostrar todo el mapa
    )
    # Ajustar la altura del gráfico para acomodar la forma alargada de Chile
    fig_chile.update_layout(height=1200, margin={"r":0, "t":0, "l":0, "b":0})
    st.plotly_chart(fig_chile, use_container_width=True)

# Visualizar el gráfico de calor en la columna de la derecha
with col2:
    st.title('Heatmap de Datos')
    fig_heatmap = px.density_heatmap(
        df_filtered,
        x='sector', 
        y='test_type', 
        z=variable, 
        histfunc="sum",
        title="Heatmap"
    )
    fig_heatmap.update_layout(margin={"r":0, "t":30, "l":0, "b":0})
    st.plotly_chart(fig_heatmap, use_container_width=True)