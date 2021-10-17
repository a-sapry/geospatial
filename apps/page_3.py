from dash.dcc.Loading import Loading
import pandas as pd
import rtree
import geopandas as gpd
import plotly.express as px
import folium
from folium import features
from folium import plugins
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
options = [{'label':x,'value':x} for x in df.country_long.unique() if x in gdf.ADMIN.unique()]

# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Country',style={'textAlign':'center'}),
            html.Hr(),
        ])
    ],className='mt-3'),


    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='my-dropdown',options=options,value='Italy',persistence=True,persistence_type='session',placeholder="Select a country",style={'color':'black'},clearable=False),
            html.Iframe(id='country_map',srcDoc = '',width='100%',height='100%')
        ],xl=9,lg=9,md=12,sm=12,xs=12),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(dcc.Loading(id='load2',children=[])),
                dcc.Graph(id='my-graph',figure={}),
                dbc.CardFooter([
                    html.Label(id='number',children=[]),
                    html.Label(id='capacity',children=[]),
                    html.Label(id='powerfull',children=[])
                ])
                
            ])
        ],xl=3,lg=3,md=12,sm=12,xs=12)
    ],style={'height':'80vh'})
],fluid=True)



@app.callback(
    [Output(component_id='country_map',component_property='srcDoc'),
    Output(component_id='load2',component_property='children'),
    Output(component_id='my-graph',component_property='figure'),
    Output(component_id='number',component_property='children'),
    Output(component_id='capacity',component_property='children'),
    Output(component_id='powerfull',component_property='children')],
    Input(component_id='my-dropdown',component_property='value')
)
def update_global_map(val):
    country = gdf[gdf['ADMIN']==val]
    dff = df[df['country_long']==val]

    tiles = ['cartodbpositron','stamenwatercolor','stamentoner','openstreetmap']
    url = "https://raw.githubusercontent.com/SECOORA/static_assets/master/maps/img/rose.png"
    m = folium.Map(location=[dff.latitude.mean(),dff.longitude.mean()],zoom_control=True,zoom_start=5,tiles='cartodbpositron')
    folium.GeoJson(data=country,style_function=lambda feature: {
        "fillColor": "#ffff00",
        "color": "red",
        "weight": 2,
        "dashArray": "5, 5",
    },name='Area').add_to(m)
    for i in tiles:
        folium.TileLayer(i).add_to(m)
    cm = plugins.MarkerCluster(name='clusters of powerstations')
    for idx,row in dff.iterrows():
        folium.Marker(location=[row.latitude,row.longitude],
        popup=folium.Popup(f'name=<b>{row["name"]}</b><br>owner=<b>{row["owner"]}</b><br>type of powerplant=<b>{row["primary_fuel"]}</b><br>capacity_mw=<b>{row["capacity_mw"]}</b><br>website=<b><a href="{row["url"]}">{row["url"]}</a></b>'),
        icon=folium.Icon(color="red", icon="bolt", prefix='fa')).add_to(cm)
    plugins.FloatImage(url, bottom=10, left=5).add_to(m)
    m.add_child(cm)
    folium.LayerControl().add_to(m)

    m.save('map.html')
    srcDoc = open('map.html','r').read()

    t = dff.primary_fuel.value_counts().sort_values().to_frame()
    fig = px.bar(data_frame=t,orientation='h',x='primary_fuel',log_x=True,template='gridon',text='primary_fuel',title='''Distribution of powerstation's type''')
    fig.update_traces(marker_color='#eb3d3d', textposition='inside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='hide')

    num = f'Total number of Power Plants in {val} : ',dff['name'].count()

    cap = dff['capacity_mw'].sum()
    cap = 'Total capacity in GigaWatt: ',(cap/1000).round(2)

    power = dff[dff.capacity_mw == dff.capacity_mw.max()]
    for idx,row in power.iterrows():
        name_ = row['name']
        capacity_ = row['capacity_mw']
        fuel_ = row['primary_fuel']
    power = f"The most powerfull Plant in {val} is {name_} its Capacity in MegaWatt - {capacity_} with type - {fuel_}"

    return srcDoc,val,fig,num,cap,power


# if __name__=='__main__':
#     app.run_server(debug=True)