import os, shutil, subprocess
from apps.headers import header
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash import callback_context
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH
import plotly.express as px

from apps.submission import submission, render_job_config
from apps.monitor import monitor
from apps.homepage import homepage
from apps.develop import develop
from apps.footer import footer
from apps.components.utils import check_set, my_OpenIdConnect_Utils, my_Curl
import dash_bootstrap_components as dbc
from apps.components.TaskRetriever import Retriever
from apps.components.SearchSpace import Hyperparameter
from apps.components.Phpo import Phpo 
from apps.components.utils import get_index, getMethod
import time
import json, yaml, base64
import re
import uuid 
from pandaclient import PLogger
# from queue import Queue, Empty
# from threading import Thread

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
app.title='hpogui'

application = app.server

app.layout = html.Div(
	[
		dcc.Location(id='url', refresh=False),
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
	Input('url', 'hash'),
	Input('url', 'pathname'),
	State('app-page-content', 'children'),
)
def navigate(hash, pathname, page_content):
	print(pathname)
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
		return submission(config=job_config, hyperparameters=hyperparameters, search_space=search_space)
	elif pathname=='/monitor':
		return monitor()
	elif pathname=='/develop':
		return develop()
	return homepage()

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
oidc = curl.get_my_oidc(PLogger.getPandaLogger(), verbose=True)

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

	s, o = oidc.my_run_device_authorization_flow()
	print(s,o)
	global authorization_output
	authorization_output = o
	if isinstance(authorization_output,dict) and 'verification_uri_complete' in authorization_output:
		return True, False, o['verification_uri_complete']
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
	if 'interval' in authorization_output:
		print('Getting id token')
		s, o = oidc.get_id_token(authorization_output['token_endpoint'], authorization_output['client_id'], authorization_output['client_secret'], authorization_output['device_code'], authorization_output['interval'], authorization_output['expires_in'])
		print(s,o)
	print("Is token exist?", os.path.exists(oidc.get_token_path()))
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
