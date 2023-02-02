import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import pandas as pd
from dash_bootstrap_templates import load_figure_template

load_figure_template("flatly")
# read dataset
final_df = pd.read_csv('assets/timeseries_df.csv')
# register page to app
dash.register_page(__name__, name='Crime Time Series')

# ------------------------------------------------------------------------------
# App layout

layout = html.Div(
    [
        html.Div(
            [
                # add dropdown lists
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
                    [
                        "All Districts",
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
                dcc.Dropdown(
                    ['All Deprivation Deciles', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "All Deprivation Deciles",
                    id="deprivation",
                    style={"width": "100%"},
                    placeholder="Select a deprivation decile",
                ),
            ],
            style=dict(display="flex"),
        ),

        # create first graph container and elements
        html.Div(id="output-container3", children=[]),
        dcc.Graph(id="time1", figure={}),
        # add radio items
        dcc.RadioItems(['By Crime Type', 'By District'],
                       'By Crime Type', id='radio', labelStyle={'display': 'inline'}),
        # create second graph container and elements
        html.Div(id="output-container4", children=[]),
        dcc.Graph(id="time2", figure={}),
    ]
)
# ------------------------------------------------------------------------------
# Callbacks

# first callback and charts
@callback(
    [
        Output(component_id="output-container3", component_property="children"),
        Output(component_id="time1", component_property="figure"),

    ],
    [
        Input(component_id="district", component_property="value"),
        Input(component_id="crime-type", component_property="value"),
        Input(component_id='deprivation', component_property="value"),
    ],
)
def update_graph(district, crimetype, deprivation):
    # this function creates the time series charts using the inputs above
    container = ""
    # filtering the dataframe
    dff = final_df.copy()
    dff = dff[dff["Year"] != "All years"]

    dff = dff[dff['Crime type'] == crimetype]

    if district != "All Districts":
        dff = dff[dff["Local Authority District name"] == district]

    if deprivation != "All Deprivation Deciles":
        dff = dff[dff["Index of Multiple Deprivation Decile"] == deprivation]

    # groupby year and month and sum crime count values
    dff = dff.groupby(['Year', "Month"])['Crime count'].sum()
    dff = pd.DataFrame(dff).reset_index()
    dff.loc[(dff != 0).any(axis=1)]

    # create a date column in the '%Y-%m' format
    dff['Date'] = pd.to_datetime(dff[['Year', 'Month']].assign(DAY=1))
    dff['Date'] = dff['Date'].apply(lambda x: x.strftime('%Y-%m'))

    # create the line chart
    fig = px.line(dff, x='Date', y='Crime count', template='flatly')
    fig.update_layout(title=crimetype + " Count by Month - " + district + ' - Deprivation Decile: ' + str(deprivation),
                      xaxis_title='Crime Type',
                      yaxis_title='Crime Count'
                      )

    return container, fig


# second callback and charts
@callback(
    [
        Output(component_id="output-container4", component_property="children"),
        Output(component_id="time2", component_property="figure"),

    ],
    [
        Input(component_id="district", component_property="value"),
        Input(component_id="crime-type", component_property="value"),
        Input(component_id='deprivation', component_property="value"),
        Input(component_id='radio', component_property='value')
    ],
)
def update_graph(district, crimetype, deprivation, selection):
    # this function creates a line chart showing crime counts by type or district
    container = ""
    dff = final_df.copy()

    if selection == 'By Crime Type':
        # filter dataframe
        if district != "All Districts":
            dff = dff[dff["Local Authority District name"] == district]

        dff = dff[dff['Crime type'] != "Total Crime"]

        if deprivation != "All Deprivation Deciles":
            dff = dff[dff["Index of Multiple Deprivation Decile"] == deprivation]

        # groupby year and month and sum crime count values
        dff = dff.groupby(['Year', "Month", "Crime type"])['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()
        dff.loc[(dff != 0).any(axis=1)]

        # create a date column in the '%Y-%m' format
        dff['Date'] = pd.to_datetime(dff[['Year', 'Month']].assign(DAY=1))
        dff['Date'] = dff['Date'].apply(lambda x: x.strftime('%Y-%m'))

        # create the line chart
        fig = px.line(dff, x='Date', y='Crime count', color='Crime type',
                      color_discrete_sequence=px.colors.qualitative.Dark24, template='flatly')

    else:

        dff = dff[dff['Crime type'] == crimetype]

        if deprivation != "All Deprivation Deciles":
            dff = dff[dff["Index of Multiple Deprivation Decile"] == deprivation]

        dff = dff.groupby(['Year', "Month", "Local Authority District name"])['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()
        dff.loc[(dff != 0).any(axis=1)]

        dff['Date'] = pd.to_datetime(dff[['Year', 'Month']].assign(DAY=1))
        dff['Date'] = dff['Date'].apply(lambda x: x.strftime('%Y-%m'))

        fig = px.line(dff, x='Date', y='Crime count', color='Local Authority District name',
                      color_discrete_sequence=px.colors.qualitative.Dark24, template='flatly')

    return container, fig
