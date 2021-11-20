from dash import html
import os

from pandaclient.example_task import taskParamMap

def develop():
    return html.Div(
		className="content-container bright-background",
		children=[
			html.H4(f'{os.environ}'),
            html.H4(f'{taskParamMap}'),

		]
	)