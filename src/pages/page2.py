import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import pandas as pd
from dash_bootstrap_templates import load_figure_template

load_figure_template("flatly")
# read dataset
final_df = pd.read_csv('assets/final_df.csv')
# register page to app
dash.register_page(__name__, name='Crime Statistics')

# ------------------------------------------------------------------------------
# Page layout

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
                    ["All years", '2019', '2020', '2021', '2022'],
                    "All years",
                    id="year",
                    style={"width": "100%"},
                    placeholder="Select a year",
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
            ],
            style=dict(display="flex"),
        ),
        # add radio items
        dcc.RadioItems(['By Crime Type', 'By Deprivation Decile', 'By District'],
                       'By Crime Type', id='radio', labelStyle={'display': 'inline'}),

        # create first graph container and elements
        html.Div(id="output-container1", children=[]),
        dcc.Graph(id="bar", figure={}),
        # create second graph container and elements
        html.Div(id="output-container2", children=[]),
        dcc.Graph(id="pie", figure={}),
    ]
)

# ------------------------------------------------------------------------------
# Callbacks

@callback(
    [
        Output(component_id="output-container1", component_property="children"),
        Output(component_id="bar", component_property="figure"),

    ],
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="district", component_property="value"),
        Input(component_id="crime-type", component_property="value"),
        Input(component_id='radio', component_property="value"),
    ],
)

# use inputs as function parameters
def update_graph(year, district, crimetype, selection):
    # this function creates a bar chart
    # it returns a container and the figure
    container = ""
    dff = final_df.copy()

    if selection == 'By Crime Type':
        # filter dataframe
        if district != "All Districts":
            dff = dff[dff["Local Authority District name"] == district]

        dff = dff[dff["Year"] == year]

        dff = dff[dff['Crime type'] != 'Total Crime']
        dff = dff.groupby('Crime type')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create bar chart and update layout
        fig1 = px.bar(dff, x='Crime type', y='Crime count', text_auto='.2s', template='flatly')

        fig1.update_layout(title='Crime count by Type - ' + str(year) + ' - ' + district,
                           xaxis_title='Crime Type',
                           yaxis_title='Crime Count'
                           )
        fig1.update_xaxes(tickfont_size=10)
        fig1.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    elif selection == 'By District':
        # filter dataframe
        dff = dff[dff["Year"] == year]
        dff = dff[dff['Crime type'] == crimetype]

        dff = dff.groupby('Local Authority District name')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create bar chart and update layout
        fig1 = px.bar(dff, x='Local Authority District name', y='Crime count', text_auto='.2s', template='flatly')

        fig1.update_layout(title=crimetype+ ' Count by District - ' + str(year),
                           xaxis_title='District',
                           yaxis_title='Crime Count'
                           )
        fig1.update_xaxes(tickfont_size=10)
        fig1.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    else:
        # filter dataframe
        if district != "All Districts":
            dff = dff[dff["Local Authority District name"] == district]

        dff = dff[dff["Year"] == year]

        dff = dff[dff['Crime type'] == crimetype]
        dff = dff.groupby('Index of Multiple Deprivation Decile')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create bar chart and update layout
        fig1 = px.bar(dff, x='Index of Multiple Deprivation Decile', y='Crime count',
                      text_auto='.2s', template='flatly')

        fig1.update_layout(title=crimetype + ' count by Decile - ' + str(year) + ' - ' + district,
                           xaxis_title='Multiple Deprivation Decile',
                           yaxis_title='Crime Count',
                           )

    return container, fig1

# the second callback is for the second chart on the page, a pie chart
@callback(
    [
        Output(component_id="output-container2", component_property="children"),
        Output(component_id="pie", component_property="figure"),

    ],
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="district", component_property="value"),
        Input(component_id="crime-type", component_property="value"),
        Input(component_id='radio', component_property="value")

    ],
)
def update_graph(year, district, crimetype, selection):
    # this function creates and updates the pie chart using the inputs
    # it returns a container and the figure
    container = ""
    dff = final_df.copy()

    if selection == 'By Crime Type':
        # filter dataframe
        if district != "All Districts":
            dff = dff[dff["Local Authority District name"] == district]

        dff = dff[dff["Year"] == year]

        dff = dff[dff['Crime type'] != 'Total Crime']
        dff = dff.groupby('Crime type')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create pie chart and update layout
        fig2 = px.pie(dff, names='Crime type', values='Crime count',
                      color_discrete_sequence=px.colors.qualitative.Dark24, template='flatly')
        fig2.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', showlegend=True, legend=dict(
            title_font_family='Courier New',
            font=dict(
                size=10
            )
        ))
    elif selection == 'By District':
        # filter dataframe
        dff = dff[dff["Year"] == year]
        dff = dff[dff['Crime type'] == crimetype]
        dff = dff.groupby('Local Authority District name')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create pie chart and update layout
        fig2 = px.pie(dff, names='Local Authority District name', values='Crime count',
                      color_discrete_sequence=px.colors.qualitative.Dark24, template='flatly')
        fig2.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', showlegend=True, legend=dict(
            title_font_family='Courier New',
            font=dict(
                size=10
            )
        ))

    else:
        # filter dataframe
        if district != "All Districts":
            dff = dff[dff["Local Authority District name"] == district]

        dff = dff[dff["Year"] == year]

        dff = dff[dff['Crime type'] == crimetype]
        dff = dff.groupby('Index of Multiple Deprivation Decile')['Crime count'].sum()
        dff = pd.DataFrame(dff).reset_index()

        # create pie chart and update layout
        fig2 = px.pie(dff, names='Index of Multiple Deprivation Decile', values='Crime count',
                      color_discrete_sequence=px.colors.qualitative.Dark24, template='flatly')
        fig2.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', showlegend=True, legend=dict(
            title_font_family='Courier New',
            font=dict(
                size=10
            )
        ))

    return container, fig2









