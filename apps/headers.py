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
                        href='/submission'
                    ),
                ]
            ),
            # dbc.NavbarToggler(id='navbar-toggler'),
            html.Ul(
                [
                    html.Li(
                        html.A(
                            "Monitoring",
                            href='/monitor',
                            className="nav-link"
                        ),
                        className='nav-item'
                    ),
                    html.Li(
                        html.A(
                            "Submission",
                            href='/submission',
                            className="nav-link"
                        ),
                        className='nav-item'
                    ),
                    # html.Li(
                    #     html.A(
                    #         "Development",
                    #         href='/develop',
                    #         className="nav-link"
                    #     ),
                    #     className='nav-item'
                    # ),
                    html.Li(
                        html.A(
                            "Login",
                            id='profile-button',
                            className="nav-link",
                            href="#"
                        ),
                        className='nav-item'
                    )
                ],
                className='navbar-nav'
            ),
            dcc.Loading(dbc.Offcanvas(
                children=[
                    dcc.Loading(children=[html.P(id="authentication-message")]),
                    html.Div(dbc.Button("Sign in with CERN SSO", color='success', href="#", target="_blank", id="authentication-button"), hidden=True, id="signin-button-container"),
                    html.Div(dbc.Button("Sign out", color='danger', id="signout-button"), hidden=True, id='signout-button-container')
                ],
                is_open=False,
                id="authentication-button-container", 
                keyboard=True,
                placement="end",
                title=""
            ), fullscreen=True),
            dcc.Loading(dcc.Store(storage_type='session', id='session-storage', data={}), fullscreen=True)
        ],
        dark=True,
        light=False,
        color="primary",
        sticky='top'
    )