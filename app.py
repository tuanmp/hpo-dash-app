import os, shutil, subprocess
from apps.headers import header
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash import callback_context
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px

from apps.submission import submission, render_job_config
from apps.monitor import monitor
from apps.homepage import homepage
from apps.develop import develop
from apps.footer import footer
from apps.components.utils import check_set, my_OpenIdConnect_Utils, my_Curl
import dash_bootstrap_components as dbc
from apps.components.TaskRetriever import Retriever
from apps.components.SearchSpace import Hyperparameter, SearchSpace, Hyperparameters
from apps.components.Phpo import Phpo 
from apps.components.JobConfigurations import JobConfig
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
		dcc.Location(id='url', refresh=True),
		dcc.Loading(dcc.Store(id='local-storage', storage_type='local', data=dev_token), fullscreen=True),
		html.Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css", rel="stylesheet"),
		# html.Link(href="https://codepen.io/rmarren1/pen/mLqGRg.css", rel="stylesheet"),
		header(),
		html.Div(
			id='app-page-content',
			children=[]
		),
		# footer()
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

def add_search_space_element(name, value, current_search_space):
	index = max([int(id) for id in current_search_space.keys()]) + 1
	tmp = Hyperparameter(index)
	tmp.parse(name, value)
	if tmp.isValid:
		current_search_space[index]={
			'name': name,
			'method': value['method'],
			'dimension': value['dimension']
		}
	return current_search_space


@app.callback(
	Output('app-page-content', 'children'),
	Output('profile-button', 'children'),
	# Output('profile-button', 'children'),
	# Output('user-credentials', 'data'),
	Input('url', 'hash'),
	Input('url', 'pathname'),
	# Input('user-credentials-container', 'children'),
	# State('app-page-content', 'children'),
	State('local-storage', 'data'),
	# State('task-configuration-storage','data'),
	# State('profile-button', 'label'),
	# State('profile-button', 'children'),
)
def navigate(hash, pathname, data):

	oidc = my_Curl().get_oidc(PLogger.getPandaLogger(), verbose=True)
	status, token, dec = oidc.check_token(data)

	try:
		label = dec['preferred_username']
	except:
		label = 'Sign in'
	if pathname=='/submission':
		return submission(), label
	elif pathname=='/home':
		return homepage(), label
	elif pathname=='/monitor':
		return monitor(), label
	# elif pathname=='/develop':
	# 	return develop(uid), label
	return submission(), label

@app.callback(
	Output("authentication-button-container", "is_open"),
	Output("authentication-button-container", "title"),
	Output('authentication-message', 'children'),
	Output('signin-button-container', 'hidden'),
	Output('signout-button-container', 'hidden'),
	Output("session-storage", 'data'),
	Output('authentication-button', 'href'),
	Input("profile-button", "n_clicks"),
	Input('signout-button', 'n_clicks'),
	State("authentication-button-container", "is_open"),
	State('local-storage', 'data'),
	prevent_initial_call=True
)
def toggle_authentication_button(signal, signout_signal, is_open, data):
	trigger = callback_context.triggered[0]['prop_id']
	if 'signout-button' in trigger:
		return False, "", ["", dcc.Location(href='/home', id='extra-location')], True, True, {"token_valid": False, "refreshing": False, 'authenticating': False, 'signout': True}, '#'
	if is_open:
		raise PreventUpdate()
	curl = my_Curl()
	oidc = curl.get_oidc(PLogger.getPandaLogger(), verbose=True)
	status, token_detail, dec = oidc.check_token(data)
	if status:
		return True, "Valid ID token available", "No further action required.", True, False, {"token_valid": True, "refreshing": False, 'authenticating': False, "token": token_detail}, '#'
	elif token_detail.get('refresh_token') is not None:
		s, o = oidc.run_refresh_token_flow(token_detail.get('refresh_token'))
		print(s,o)
		if s:
			return True,  "Valid ID token available", "No further action required.", True, False, {"token_valid": True, "refreshing": True, 'authenticating': False, "token": o}, '#'
	s, o, _ = oidc.run_device_authorization_flow(data)
	if s:
		return True, "Valid ID token unavailable", "Following the following link to authenticate with PANDA server", False, True, {"token_valid": False, "refreshing": False, 'authenticating': True, "authentication_output": o}, o.get('verification_uri_complete', '#')
	return True, "Valid ID token unavailable", "Sign out and reauthenticate", False, True, {"token_valid": False, "refreshing": False, 'authenticating': False, "authentication_output": o}, '#'


@app.callback(
	Output('local-storage', 'data'),
	# Output('storage-container', 'children'),
	Input("session-storage", 'data'),
	Input('authentication-button', 'n_clicks'),
	prevent_initial_call=True
)
def update_id_token(data, signal):
	trigger=callback_context.triggered[0]['prop_id']
	if "session-storage" in trigger:
		if data.get('signout')==True:
			print('signin out')
			return {}
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
	raise PreventUpdate()

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
	Output('saved-search-space-review', 'children'),
	Input('submission-tabs', 'value'),
	State('task-configuration-storage','data'),
	State('search-space-storage', 'data'),
	prevent_initial_call=True
)
def display_review(value, saved_data, search_space_data):
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
		("evaluationOutput", 'Evaluation output'),
		("evaluationMetrics", 'Evaluation metrics'),
		("customOutDS", 'Output dataset name'),
	)
	if value=='4':
		job_config = JobConfig()
		job_config.parse(saved_data)
		ss = SearchSpace()
		ss.parse_from_memory(search_space_data)
		data = {}
		for att, index in configurations:
			if getattr(job_config, att):
				data[index] = [str(getattr(job_config, att))]
		table = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
		table.index.set_names('Configuration', inplace=True)
		table = dbc.Table.from_dataframe(table, striped=True, bordered=True, hover=True, index=True)	
		return table, [item.display_search_space_element() for item in ss.search_space_objects.values()]
	else:
		raise PreventUpdate()

### Callbacks for saving configurations
@app.callback(
	# Output("configuration-alert", 'is_open'),
	# Output("configuration-alert", 'header'),
	# Output("configuration-alert", 'children'),
	# Output("configuration-alert", 'icon'),
	Output("configuration-container", 'children'),
	Output('task-configuration-storage','data'),
	Input({'type': 'save-button', 'index':'3'}, 'n_clicks'),
	Input("upload-task-conf", "contents"),
	Input("upload-task-conf", "filename"),
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
	# State("evaluationTrainingData", 'value'),
	State("evaluationOutput", 'value'),
	State("evaluationMetrics", 'value'),
	State("customOutDS", 'value'),
	# State('task-configuration-storage','data'),
	prevent_initial_call=True
)
def save_config(*args):
	trigger=callback_context.triggered[0]['prop_id']
	error_messages = []
	job_config = JobConfig()
	if 'save-button' in trigger:
		for state in callback_context.states_list:
			n_errors = len(error_messages)
			att = state.get('id')
			value = state.get('value')
			if att=='task-configuration-storage': continue
			success, ret = check_set(att, value, job_config)
			if not success:
				error_messages.append( f'({n_errors+1}) ' + str(ret))
	 #True, messages['configuration']['invalid']['header'], '\n'.join(error_messages), 'warning'
	else:
		filename=args[2]
		content=args[1]
		content_type, content_string = content.split(",")
		configs = json.loads(base64.b64decode(content_string))
		for att, value in configs.items():
			success, ret = check_set(att, value, job_config)
			if not success:
				print(f"{att}: {value} not set. {ret}")
	return render_job_config(job_config), job_config.storage_config

@app.callback(
	Output('name-input', 'value'),
	Output('search-space-storage', 'data'),
	Output("search-space-board", "children"), 
	Input('add-button', 'n_clicks'), 
	# Input({"type":"add-item-button", "index": ALL}, "n_clicks"),
	Input({"type": "sampling-method-selector", "index": ALL}, "value"),
	Input({"type": 'max', "index": ALL}, 'value'),
	Input({"type": 'min', "index": ALL}, 'value'),
	Input({"type":"item-value-input", "index": ALL}, 'value'),
	Input({"type": "delete-button", "index": ALL}, 'n_clicks'),
	Input("upload-search-space", "contents"),
	State("upload-search-space", "filename"),
	# Input({"type": "display-items", "index": ALL}, 'value'),
	State('search-space-storage', 'data'),
	State('name-input', 'value'),
	
	prevent_initial_call=True
)
def modify_search_space(signal, method_list, maxes, mins, category_inputs, delete_signal, content, filename, data, name):
	trigger=callback_context.triggered[0]['prop_id']
	ss = SearchSpace()
	# print(data)
	ss.parse_from_memory(data)
	print(f'Parsed search space: {ss.search_space}')
	if "add-button" in trigger:
		if not name:
			raise PreventUpdate()
		ss.add_hyperparameter(name)
		return "", ss.search_space, [hp.render() for hp in ss.search_space_objects.values()]
	if 'upload-search-space' in trigger:
		if not filename.endswith(".json"):
			raise PreventUpdate()
		content_type, content_string = content.split(",")
		content = json.loads(base64.b64decode(content_string))
		for name, element in content.items():
			ss.add_hyperparameter(name, element)
		return "", ss.search_space, [hp.render() for hp in ss.search_space_objects.values()]
	index = json.loads(trigger.split('.')[0])['index']
	if "sampling-method-selector" in trigger:
		method = method_list[index]
		ss.search_space[index]['method'] = method
	elif "min" in trigger:
		ss.search_space[index]['dimension']['low'] = mins[index]
	elif 'max' in trigger:
		ss.search_space[index]['dimension']['high'] = maxes[index]
	elif 'item-value-input' in trigger:
		category_inputs=category_inputs[index].replace(' ', '').split(',')
		ss.search_space[index]['dimension']['categories'] = category_inputs
	elif 'delete-button' in trigger:
		ss.search_space.pop(index)
	print(f'Current search space: {ss.search_space}')

	return '', ss.search_space, [hp.render() for hp in ss.search_space_objects.values()]

@app.callback(
	Output('additional-file-storage', 'data'),
	Input('upload-additional-file', 'contents'),
	State('upload-additional-file', 'filename'),
	State('additional-file-storage', 'data'),
	prevent_initial_call=True
)
def upload_additional_file(contents, filename, data):
	# print(contents, filename)
	print(data)
	dst = data.get('tmp_file_location', f'tmp/{uuid.uuid4()}')
	data['tmp_file_location'] = dst
	if not os.path.isdir(dst):
		os.makedirs(dst, exist_ok=True)
	for name, content in zip(filename, contents):
		content_type, content_string = content.split(",")
		content = base64.b64decode(content_string).decode('utf-8')
		with open(f'{dst}/{name}', 'w') as f:
			f.write(content)
	return data

@app.callback(
	Output('download-search-space', "data"),
	Output('download-config', 'data'),
	Input('download-button', 'n_clicks'),
	State('download-dropdown', "value"),
	State('task-configuration-storage','data'),
	State('search-space-storage', 'data'),
	prevent_initial_call=True
)
def download(n, files, task_config, search_space):
	job_config = JobConfig()
	job_config.parse(task_config)
	ss = SearchSpace()
	ss.parse_from_memory(search_space)
	return {'content': json.dumps(ss.json_search_space), 'filename': 'search_space.json'} if ('search_space' in files and len(search_space)>0) else None, {'content': json.dumps(job_config.config), 'filename': 'config.json'} if 'configuration' in files else None, 

@app.callback(
	Output('task-submit-button-container', 'hidden'),
	Output('task-submission-alert-title', 'children'),
	Output('task-submission-alert-body', 'children'),
	Output('task-submission-alert', 'is_open'),
	Input('task-verification', 'n_clicks'),
	State('search-space-storage', 'data'),
	State('task-configuration-storage','data'),
	State('local-storage', 'data'),
	prevent_initial_call=True
)
def check_task(n, search_space, task_config, token_data):
	oidc= my_Curl().get_oidc(PLogger.getPandaLogger(), verbose=True)
	status, token_detail, dec = oidc.check_token(token_data)
	if not status and token_detail.get('refresh_token') is not None:
		return True, "Your ID token has expired", "Click on your username to refresh the token", True
	elif not status:
		return True, "Your ID token is invalid", "If you have not signed in, please sign in. Otherwise, sign out and reauthenticated.", True
	exp_time = datetime.datetime.utcfromtimestamp(dec['exp'])
	if status and datetime.datetime.utcnow() + datetime.timedelta(seconds=120) > exp_time:
		return True, "Your ID token is expiring soon", "Click on your username to refresh the token.", True
	job_config = JobConfig()
	job_config.parse(task_config)
	status, error_config = job_config.is_valid
	if not status:
		return True, "Your task config is invalid", f"Please check the following configuration: {error_config}", True
	ss = SearchSpace()
	ss.parse_from_memory(search_space)
	is_valid = ss.is_valid
	if len(is_valid)==0:
		return True, "Empty search space", f"The search space must have at least one hyperparameter. Please return to 'Search Space' tab to define the search", True
	for status, error in ss.is_valid:
		if not status:
			return True, "One of the hyperparameters is invalid", f"{error}", True
	return False, "Task ready to submit", "Click on Submit button to submit task", True


@app.callback(
	Output("submission-status-alert", "is_open"),
	Input("task-submit-button", "n_clicks"),
	State('search-space-storage', 'data'),
	State('task-configuration-storage','data'),
	State('local-storage', 'data'),
	State('additional-file-storage', 'data'),
	prevent_initial_call=True)
def submit(signal, search_space, task_config, token_data, file_location):
	if file_location.get('tmp_file_location') is None:
		file_location['tmp_file_location']=f'tmp/{uuid.uuid4()}'
	tmp_dir = file_location.get('tmp_file_location')
	os.makedirs(tmp_dir, exist_ok=True)
	# uid = tmp_dir.split('/')[-1]
	# token_file = f'.token-{uid}'
	token_file='.token'
	token_dir = os.environ['PANDA_CONFIG_ROOT']
	token_dir = os.path.expanduser(token_dir)
	os.makedirs(token_dir, exist_ok=True)
	with open(os.path.join(token_dir, '.token'), 'w') as f:
		print(f'dumping new token at {os.path.join(token_dir, token_file)}')
		token=json.dumps(token_data)
		f.write(token)
	job_config = JobConfig()
	job_config.parse(task_config)
	ss = SearchSpace()
	ss.parse_from_memory(search_space)
	task=Phpo(job_config=job_config, id_token=token_data['id_token'], verbose=True, tmp_dir=tmp_dir, token_file=token_file)
	task.HyperParameters = ss.search_space_objects
	cu_dir = os.getcwd()
	os.chdir(tmp_dir)
	with open("config.json", 'w') as f:
		json.dump(job_config.config, f)
	with open('search_space.json', 'w') as f:
		json.dump(ss.json_search_space, f)
	cmd = 'phpo --loadJson config.json --searchSpaceFile search_space.json -v'
	os.system(cmd)
	os.chdir(cu_dir)
	# task.submit()	
	return True

@app.callback(
	Output({'type': 'help-panel', 'index': MATCH}, 'is_open'),
	Input({'type': 'help-button', 'index': MATCH}, 'n_clicks'),
	prevent_initial_call=True
)
def open_help_panel(signal):
	return True

if __name__ == '__main__':
	app.run_server(debug=True)