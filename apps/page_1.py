import pandas as pd
import rtree
import geopandas as gpd
import plotly.express as px
import folium
import folium.features as features
import folium.plugins
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
# import dash_core_components as dcc
# import dash_html_components as html
from app import app


df = pd.read_csv(r'datasets\plants.csv')
gdf = gpd.read_file(r'datasets\countries\countries.shp')


# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Global World',style={'textAlign':'center'}),
            html.Hr(),
        ])
    ],className='mt-3'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='top-5',figure={}),
            dbc.Card(dbc.CardImg(src='/assets/plant.jpeg',alt='GlobalWorld'),id='hover-target'),
            dbc.Popover([
                        dbc.PopoverHeader('GeoProject'),
                        dbc.PopoverBody('''This App is effort to show distribution of power plants in the Global World, Continents and some Countries. Used Python's Libraries: Dash, Plotly.express, Pandas, Geopandas, Folium. Data resourse: ***https://datasets.wri.org/dataset/globalpowerplantdatabase***'''),
                        dbc.PopoverHeader('Created by Sapr*')],
                        id='hover',
                        target='hover-target',
                        trigger='hover'
                    )
        ],xl={'order':1, 'size':3},lg={'order':1, 'size':3},md={'order':2, 'size':6},sm={'order':2, 'size':12},xs={'order':2, 'size':12}),
        dbc.Col([
            dcc.RadioItems(id='my-dropdown',value='total capacity, MW',options=[{'label':'number of plants','value':'number of plants'},{'label':'total capacity','value':'total capacity, MW'}],labelStyle={'display': 'flex'}),
            dcc.Graph(id='global_map',figure={})
        ],xl={'order':2, 'size':6},lg={'order':2, 'size':6},md={'order':1, 'size':12},sm={'order':1, 'size':12},xs={'order':1, 'size':12}),
        dbc.Col([
            dcc.Graph(id='global_distribution_power',figure={}),
            dbc.Card(dbc.CardBody(id='global_info',children='', style={'fontWeight':'bold','textAlign':'center'}))
        ],xl={'order':3, 'size':3},lg={'order':3, 'size':3},md={'order':3, 'size':6},sm={'order':3, 'size':12},xs={'order':3, 'size':12}),
    ])
],fluid=True)

    

@app.callback(
    [Output(component_id='global_map',component_property='figure'),
    Output(component_id='global_distribution_power',component_property='figure'),
    Output(component_id='top-5',component_property='figure'),
    Output(component_id='global_info',component_property='children')],
    Input(component_id='my-dropdown',component_property='value')
)
def update_global_map(val):

    df_grouped = df.groupby(['country','country_long']).agg({'name':'count','capacity_mw':'sum'}).reset_index()
    df_grouped.columns = ['iso','country name','number of plants','total capacity, MW']
    df_fuel = df.groupby('primary_fuel').agg({'name':'count','capacity_mw':'sum'}).reset_index()
    df_fuel.columns = ['type of powerstation','number of plants','total capacity, MW']
    gw = df_grouped['total capacity, MW'].sum()/1000
    gw = gw.round().astype('int')
    num_plants = df_grouped['number of plants'].sum()
    num = df_grouped['country name'].nunique()

    if val=='total capacity, MW':

        fig = px.choropleth(data_frame=df_grouped,locations = 'iso',color='total capacity, MW',color_continuous_scale='YlOrRd',hover_name='country name',template='ggplot2')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_geos(fitbounds="locations", visible=True)

        fig2 = px.bar(data_frame=df_fuel.sort_values('total capacity, MW',ascending=True),orientation='h',x='total capacity, MW',y='type of powerstation',template='plotly_white',log_x=True,text='total capacity, MW',title='''World distibution of powerstation's type''')
        fig2.update_traces(marker_color='#eb3d3d', textposition='inside')
        fig2.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')

        fig3 = px.bar(data_frame=df_grouped.sort_values('total capacity, MW',ascending=False).head(),x='country name',y='total capacity, MW',template='plotly_white',text='total capacity, MW',title='TOP 5 Countries')
        fig3.update_traces(marker_color='#eb3d3d', textposition='inside')
        fig3.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')

        text_gw = f'total capacity {gw} gigawatt in the World // number of countries - {num}'

        return fig,fig2,fig3,text_gw

    else:

        fig = px.choropleth(data_frame=df_grouped,locations = 'iso',color='number of plants',color_continuous_scale='purples',hover_name='country name',template='ggplot2')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_geos(fitbounds="locations", visible=True)

        fig2 = px.bar(data_frame=df_fuel.sort_values('number of plants',ascending=True),orientation='h',x='number of plants',y='type of powerstation',template='plotly_white',log_x=True,text='number of plants',title='''World distibution of powerstation's type''')
        fig2.update_traces(marker_color='#3d51eb', textposition='inside')
        fig2.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')

        fig3 = px.bar(data_frame=df_grouped.sort_values('number of plants',ascending=False).head(),x='country name',y='number of plants',template='plotly_white',text='number of plants',title='TOP 5 Countries')
        fig3.update_traces(marker_color='#3d51eb', textposition='inside')
        fig3.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')

        text_gw = f'total number of plants {num_plants} in the World // number of countries - {num}'

        return fig,fig2,fig3,text_gw



# if __name__=='__main__':
#     app.run_server(debug=True)