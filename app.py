import os, shutil, subprocess
from apps.headers import header
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash import callback_context
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH
import plotly.express as px

from apps.submission import submission, render_job_config
from apps.monitor import monitor
from apps.homepage import homepage
from apps.develop import develop
from apps.footer import footer
from apps.login import login
from apps.components.utils import check_set, my_OpenIdConnect_Utils, my_Curl
import dash_bootstrap_components as dbc
from apps.components.TaskRetriever import Retriever
from apps.components.SearchSpace import Hyperparameter
from apps.components.Phpo import Phpo 
from apps.components.utils import get_index, getMethod, decode_id_token
import time
import json, yaml, base64, datetime
import re
import uuid 
from pandaclient import PLogger
# from queue import Queue, Empty
# from threading import Thread

external_stylesheets=[dbc.themes.LUX]

dev_token = {
# 	'access_token': 'eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI0ZTkyMzgyZi03MDJmLTQ5MTktYTUzMy05ZjhmZTdiZjY5Y2YiLCJpc3MiOiJodHRwczpcL1wvYXRsYXMtYXV0aC53ZWIuY2Vybi5jaFwvIiwiZXhwIjoxNjQ0NzIzMjQxLCJpYXQiOjE2NDQ3MTk2NDEsImp0aSI6ImFmNmJjMzY4LTRmOTEtNDgyMC1iMmUwLWRiM2ZhZDNiMDk5YSIsImNsaWVudF9pZCI6ImRhMWViNjVmLTc2ZTItNDk1My1hNTAzLWJiNDZlMmEyODFkMyJ9.DY8FjNtoJc1fSfWcSltvUrZln2mgPP-8u_GuQWnCr6Zkjbqf6ucLo-xfYVSvd_2m0929vsh6SjEAOy94KKh1XamVcw_xMsCoGjmYmVaQiKHZ_lMIFjcyL40Ki2N7PEp2jFrYgwEcFjJ_KcZFOzi6wzcvo5g57mTPmffH65_7Ebo',
#  'expires_in': 3599,
#  'id_token': 'eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI0ZTkyMzgyZi03MDJmLTQ5MTktYTUzMy05ZjhmZTdiZjY5Y2YiLCJhdWQiOiJkYTFlYjY1Zi03NmUyLTQ5NTMtYTUwMy1iYjQ2ZTJhMjgxZDMiLCJraWQiOiJyc2ExIiwiaXNzIjoiaHR0cHM6XC9cL2F0bGFzLWF1dGgud2ViLmNlcm4uY2hcLyIsIm5hbWUiOiJUVUFOIE1JTkggUEhBTSIsImdyb3VwcyI6WyJhdGxhcyJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ0dXBoYW0iLCJvcmdhbmlzYXRpb25fbmFtZSI6ImF0bGFzIiwiZXhwIjoxNjQ0NzIwMjQxLCJpYXQiOjE2NDQ3MTk2NDEsImp0aSI6IjBhZDVjZGNhLTUxN2QtNDc5Zi05ZTljLTZlNDRkMDk2ZjFjOCIsImVtYWlsIjoidHVhbi5taW5oLnBoYW1AY2Vybi5jaCJ9.JJBptVyjQ253uWhhbICrOBIrorA4_0_50wcTM_QCjOEktwoijuNCFw87z4198NhsdCU_GYwWsMJjt6rBQX5WxESjAFFbzdCTxzvu6Z_Yqi7kVTjHQC2oP5o1Lk1Ksg_K-Dncd1uPHaSkB5i3UO7WEzQrSDVCEUsC4Y-65BSsOjE',
#  'refresh_token': 'eyJhbGciOiJub25lIn0.eyJqdGkiOiI4NTc0M2U4Ny1kM2UxLTQwNzMtYTBkNi0zNzczY2I3ODA2YjcifQ.',
#  'scope': 'email openid offline_access profile',
#  'token_type': 'Bearer'
 }

app = dash.Dash(__name__, 
				external_stylesheets=external_stylesheets, 
				suppress_callback_exceptions=True)

server = app.server
app.title='hpogui'

application = app.server

app.layout = html.Div(
	[
		dcc.Location(id='url', refresh=False),
		dcc.Store(id='local-storage', storage_type='local', data=dev_token),
		html.Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css", rel="stylesheet"),
		# html.Link(href="https://codepen.io/rmarren1/pen/mLqGRg.css", rel="stylesheet"),
		header(),
		html.Div(
			id='app-page-content',
			children=[]
		),
		footer()
	], style={'height': "100vh"})

task=Phpo()
job_config = task.JobConfig
hyperparameters = {}
search_space = task.HyperParameters
index=len(hyperparameters)+len(search_space)
authorization_output = {}
uid = uuid.uuid4()
info = ' (marked for removal)'
                                    
with open('apps/messages.json') as f:
	messages = json.load(f)

def enqueue_output(out, queue):
	for line in iter(out.readline, b''):
		queue.put(line)
	out.close()


def getOutput(outQueue):
	outStr = ''
	try:
		while True: # Adds output from the Queue until it is empty
			outStr+=outQueue.get_nowait()

	except Empty:
		return outStr

@app.callback(
	Output('app-page-content', 'children'),
	# Output('profile-button', 'label'),
	# Output('profile-button', 'children'),
	# Output('user-credentials', 'data'),
	Input('url', 'hash'),
	Input('url', 'pathname'),
	# Input('user-credentials-container', 'children'),
	# State('app-page-content', 'children'),
	State('local-storage', 'data'),
	# State('profile-button', 'label'),
	# State('profile-button', 'children'),
)
def navigate(hash, pathname, data):
	# profile_button_children = []
	# curl = my_Curl()
	# oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
	# status, token, dec = oidc.check_token(data)
	# trigger=callback_context.triggered[0]['prop_id']
	# if "user-credentials-container" in trigger:
	# 	return page_content, json.loads(credentials), label, profile_content
	# if pathname!='/login':
	# 	if status:
	# 		# exp_time = datetime.datetime.utcfromtimestamp(dec['exp'])
	# 		# delta = exp_time - datetime.datetime.utcnow()
	# 		# profile_button_children.append(
	# 		# 	dbc.DropdownMenuItem(f'Token expires in {delta}', header=True)
	# 		# )
	# 		pass
	# 	elif isinstance(token, dict) and 'refresh_token' in token:
	# 		try:
	# 			refresh_token_string = token.get('refresh_token')
	# 			s, o = oidc.fetch_page(oidc.auth_config_url)
	# 			if not s:
	# 				print(f'Cannot fetch {oidc.auth_config_url}')
	# 			auth_config = o
	# 			s, o = oidc.fetch_page(auth_config['oidc_config_url'])
	# 			if not s:
	# 				print(f"Cannot fetch {auth_config['oidc_config_url']}")
	# 				return data
	# 			endpoint_config = o
	# 			if refresh_token_string is not None:
	# 				oidc.log_stream.info('Refreshing token')
	# 				s, o = oidc.refresh_token(endpoint_config['token_endpoint'], auth_config['client_id'], auth_config['client_secret'], refresh_token_string)
	# 				# refreshed
	# 				if s:
	# 					oidc.log_stream.info('token refreshed')
	# 					for key, value in o.items():
	# 						data[key] = value
	# 				else:
	# 					if oidc.verbose:
	# 						oidc.log_stream.debug('failed to refresh token: {0}'.format(o))
	# 		except Exception as e:
	# 			print(e)
	# 	else:
	# 		s, data, _ = oidc.run_device_authorization_flow(data)
	# 		data['expires_at']=datetime.datetime.utcnow() + datetime.timedelta(seconds=data['expires_in'])
	# 		profile_button_children.append(
	# 			dbc.DropdownMenuItem(f'Sign in', id='authenticate-button', href="/login"),
	# 		)
	# try:
	# 	label = dec['preferred_username']
	# except:
	# 	label = 'Login'
	if pathname=='/home':
		return homepage()
	elif pathname=='/submission':
		global task
		task=Phpo()
		global hyperparameters
		hyperparameters={}
		global search_space
		search_space=task.HyperParameters
		global job_config
		job_config=task.JobConfig
		global index
		index=len(hyperparameters)+len(search_space)
		if len(hyperparameters)==0:
			hyperparameters[0]=Hyperparameter(index=0)
		return submission(config=job_config, hyperparameters=hyperparameters, search_space=search_space), label, profile_button_children, data
	elif pathname=='/monitor':
		return monitor()
	elif pathname=='/develop':
		return develop(uid)
	# elif pathname=='/login':
	# 	if "verification_uri_complete" not in data:
	# 		raise PreventUpdate()
	# 	return login(verification_uri_complete=data['verification_uri_complete']), label, []
	return homepage()

@app.callback(
	Output("authentication-button-container", "is_open"),
	Output("session-storage", 'data'),
	Output('authentication-button', 'href'),
	Input("profile-button", "n_clicks"),
	State("authentication-button-container", "is_open"),
	State('local-storage', 'data'),
	prevent_initial_call=True
)
def toggle_authentication_button(signal, is_open, data):
	if is_open:
		raise PreventUpdate()
	curl = my_Curl()
	oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
	status, token_detail, dec = oidc.check_token(data)
	if status:
		return False, {"token_valid": True, "refreshing": False, 'authenticating': False, "token": token_detail}, '#'
	elif token_detail.get('refresh_token') is not None:
		s, o = oidc.run_refresh_token_flow(token_detail.get('refresh_token'))
		print(s,o)
		if s:
			return False, {"token_valid": True, "refreshing": True, 'authenticating': False, "token": o}, '#'
	s, o, _ = oidc.run_device_authorization_flow(data)
	if s:
		return True,  {"token_valid": False, "refreshing": False, 'authenticating': True, "authentication_output": o}, o.get('verification_uri_complete', '#')
	return False, {"token_valid": False, "refreshing": False, 'authenticating': False, "authentication_output": o}, '#'


@app.callback(
	Output('local-storage', 'data'),
	Input("session-storage", 'data'),
	Input('authentication-button', 'n_clicks'),
	prevent_initial_call=True
)
def update_id_token(data, signal):
	trigger=callback_context.triggered[0]['prop_id']
	if "session-storage" in trigger:
		if data['token_valid'] and data['refreshing']:
			return data['token']
		else:
			raise PreventUpdate()
	elif data['authenticating']:
		oidc=my_Curl().get_oidc(PLogger.getPandaLogger(), verbose=True)
		authentication_output=data['authentication_output']
		if not all( [key in authentication_output for key in ['token_endpoint', 'client_id', 'client_secret', 'device_code', 'expires_in']]):
			raise PreventUpdate()
		s, o = oidc.get_id_token(
			authentication_output['token_endpoint'],
			authentication_output['client_id'],
			authentication_output['client_secret'],
			authentication_output['device_code'],
			5,
			authentication_output['expires_in']
		)
		if not s:
			raise PreventUpdate()
		return o


# @app.callback(
# 	Output('user-credentials-container', 'children'),
# 	Input('login-button', 'n_clicks'),
# 	State('user-credentials', 'data'),
# 	prevent_initial_call=True
# )
# def authenticate(signal, data):
# 	print("Getting ID token")
# 	curl=my_Curl()
# 	oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
# 	if not all([element in data for element in ['token_endpoint', 'client_id', 'client_secret', 'device_code', 'expires_in']]):
# 		oidc.log_stream.error('Not enough elements to obtain token')
# 		raise PreventUpdate()
# 	s, o = oidc.get_id_token(
# 		data['token_endpoint'],
# 		data['client_id'],
# 		data['client_secret'],
# 		data['device_code'],
# 		5, 
# 		data['expires_in']
# 	)
# 	if not s:
# 		oidc.log_stream.error(f"Cannot obtain token. Error message {o}")
# 		raise PreventUpdate()
# 	print(o)
# 	return f'{o}'

# @app.callback(
# 	Output('profile-button', 'label'),
# 	Output('profile-button', 'children'),
# 	Output('user-credentials', 'data'),
# 	Input('user-credentials', 'data'),
# 	State('url', 'pathname')
# )
# def format_login_button(data, pathname):
# 	curl=my_Curl()
# 	oidc= curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
# 	status, token, dec=oidc.check_token(data)
# 	label="login"
# 	children=[]
	
# 	if status:
# 		label = dec['preferred_username']
# 	else:
# 		label = 


# @app.callback(
# 	Output('user-credentials', 'data'),
# 	Input('refresh-button', 'n_clicks'),
# 	State('user-credentials', 'data'),
# 	prevent_initial_call=True
# )
# def get_token(signal, data):
# 	trigger = callback_context.triggered[0]['prop_id']
# 	print(trigger)
# 	curl = my_Curl()
# 	oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
# 	status, token, dec = oidc.check_token(data)
# 	if 'refresh-button' in trigger:
# 		if status:
# 			oidc.log_stream.info("Token still valid")
# 			return data
# 		try:
# 			refresh_token_string = token.get('refresh_token')
# 			s, o = oidc.fetch_page(oidc.auth_config_url)
# 			if not s:
# 				print(f'Cannot fetch {oidc.auth_config_url}')
# 				return data
# 			auth_config = o
# 			s, o = oidc.fetch_page(auth_config['oidc_config_url'])
# 			if not s:
# 				print(f"Cannot fetch {auth_config['oidc_config_url']}")
# 				return data
# 			endpoint_config = o
# 			if refresh_token_string is not None:
# 				oidc.log_stream.info('Refreshing token')
# 				s, o = oidc.refresh_token(endpoint_config['token_endpoint'], auth_config['client_id'], auth_config['client_secret'], refresh_token_string)
# 				# refreshed
# 				if s:
# 					oidc.log_stream.info('token refreshed')
# 					for key, value in o.items():
# 						data[key] = value
# 				else:
# 					if oidc.verbose:
# 						oidc.log_stream.debug('failed to refresh token: {0}'.format(o))
# 			return data
# 		except Exception as e:
# 			print(e)
# 			return {}
# 	else:
# 		return data


@app.callback(
	Output("taskID-search-alert-header", "children"),
	Output("taskID-search-alert-body", "children"),
	Output("taskID-search-alert", "is_open"),
 	Output("taskID-search-result", "children"),
	Output("taskID-search-button", "children"),
	Output("criteria-search-button", "children"),
	Output("search-result-container", "hidden"),
	Input("taskID-search-button", "n_clicks"),
	Input("criteria-search-button", "n_clicks"),
	State("taskID", "value"),
	State("criteria-username", "value"),
	State("criteria-age", "value"),
	State("criteria-taskname", "value"),
	State("taskID-search-button", "children"),
	State("criteria-search-button", "children"),
	State("search-result-container", "hidden"),
	prevent_initial_call=True)
def retrieve_taskID(signal_1, signal_2, value, username, age, taskname,  _button1, _button2, hide_result):
	trigger=callback_context.triggered[0]['prop_id']
	print(trigger)
	retriever=Retriever()
	qr = []
	taskIDs = []
	if 'taskID-search-button' in trigger:
		try:
			inputs = value.replace(" ", "").split(",")
			print(inputs)
			while True:
				taskIDs += [n for n in inputs if not "?" in n]
				inputs = [n for n in inputs if "?" in n]
				if len(inputs) == 0:
					break
				inputs = list(itertools.chain.from_iterable([[n.replace("?", "%d" % m, 1) for m in range(10)] for n in inputs]))
				taskIDs = [taskID for taskID in taskIDs if taskID.isnumeric()]
		except:
			time.sleep(1)
			return "Invalid JEDI task ID", "{} is not a valid value for a JEDI task ID. The task ID must be a positive integer.".format(
				value if value != "" else None), True, None, _button1, _button2, hide_result
		for taskID in taskIDs:
			status, res = retriever.retrieve_task(taskID=taskID)
			if status==200:
				qr += res
	elif 'criteria-search-button' in trigger:
		if not username:
			return "No username provided", "You must specify your PANDA username. Note: This username might be different from your CERN account username.", True, None, _button1, _button2, hide_result
		status, res = retriever.retrieve_task(username=username.strip(), age=age, taskname=taskname)
		if status==200:
			qr+=res
		if age:
			qr=[task for task in qr if task['age']<age]
	else:
		pass

	if len(qr) == 0:
		return "Query gets no response", "Could not get a meaningful response from BigPanda. If you are searching by task IDs, they is likely incorrect. If you are searching by username, your username might be incorrect or there are no tasks satisfying the search criteria", True, None, _button1, _button2, hide_result
	
	columns = [
		("Task ID", "jeditaskid"),
		("Username", "username"),
		("Creation Date", "creationdate"),
		("Start Time", "starttime"),
		("End Time", "endtime"),
		("Status", "status"),
		("Superstatus", "superstatus")]
	summary_table = []
	for i in range(len(qr)):
		task = qr[i]
		summary_table.append({})
		for column in columns:
			value = task[column[1]]
			try:
				value = datetime.fromisoformat(value).strftime("%H:%M:%S %m-%d-%y")
			except:
				pass
			if value == None:
				value = ""
			summary_table[i][column[0]] = value
	
	columns = [{'id': columns[i][0], 'name': columns[i][0]} for i in range(len(columns))]
	summary_table = dash_table.DataTable(
		data=summary_table, columns=columns, style_as_list_view=True,
		id="taskID-search-result-table",
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgba(50, 52, 56, 1)',
				'color': 'white'
			}
		],
		style_cell={
			'padding': '5px',
			"backgroundColor": 'rgba(50, 52, 56, 0.2)',
			"color": "black",
			"font-size": "15px",
			'height': 'auto' },
		style_header={
			'fontWeight': 'bold'
		},
		style_table={'overflowX': 'auto'},
		row_selectable="single")
	return None, None, False, summary_table, _button1, _button2, False

@app.callback(
	Output("hidden-dropdown-value", "children"),
	Input("job-detail-dropdown", "value"),
	prevent_initial_call=True
)
def record_dropdown_value(value):
	if value:
		print(value)
		return value
	else:
		return []

@app.callback(
	Output("job-detail-alert-header", "children"),
	Output("job-detail-alert-body", "children"),
	Output("job-detail-alert", "is_open"),
	Output("job-detail-dropdown", "options"),
	Output("job-detail-dropdown", "value"),
	Output("detail-container", 'hidden'),
	Output("taskID-result-title", 'children'),
	Input("taskID-search-result-table", "selected_rows"),
	State("taskID-search-result-table", "data"),
	State("detail-container", 'hidden'),
	State("taskID-result-title", 'children'),
	prevent_initial_call=True
)
def show_job_detail(row_ids, data, hide_detail, _):
	if row_ids == None or row_ids == []:
		return None, None, False, [], [], hide_detail, _
	taskID = data[row_ids[0]]["Task ID"]
	retriever = Retriever()
	status, jobs = retriever.retrieve_jobs(taskID=taskID)
	if not status == 200:
		return "Unable to retrieve jobs", "Cannot retrieve jobs with task ID %d. This might be due to bad connection. You can make another attempt to retrieve the jobs." % taskID, True, None, [], hide_detail, _
	if len(jobs) == 0:
		return "No Job Found", "Found no job for task ID %d" % taskID, True, [], [], hide_detail, _
	global df
	df = pd.DataFrame(jobs)
	if not ('computingsite' in df.columns and "jobstatus" in df.columns):
		return "Computing Sites Unavailable", "No information on computing site is available. Cannot plot the histogram", True, [], [], hide_detail, _
	
	df['durationhour'] = df["durationmin"] / 60
	
	return None, None, False, [{'label': col, 'value': col} for col in df.columns], ['computingsite', 'durationhour'], False, _

@app.callback(
	Output("job-detail", "children"),
	Input("hidden-dropdown-value", "children"),
	prevent_initial_call=True
)
def make_plots(plots):
	output = []
	for plot in plots:
		try:
			global df
			output.append(html.Div(dcc.Graph(figure=px.histogram(df, x=plot, color="jobstatus")), className="plot-container"))
		except:
			continue
	return output

### Callbacks for switching between panels in submission
@app.callback(
	Output('submission-tabs', 'value'),
	Input({'type': 'back-button', 'index': '2'}, 'n_clicks'),
	Input({'type': 'back-button', 'index': '3'}, 'n_clicks'),
	Input({'type': 'back-button', 'index': '4'}, 'n_clicks'),
	Input({'type': 'next-button', 'index': '1'}, 'n_clicks'),
	Input({'type': 'next-button', 'index': '2'}, 'n_clicks'),
	Input({'type': 'next-button', 'index': '3'}, 'n_clicks'),
	prevent_initial_call=True
)
def switch_tab(nb2,nb3,nb4, nn1, nn2, nn3):
	trigger = json.loads(callback_context.triggered[0]['prop_id'].replace('.n_clicks', ''))
	current_tab = int(trigger['index'])
	button_type = trigger['type']
	if button_type == 'back-button':
		return str(current_tab - 1)
	else:
		return str(current_tab + 1)

@app.callback(
	Output('task-config-review', 'children'),
	Input('submission-tabs', 'value')
)
def display_review(value):
	configurations = (
		("nParallelEvaluation", 'Number of parallel evaluations'),
		("maxPoints", 'Max number of points'),
		("maxEvaluationJobs", 'Max number of evaluation jobs'),
		("nPointsPerIteration", 'Number of points per iterations'),
		("minUnevaluatedPoints", 'Min number unevaluated jobs'),
		("searchAlgorithm", 'Search algorithm'),
		("sites", 'Grid sites'),
		("evaluationContainer", 'Evaluation container'),
		("evaluationExec", 'Evaluation execution'),
		("evaluationInput", 'Evaluation input'),
		("trainingDS", 'Training dataset'),
		("evaluationTrainingData", 'Training data'),
		("evaluationOutput", 'Evaluation output'),
		("evaluationMetrics", 'Evaluation metrics'),
		("customOutDS", 'Output dataset name'),
	)
	if value=='4':
		data = {}
		for att, index in configurations:
			if getattr(job_config, att):
				data[index] = [str(getattr(job_config, att))]
		table = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
		table.index.set_names('Configuration', inplace=True)
		table = dbc.Table.from_dataframe(table, striped=True, bordered=True, hover=True, index=True)	
		return table
	else:
		return None

### Callbacks for saving configurations
@app.callback(
	Output("configuration-alert", 'is_open'),
	Output("configuration-alert", 'header'),
	Output("configuration-alert", 'children'),
	Output("configuration-alert", 'icon'),
	Input({'type': 'save-button', 'index':'3'}, 'n_clicks'),
	State("nParallelEvaluation", 'value'),
	State("maxPoints", 'value'),
	State("maxEvaluationJobs", 'value'),
	State("nPointsPerIteration", 'value'),
	State("minUnevaluatedPoints", 'value'),
	State("searchAlgorithm", 'value'),
	State("sites", 'value'),
	State("evaluationContainer", 'value'),
	State("evaluationExec", 'value'),
	State("evaluationInput", 'value'),
	State("trainingDS", 'value'),
	State("evaluationTrainingData", 'value'),
	State("evaluationOutput", 'value'),
	State("evaluationMetrics", 'value'),
	State("customOutDS", 'value'),
	prevent_initial_call=True
)
def save_config(*args):
	print(callback_context.states_list)
	error_messages = []
	for state in callback_context.states_list:
		n_errors = len(error_messages)
		att = state.get('id')
		value = state.get('value')
		success, ret = check_set(att, value, job_config)
		if not success:
			error_messages.append( f'({n_errors+1}) ' + str(ret))
	if len(error_messages) == 0:
		return True, messages['configuration']['valid']['header'], messages['configuration']['valid']['body'], 'success'
	else:
		error_messages.insert(0, messages['configuration']['invalid']['body'])
		return True, messages['configuration']['invalid']['header'], '\n'.join(error_messages), 'warning'

### Change name of hyperparameter upon input name
@app.callback(Output({"type": "hyperparameter-name", "index": MATCH}, "children"), 
			Input({"type": "hyperparameter-name-input", "index": MATCH}, "value"), 
			prevent_initial_call=True)
def change_title(name):
	index=callback_context.inputs_list[0]['id']["index"]
	if name and (not bool(re.search(u"\W", name))):
		hyperparameters[index].name=name
		return name
	else:
		hyperparameters[index].name=None
		return "Undefined Hyperparameter"

### Display method dimension
@app.callback(
	Output({"type": "method-dimension-container", "index": MATCH}, "children"),
	Input({"type": "sampling-method-selector", "index": MATCH}, "value"),
	prevent_initial_call=True
)
def show_method_info(selected_method):
	index=callback_context.inputs_list[0]['id']["index"]
	messages={
		"Categorical": "The value of this hyperparameter in a hyperparameter point is uniformly picked from a list of values that you will specify.",
		'Normal': 'The numerical value of this hyperparameter or its logarithm is sampled over a Gaussian distribution defined by a mean \u03BC and variance \u03C3\u00B2 that you will specify.',
		'Uniform': 'The numberical value of this hyperparameter or logarithms is uniformly sampled from a range that you will specify'
	}
	hyperparameters[index].method=selected_method
	return hyperparameters[index].display_method

### Add value to categories
@app.callback(
	Output({"type": "display-items", "index": MATCH}, "options"),
	Output({"type": "display-items", "index": MATCH}, "value"),
	Output({"type":"item-value-input", "index": MATCH}, "value"),
	Input({"type":"add-item-button", "index": MATCH}, "n_clicks"),
	Input({"type": "display-items", "index": MATCH}, "value"),
	State({"type":"item-value-input", "index": MATCH}, "value"),
	State({"type": "display-items", "index": MATCH}, "options"),
	State({"type": "display-items", "index": MATCH}, "value"),
	prevent_initial_call=True)
def display_values(n1, activeValues, inputValue, options, values):
	index=callback_context.inputs_list[0]['id']["index"]
	triggeringInput="new-value"
	if "display-items" in callback_context.triggered[0]["prop_id"]:
		triggeringInput="active-value"
	if triggeringInput=="new-value":
		if inputValue is None: 
			inputValue = ""
		inputValue = inputValue.strip()
		if not {"label": inputValue, "value": inputValue} in options:
			hyperparameters[index].dimensions["Categorical"]["categories"].append(inputValue)
			return options + [{"label": inputValue, "value": inputValue}], values+[inputValue], ""
		else:
			return options, values, inputValue
	else: 
		hyperparameters[index].dimensions["Categorical"]['categories']=activeValues
		return options, values, inputValue

@app.callback(
	Output({"type": "low", "index": MATCH}, "valid"),
	Output({"type": "low", "index": MATCH}, "invalid"),
	Output({"type": "high", "index": MATCH}, "valid"),
	Output({"type": "high", "index": MATCH}, "invalid"),
	Input({"type": "low", "index": MATCH}, "value"),
	Input({"type": "high", "index": MATCH}, "value"),
	Input({"type": 'isInt', "index": MATCH}, 'value'),
	prevent_initial_call=True
)
def low_high_reaction(low, high, isInt):
	index=callback_context.inputs_list[0]['id']["index"]
	hyperparameters[index].dimensions['Uniform']['isInt']=isInt
	if isInt:
		if checkInt(low) and checkInt(high) and int(high)>int(low):
			hyperparameters[index].dimensions["Uniform"]["high"]=int(high)
			hyperparameters[index].dimensions["Uniform"]["low"]=int(low)
			return True, False, True, False,
		else:
			hyperparameters[index].dimensions["Uniform"]["high"]=None
			hyperparameters[index].dimensions["Uniform"]["low"]=None
			return False, True, False, True
	else:
		if checkFloat(low) and checkFloat(high) and high>low:
			hyperparameters[index].dimensions["Uniform"]["high"]=float(high)
			hyperparameters[index].dimensions["Uniform"]["low"]=float(low)
			return True, False, True, False,
		else:
			hyperparameters[index].dimensions["Uniform"]["high"]=None
			hyperparameters[index].dimensions["Uniform"]["low"]=None
			return False, True, False, True

@app.callback(
	Output({"type": "log", "index": MATCH}, "valid"),
	Output({"type": "log", "index": MATCH}, "invalid"),
	Input({"type": "log", "index": MATCH}, "value"),
	State({"type": "sampling-method-selector", "index": MATCH}, "value"),
	prevent_initial_call=True
)
def log_reaction(value, Method):
	index=callback_context.inputs_list[0]['id']["index"]
	hyperparameters[index].dimensions[Method]["base"]=value
	if value is None:
		return False, False
	elif value==0:
		hyperparameters[index].dimensions[Method]["base"]=None
		return False, True
	else:
		return True, False

@app.callback(
	Output({"type": "q", "index": MATCH}, "valid"),
	Output({"type": "q", "index": MATCH}, "invalid"),
	Input({"type": "q", "index": MATCH}, "value"),
	State({"type": "sampling-method-selector", "index": MATCH}, "value"),
	prevent_initial_call=True
)
def q_reaction(value, Method):
	index=callback_context.inputs_list[0]['id']["index"]
	hyperparameters[index].dimensions[Method]["q"]=value
	if value is None:
		return False, False
	elif value==0:
		hyperparameters[index].dimensions[Method]["q"]=None
		return False, True
	else:
		return True, False

@app.callback(
	Output({"type": "min", "index": MATCH}, "valid"),
	Output({"type": "min", "index": MATCH}, "invalid"),
	Output({"type": "max", "index": MATCH}, "valid"),
	Output({"type": "max", "index": MATCH}, "invalid"),
	Input({"type": "min", "index": MATCH}, "value"),
	Input({"type": "max", "index": MATCH}, "value"),
	State({"type": "sampling-method-selector", "index": MATCH}, "value")
)
def min_max_reaction(min, max, Method):
	index=callback_context.inputs_list[0]['id']["index"]
	# hyperparameters[index].dimensions[Method]["q"]=value
	min_valid, max_valid=True, True
	if min is not None and max is not None and min >= max:
		min_valid, max_valid=False, False
	if max is None:
		max_valid=False
	if min is None:
		min_valid=False
	if min_valid and max_valid:
		hyperparameters[index].dimensions[Method]["low"]=min
		hyperparameters[index].dimensions[Method]["high"]=max
	return min_valid, not min_valid, max_valid, not max_valid

@app.callback(
	Output({"type": "mu", "index": MATCH}, "valid"),
	Output({"type": "mu", "index": MATCH}, "invalid"),
	Output({"type": "sigma", "index": MATCH}, "valid"),
	Output({"type": "sigma", "index": MATCH}, "invalid"),
	Input({"type": "mu", "index": MATCH}, "value"),
	Input({"type": "sigma", "index": MATCH}, "value"),
	State({"type": "sampling-method-selector", "index": MATCH}, "value")
)
def mu_sigma_reaction(mu, sigma, Method):
	index=callback_context.inputs_list[0]['id']["index"]
	# hyperparameters[index].dimensions[Method]["q"]=value
	mu_valid, sigma_valid=True, True
	if mu is None:
		mu_valid=False
	if sigma is None or sigma==0:
		sigma_valid=False
	if mu_valid and sigma_valid:
		hyperparameters[index].dimensions[Method]["mu"]=mu
		hyperparameters[index].dimensions[Method]["sigma"]=sigma
	return mu_valid, not mu_valid, sigma_valid, not sigma_valid

# Save current hyperparameter and add new one
@app.callback(Output("search-space-board", "children"), 
			Output("saved-search-space", "children"),
			Output('saved-search-space-review', 'children'),

			Output("search-space-info", "children"),
			Output("search-space-info", "is_open"),

			Input("add-button", "n_clicks"), 
			Input("save-button", "n_clicks"),

			Input("upload-search-space", "contents"),
			Input("upload-search-space", "filename"),

			State("saved-search-space", "children"),
			prevent_initial_call=True)
def save_add_hyperparameter(index, saveSignal, contents, filenames, saved_hyperparameters):
	trigger=callback_context.triggered[0]["prop_id"]
	n=0
	if "add-button" in trigger:
		hyperparameters[index]=Hyperparameter(index=index)
	elif 'save-button' in trigger:
		# check the HPs in the editor for those that are valid
		print(hyperparameters)
		print(search_space)
		removing_items = {id: search_space.get(id) for id in [item.get('props',{}).get('id',{}).get('index', -1) for item in saved_hyperparameters if info in item.get('props',{}).get('title',"")]}
		for id, hp in hyperparameters.items():
			# check if it is possible to generate a search space element from the HP, this also checks if the HP is valid
			print(hp.isValid)
			if not hp.isValid: continue
			if hp.name in [element.name for element in search_space.values()]: continue
			# add HP to search_space
			search_space[id]=hp
		for id, item in search_space.items():
			if id in hyperparameters:
				hyperparameters.pop(id)
		for id, item in removing_items.items():
			if id in search_space:
				search_space.pop(id)
	else:
		for content, filename in zip(contents, filenames):
			if not filename.endswith(".json"):
				continue
			content_type, content_string = content.split(",")
			content = json.loads(base64.b64decode(content_string))
			for name, element in content.items():
				n+=task.add_hyperparameter(name, element)
	return [hp.render() for hp in hyperparameters.values()], [element.display_search_space_element() for element in search_space.values()], [element.display_search_space_element(review=True) for element in search_space.values()], html.P("%d elements were successfully loaded from the provided search space file." % n if n>0 else "None of the elements in the provided file were loaded to the search space."), 'upload-search-space' in trigger 

@app.callback(
	Output({"type": "display-searchspace-element", "index": MATCH}, "title"),
	Output({"type": "display-searchspace-element-delete", "index": MATCH}, 'children'),
	Output({"type": "display-searchspace-element-delete", "index": MATCH}, 'color'),
	Input({"type": "display-searchspace-element-delete", "index": MATCH}, 'n_clicks'),
	State({"type": "display-searchspace-element", "index": MATCH}, "title"),
	prevent_initial_call=True
)
def mark_hyperparameter_for_removal(n, title):
	if n % 2==1:
		return title + info, 'Keep hyperparameter', 'primary'
	else:
		return title.replace(info, ""), 'Mark for removal', 'danger'

@app.callback(
	Output('download-search-space', "data"),
	Output('download-config', 'data'),
	Input('download-button', 'n_clicks'),
	State('download-dropdown', "value"),
	prevent_initial_call=True
)
def download(n, files):
	return {'content': json.dumps(task.SearchSpace), 'filename': 'search_space.json'} if ('search_space' in files and len(search_space)>0) else None, {'content': job_config.to_json(), 'filename': 'config.json'} if 'configuration' in files else None, 

@app.callback(
	Output("task-conf-info", "children"),
	Output("task-conf-info", "is_open"),
	Output("configuration-container", 'children'),
	Input("upload-task-conf", "contents"),
	Input("upload-task-conf", "filename"),
	prevent_initial_call=True 
)
def load_search_space(content, filename):
	if not filename.endswith(".json"):
		return "Task configration input file must be in .json format.", True, render_job_config(job_config)
	content_type, content_string = content.split(",")
	configs = json.loads(base64.b64decode(content_string))
	failList = []
	for config, value in configs.items():
		# print(config, value)
		failList+=task.set_config(config, value)
	# print(configs)
	if len(failList) > 0:
		return "The following configurations cannot be set from the input file. Please manually set them in the Configuration \n %s" % ", ".join(
			failList), True, render_job_config(job_config)
	else:
		return "All configurations successfully set.", True, render_job_config(job_config)

curl = my_Curl()
oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
is_token_valid = False

@app.callback(
	Output("task-submit-button", "disabled"),
	Output('oidc-auth-window', 'hidden'),
	Output('oidc-auth-window', 'href'),
	Input("task-submit-button", "n_clicks"),
	prevent_initial_call=True)
def submit(signal):
	print('submit')
	# proc = (task.submit(verbose=True, files_from='demo/quick_submit'))
	# tmp_dir = f'./tmp/{uuid.uuid4()}'

	global curl
	global oidc
	global is_token_valid
	global authorization_output

	status, authorization_output, is_token_valid = oidc.my_run_device_authorization_flow()
	print(status, authorization_output, is_token_valid)
	if isinstance(authorization_output, dict) and 'verification_uri_complete' in authorization_output:
		return True, False, authorization_output['verification_uri_complete']
	else:
		return True, True, '#'

@app.callback(
	Output('task-submit-continue-after-auth-button', 'disabled'),
	Input("task-submit-continue-after-auth-button", "n_clicks"),
	prevent_initial_call=True
)
def continue_auth(signal):
	global authorization_output
	global oidc 
	global is_token_valid
	try:
		print('Getting id token')
		s, o = oidc.get_id_token(authorization_output['token_endpoint'], authorization_output['client_id'], authorization_output['client_secret'], authorization_output['device_code'], authorization_output['interval'], authorization_output['expires_in'])
		print(s,o)
	except:
		print("Unable to get id token")
	print("Does token exist?", os.path.exists(oidc.get_token_path()))
	s, id, _ = oidc.check_token()
	print(s, id, _)
	# from pandaclient import Client
	# local_curl = Client._Curl()
	# local_oidc = local_curl.get_oidc(PLogger.getPandaLogger())
	# print(local_oidc.get_token_path())
	# print("Is token exist?", os.path.exists(local_oidc.get_token_path()))
	# print(local_oidc.check_token())
	if s:
		task.submit(verbose=True, files_from='demo/quick_submit')
	else:
		print("Invalid Id Token, not submitting")
	return True

if __name__ == '__main__':
	app.run_server(debug=True)
