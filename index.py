from dash import dcc
from dash import html
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from app import server

from apps import page_1,page_2,page_3


app.layout = html.Div([
    html.Div([
        dcc.Link('General Information|', href='/apps/page_1'),
        dcc.Link('Continent Information|', href='/apps/page_2'),
        dcc.Link('Country Information', href='/apps/page_3'),
    ]),
    dcc.Location(id='url', refresh=False, pathname='/apps/page_1'),
    html.Div(id='page-content', children=[])
])


@app.callback(
    Output(component_id='page-content', component_property='children'),
    Input(component_id='url', component_property='pathname')
)
def display_page(pathname):
    if pathname == '/apps/page_1':
        return page_1.layout
    elif pathname == '/apps/page_2':
        return page_2.layout
    elif pathname == '/apps/page_3':
        return page_3.layout
    else:
        return "404 Page Error! Choose a link"


if __name__ == '__main__':
    app.run_server(debug=True)