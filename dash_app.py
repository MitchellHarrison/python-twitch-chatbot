import dash 
import sqlite3
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# these colors aren't defined in CSS because graphs don't accept CSS styling
colors = {
    "background" : "#05101E", 
    "text_base" : "#E0E0E0",
    "chart_highlight_blue" : "#0597DC",
    "chart_deep_gray" : "#303030",
    "chart_light_gray" : "#6C6C6C"
}
chart_layout = {
    "font" : dict(
        family = "poppins",
        size = 20,
        color = colors["text_base"]),
    "paper_bgcolor" : "rgba(0,0,0,0)",
    "plot_bgcolor" : "rgba(0,0,0,0)",
    "height" : 700,
    "yaxis" : dict(showgrid = False) # nice
}


def get_chat_messages():
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM chat_messages", conn)
    conn.close()
    return df


def build_title_banner():
    return html.Div(
        id = "title-banner", 
        children = [
            html.H5(
                id="app-title",
                children = "Twitch Data Visualization Dashboard"
            ),
            html.Img(
                id = "twitch-icon", 
                alt = "twitch icon", 
                src = app.get_asset_url("twitch_icon.png"),
                height = 20
            ),  
            html.A(
                id = "app-subtitle", 
                href = "https://twitch.tv/MitchsWorkshop",
                children = "Built Live by Mitch Harrison"
            )
        ])


def build_all_tabs():
    return html.Div(
        id = "tab-container", 
        children = [
            dcc.Tabs(
                id = "all-tabs", 
                className = "app-tabs",
                value = "tab-chat",
                children = [
                    dcc.Tab(
                        id = "tab-chat",
                        value = "tab-chat",
                        className = "app-tab",
                        label = "Chat",
                        selected_className = "app-tab--selected"
                    ),
                    dcc.Tab(
                        id = "tab-vod-analysis",
                        value = "tab-vod-analysis",
                        className = "app-tab",
                        label = "VOD Analysis",
                        selected_className = "app-tab--selected"
                    ),
                    dcc.Tab(
                        id = "tab-followers",
                        value = "tab-followers",
                        className = "app-tab",
                        label = "Followers",
                        selected_className = "app-tab--selected"
                    ),
                    dcc.Tab(
                        id = "tab-stream-summary",
                        value = "tab-stream-summary",
                        className = "app-tab",
                        label = "Stream Summary",
                        selected_className = "app-tab--selected"
                    )
                ])
            ])


def build_tab_chat() -> list:
    return [
        html.Div(
            id = "chat-tab", 
            children = [
                    build_pct_chat_following(),
                    dcc.Dropdown(
                        id = "chat-graph-dropdown",
                        options = [
                            {"label": "Top Chatters - All Time", "value": "top chatters"},
                            {"label": "Total Command Use - All Time", "value": "command use"}
                        ],
                        value = "top chatters"
                    ),
                    html.Div(id="chat-tab-bar-card")
                ]
            )
        ]


def build_tab_followers() -> list:
    return [
        html.Div(
            children = [
                html.P(
                    "This is the followers tab, where follower data will be visualized."
                )
            ],
            style = {
                "color": "white",
                "font-size": "2rem"
            }
        )
    ]


def build_tab_vod_analysis() -> list:
    return [
        html.Div(
            children = [
                html.P(
                    "This is where VOD analysis will take place, with most recent broadcast embedded."
                )
            ],
            style = {
                "color": "white",
                "font-size": "2rem"
            }
        )
    ]


def build_tab_stream_summary() -> list:
    return [
        html.Div(
            children = [
                html.P(
                    "This is where the most recent stream's summary data will be."
                )
            ],
            style = {
                "color": "white",
                "font-size": "2rem"
            }
        )
    ]


def build_chatter_slider() -> dcc.Slider:
    df = get_chat_messages()
    num_chatters = len(df["user"].unique())
    slider_max = 50 if num_chatters > 50 else num_chatters
    # step = slider_max // 15
    return dcc.Slider(
                id = "top-chatter-number",
                min = 1,
                max = slider_max,
                value = slider_max // 2,
                marks = {i : str(i) for i in range(1,slider_max)}
            )


def build_pct_chat_following() -> html.Div:
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    with conn:
        cursor.execute("SELECT DISTINCT username FROM followers")
        followers = [u[0] for u in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT user FROM chat_messages")
        chatters = [u[0] for u in cursor.fetchall()]
        chatters_not_following = [c for c in chatters if c not in followers]
        pct_not_followed = round(len(chatters_not_following) / len(chatters) * 100, 1)

    return html.Div(
        id = "pct-chat-following",
        className = "text-insight",
        children = [
            html.H2(
                id = "pct-following-display",
                className = "text-insight-value",
                children = f"{pct_not_followed}%"
            ),
            html.P(
                id = "chatters-not-following",
                className = "text-insight-subtext",
                children = "of chatters aren't following"
            )
        ]
    )


def build_footer() -> html.Div:
    return html.Div(id = "discord-footer", children = [
        html.Span(id = "discord-icon", children = [
            html.Img(
                alt = "discord icon",
                src = app.get_asset_url("discord_icon.png"),
                height = 22
            )
        ]),
        html.A(
            "Join the Discord for discussion!", 
            id = "discord-cta", 
            href = "https://discord.gg/7nefPK6"
        )
    ])


### LAYOUT ###
app.layout = html.Div(
    id = "master-container", 
    children = [
        dcc.Interval(
            id = "interval-counter",
            interval = 1 * 1000, # in milliseconds
            n_intervals = 0
            ),
        build_title_banner(),
        build_all_tabs(),
        html.Div(
            id = "app-container", 
            children = [
                html.Div(id = "active-tab"),
                build_footer()
            ]
        )
    ]
)


@app.callback(
    [Output(component_id="active-tab", component_property="children")],
    [Input(component_id="all-tabs", component_property="value")]
)
def build_tab(tab: str) -> list:
    if tab == "tab-chat":
        return build_tab_chat()
    elif tab == "tab-vod-analysis":
        return build_tab_vod_analysis()
    elif tab == "tab-followers":
        return build_tab_followers()
    else:
        return build_tab_stream_summary()


@app.callback(
    Output(component_id="chat-tab-bar-card", component_property="children"),
    [Input(component_id="chat-graph-dropdown", component_property="value")]
)
def build_bar_graph(title: str) -> list:
    if title == "command use":
        return [dcc.Graph(id="command-use-bar")]
    elif title == "top chatters":
        return [
            build_chatter_slider(),
            dcc.Graph(id="top-chatters-bar")
        ]


@app.callback(
    Output(component_id="command-use-bar", component_property="figure"),
    [Input(component_id="interval-counter", component_property="n_intervals")]
)
def bar_command_use(n: int) -> go.Figure:
    conn = sqlite3.connect("data.db")
    with conn:
        df = pd.read_sql("SELECT * FROM command_use", conn)
    conn.close()
    
    data_custom = df[df["is_custom"]==True]
    data_custom = data_custom["command"].value_counts().reset_index()
    data_custom.columns = ["command", "count"]

    data_hard_coded = df[df["is_custom"]==False]
    data_hard_coded = data_hard_coded["command"].value_counts().reset_index()
    data_hard_coded.columns = ["command", "count"]

    trace1 = go.Bar(
        x = data_custom["command"],
        y = data_custom["count"],
        name = "Custom",
        text = data_custom["count"],
        textposition = "outside",
        marker_color = colors["chart_deep_gray"]
    )
    trace2 = go.Bar(
        x = data_hard_coded["command"],
        y = data_hard_coded["count"],
        name = "Default",
        text = data_hard_coded["count"],
        textposition = "outside",
        marker_color = colors["chart_light_gray"]
    )

    fig = go.Figure(data = [trace1, trace2], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top Commands Used - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                ),
            ),

        'xaxis': dict(
            categoryorder = 'array',
            categoryarray = df["command"].value_counts().index
        ),

        "legend" : dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            itemclick = False,
            itemdoubleclick = False)
        })
    return fig


@app.callback(
    Output(component_id="top-chatters-bar", component_property="figure"),
    [Input(component_id="top-chatter-number", component_property="value"), 
    Input(component_id="interval-counter", component_property="n_intervals")]
)
def bar_top_chatters(num_chatters: int, n: int) -> go.Figure:
    df = get_chat_messages()
    data = df["user"].value_counts().reset_index()
    data.columns = ["user", "message_count"]
    trace_data = data.head(num_chatters)

    trace = go.Bar(
        x = trace_data["user"],
        y = trace_data["message_count"],
        text = trace_data["message_count"],
        textposition = "outside",
        marker_color = [colors["chart_highlight_blue"]] 
            + [colors["chart_deep_gray"] for _ in range(num_chatters-1)]
    )

    fig = go.Figure(data = [trace], layout = chart_layout)
    fig.update_layout({
        "title" : dict(
            text = f"Top {num_chatters} Chatters - All Time",
            font = dict(
                family = "poppins", 
                size = 35, 
                color = colors["text_base"]
                )
            )
        })
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
