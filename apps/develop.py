from dash import html
import os
from .components.utils import my_Curl, my_OpenIdConnect_Utils
from pandaclient import PLogger

def develop(uid=None):
	curl = my_Curl()
	oidc = curl.get_my_oidc(PLogger.getPandaLogger(), verbose=True)
	s, o, dec = oidc.check_token()
	return html.Div(
		className="content-container bright-background",
		children=[
			html.H4(f'{os.environ}'),
			html.H4(f'process uid: {uid}'),
			html.H4(f'Does token exist? {s}'),
			html.H4(f'Check token output: {o}')
		]
	)