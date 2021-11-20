import dash_html_components as html
import re

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from hpogui.dash.apps.submission import inputStyle, labelColor, labelWidth, linkStyle
from hpogui.dash.components.utils import do_authentication
from hpogui.dash.main import app


def logInMessage(validUsername: bool, validHost: bool, validSSHPass: bool, validGridPass):
	children = []
	if not all([validUsername, validHost, validSSHPass, validGridPass]):
		children += [html.H4("Invalid authentication credentials!", className="alert-heading"),
					 html.P(
						 "At least one of the authentication credentials is invalid. Check gain and make sure they are in order."),
					 html.Hr()]
		if not validUsername:
			children += [html.P("Invalid username. Usernames must contain only word characters.")]
		if not validHost:
			children += [html.P(
				"Invalid ssh host. Hosts must be in the form 'lxplusXXXX', where X are digits, and contain only word characters.")]
		if (not validSSHPass) or (not validGridPass):
			children += [
				html.P("At least one of the passwords is invalid. Passwords must contain at least 8 characters")]
		return children, "warning", True
	else:
		children += [html.H4("Valid authentication credentials registered", className="alert-heading"),
					 html.P("Credentials registered. Authentication in progress.")]
		return children, "success", True


def logInPage():
	username = dbc.FormGroup(
		row=True,
		children=[
			dbc.Label(
				"Username", html_for="example-email-row", width=labelWidth, color=labelColor, className="review-label"),
			dbc.Col(
				children=[
					dbc.InputGroup(
						children=[
							dbc.Input(
								placeholder="Username", id="auth--user-name", invalid=False, pattern=u"\w+",
								type="text", value="", bs_size="sm", style=inputStyle),
							dbc.InputGroupAddon("@"),
							dbc.Input(
								placeholder="Host", id="auth--host", invalid=False, pattern=u"\w+", type="text",
								value="lxplus7", bs_size="sm", style=inputStyle),
							dbc.InputGroupAddon(".cern.ch", addon_type="append")], size="sm")],
				width=12 - labelWidth)
		], className="no-gutters")
	password = dbc.FormGroup(
		row=True,
		children=[
			dbc.Label(
				"Password", html_for="example-email-row", width=labelWidth, color=labelColor, className="review-label"),
			dbc.Col(
				children=[
					dbc.Row(
						no_gutters=True,
						children=[
							dbc.Col(
								dbc.InputGroup(
									children=[
										dbc.InputGroupAddon("SSH", addon_type="prepend"),
										dbc.Input(
											placeholder="ssh password", id="auth--ssh-password", invalid=False,
											type="password", value="", style=inputStyle)
									], size="sm"), width=6),
							dbc.Col(
								dbc.InputGroup(
									children=[
										dbc.InputGroupAddon("Grid", addon_type="prepend"),
										dbc.Input(
											placeholder="grid certification password", id="auth--grid-password",
											invalid=False, type="password", value="", style=inputStyle)
									], size="sm"), width=6)])
				], width=12 - labelWidth)
		], className="no-gutters")
	authoriseButton = dbc.Button("Authorise", color="success", id="auth--submit-button")
	alert = dbc.Alert(children=[], is_open=False, duration=15000, id='auth--auth-info', fade=True)
	usernamePopover = dbc.Popover(
		[dbc.PopoverHeader("Username"),
		 dbc.PopoverBody("Your cern account username. Must contain only word characters.")], target="auth--user-name",
		trigger="focus", placement="bottom-end")
	hostPopover = dbc.Popover(
		[dbc.PopoverHeader("Host"),
		 dbc.PopoverBody("Your preferred lxplus SSH host. Your machine must have login permission to this host.")],
		target="auth--host", trigger="focus", placement="bottom-end")
	sshPassPopover = dbc.Popover(
		[dbc.PopoverHeader("SSH Password"),
		 dbc.PopoverBody("Password to log in your SSH host. Contains at least 8 characters.")],
		target="auth--ssh-password", trigger="focus", placement="bottom-end")
	gridPassPopover = dbc.Popover(
		[dbc.PopoverHeader("Grid Password"),
		 dbc.PopoverBody("Your grid certifiation password. Contains at least 8 characters.")],
		target="auth--grid-password", trigger="focus", placement="bottom-end")
	return html.Div(
		id="log-in-page",
		children=[
			html.H4("Authorisation", style=linkStyle),
			html.P(
				"If task submission fails, it is likely that you are not authorised. Please fill in the authorisation credentials to obtain a proxy for this machine.",
				style={"color": "white"}),
			username,
			password,
			dbc.Row(authoriseButton, justify="center"),
			alert,
			usernamePopover, hostPopover, sshPassPopover, gridPassPopover
		], className="task-conf-body")


layout = html.Div(
	[
		logInPage()
	], className="task-conf-main-body")


@app.callback(
	Output("auth--user-name", "valid"),
	Output("auth--user-name", "invalid"),
	Output("auth--host", "valid"),
	Output("auth--host", "invalid"),
	Output("auth--ssh-password", "valid"),
	Output("auth--grid-password", "valid"),
	Input("auth--user-name", "value"),
	Input("auth--host", "value"),
	Input("auth--ssh-password", "value"),
	Input("auth--grid-password", "value"))
def check_input(username, host, ssh, grid):
	return bool(re.search("^\w+$", username)), bool(re.search("\W+", username)), bool(
		re.search("^lxplus\d*$", host)), not bool(re.search("^lxplus\d*$", host)), len(ssh) > 7, len(grid) > 7


@app.callback(
	Output('auth--auth-info', 'children'),
	Output("auth--auth-info", "color"),
	Output('auth--auth-info', "is_open"),
	Input('auth--submit-button', 'n_clicks'),
	State("auth--user-name", "valid"),
	State("auth--host", "valid"),
	State("auth--ssh-password", "valid"),
	State("auth--grid-password", "valid"),
	State("auth--user-name", "value"),
	State("auth--host", "value"),
	State("auth--ssh-password", "value"),
	State("auth--grid-password", "value"),
	prevent_initial_call=True)
def submit(n_clicks, validUsername, validHost, validSSHPass, validGridPass, Username, Host, SSHPass, GridPass, ):
	if all([validUsername, validHost, validSSHPass, validGridPass]):
		do_authentication(Username, Host + ".cern.ch", SSHPass, GridPass)
	
	return logInMessage(validUsername, validHost, validSSHPass, validGridPass)
