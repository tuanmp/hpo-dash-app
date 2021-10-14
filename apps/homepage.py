from dash import html, dcc
import lorem

def homepage(**kwargs):
    return html.Div(
            children=[
                html.Div(
                    className="content-container white-background", 
                    children=[
                        html.H1("About PANDA Hyperparameter Optimization"),
                        html.P(lorem.text()),
                        html.Div(
                            className="centered-container",
                            children=[
                                html.A(className="button", children="Explore Submission Tool", href="#submission"),
                                html.A(className="button", children="Explore Monitoring Tool", href="#monitoring"),
                                ]   
                            )
                        ]
                    ),
                html.Div(
                    className="content-container polygon blue-background ", 
                    id="submission",
                    children=[
                        html.H1("Task Submission"),
                        html.P(lorem.paragraph()), 
                        html.Div(
                            className="centered-container",
                            children=[
                                html.A(className="button", children="Go to Submission", href="/submission"),
                                ]   
                            )
                        ]
                    ),
                html.Div(
                    className="content-container bright-background", 
                    id="monitoring",
                    children=[
                        html.H1("Task Monitoring"),
                        html.P(lorem.paragraph()), 
                        html.Div(
                            className="centered-container",
                            children=[
                                html.A(className="button", children="Go to Monitoring", href="/monitor"),
                                ]   
                            )
                        ]
                    )
                ]
        )