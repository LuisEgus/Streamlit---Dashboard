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

# Cargar datos (raw-github)
geojson_url = 'https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson'
chile_geojson = requests.get(geojson_url).json()
region_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/region_summary.csv'
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
    color_theme = st.selectbox('Select Color Theme', ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis'])

# Filtrar datos
df_filtered = df_region[df_region['test_type'] == test_type].fillna(0)
df_sector_filtered = df_sector[df_sector['test_type'] == test_type].fillna(0)
df_industry_filtered = df_industry[df_industry['test_type'] == test_type].fillna(0)
df_buyer_filtered = df_buyer[(df_buyer['test_type'] == test_type) & (df_buyer['sector'] == sector)]

# Crear un mapa coroplético centrado en Chile
def create_choropleth(df):
    
    fig = px.choropleth(df,
                        geojson=chile_geojson,
                        locations='codregion',
                        color='beta_robust',
                        color_continuous_scale=color_theme,
                        featureidkey="properties.codregion",
                        hover_data={'beta_robust': True, 'p_value': True, 'num_observ': True}
                       )
    fig.update_geos(
        fitbounds="locations",
        visible=True,
        showcountries=True,
        showcoastlines=False,
        showland=False,
        showocean=False,
        center={"lat": -35.6751, "lon": -71.543}
        # Elimina la línea de 'projection': {"type": "mercator"}
    )
    fig.update_layout(
        margin={"r":0, "t":0, "l":0, "b":0},  # Reduce los márgenes si es necesario
        height=800  # Ajusta la altura para aumentar la longitud del mapa
    )
    fig.update_traces(marker_line_color='black', marker_line_width=0.5)  # Puedes ajustar el grosor de las líneas aquí
    return fig

fig_chile1 = create_choropleth(df_filtered)
fig_chile2 = create_choropleth(df_filtered)


fig_chile1 = create_choropleth(df_filtered)
fig_chile2 = create_choropleth(df_filtered)

# Crear un gráfico de vector de calor para los sectores
fig_heatmap = px.density_heatmap(df_sector_filtered,
                                 x='test_type',
                                 y='sector',
                                 z='beta_robust',
                                 color_continuous_scale=color_theme,
                                 labels={'beta_robust':'Beta Robust', 'p_value':'P-Value', 'num_observ':'Number of Observations'},
                                 title='Vector of sectors'
                                 )

# Creación de la matriz de calor para la industria
fig_heatmap_industry = px.density_heatmap(df_industry_filtered,
                                          x='rubro3', 
                                          y='zone', 
                                          z='beta_robust', 
                                          color_continuous_scale=color_theme,
                                          title='Matrix of macrozones'
                                         )
fig_heatmap_industry.update_traces(hovertemplate='<b>%{x}</b><br>%{y}<br>Beta Robust: %{z:.2f}<br>P-value: %{customdata[0]:.2f}<br>Num. Observ: %{customdata[1]:.0f}',
                                   customdata=df_industry_filtered[['p_value', 'num_observ']].values)
fig_heatmap_industry.update_layout(height=600, margin={"r":0, "t":50, "l":0, "b":100})


# Crear el gráfico de barras para Buyer Summary filtrado
fig_bar = px.bar(
    df_buyer_filtered,
    x='rutunidadcompra',  # Asumiendo que 'rutunidadcompra' es la columna correcta para los compradores
    y='beta_robust',
    title='Bar Chart of Buyers',
    labels={'rutunidadcompra': 'Buyer', 'beta_robust': 'Beta Robust'},
    hover_data=['p_value', 'num_observ']  # Agregar más datos al hover
)

# Ajustar los estilos del gráfico de barras
fig_bar.update_layout(
    margin={"r":0, "t":50, "l":0, "b":0},
    height=400
)


# Distribución de gráficos en el dashboard
col1, col2, col3 = st.columns([1, 1, 1])  # Ajusta las proporciones si es necesario

with col1:
    st.plotly_chart(fig_chile1, use_container_width=True)

with col2:
    st.plotly_chart(fig_chile2, use_container_width=True)

with col3:
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.plotly_chart(fig_heatmap_industry, use_container_width=True)

# Mostrar el gráfico de barras debajo de los otros gráficos
st.plotly_chart(fig_bar, use_container_width=True)