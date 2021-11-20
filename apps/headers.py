from dash import html
from dash import dcc

def header(app_title="PANDA Hyperparameter Optimization"):
    return html.Div(
        id='app-headers', 
        className='header',
        children=[
            html.A(
                id='app-logo', 
                children=[
                    html.Img(src="assets/panda-img.jpeg", height="70px"),
                ],
                href='/home'
            ),
            html.H2(app_title),
            html.Div(
                className="header-link",
                children=html.A( 
                    children="Monitoring",
                    href='/monitor'
                )
            ),
            html.Div(
                className="header-link",
                children=html.A( 
                    children="Submission",
                    href='/submission'
                )
            ),
            html.Div(
                className="header-link",
                children=html.A( 
                    children="Development",
                    href='/develop'
                )
            )
        ]
    )