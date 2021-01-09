import pandas as pd
import numpy as np
import dash_table
from pivottablejs import pivot_ui
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from IPython.display import HTML
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Symbol, Group
import plotly.express as px

# import plotly.graph_objects as go


archivo_carteras = "Cartera Principal.xlsx"
archivo_aums = "Otros datos.xlsx"
catalogotv = "Catálogo TV.xlsx"
catalogoetfs = "Catalogo2.xlsx"
# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

df_cartera = pd.read_excel(archivo_carteras, sheet_name="Cartera")
df_aums = pd.read_excel(archivo_aums, sheet_name="Activos Netos")
df_generales = pd.read_excel(archivo_aums, sheet_name="Generales")
df_fees = pd.read_excel(archivo_aums, sheet_name="Suma de Cuotas")
df_catalogotv = pd.read_excel(catalogotv, sheet_name="Catálogo TV")
df_catalogoetfs = pd.read_excel(catalogoetfs, sheet_name="Catálogo")

df_generales.drop("Operadora", axis=1, inplace=True)
df_generales.drop("Calificación  del  Mes  Actual", axis=1, inplace=True)

df_aumstot = df_aums.groupby(["Fondo"]).sum().reset_index()

df_analisiscartera = df_cartera.merge(df_aumstot, on=["Fondo"])
df_analisiscartera = df_analisiscartera.merge(df_catalogotv, on=["Tipo de valor"])
df_analisiscartera = df_analisiscartera.merge(df_generales, on=["Fondo"])
df_analisiscartera["% Portafolio"] = df_analisiscartera["Valor razonable o contable total"] / df_analisiscartera[
    "ACTIVOS  NETOS  CIERRE  MES  ACTUAL"]
df_analisiscartera.drop("Bursatilidad instrumento de renta variable", axis=1, inplace=True)
df_analisiscartera.drop("Calificación de Instrumento de Deuda", axis=1, inplace=True)
df_analisiscartera.drop("ID Mercado", axis=1, inplace=True)

a = df_analisiscartera.loc[
    df_analisiscartera["Emisora"].isin(df_catalogoetfs["Emisora"]) & df_analisiscartera["Serie"].isin(
        df_catalogoetfs["Serie"])]
a["Asset"] = a["Emisora"].map(df_catalogoetfs.set_index("Emisora")["Asset"])
a["Tipo de Mercado"] = a["Emisora"].map(df_catalogoetfs.set_index("Emisora")["Tipo de Mercado"])

df_analisiscartera.update(a)

del a

tabla_emisora = pd.pivot_table(df_analisiscartera, "% Portafolio",
                               index=['Emisora', "Serie", 'Tipo de inversión', "Asset"], columns=['Fondo'],
                               aggfunc=np.sum, fill_value=0, margins=True)

dff = df_analisiscartera.copy()
dff.drop("Tipo de inversión", axis=1, inplace=True)
dff.drop("Tipo de valor", axis=1, inplace=True)
dff.drop("Cantidad de títulos operados", axis=1, inplace=True)
dff.drop("Valor razonable o contable total", axis=1, inplace=True)
dff.drop("Días por vencer", axis=1, inplace=True)
dff.drop("Emisora", axis=1, inplace=True)
dff.drop("Serie", axis=1, inplace=True)
dff.drop("Tipo de Mercado", axis=1, inplace=True)
# dff.drop("Tipo  de  Fondo", axis=1, inplace=True)
dff.drop("% Portafolio", axis=1, inplace=True)
dff.drop("Asset", axis=1, inplace=True)
dff.drop("Descripción", axis=1, inplace=True)

dff = dff.groupby(["Fondo"]).max().reset_index()
dff['id'] = dff['Fondo']
dff.set_index('id', inplace=True, drop=False)
dff = dff.reindex(columns=["Operadora", "Fondo", "Tipo  de  Fondo", "Clasificación  del  Fondo",
                           "ACTIVOS  NETOS  CIERRE  MES  ACTUAL", "id"])
print(dff.dtypes)

dffb = df_analisiscartera.copy()
dffb.drop("Tipo de inversión", axis=1, inplace=True)
dffb.drop("Tipo de valor", axis=1, inplace=True)
dffb.drop("Cantidad de títulos operados", axis=1, inplace=True)
dffb.drop("Valor razonable o contable total", axis=1, inplace=True)
dffb.drop("Días por vencer", axis=1, inplace=True)
dffb.drop("Tipo  de  Fondo", axis=1, inplace=True)
dffb.drop("Clasificación  del  Fondo", axis=1, inplace=True)
dffb.drop("ACTIVOS  NETOS  CIERRE  MES  ACTUAL", axis=1, inplace=True)

opciones2 = dict(zip(df_analisiscartera.Operadora, df_analisiscartera.Operadora))
options = [{'label': v, 'value': k} for k, v in sorted(opciones2.items())]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = dbc.Container([

    dbc.Row(dbc.Col(html.H1("Comparador de Fondos de Inversión",
                            className='text-center text-primary mb-4'),
                    width={'size': 12, 'offset': 0},
                    ),
            ),

    dbc.Row(
        dbc.Col(html.H4("Bienvenido al comparador de Fondos, una herramienta para evaluar alternativas de inversión ",
                        className='text-center text-secondary mb-4'),
                width={'size': 12, 'offset': 0}
                )
        ),

    dbc.Row(dbc.Col(html.P(
        "Al seleccionar el fondo deseado se podrás ver el detalle del fondo en la parte de abajo de la página para entenderlo un poco mejor ",
        className='alert alert-dismissible alert-info'),
                    width={'size': 12, 'offset': 0}
                    )
            ),

    dbc.Row([

        dbc.Col([
            dcc.Dropdown(id='c_dropdown', multi=True, placeholder='Seleccione la operadora que desea analizar',
                         options=options),

        ], width={'size': 8, "offset": 0, 'order': 1}),

    ]),

    dbc.Row([

        dbc.Col([
            dcc.Checklist(id='checklist1',
                          className='form-check',
                          labelClassName="mr-3",
                          options=[
                              {'label': '  Fondos de Deuda   ', 'value': 'D'},
                              {'label': '  Fondos de Renta Variable   ', 'value': 'RV'}],
                          value=['RV', 'D'],

                          labelStyle={'display': 'inline-block'}
                          )
        ])
    ]),

    dbc.Row([

        dbc.Col([
            dash_table.DataTable(id='tabla1',
                                 columns=[{"name": i, "id": i, "hideable": True, "type": "numeric",
                                           "format": FormatTemplate.money(2)}
                                          if i == "Fondo" or i == "id"
                                          else {"name": i, "id": i, "hideable": True, "type": "numeric",
                                                "format": FormatTemplate.money(2)}
                                          for i in dff],
                                 style_cell={'textAlign': 'left', "maxWidth": "250px"},
                                 sort_action="native",
                                 sort_mode="multi",
                                 page_action="native",
                                 page_current=0,
                                 page_size=20,
                                 row_selectable='single',
                                 selected_rows=[],
                                 style_data={  # overflow cells' content into multiple lines
                                     'whiteSpace': 'normal',
                                     'height': 'auto'
                                 },
                                 #                                    style_table={
                                 #     'maxHeight': '500px',
                                 #     'overflowY': 'scroll'
                                 # },

                                 # style_as_list_view=True,
                                 #  style_data_conditional=(

                                 # data_bars(dff, 'ACTIVOS  NETOS  CIERRE  MES  ACTUAL')
                                 #      ),



                                 style_cell_conditional=[

                                     {
                                         'if': {'column_id': i},

                                         'textAlign': 'right'
                                     } for i in ['ACTIVOS  NETOS  CIERRE  MES  ACTUAL']

                                 ],

                                 )

        ])

    ]),

    html.Br(),
    html.Br(),

    html.Br(),

    html.Br(),
    html.Br(),

    html.Div(id='pie-container', children=[]),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    html.Div(id='sunburn-container', children=[]),

], fluid=False)


@app.callback(

    dash.dependencies.Output('tabla1', 'data'),
    [dash.dependencies.Input('c_dropdown', 'value'),
     dash.dependencies.Input('checklist1', 'value')],

    prevent_initial_call=True
)
def tablafondos(val_chosen, valcheck):
    if len(val_chosen) > 0:
        # print(n)
       # print(f"value user chose: {val_chosen}")
        #print(type(val_chosen))
        dff2 = dff[dff["Operadora"].isin(val_chosen)]

        if len(valcheck) < 0:
            return dff2.to_dict('records')
        else:
            dff3 = dff2[dff2["Tipo  de  Fondo"].isin(valcheck)]
            return dff3.to_dict('records')


@app.callback(
    dash.dependencies.Output(component_id='pie-container', component_property='children'),
    [dash.dependencies.Input(component_id='tabla1', component_property="derived_virtual_data"),
     dash.dependencies.Input(component_id='tabla1', component_property='derived_virtual_selected_rows'),
     dash.dependencies.Input(component_id='tabla1', component_property='derived_virtual_selected_row_ids')],

    prevent_initial_call=True

)
def grafica(slctd_row_indices, slct_rows_names, slctd_rows):
    dffb2 = dffb[dffb["Fondo"].isin(slctd_rows)]
    # dffb2 = dffb2.groupby(["Descripción"]).sum().reset_index()
    # dffb3 = pd.DataFrame(dffb2)
    dffb2.to_dict("records")

    # fig = px.sunburst(dffb2, path=['Asset', 'Descripción'], values='% Portafolio', color = "Asset" , branchvalues="total")


    fig = px.pie(dffb2, names="Asset", values="% Portafolio", title=" Cartera del fondo {}".format(slctd_rows), hole=.3)
    fig.update_traces(textposition='inside')

    fig.update_layout(legend=dict(
        itemsizing='constant',

        orientation="v",
        yanchor="bottom",
        y=0,
        xanchor="right",
        x=-1.5),
        font=dict(

            size=11,
            color="black"))

    # fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    return dcc.Graph(id='pie', figure=fig)


@app.callback(
    dash.dependencies.Output(component_id='sunburn-container', component_property='children'),
    [dash.dependencies.Input(component_id='tabla1', component_property="derived_virtual_data"),
     dash.dependencies.Input(component_id='tabla1', component_property='derived_virtual_selected_rows'),
     dash.dependencies.Input(component_id='tabla1', component_property='derived_virtual_selected_row_ids')],

    prevent_initial_call=True

)
def grafica2(slctd_row_indices, slct_rows_names, slctd_rows):
    dffb2 = dffb[dffb["Fondo"].isin(slctd_rows)]
    # dffb2 = dffb2.groupby(["Descripción"]).sum().reset_index()
    # dffb3 = pd.DataFrame(dffb2)
    dffb2.to_dict("records")

    fig = px.sunburst(dffb2, path=['Asset', "Emisora"],
                      values='% Portafolio',
                      hover_name="Asset",
                      # hover_data={'% Portafolio': False},
                      labels="% Portafolio",
                      color="Asset",
                      branchvalues="total",
                      maxdepth=2,
                      )

    fig.update_traces(textinfo='label+percent root')
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    return dcc.Graph(id='sunburn', figure=fig)


# pivot_ui(df_analisiscartera,outfile_path="pivottablejs.html")
# HTML("pivottablejs.html")



if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=True)