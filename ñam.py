#import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
import plotly.graph_objects as go
import numpy as np
def load_data(url):
    response = requests.get(url)
    csv_raw = StringIO(response.text)
    return pd.read_csv(csv_raw)


ownership_summary_url = 'https://raw.githubusercontent.com/LuisEgus/Streamlit---Dashboard/main/data%20CHILE/dta/ownership_summary.csv'
df_ownership = load_data(ownership_summary_url)
df_ownership



df_ownership1 = pd.read_csv(r'C:\Users\Admin\Documents\GitHub\Streamlit---Dashboard\data CHILE\dta\ownership_summary.csv')
df_ownership1 = df_ownership1['sample'].unique