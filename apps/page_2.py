from dash.dcc.Loading import Loading
from dash_bootstrap_components._components.Card import Card
from dash_bootstrap_components._components.CardHeader import CardHeader
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
gdf_short = gdf[['ADM0_A3','ISO_A2','CONTINENT']]
df_joined = pd.merge(df,gdf_short,left_on='country',right_on='ADM0_A3')
df_joined[['latitude_avg','longitude_avg']] = df_joined.groupby('country')[['latitude','longitude']].transform('mean')
# df[['latitude_avg','longitude_avg']] = df.groupby('country')[['latitude','longitude']].transform('mean')
# gdf_points = gpd.GeoDataFrame(data=df.drop(columns=['latitude','longitude']),geometry=gpd.points_from_xy(df.longitude,df.latitude),crs=gdf.crs)
options = [{'label': 'Asia', 'value': 'Asia'},
        {'label': 'South America', 'value': 'South America'},
        {'label': 'Africa', 'value': 'Africa'},
        {'label': 'Europe', 'value': 'Europe'},
        {'label': 'North America', 'value': 'North America'},
        {'label': 'Oceania', 'value': 'Oceania'},
        {'label': 'Antarctica', 'value': 'Antarctica'}]

# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Continent',style={'textAlign':'center'}),
            html.Hr(),
        ])
    ],className='mt-3'),

    dbc.Row([
        dbc.Col([
            dcc.RadioItems(id='my-dropdown',value='South America',persistence=True,persistence_type='memory',options=options,labelStyle={'display': 'inline-block'}),
            dcc.Loading(id='load',children=[]),
            html.Iframe(id='continent_map',srcDoc = '',width='100%',height='100%')
        ])
    ],style={'height':'80vh'})
],fluid=True)


@app.callback(
    [Output(component_id='continent_map',component_property='srcDoc'),
    Output(component_id='load',component_property='children')],
    Input(component_id='my-dropdown',component_property='value')
)
def update_global_map(val):
    gdf_temp = gdf[gdf['CONTINENT']==val].copy()
    joined_group = df_joined[df_joined['CONTINENT']==val].copy()
    gdf_geom = gdf[gdf['CONTINENT']==val][['ADM0_A3','geometry']]
    joined_group = joined_group.groupby(['ADM0_A3','country_long']).agg({'name':'count','capacity_mw':'sum'}).reset_index()
    joined_group.columns = ['iso','name','number of plants','total capacity, MW']
    df_joined_drop = df_joined[['ADM0_A3','ISO_A2','latitude_avg','longitude_avg']].drop_duplicates()
    df_merged = pd.merge(joined_group,df_joined_drop,how='left',left_on='iso',right_on='ADM0_A3')
    df_merged2 = pd.merge(gdf_geom,df_merged,on='ADM0_A3')

    popup = features.GeoJsonPopup(fields=['name','number of plants','total capacity, MW'],aliases=['country','number of plants','total capacity, MW'])
    location = [df_merged.iloc[0]['latitude_avg'],df_merged.iloc[0]['longitude_avg']]
    url = "https://raw.githubusercontent.com/SECOORA/static_assets/master/maps/img/rose.png"
    m = folium.Map(location=location,zoom_control=True,zoom_start=3,tiles='cartodbdark_matter')
    folium.Choropleth(geo_data=gdf_temp,data=df_merged,columns=['iso','total capacity, MW'],key_on='feature.properties.ISO_A3',fill_color='OrRd',highlight=True,fill_opacity=0.2,line_opacity=0.5,nan_fill_color='white',legend_name='total capacity, MW').add_to(m)
    features.GeoJson(data=df_merged2,tooltip=features.GeoJsonTooltip(fields=['name'],aliases=['']),popup=popup,style_function=lambda feature: {
            "fillColor": "red",
            "color": "black",
            "weight": 3,
        }).add_to(m)
    plugins.FloatImage(url, bottom=10, left=5).add_to(m)
    for idx,row in df_merged.iterrows():
        flag = row['ISO_A2']
        try:
            location = [row['latitude_avg'],row['longitude_avg']]
            folium.CircleMarker(radius=4, fill_color="green",color="black", location=location,popup=folium.Popup(folium.Html(f"<br> <img src='https://www.flagistrany.ru/data/flags/w580/{flag.lower()}.webp' width=100>",script=True))).add_to(m)
        except:
            location = [0,0]

    m.save('map.html')
    srcDoc = open('map.html','r').read()
    return srcDoc,val



# if __name__=='__main__':
#     app.run_server(debug=True)