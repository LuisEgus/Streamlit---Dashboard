import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chile Map Dashboard", page_icon="🌎", layout="wide")

# Función para cargar datos desde una URL de archivo raw de GitHub
def load_data(url):
    response = requests.get(url)
    csv_raw = StringIO(response.text)
    return pd.read_csv(csv_raw)

# Cargar los datos de GeoJSON para el mapa de las regiones de Chile
geojson_url = 'https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson'
chile_geojson = requests.get(geojson_url).json()

# Cargar datos para el mapa coroplético
region_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/region_summary.csv'
df_region = load_data(region_summary_url)

# Cargar datos para el vector de calor
sector_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/sector_summary.csv'
df_sector = load_data(sector_summary_url)

# Cargar datos para industria
df_industry = load_data('https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/industry_summary.csv')


# Sidebar - Selección de tipo de test
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type = st.selectbox('Select Test Type', df_region['test_type'].unique())
    color_theme = st.selectbox('Select Color Theme', ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis'])

# Filtrar los datos basados en el tipo de test seleccionado
df_filtered = df_region[df_region['test_type'] == test_type]
df_sector_filtered = df_sector[df_sector['test_type'] == test_type]
df_industry_filtered = df_industry[df_industry['test_type'] == test_type]

# Asegurarse de que no haya valores NaN que puedan afectar la visualización
df_filtered['beta_robust'].fillna(0, inplace=True)
df_filtered['p_value'].fillna(1, inplace=True)  # Puede elegir otro valor por defecto que tenga sentido en su contexto
df_filtered['num_observ'].fillna(0, inplace=True)

# Crear un mapa coroplético centrado en Chile
fig_chile = px.choropleth(df_filtered,
                          geojson=chile_geojson,
                          locations='codregion',
                          color='beta_robust',
                          featureidkey="properties.codregion",
                          hover_data={'beta_robust': True, 'p_value': True, 'num_observ': True}
                         )

fig_chile.update_geos(
    fitbounds="locations",
    visible=True,
    showcountries=False,
    showcoastlines=False,
    showland=False,
    showocean=False,
    center={"lat": -35.6751, "lon": -71.543},
    projection_scale=5  # Ajustar para mejorar el ajuste al área geográfica de Chile
)

fig_chile.update_layout(
    margin={"r":0, "t":0, "l":0, "b":0},
    height=600
)

fig_chile.update_traces(marker_line_color='black', marker_line_width=1)

# Crear un gráfico de vector de calor para los sectores
fig_heatmap = px.density_heatmap(df_sector_filtered,
                                 x='sector',
                                 y='test_type',
                                 z='beta_robust',
                                 hover_data=['beta_robust', 'p_value', 'num_observ'],
                                 labels={'beta_robust':'Beta Robust', 'p_value':'P-Value', 'num_observ':'Number of Observations'},
                                 title='Heatmap de Sectores')


# Creación de la matriz de calor para la industria
fig_heatmap_industry = px.density_heatmap(
    df_industry_filtered,
    x='rubro3', 
    y='zone', 
    z='beta_robust', 
    color_continuous_scale=color_theme, 
    title='Heatmap de Industrias',
    hover_data={'beta_robust': ':.2f', 'p_value': ':.2f', 'num_observ': ':.0f'}
)

# Agregar etiquetas de datos con 'hover_data'
fig_heatmap_industry.update_traces(
    hovertemplate='<b>%{x}</b><br>%{y}<br>Beta Robust: %{z:.2f}<br>P-value: %{customdata[0]:.2f}<br>Num. Observ: %{customdata[1]:.0f}',
    customdata=df_industry_filtered[['p_value', 'num_observ']].values
)

# Actualizar estilos del gráfico de matriz de calor
fig_heatmap_industry.update_layout(
    margin={"r":0, "t":50, "l":0, "b":100},
    height=600,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

# Mostrar gráficos en el dashboard
st.plotly_chart(fig_chile, use_container_width=True)
st.plotly_chart(fig_heatmap, use_container_width=True)
st.plotly_chart(fig_heatmap_industry, use_container_width=True)