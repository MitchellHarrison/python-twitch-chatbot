import dash 
import sqlite3
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
colors = {
    "background" : "#05101E",
    "text_base" : "#E0E0E0",
}
app_style = {
    "background-color" : colors["background"]
}
chart_layout = {
    "font" : dict(
        family = "poppins",
        size = 20,
        color = colors["text_base"]),
    "paper_bgcolor" : colors["background"],
    "plot_bgcolor" : "rgba(0, 0, 0, 0)",
    "height" : 700
}

# create dataframes from DB
conn = sqlite3.connect("data.db")
chat_messages = pd.read_sql("SELECT * FROM chat_messages", conn)
command_use = pd.read_sql("SELECT * FROM command_use", conn)
conn.close()

app.layout = html.Div(style = app_style, children = [
    html.H1(
        children = "Twitch Data Visualization Dashboard",
        style = {
            "font-family" : "poppins",
            "text-align" : "center",
            "color" : colors["text_base"],
            "font-size" : "80px",
            "padding" : "0px",
            "margin" : "0px",
            "font-weight" : "normal"
            }
        ),

    html.H2(
        children = "By Mitch",
        id = "subtitle",
        style = {
            "font-family" : "poppins",
            "text-align" : "center",
            "color" : colors["text_base"],
            "padding" : "px",
            "margin" : "0px"
            }
        ),

    dcc.Slider(
        id = "top-chatter-number",
        min = 5,
        max = len(chat_messages["user"].unique()),
        value = 10,
        marks = {i : i for i in range(5, len(chat_messages["user"].unique()) + 1)},
        step = 1
    ),

    dcc.Graph(id = "bar-top-chatters"),

    dcc.Slider(
        id = "top-command-use",
        min = 1,
        max = len(command_use["command"].unique()),
        value = len(command_use["command"].unique()),
        marks = {i : i for i in range(1, len(command_use["command"].unique())+1)},
        step = 1
    ),

    dcc.Graph(id = "bar-top-commands")
])

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
    app.run_server()
