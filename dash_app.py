import dash 
import sqlite3
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# these colors aren't defined in CSS because graphs don't accept CSS styling
colors = {"background" : "#05101E", "text_base" : "#E0E0E0"}
chart_layout = {
    "font" : dict(
        family = "poppins",
        size = 20,
        color = colors["text_base"]),
    "paper_bgcolor" : "rgba(0,0,0,0)",
    "plot_bgcolor" : "rgba(0,0,0,0)",
    "height" : 700
}

def build_title():
    return html.Div(id = "title-banner", children = [
        html.H1("Twitch Data Visualization Dashboard", id="app-title"),
        html.Img(
            id = "twitch-icon", 
            alt = "twitch icon", 
            src = app.get_asset_url("twitch_icon.png"),
            height = 20
        ),  
        html.A("Built Live by Mitch Harrison", id = "app-subtitle", href = "https://twitch.tv/MitchsWorkshop")
    ])


def build_footer():
    return html.Div(id = "discord-footer", children = [
        html.Span(id = "discord-icon", children = [
            html.Img(
                alt = "discord icon",
                src = app.get_asset_url("discord_icon.png") ,
                height = 22
            )
        ]),
        html.A(
            "Join the Discord for discussion!", 
            id = "discord-cta", 
            href = "https://discord.gg/7nefPK6"
        )
    ])


# top chatters bar graph
@app.callback(
    Output(component_id="bar-top-chatters", component_property="figure"),
    [Input(component_id="top-chatter-number", component_property="value"),
    Input(component_id="interval-counter", component_property="n_intervals")]
)
def bar_top_chatters(top_num: int, n:int) -> go.Figure:
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM chat_messages", conn)

    data = df["user"].value_counts().reset_index()
    data.columns = ["user", "message_count"]
    trace_data = data.head(top_num)

    trace = go.Bar(
        x = trace_data["user"],
        y = trace_data["message_count"]
    )

    fig = go.Figure(data = [trace], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top {top_num} Chatters - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                )
            )
        })
    return fig


# command use bar graph
@app.callback(
    Output(component_id = "bar-top-commands", component_property = "figure"),
    [Input(component_id = "top-command-use", component_property = "value"),
    Input(component_id = "interval-counter", component_property = "n_intervals")]
)
def bar_command_use(top_num: int, n: int) -> go.Figure:
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM command_use", conn)
    
    data = df["command"].value_counts().reset_index()
    data.columns = ["command", "count"]
    trace_data = data.head(top_num)

    trace = go.Bar(
        x = trace_data["command"],
        y = trace_data["count"]
    )

    fig = go.Figure(data = [trace], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top {top_num} Commands Used - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                ),
            )
        })
    return fig


# start of app 
app.layout = html.Div([
    dbc.Row(dbc.Col(build_title())),

    dbc.Row([
        dbc.Col(
            dcc.Slider(
                id = "top-command-use",
                min = 1,
                max = 4,
                value = 4,
                marks = {i : str(i) for i in range(1,5)},
                step = 1
            ),
            width = 3
        ),

        dbc.Col(
            dcc.Slider(
                id = "top-chatter-number",
                min = 1,
                max = 40,
                value = 20,
                marks = {i : str(i) for i in range(1,41)},
                step = 1
            )
        )
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id = "bar-top-commands"), width = 3),
        dbc.Col(dcc.Graph(id = "bar-top-chatters"))
    ]),

    dcc.Interval(
        id = "interval-counter",
        interval = 5 * 1000, # in milliseconds
        n_intervals = 0
    ),

    dbc.Row(dbc.Col(build_footer()))
])


if __name__ == '__main__':
    app.run_server(debug=True)
