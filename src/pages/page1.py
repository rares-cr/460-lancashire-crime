import dash
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback
import pandas as pd


final_df = pd.read_csv('assets/final_df.csv')
pop = pd.read_csv("assets/population.csv")
pop = pop.apply(lambda x: x.str.replace(',', ''))

dash.register_page(__name__, name='Crime Map', path='/')


# ------------------------------------------------------------------------------
# App layout

layout = html.Div(
    [

        html.Div(
            [
                dcc.Dropdown(
                    [
                        "Total Crime",
                        "Anti-social behaviour",
                        "Bicycle theft",
                        "Burglary",
                        "Criminal damage and arson",
                        "Drugs",
                        "Other crime",
                        "Other theft",
                        "Possession of weapons",
                        "Public order",
                        "Robbery",
                        "Shoplifting",
                        "Theft from the person",
                        "Vehicle crime",
                        "Violence and sexual offences",
                    ],
                    "Total Crime",
                    id="crime-type",
                    style={"width": "100%"},
                    placeholder="Select a crime type",
                ),
                dcc.Dropdown(
                    ['All years', '2019', '2020', '2021', '2022'],
                    'All years',
                    id="year",
                    style={"width": "100%"},
                    placeholder="Select a year",
                ),
                dcc.Dropdown(
                    ['All Deprivation Deciles', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "All Deprivation Deciles",
                    id="deprivation",
                    style={"width": "100%"},
                    placeholder="Select a deprivation decile",
                ),
                dcc.Dropdown(
                    [
                        'All Districts',
                        "Blackburn with Darwen",
                        "Blackpool",
                        "Burnley",
                        "Chorley",
                        "Fylde",
                        "Hyndburn",
                        "Lancaster",
                        "Pendle",
                        "Preston",
                        "Ribble Valley",
                        "Rossendale",
                        "South Ribble",
                        "West Lancashire",
                        "Wyre",

                    ],
                    "All Districts",
                    id="district",
                    style={"width": "100%"},
                    placeholder="Select a local authority",
                ),
            ],
            style=dict(display="flex"),
            className="mb-4"
        ),
        dcc.RadioItems(['Show Crime Count', 'Show Crime Rate'],
                       'Show Crime Count', id='radio', labelStyle={'display': 'inline'}),
        html.Div(id="output-container", children=[]),
        html.Br(),
        dcc.Graph(id="my-map", figure={}),

    ], className="mb-4"
)


@callback(
    [
        Output(component_id="output-container", component_property="children"),
        Output(component_id="my-map", component_property="figure"),
    ],
    [
        Input(component_id="crime-type", component_property="value"),
        Input(component_id="year", component_property="value"),
        Input(component_id="deprivation", component_property="value"),
        Input(component_id="district", component_property="value"),
        Input(component_id="radio", component_property="value")
    ],
)
def update_graph(crimetype, year, deprivation, district, selection):

    container = ""
    token = "pk.eyJ1IjoicmFyZXNjciIsImEiOiJjbGJpMmQ3Y2swOG9mM3dvOTFteGtmaTBkIn0.SQ1JLnGk9CTTs-AY8ZXyIw"

    dff = final_df.copy()
    dff = dff[dff["Crime type"] == crimetype]
    dff = dff[dff["Year"] == year]

    if deprivation != "All Deprivation Deciles":
        dff = dff[dff["Index of Multiple Deprivation Decile"] == deprivation]

    if district != "All Districts":
        dff = dff[dff["Local Authority District name"] == district]

    dff = dff[dff['Crime count'] != 0]

    new_df = dff.merge(pop, how='left', left_on='LSOA code', right_on='LSOA Code')
    new_df.drop(columns=['LSOA Code'], inplace=True)
    new_df['Population'] = new_df['Population'].astype(int)
    new_df['Crime Rate'] = round(new_df['Crime count'] / new_df['Population'] * 1000,2)

    if selection == 'Show Crime Count':
        max = dff["Crime count"].max()

        # Plotly Express
        fig = go.Figure(
            data=[
                go.Scattermapbox(
                    lat=dff["Latitude"],
                    lon=dff["Longitude"],
                    mode="markers",
                    customdata=dff,
                    hovertemplate="LSOA Code: %{customdata[0]}<br> Crime Count:%{customdata[4]}<extra></extra>",
                    marker=go.scattermapbox.Marker(
                        size=dff["Crime count"],
                        sizemode="diameter",
                        sizemin=3,
                        sizeref=max / 30,
                        color=dff["Crime count"],
                        colorscale="reds",
                        showscale=True,
                    ),
                )
            ]
        )

        fig.update_layout(
            mapbox=dict(
                style="dark",
                accesstoken=token,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=final_df["Latitude"].mean()+0.05,
                    lon=final_df["Longitude"].mean(),
                ),
                zoom=8.5,
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height = 700
        )
    else:
        max = new_df["Crime Rate"].max()

        # Plotly Express
        fig = go.Figure(
            data=[
                go.Scattermapbox(
                    lat=new_df["Latitude"],
                    lon=new_df["Longitude"],
                    mode="markers",
                    customdata=new_df,
                    hovertemplate="LSOA Code: %{customdata[0]}<br> Crime Rate:%{customdata[9]}<extra></extra>",
                    marker=go.scattermapbox.Marker(
                        size=new_df["Crime Rate"],
                        sizemode="diameter",
                        sizemin=3,
                        sizeref=max / 30,
                        color=new_df["Crime Rate"],
                        colorscale="reds",
                        showscale=True,
                    ),
                )
            ]
        )

        fig.update_layout(
            mapbox=dict(
                style="dark",
                accesstoken=token,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=final_df["Latitude"].mean() + 0.05,
                    lon=final_df["Longitude"].mean(),
                ),
                zoom=8.5,
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=700
        )

    return container, fig

