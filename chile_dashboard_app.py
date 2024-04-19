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
df_ownership = load_data(ownership_summary_url)

# Sidebar - Selección de tipo de test
with st.sidebar:
    st.title('🌎 Chile Data Dashboard')
    test_type = st.selectbox('Select Test Type', df_region['test_type'].unique())
    sector = st.sidebar.selectbox('Select Sector', df_buyer['sector'].unique())
    rubro2 = st.selectbox('Select Pharmaceutical Drug Class', df_industry['rubro2'].unique())

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

# Filtrar datos
df_filtered = df_region[df_region['test_type'] == test_type].fillna(0)
df_sector_filtered = df_sector[df_sector['test_type'] == test_type].fillna(0)
df_industry_filtered = df_industry[(df_industry['test_type'] == test_type) & (df_industry['rubro2'] == rubro2)].fillna(0)
df_buyer_filtered = df_buyer[(df_buyer['test_type'] == test_type) & (df_buyer['sector'] == sector)]
df_zone_filtered = df_zone[(df_zone['test_type'] == test_type)].fillna(0)
df_ownership_filtered = df_ownership[(df_ownership['test_type'] == test_type)]

###########
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
    center={"lat":-35.675147, "lon":-71.542969}
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
                'width': 0,
            },
        }
    ]
                     
)


####Función para escala de colores:

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

# Crear el gráfico de barras horizontal con Plotly Graph Objects
bar_trace = go.Bar(
    x=df_zone_filtered['beta_robust'],  # Valores para la longitud de las barras
    y=df_zone_filtered['zone'],  # Valores para el eje Y
    orientation='h',  # Hace que el gráfico sea horizontal
    marker=dict(
        color=df_zone_filtered['beta_robust'],  # Asigna un color basado en el valor de 'beta_robust'
        colorscale=colorscale_bar,  # Usa la escala de colores personalizada
        cmin=df_zone_filtered['beta_robust'].min(),  # Mínimo de la escala de colores
        cmax=df_zone_filtered['beta_robust'].max(),
        line=dict(color='rgb(204, 202, 202)', width=0.75),  # Máximo de la escala de colores
        colorbar_title=''
    ),
    hoverinfo='text',
    text=df_zone_filtered.apply(lambda row: f"Zone: {row['zone']}<br>Beta Robust: {row['beta_robust']:.3f}<br>P-Value: {row['p_value']:.3f}<br>Num.Observ: {row['num_observ']}", axis=1)
)

# Crear la figura con el objeto Bar y la configuración de layout
fig_bar_zones = go.Figure(data=[bar_trace])

# Actualizar el layout de la figura para añadir título y la barra de colores
fig_bar_zones.update_layout(
    title='Bar Chart of Zones',
    xaxis_title="Beta Robust",
    yaxis_title="Zones",
    height=550,
    margin=dict(r=20, t=50, l=10, b=100),
    # Configuración de la barra de colores
    coloraxis=dict(
        colorbar_len=0.5,  # Longitud de la barra de colores
        colorbar_thickness=10,  # Grosor de la barra de colores
        colorbar_title='',
        colorscale=colorscale_bar,  # Usa la escala de colores personalizada
        cmin=df_zone_filtered['beta_robust'].min(),  # Mínimo de la escala de colores
        cmax=df_zone_filtered['beta_robust'].max()  # Máximo de la escala de colores
    )
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
    coloraxis_colorbar={'title': 'Beta Robust Scale'},
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
    height=500,
    coloraxis_colorbar={'title': 'Beta Robust Scale'},
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
# Crea la escala de colores personalizada
colorscale_bar = build_colorscale(df_buyer_filtered['beta_robust'].min(), df_buyer_filtered['beta_robust'].max(), color_theme)

# Crear el gráfico de barras vertical con Plotly Graph Objects
bar_trace = go.Bar(
    x=df_buyer_filtered['rutunidadcompra'],  # Valores para el eje X
    y=df_buyer_filtered['beta_robust'],  # Valores para la altura de las barras
    marker=dict(
        color=df_buyer_filtered['beta_robust'],  # Asigna un color basado en el valor de 'beta_robust'
        colorscale=colorscale_bar,  # Usa la escala de colores personalizada
        showscale=True,
        line=dict(color='rgb(204, 202, 202)', width=0.75),  # Muestra la barra de la escala de colores
    ),
    hoverinfo='text',
    hovertemplate=(
        "Buyer: %{x}<br>" +
        "Beta Robust: %{y:.3f}<br>" +
        "P-Value: %{customdata[0]:.3f}<br>" +
        "Num.Observ: %{customdata[1]}<extra></extra>"
    ),
    customdata=df_buyer_filtered[['p_value', 'num_observ']]
)

# Crear la figura con el objeto Bar y la configuración de layout
fig_bar = go.Figure(data=[bar_trace])

# Configuración de la barra de la escala de colores
colorbar_params = {
    'title': 'Escala de Beta Robust',
    'len': 0.5,  # Longitud de la barra de colores
    'thickness': 10,  # Grosor de la barra de colores
    'borderwidth': 1,
    'bordercolor': 'black'
}

# Actualizar el layout de la figura para añadir título y la barra de colores con el formato deseado
fig_bar.update_layout(
    title='Bar Chart of Buyers',
    xaxis_title="(Public Agency)",
    yaxis_title="Beta Robust",
    height=500,
    width=1200,
    margin=dict(r=10, t=50, l=10, b=100),
    coloraxis=dict(
        colorbar=colorbar_params,
        colorscale=colorscale_bar,  # Usa la escala de colores personalizada
        cmin=df_buyer_filtered['beta_robust'].min(),  # Mínimo de la escala de colores
        cmax=df_buyer_filtered['beta_robust'].max()  # Máximo de la escala de colores
    )
)

####################################
# Crear columnas para los diferentes 'samples' y mostrar KPIs
samples = ['Full sample ', 'Auctions involving bidders without cross-ownership', 'Auctions involving bidders with cross-ownership']
columns = st.columns(len(samples))  # Una columna para cada métrica

for index, sample in enumerate(samples):
    with columns[index]:
        # Título del sample
        st.markdown(f'<div style="text-align: center;"><span style="font-weight: bold; font-size: large;">{sample}</span></div>', unsafe_allow_html=True)
        # Obtener datos para el sample actual
        sample_data = df_ownership_filtered[df_ownership_filtered['sample'] == sample]
        
        if not sample_data.empty:
            # Métricas en Markdown con estilo personalizado para centrar verticalmente y aumentar tamaño de número
            beta_robust = sample_data['beta_robust'].iloc[0]
            p_value = sample_data['p_value'].iloc[0]
            num_observ = sample_data['num_observ'].iloc[0]
            # Usamos Markdown para personalizar la presentación de las métricas
            st.markdown(f"""
            <div style="text-align: center;">
                <p><strong>Beta Robust</strong></p>
                <p style="font-size: xx-large;">{beta_robust:.4f}</p>
                <p><strong>P-Value</strong></p>
                <p style="font-size: xx-large;">{p_value:.4f}</p>
                <p><strong>N° of Observations</strong></p>
                <p style="font-size: xx-large;">{num_observ:,}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="text-align: center;">
                        <br>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.error("No data available for this test type and sample combination.")

# Distribución de gráficos en el dashboard
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.plotly_chart(fig_chile1, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar_zones, use_container_width=True)
with col3:
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Mostrar el gráfico de barras y el mapa de calor de la industria
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_heatmap_industry, use_container_width=True)