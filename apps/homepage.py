from dash import html, dcc
import dash_bootstrap_components as dbc
import lorem

def homepage(**kwargs):
    return html.Div(
            children=[
                html.Div(
                    [
                        html.H1("About PANDA Hyperparameter Optimization"),
                        html.P(lorem.text()),
                        html.Div(
                            [
                                dbc.Button("Explore Submission Tool", href="#submission", color="primary", class_name='me-md-2', outline=True),
                                dbc.Button("Explore Monitoring Tool", href="#monitoring", color="primary", class_name='me-md-2', outline=True),
                            ],
                            className="d-grid gap-2 d-md-flex justify-content-md-center"
                        )
                    ]
                ),
                html.Div(
                    [
                        html.H1("Task Submission"),
                        html.P(lorem.paragraph()),
                        html.Div(
                            [
                                dbc.Button("Go to Submission", href="/submission", color="primary", class_name='me-md-2', outline=True),
                            ],
                            className="d-grid gap-2 d-md-flex justify-content-md-center"
                        )
                    ]
                ),
                html.Div(
                    [
                        html.H1("Task Monitoring"),
                        html.P(lorem.paragraph()), 
                        html.Div(
                            [
                                dbc.Button("Go to Monitoring", href="/monitor", color="primary", class_name='me-md-2', outline=True),
                            ],
                            className="d-grid gap-2 d-md-flex justify-content-md-center"
                        )
                    ]
                )
            ]
        )