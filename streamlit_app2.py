import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
import plotly.graph_objects as go

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chile Map Dashboard", page_icon="🌎", layout="wide")

# Función para cargar datos desde una URL de archivo raw de GitHub
def load_data(url):
    response = requests.get(url)
    csv_raw = StringIO(response.text)
    return pd.read_csv(csv_raw)

# Cargar datos (raw-github)
geojson_url = 'https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson'
chile_geojson = requests.get(geojson_url).json()
region_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/region_summary1.csv'
sector_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/sector_summary.csv'
industry_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/industry_summary.csv'
buyer_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/buyer_summary.csv'

# Cargar los dataset como dataframe
df_region = load_data(region_summary_url)
df_sector = load_data(sector_summary_url)
df_industry = load_data(industry_summary_url)
df_buyer = load_data(buyer_summary_url)

# Sidebar - Selección de tipo de test
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type = st.selectbox('Select Test Type', df_region['test_type'].unique())
    sector = st.sidebar.selectbox('Select Sector', df_buyer['sector'].unique())
    

color_theme = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']

# Filtrar datos
df_filtered = df_region[df_region['test_type'] == test_type].fillna(0)
df_sector_filtered = df_sector[df_sector['test_type'] == test_type].fillna(0)
df_industry_filtered = df_industry[df_industry['test_type'] == test_type].fillna(0)
df_buyer_filtered = df_buyer[(df_buyer['test_type'] == test_type) & (df_buyer['sector'] == sector)]

# Función para crear un mapa coroplético con escala de colores dinámica
def create_choropleth(df, color_theme):
    min_val, max_val = df['beta_robust'].min(), df['beta_robust'].max()
    
    # Usar una escala de colores de Plotly, y crear una personalizada para el valor 0
    colorscale = px.colors.diverging.RdBu
    if min_val >= 0:
        colorscale = [[0, "white"], [1, colorscale[-1]]]
    elif max_val <= 0:
        colorscale = [[0, colorscale[0]], [1, "white"]]
    else:  
        zero_norm = abs(min_val) / (max_val - min_val)
        colorscale = [[0, colorscale[0]], [zero_norm, "white"], [1, colorscale[-1]]]

    fig = go.Figure(go.Choropleth(
        geojson=chile_geojson,
        locations=df['codregion'],
        z=df['beta_robust'],
        colorscale=colorscale,
        featureidkey="properties.codregion",
        text=df.apply(lambda row: f"Beta Robust: {row['beta_robust']}<br>p-value: {row['p_value']}<br>Num. Obsev.: {row['num_observ']}", axis=1),
        hoverinfo="text",
        marker_line_color='black',
        marker_line_width=0.5
    ))

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        showland=False,
        showocean=False,
        projection_type="mercator",
        center={"lat": -35.6751, "lon": -71.543}
    )

    fig.update_layout(
        margin={"r":0, "t":0, "l":0, "b":0},
        height=500

    )
    return fig

# Crear el gráfico de mapa coroplético
fig_chile1 = create_choropleth(df_filtered, color_theme)
fig_chile2 = create_choropleth(df_filtered, color_theme)

# Función auxiliar para construir una escala de colores que mapea 0 a blanco
def build_colorscale(min_val, max_val, color_theme):
    if min_val < 0 and max_val > 0:
        scale = [
            [0, px.colors.diverging.RdBu[0]],
            [abs(min_val) / (abs(min_val) + max_val), "white"],
            [1, px.colors.diverging.RdBu[-1]]
        ]
    elif max_val <= 0:
        scale = [[0, px.colors.diverging.RdBu[0]], [1, "white"]]
    else:
        scale = [[0, "white"], [1, px.colors.diverging.RdBu[-1]]]
    return scale

# Crear un gráfico de vector de calor para los sectores
colorscale_sector = build_colorscale(df_sector_filtered['beta_robust'].min(), df_sector_filtered['beta_robust'].max(), color_theme)
fig_heatmap = px.density_heatmap(
    df_sector_filtered,
    x='test_type',
    y='sector',
    z='beta_robust',
    color_continuous_scale=colorscale_sector,
    labels={'beta_robust': 'Beta Robust', 'p_value': 'P-Value', 'num_observ': 'Number of Observations'},
    title='Vector of sectors'
)
# Modificar la altura del gráfico de vector de calor para los sectores
fig_heatmap.update_layout(
    height=500,  # Ajusta esto a la altura deseada
    # width=800,  # Descomenta y ajusta esto si también quieres cambiar el ancho
)

# Creación de la matriz de calor para la industria
colorscale_industry = build_colorscale(df_industry_filtered['beta_robust'].min(), df_industry_filtered['beta_robust'].max(), color_theme)
fig_heatmap_industry = px.density_heatmap(
    df_industry_filtered,
    x='rubro3',
    y='zone',
    z='beta_robust',
    color_continuous_scale=colorscale_industry,
    title='Matrix of macrozones'
)
fig_heatmap_industry.update_traces(
    hovertemplate='<b>%{x}</b><br>%{y}<br>Beta Robust: %{z:.2f}<br>P-value: %{customdata[0]:.2f}<br>Num. Observ: %{customdata[1]:.0f}',
    customdata=df_industry_filtered[['p_value', 'num_observ']].values
)
fig_heatmap_industry.update_layout(height=600, margin={"r":0, "t":50, "l":0, "b":100})

# Modificar la altura de la matriz de calor para la industria
fig_heatmap_industry.update_layout(
    height=700,  # Ajusta esto a la altura deseada
    # width=800,  # Descomenta y ajusta esto si también quieres cambiar el ancho
    margin={"r":0, "t":50, "l":0, "b":100}
)

# Crear el gráfico de barras para Buyer Summary filtrado
colorscale_bar = build_colorscale(df_buyer_filtered['beta_robust'].min(), df_buyer_filtered['beta_robust'].max(), color_theme)
fig_bar = px.bar(
    df_buyer_filtered,
    x='rutunidadcompra',
    y='beta_robust',
    color='beta_robust',  # Asegurarse de que la barra se coloree basada en 'beta_robust'
    color_continuous_scale=colorscale_bar,  # Usar la escala de colores personalizada
    title='Bar Chart of Buyers',
    labels={'rutunidadcompra': 'Buyer', 'beta_robust': 'Beta Robust'},
    hover_data=['p_value', 'num_observ']
)
fig_bar.update_layout(
    margin={"r":0, "t":50, "l":0, "b":0},
    height=500,
    coloraxis_colorbar={
        'title':'Beta Robust'
    }
)

# Distribución de gráficos en el dashboard
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.plotly_chart(fig_chile1, use_container_width=True)
with col2:
    st.plotly_chart(fig_chile2, use_container_width=True)
with col3:
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Mostrar el gráfico de barras y el mapa de calor de la industria
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_heatmap_industry, use_container_width=True)