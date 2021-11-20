import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# from hpogui.dash.apps.auth import logInPage
from hpogui.dash.main import app, task, inputStyle, labelAlignment, labelColor, labelSize, labelWidth, linkStyle

layout = [
	dbc.Row(
		[
			dbc.Col([dbc.Jumbotron(children=[])], width=6),
			dbc.Col([dbc.Jumbotron(children=[])], width=6)
		], no_gutters=True),
	dbc.Alert(id="review-alert-task-conf", duration=10000, is_open=False),
	dbc.Alert(id="review-alert-search-space", duration=10000, is_open=False),
	html.Div(
		className="task-conf-body",
		children=[
			html.H4("Submit and Save Configrations", style=linkStyle),
			dbc.Row(
				dbc.Button("Submit Task", id="task-submit-button", block=True, className="bold-button", color="info"),
				no_gutters=True, justify="center"),
			dbc.FormGroup(
				[
					dbc.Label(
						"Save Task Conf", html_for="example-email-row", width=labelWidth, align=labelAlignment,
						color=labelColor, size=labelSize, className="review-label"),
					dbc.Col(
						dbc.InputGroup(
							[
								dbc.Input(
									id="save-task-conf-to-file-name", placeholder="Task configuration file name",
									style=inputStyle),
								dbc.InputGroupAddon(
									dbc.Button(
										"Save task configuration", id="save-task-conf-to-file-button", color="info",
										className="bold-button"), addon_type="append"),
							]), width=12 - labelWidth)
				], row=True, className="no-gutters"),
			dbc.FormGroup(
				[
					dbc.Label(
						"Save Search Space", html_for="example-email-row", width=labelWidth, align=labelAlignment,
						color=labelColor, size=labelSize, className="review-label"),
					dbc.Col(
						dbc.InputGroup(
							[
								dbc.Input(
									id="save-search-space-to-file-name", placeholder="Search Space file name",
									style=inputStyle),
								dbc.InputGroupAddon(
									dbc.Button(
										"Save search space", id="save-search-space-to-file-button", color="info",
										className="bold-button"), addon_type="append"),
							]), width=12 - labelWidth)
				], row=True, className="no-gutters"),
		]),
	# logInPage()
]


@app.callback(
	Output("task-submit-button", "active"),
	Input("task-submit-button", "n_clicks"),
	prevent_initial_call=True)
def submit(signal):
	task.submit(verbose=True)


@app.callback(
	Output('review-alert-task-conf', "is_open"),
	Output('review-alert-task-conf', "color"),
	Output('review-alert-task-conf', 'children'),
	Input("save-task-conf-to-file-button", 'n_clicks'),
	State("save-task-conf-to-file-name", "value"),
	prevent_initial_call=True)
def save_task_conf(signal, filename):
	if not filename or not filename.endswith(".json"):
		return True, 'danger', 'File name must be a non-empty string and end with ".json"'
	task.saveConfig(name=filename)
	return True, 'info', f'{filename} is saved to this local directory'


@app.callback(
	Output('review-alert-search-space', "is_open"),
	Output('review-alert-search-space', "color"),
	Output('review-alert-search-space', 'children'),
	Input("save-search-space-to-file-button", 'n_clicks'),
	State("save-search-space-to-file-name", "value"),
	prevent_initial_call=True)
def save_search_space(signal, filename):
	if not filename or not filename.endswith(".json") or not filename.replace(".json", ""):
		return True, 'danger', 'File name must be a non-empty string and end with ".json"'
	task.saveSearchSpace(name=filename)
	return True, 'info', f'{filename} is saved to this local directory'
