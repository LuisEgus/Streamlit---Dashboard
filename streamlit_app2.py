import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
import plotly.graph_objects as go
import numpy as np

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chile Map Dashboard", page_icon="🌎", layout="wide")

# Función para cargar datos desde una URL de archivo raw de GitHub
def load_data(url):
    response = requests.get(url)
    csv_raw = StringIO(response.text)
    return pd.read_csv(csv_raw)

# Cargar datos (raw-github)
#geojson_url = 'https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson'
geojson_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/json/geojason%20modificados.geojson'

chile_geojson = requests.get(geojson_url).json()

#region_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/region_summary.csv'

region_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/region_summary.csv'
sector_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/sector_summary.csv'
industry_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/industry_summary.csv'
buyer_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/buyer_summary.csv'
zone_sumary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/zone_summary%20(1).csv'
ownership_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/ownership_summary.csv'

# Cargar los dataset como dataframe
df_region = load_data(region_summary_url)
df_sector = load_data(sector_summary_url)
df_industry = load_data(industry_summary_url)
df_buyer = load_data(buyer_summary_url)
df_zone = load_data(zone_sumary_url)

# Sidebar - Selección de tipo de test
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type = st.selectbox('Select Test Type', df_region['test_type'].unique())
    sector = st.sidebar.selectbox('Select Sector', df_buyer['sector'].unique())
    rubro2 = st.selectbox('Select Rubro2', df_industry['rubro2'].unique())

    #zone_selected = st.selectbox('Select Zone', df_zone['zone'].unique())
    # Justificar texto usando HTML y CSS
    st.markdown("""

        <br>
        <br>
 
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center;'>
        <b>Detection of Collusion in Public Procurement Auctions: The
Case of the Chilean Pharmaceutical Market</b><br>
        <br>
        <div style='text-align: justify;'>
        We apply the regression discontinuity (RD) based collusion tests developed in Kawai et al.
        (2022) to detect and flag collusion in public procurement auctions for pharmaceutical products
        in Chile from 2017 to 2022. We observe that marginal winning firms are significantly more likely
        to be incumbents than marginal losers. Additionally, the standardized backlog of marginal
        winning firms is significantly lower than that of marginal losers. These findings underscore
        non-competitive behaviors, suggesting the presence of collusive agreements involving both
        market share allocation and bid rotation in public procurement auctions within the Chilean
        pharmaceutical market.
        <br>
        <br>     
        When dividing the data sample into procurement auctions with
        cross-ownership between bidders and those without, we find collusion to be more prevalent in
        auctions with ownership connections, specifically in the form of bid rotation. However, we did
        not find statistically significant results for the incumbency status test. Furthermore, we conduct
        collusion tests at various levels, including sector, zone, region, buyer, pharmaceutical drug
        category, pharmaceutical product, and industry. Our findings indicate evidence of collusive
        agreements involving both market share allocations and bid rotation in 2 out of 5 sectors, all
        zones, 11 out of 16 regions, 93 out of 550 buyers (public agencies), 44 out of 109 pharmaceutical
        drug categories, 166 out of 1689 pharmaceutical products, and 64 out of 545 industries analyzed.
    </div>
    """, unsafe_allow_html=True)

    
color_theme = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']

# Definir un diccionario de zonas y regiones
zone_to_regions = {
    'North': [2, 15, 3, 1],
    'South': [11, 9, 10, 14, 12],
    'South Center': [8, 6, 7, 16],
    'North Center': [4, 5],
    'Metropolitan': [13]
}

# Filtrar datos
df_filtered = df_region[df_region['test_type'] == test_type].fillna(0)
df_sector_filtered = df_sector[df_sector['test_type'] == test_type].fillna(0)
df_industry_filtered = df_industry[(df_industry['test_type'] == test_type) & (df_industry['rubro2'] == rubro2)].fillna(0)
df_buyer_filtered = df_buyer[(df_buyer['test_type'] == test_type) & (df_buyer['sector'] == sector)]
df_zone_filtered = df_zone[(df_zone['test_type'] == test_type)].fillna(0)

# Función para crear un mapa coroplético con escala de colores dinámica
# Definición de valores mínimos y máximos para la escala de colores
min_val, max_val = df_filtered['beta_robust'].min(), df_filtered['beta_robust'].max()

# Usar una escala de colores de Plotly, y crear una personalizada para el valor 0
colorscale2 = px.colors.diverging.RdBu
if min_val >= 0:
    colorscale2 = [[0, "white"], [1, colorscale2[-1]]]
elif max_val <= 0:
    colorscale2 = [[0, colorscale2[0]], [1, "white"]]
else:
    zero_norm2 = abs(min_val) / (max_val - min_val)
    colorscale2 = [[0, colorscale2[0]], [zero_norm2, "white"], [1, colorscale2[-1]]]

# Crear el gráfico de mapa coroplético directamente
fig_chile1 = go.Figure(go.Choropleth(
    geojson=chile_geojson,
    locations=df_filtered['codregion'],
    z=df_filtered['beta_robust'],
    colorscale=colorscale2,
    featureidkey="properties.codregion",
    text=df_filtered.apply(lambda row: f"Beta Robust: {row['beta_robust']}<br>P-value: {row['p_value']}<br>Num. Observ.: {row['num_observ']}", axis=1),
    hoverinfo="text",
    marker_line_color='black',
    marker_line_width=0.5
))

fig_chile1.update_geos(
    fitbounds="geojson",
    visible=False,
    showcountries=False,
    showcoastlines=False,
    showland=False,
    showocean=False,
    projection_type="mercator",
    center={"lat": -38, "lon": -74}
)

fig_chile1.update_layout(
    title={
        'text': "Chloropetic Map of Chile",
        'y': 0.975,  # Posición del título en el eje Y, en el rango de 0 a 1
        'x': 0,  # Posición del título en el eje X, centrado
    },
    height=550,
    coloraxis_colorbar={
        'title':''
    },
    margin={"r":10, "t":50, "l":10, "b":100},
     geo=dict(
        domain={'x': [0, 1], 'y': [0, 1]}  # Ajuste del dominio para maximizar el uso del espacio
    ),
    #plot_bgcolor='rgb(233,233,233)',  # Fondo del área del gráfico (gris claro)
    #paper_bgcolor='rgb(233,233,233)',  # Fondo del área fuera del gráfico (gris claro)
    shapes=[
        # Borde no lleno, solo el contorno
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0,
            'y0': 0,
            'x1': 1,
            'y1': 1,
            'line': {
                'color': 'rgb(204, 202, 202)',
                'width': 1,
            },
        }
    ]
)

def build_colorscale(min_val, max_val, color_theme):
    # Si tanto el valor mínimo como el máximo son 0, retornar una escala de colores que sólo muestre blanco
    if min_val == 0 and max_val == 0:
        return [[0, "white"], [1, "white"]]
    
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


###############PRUEBA


# Crear el gráfico de barras para zone Summary filtrado
colorscale_bar = build_colorscale(df_zone_filtered['beta_robust'].min(), df_zone_filtered['beta_robust'].max(), color_theme)
fig_bar_zones = px.bar(
    df_zone_filtered,
    x='beta_robust',
    y='zone',
    color='beta_robust',  # Asegurarse de que la barra se coloree basada en 'beta_robust'
    color_continuous_scale=colorscale_bar,  # Usar la escala de colores personalizada
    title='Bar Chart of Zones',
    labels={'zone': 'Zones', 'beta_robust': 'Beta Robust'},
    hover_data={
        'p_value': ':.3f',  # Formato de 3 decimales para p_value
        'num_observ': True  # Mostrar como está
    },
    custom_data=['p_value', 'num_observ']  # Datos personalizados para usar en las etiquetas de hover
)


fig_bar_zones.update_traces(
    marker_line_color='rgb(204, 202, 202)',  # Define el color del borde de las barras
    marker_line_width=0.5, 
    hovertemplate="<br>".join([
        "Zone: %{y}",
        "Beta Robust: %{x}",
        "P-Value: %{customdata[0]:.3f}",  # Formato de 3 decimales
        "Num.Observ: %{customdata[1]}"
    ])
)

fig_bar_zones.update_layout(
    height=550,
    coloraxis_colorbar={
        'title':''
    },
    margin={"r":10, "t":50, "l":10, "b":100},
    #plot_bgcolor='rgb(233,233,233)',  # Fondo del área del gráfico (gris claro)
    #paper_bgcolor='rgb(233,233,233)',  # Fondo del área fuera del gráfico (gris claro)
    shapes=[
        # Borde no lleno, solo el contorno
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0,
            'y0': 0,
            'x1': 1,
            'y1': 1,
            'line': {
                'color': 'rgb(204, 202, 202)',
                'width': 1,
            },
        }
    ]
)

#########################################################
# Crear un gráfico de vector de calor para los sectores
colorscale_sector = build_colorscale(df_sector_filtered['beta_robust'].min(), df_sector_filtered['beta_robust'].max(), color_theme)


# Creación del heatmap con Plotly Graph Objects
trace2 = go.Heatmap(
    x=df_sector_filtered['test_type'],
    y=df_sector_filtered['sector'],
    z=df_sector_filtered['beta_robust'],
    colorscale=colorscale_sector,
    hoverongaps=False,
    text=df_sector_filtered.apply(lambda row: (
        f"Beta Robust: {row['beta_robust']:.2f}<br>"
        f"P-value: {row['p_value']:.2f}<br>"
        f"Num. Observ: {row['num_observ']}"
    ), axis=1),
    hoverinfo='text'
)

# Configuración del layout del gráfico
layout = go.Layout(
    title='Vector of sectors',
    xaxis={'title': 'Type of Test'},
    yaxis={'title': 'Sector'},
    height=550,
    #margin={"r":0, "t":50, "l":0, "b":100},
    coloraxis_colorbar={'title': ''},
    margin={"r":10, "t":50, "l":10, "b":100},
    #plot_bgcolor='rgb(233,233,233)',  # Fondo del área del gráfico (gris claro)
    #paper_bgcolor='rgb(233,233,233)',  # Fondo del área fuera del gráfico (gris claro)
    shapes=[
        # Borde no lleno, solo el contorno
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0,
            'y0': 0,
            'x1': 1,
            'y1': 1,
            'line': {
                'color': 'rgb(204, 202, 202)',
                'width': 1,
            },
        }
    ]
)


fig_heatmap = go.Figure(data=trace2, layout=layout)

# Crear la figura y agregar el trazo del heatmap
#######################################################
# Creación de la matriz de calor para la industria
colorscale_industry = build_colorscale(df_industry_filtered['beta_robust'].min(), df_industry_filtered['beta_robust'].max(), color_theme)

# Preparación de los datos
df_industry_prepared = df_industry_filtered.sort_values(by=['rubro3', 'zone'])

# Creación del heatmap con Plotly Graph Objects
trace = go.Heatmap(
    x=df_industry_prepared['rubro3'],
    y=df_industry_prepared['zone'],
    z=df_industry_prepared['beta_robust'],
    colorscale=colorscale_industry,
    hoverongaps=False,
    text=df_industry_prepared.apply(lambda row: (
        f"Beta Robust: {row['beta_robust']:.2f}<br>"
        f"P-value: {row['p_value']:.2f}<br>"
        f"Num. Observ: {row['num_observ']}"
    ), axis=1),
    hoverinfo='text'
)

# Configuración del layout del gráfico
layout = go.Layout(
    title='Analysis at the Industry Level',
    xaxis={'title': 'Pharmaceutical Drug Group'},
    yaxis={'title': 'Zone'},
    height=700,
    coloraxis_colorbar={'title': ''},
    margin={"r":10, "t":50, "l":10, "b":100},
    #plot_bgcolor='rgb(233,233,233)',  # Fondo del área del gráfico (gris claro)
    #paper_bgcolor='rgb(233,233,233)',  # Fondo del área fuera del gráfico (gris claro)
    shapes=[
        # Borde no lleno, solo el contorno
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0,
            'y0': 0,
            'x1': 1,
            'y1': 1,
            'line': {
                'color': 'rgb(204, 202, 202)',
                'width': 1,
            },
        }
    ]
)

# Crear la figura y agregar el trazo del heatmap
fig_heatmap_industry = go.Figure(data=trace, layout=layout)

################################################################

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
    hover_data={
        'p_value': ':.3f',  # Formato de 3 decimales para p_value
        'num_observ': True  # Mostrar como está
    },
    custom_data=['p_value', 'num_observ']  # Datos personalizados para usar en las etiquetas de hover
)

# Personalizar el texto de hover para incluir las etiquetas 'P-Value' y 'Num.Observ'
fig_bar.update_traces(
    marker_line_color='rgb(204, 202, 202)',  # Define el color del borde de las barras
    marker_line_width=0.5, 
    hovertemplate="<br>".join([
        "Buyer: %{x}",
        "Beta Robust: %{y:.3f}",  # Asumiendo que quieras mostrar beta robust como flotante
        "P-Value: %{customdata[0]:.3f}",  # Formato de 3 decimales
        "Num.Observ: %{customdata[1]}"
    ])
)

fig_bar.update_layout(
    height=500,
    width=200,
    coloraxis_colorbar={
        'title':'Beta Robust Scale'
    },
    margin={"r":10, "t":50, "l":10, "b":100},
    shapes=[
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0,
            'y0': 0,
            'x1': 1,
            'y1': 1,
            'line': {
                'color': 'rgb(204, 202, 202)',
                'width': 1,
            },
        }
    ]
)

# Distribución de gráficos en el dashboard
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.plotly_chart(fig_chile1, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar_zones, use_container_width=True)
with col3:
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Mostrar el gráfico de barras y el mapa de calor de la industria
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_heatmap_industry, use_container_width=True)