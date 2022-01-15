###############################################
#   LIBRARIES
# region###############################################

import pandas as pd
import numpy as np
pd.options.plotting.backend = "plotly"

import json

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

import plotly.io as pio
pio.templates.default = "plotly_dark"
import plotly.offline as pyo
import plotly.express as px
import plotly.graph_objs as go

#endregion



###############################################
#   LOADING AND TRANSFORMING THE DATA
# region###############################################
# salvando a url dos conjuntos de dados proveninentes do ministerio do turismo (Ultimo ano disponivel e o ano de 2019)
#url_conjunto_2017 = "https://dados.turismo.gov.br/pt_BR/dataset/184e0ddd-7eaf-488d-ad84-0331219d6e99/resource/86134fdc-fbfe-44d0-ad2e-315b16f70233/download/chegadas_2017.csv"
#url_conjunto_2018 = "https://dados.turismo.gov.br/pt_BR/dataset/184e0ddd-7eaf-488d-ad84-0331219d6e99/resource/7495cab5-6597-4015-95ec-d161d756ee41/download/chegadas_2018.csv"
#url_conjunto_2019 = "https://dados.turismo.gov.br/pt_BR/dataset/184e0ddd-7eaf-488d-ad84-0331219d6e99/resource/24057369-a5dc-45b4-a66f-9a6a8f8e3422/download/chegadas_2019.csv"

path_dataset_2017 = "C:/Users/marea/PycharmProjects/Dashboard/data/chegadas_2017.csv"
path_dataset_2018 = 'C:/Users/marea/PycharmProjects/Dashboard/data/chegadas_2018.csv'
path_dataset_2019 = 'C:/Users/marea/PycharmProjects/Dashboard/data/chegadas_2019.csv'

# lendo os arquivos CSV e salvando cada dataset
dataset_2017 = pd.read_csv(path_dataset_2017,
                           sep=';',
                           error_bad_lines=False,
                           encoding='latin-1')  # usando codificação latin-1 codificação utf-8 gerou erro

dataset_2018 = pd.read_csv(path_dataset_2018,
                           sep=';',
                           error_bad_lines=False,
                           encoding='utf-8')  # usando codificação utf-8 codificação latin-1 gerou erro

dataset_2019 = pd.read_csv(path_dataset_2019,
                           sep=';',
                           error_bad_lines=False,
                           encoding='latin-1')  # usando codificação latin-1 codificação utf-8 gerou erro


df_turismo = pd.concat([dataset_2017, dataset_2018, dataset_2019]) #concatenando os tres datasets

df_turismo['Mês'] = df_turismo['Mês'].str.capitalize() #normalizando a coluna 'Mês' pois a mesma tem meses com a inicial maiuscula e outros com a inicial minuscula

df_turismo.drop(['cod continente', 'cod pais', 'cod uf', 'cod via'], axis=1, inplace=True) #Excluindo as colunas desnescessarias

with open(
        'C:/Users/marea/PycharmProjects/Dashboard/data/brazil-states.geojson') as data:  # carregando o arquivo ".geojson"
    limites_brasil = json.load(data)

for feature in limites_brasil['features']:  # adicionado o ID aos dados
    feature['id'] = feature['properties']['name']

# endregion

df_continente = df_turismo.groupby(['Continente', 'Via'])['Chegadas'].sum().reset_index()
df_continente = df_continente.sort_values(by=['Continente', 'Chegadas']).reset_index(drop=True)
df_top10 = df_turismo.groupby('País')['Chegadas'].sum().sort_values(ascending=False).nlargest(10).reset_index()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

###############################################
#   CSS STYLES
# region###############################################

colors = {
    'title-text': '#7FDBFF',
    'background': '#111111'

}

# endregion


barra = px.bar(df_top10,
                        x='Chegadas',
                        y= 'País',
                        title='Chegadas X País',
                        orientation='h',
                        text_auto='.2s',
               width=500,
               height=500)

pizza = px.pie(df_turismo.groupby(['ano', 'Via'])['Chegadas'].sum().reset_index(inplace=False),
              values='Chegadas',
              names='Via',
              title='Chegadas X Via',
              hole=.3,
               width= 490,
               height=300)

coropletico = px.choropleth_mapbox(
    df_turismo,
    locations='UF',
    geojson=limites_brasil,
    color='Chegadas',
    mapbox_style='carto-positron',
    zoom=3,
    opacity=0.5)

# endregion

anos = [2017, 2018, 2019, 'ALL'],


# region ##########################Criando a Dashboard####################

app.layout = html.Div(children=[
        html.Div(

            html.H3(children='Entrada de Turistas Internacionais no Brasil',
                    style={'color':colors['title-text'], 'align':'center', 'fontFamily':'fantasy', 'fontSize':25}),
            className='row1', style={'textAlign':'center'}),

            html.Div([html.Div(dcc.Graph(id='g1', figure=barra),className='two_columns', style={'display': 'inline-block'}),
                      html.Div(dcc.Graph(id='g2', figure=pizza),className='two_columns', style={'display': 'inline-block'})
                     ], className='row4', style={'width':1100, 'height':600}),

            html.Div(html.P('Dashboard desenvolvida por Cristiano'), style={'color':'#FFFFFF', 'fontSize':15})

], style={'backgroundColor':colors['background']})


# endregion

###############################################
#   RUN SERVER
# region###############################################
if __name__ == "__main__":
  app.run_server(
    debug=True,
    host="127.0.0.1",
    port=8050,
    dev_tools_hot_reload=True
  )
# endregion###############################
