from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

def header(app_title="PANDA Hyperparameter Optimization"):
    return dbc.Navbar(
        [
            dbc.Container(
                [
                    html.A(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(dbc.NavbarBrand(app_title))
                                ]
                            )
                        ],
                        href='/home'
                    ),
                ]
            ),
            dbc.NavbarToggler(id='navbar-toggler'),
            dbc.NavLink( 
                "Monitoring",
                href='/monitor'
            ),
            dbc.NavLink( 
                "Submission",
                href='/submission'
            ),
            dbc.NavLink( 
                "Development",
                href='/develop'
            )
        ],
        light=True,
        sticky='top'
    )