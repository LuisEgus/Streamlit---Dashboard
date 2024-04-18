

import pandas as pd
import geopandas as gpd

# Cargar las relaciones de region_ID a macrozone desde el archivo Excel
df_relations = pd.read_excel(r'C:\Users\Admin\Documents\GitHub\Streamlit---Dashboard\data CHILE\dta\xlsx\id_zone.xlsx')

# Carga el archivo GeoJSON original de regiones
gdf_regions = gpd.read_file(r'C:\Users\Admin\Documents\GitHub\Streamlit---Dashboard\json\Regional.geojson')

# Asegúrate de que el tipo de dato de la columna 'codregion' en gdf_regions es int para que coincida con 'region_ID' en df_relations
gdf_regions['codregion'] = gdf_regions['codregion'].astype(int)

# Combina los datos de macrozona con el GeoDataFrame
gdf = gdf_regions.merge(df_relations, left_on='codregion', right_on='region_ID')

# Disuelve las fronteras de las regiones para formar macrozonas
gdf_dissolved = gdf.dissolve(by='macrozone')

# Guarda el nuevo GeoJSON
output_geojson = r'C:\Users\Admin\Documents\GitHub\Streamlit---Dashboard\json\macrozones.geojson'
gdf_dissolved.to_file(output_geojson, driver='GeoJSON')

print(f"Nuevo archivo GeoJSON de macrozonas guardado: {output_geojson}")
