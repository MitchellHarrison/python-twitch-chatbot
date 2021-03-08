import dash 
import sqlite3
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"
]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

colors = {"background" : "#05101E", "text_base" : "#E0E0E0"}

# create dataframes from DB
conn = sqlite3.connect("data.db")
chat_messages = pd.read_sql("SELECT * FROM chat_messages", conn)
command_use = pd.read_sql("SELECT * FROM command_use", conn)
conn.close()

# start of app layout
app.layout = html.Div([
    dbc.Row(
        dbc.Col(html.H1("Twitch Data Visualization Dashboard",id="app-title"))
        ),

    dbc.Row(
        dbc.Col(html.H2("By Mitch",id = "app-subtitle"))
        ),

    dbc.Row([
        dbc.Col(
            dcc.Slider(
                id = "top-command-use",
                min = 1,
                max = len(command_use["command"].unique()),
                value = len(command_use["command"].unique()),
                marks = {i : str(i) for i in range(1, len(command_use["command"].unique())+1)},
                step = 1
            ), 
            width = 6
        ),

        dbc.Col(
            dcc.Slider(
                id = "top-chatter-number",
                min = 5,
                max = len(chat_messages["user"].unique()),
                value = 10,
                marks = {i : str(i) for i in range(5, len(chat_messages["user"].unique()) + 1)},
                step = 1
            ),
            width = 6
        )
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id = "bar-top-commands")),
        dbc.Col(dcc.Graph(id = "bar-top-chatters"))
        ])
])


chart_layout = {
    "font" : dict(
        family = "poppins",
        size = 20,
        color = colors["text_base"]),
    "paper_bgcolor" : "rgba(0,0,0,0)",
    "plot_bgcolor" : "rgba(0,0,0,0)",
    "height" : 700
}


@app.callback(
    Output(component_id = "bar-top-chatters", component_property = "figure"),
    Input(component_id = "top-chatter-number", component_property = "value")
)
def bar_top_chatters(top_num: int):
    data = chat_messages["user"].value_counts().reset_index()
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
            font = dict(family = "poppins", size = 35, color = colors["text_base"]))
    })
    return fig


@app.callback(
    Output(component_id = "bar-top-commands", component_property = "figure"),
    Input(component_id = "top-command-use", component_property = "value")
)
def bar_command_use(top_num: int):
    data = command_use["command"].value_counts().reset_index()
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
            font = dict(family = "poppins", size = 35, color = colors["text_base"]),
            )
    })
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
