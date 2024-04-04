import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chile Map Dashboard", page_icon="🌎", layout="wide")

# Cargar los datos de GeoJSON para el mapa
geojson_url = "https://raw.githubusercontent.com/LuisEgus/chile-json/main/cl.json"
chile_geojson = requests.get(geojson_url).json()

# Cargar los datos del archivo Excel
df = pd.read_excel(r'C:\Users\Admin\Desktop\QLAB\Streamlit\data CHILE\data provincias.xlsx')

# Reemplazar '.' por NaN y ',' por nada en la columna 'num. obsev.' y luego convertir a flotante
df['num. obsev.'] = df['num. obsev.'].replace({',': '', '.': 'NaN'}, regex=True)
df['num. obsev.'] = pd.to_numeric(df['num. obsev.'], errors='coerce')

# Sidebar - Selección de tipo de test y variable a visualizar
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type_id = st.selectbox('Select Test Type', df['test_type_ID'].unique())
    variable = st.selectbox('Select Variable', ['beta_robust', 'p-value', 'num. obsev.'])

# Filtrar los datos basados en el tipo de test seleccionado
df_filtered = df[df['test_type_ID'] == test_type_id]

# Visualizar el mapa coroplético de Chile sin datos
st.title('Mapa Coroplético de Chile')
fig_chile = px.choropleth_mapbox(geojson=chile_geojson, locations=[],
                                 center={"lat": -35.6751, "lon": -71.5430},
                                 mapbox_style="carto-positron", zoom=3)
fig_chile.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
st.plotly_chart(fig_chile, use_container_width=True)

# Visualizar el gráfico de calor
st.title('Heatmap de Datos')
fig_heatmap = px.density_heatmap(df_filtered, x='sector', y='test_type_ID', z=variable, 
                                 histfunc="sum", title="Heatmap", nbinsx=20)
fig_heatmap.update_layout(margin={"r":0, "t":30, "l":0, "b":0})
st.plotly_chart(fig_heatmap, use_container_width=True)