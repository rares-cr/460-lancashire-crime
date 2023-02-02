import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import pandas as pd
from dash_bootstrap_templates import load_figure_template

load_figure_template("flatly")

# read datasets
crime_df = pd.read_csv('assets/Lancashire_demographics_crime.csv')
population_df = pd.read_csv('assets/lancashire_population_2014_2020.csv')
score_df = pd.read_csv('assets/File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv')
# register page to app
dash.register_page(__name__, name='Crime and IMD Score')

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
                    id="crime-type-03",
                    style={"width": "100%"},
                    placeholder="Select a crime type",
                ),
                dcc.Dropdown(
                    ['2019', '2020'],
                    '2019',
                    id="year-03",
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
                    id="district-03",
                    style={"width": "100%"},
                    placeholder="Select a local authority",
                ),
            ],
            style=dict(display="flex"),
        ),
        # create graph container and elements
        html.Div(id="output-container-03", children=[]),
        html.Br(),
        dcc.Graph(id="my-map-03", figure={}),
        html.Div('***This chart is only looking at 2019 and 2020, since we could not find values for 2021 and 2022.', style={'fontSize':10})
    ]
)

# ------------------------------------------------------------------------------
# Callbacks

@callback(
    [
        Output(component_id="output-container-03", component_property="children"),
        Output(component_id="my-map-03", component_property="figure"),
    ],
    [
        Input(component_id="crime-type-03", component_property="value"),
        Input(component_id="year-03", component_property="value"),
        Input(component_id="district-03", component_property="value"),
    ],
)
def update_output_div(crimetype, year, district):
    # this function creates the bubble chart using the inputs above

    # create copies of dataframes
    tmp_df = crime_df.copy()
    tmp_population_df = population_df.copy()
    tmp_score_df = score_df.copy()

    # filtering the dataframe
    if crimetype != 'Total Crime':
        df = tmp_df[tmp_df['Crime type'] == crimetype]
    else:
        df = tmp_df

    # grouping by certain features and aggregating crime count
    df = df.groupby(['Year', 'LSOA code', 'LSOA name', 'Local Authority District name']).agg(
    crime_count = pd.NamedAgg(column='Index', aggfunc='count')).reset_index()

    tmp_population_df.rename(columns={'LSOA Code': 'LSOA code'}, inplace=True)

    # merging dataframe with population
    df = pd.merge(df, tmp_population_df)

    df = df[df['Year'] == int(year)]

    if district != 'All Districts':
        df = df[df['Local Authority District name'] == district]

    tmp_score_df.rename(columns={'LSOA code (2011)': 'LSOA code', 'Index of Multiple Deprivation (IMD) Score': 'imd_score'}, inplace=True)
    tmp_score_df = tmp_score_df[['LSOA code', 'imd_score']]

    # merging dataframe with IMD score
    df = pd.merge(df, tmp_score_df)

    # producing the scatterplot
    fig = px.scatter(df, x="imd_score", y="crime_count", color="Local Authority District name", size='Population',
                 color_discrete_sequence=px.colors.qualitative.Light24,labels={''}, template='flatly')
    fig.update_layout(xaxis_title='IMD Score',
                      yaxis_title='Crime Count',
                      title='Crime Count by IMD Score and Population (size of bubbles) - ' + district + ' - ' + year)

    return '', fig