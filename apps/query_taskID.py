import datetime
import itertools
import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH
from dash import callback_context
import plotly.express as px

from hpogui.dash.components.TaskRetriever import Retriever
from hpogui.dash.main import app

df = pd.DataFrame()

popover_children = [
    dbc.PopoverHeader("Enter task IDs"),
    dbc.PopoverBody("Enter one or multiple comma-separated task IDs. If you want to scan over a digit, put a '?' in its place. \nFor example, '100000?0' is equivalent to '10000000, 10000010, 10000020, 10000030, 10000040, 10000050, 10000060, 10000070, 10000080, 10000090'"),
]

query = dbc.Row(
	html.Div(
		children=[html.H4("Search by JEDI task ID", className="underline"),
				  dbc.FormGroup(
					  [
						  dbc.Label(
							  "Task ID", width=2, align="center",
							  color="white", size="lg", style={"padding": "0 0.5rem"}),
						  dbc.Col(
							  dbc.Input(id="taskID"), width=10),
						dbc.Popover(popover_children, id="taskID-popover", target="taskID", trigger="focus")
					  ], row=True, className="no-gutters"),
				  dbc.Row(dbc.Button(
					  "Make Query", id={"type": "taskID-search-button", "index": "taskID"},
					  color="info"), no_gutters=True, justify="end")
				  ], className="monitor-body"), no_gutters=True)

result = dbc.Row(
	dcc.Loading(
		html.Div(
			[html.H4("Search Result", className="underline"),
			 html.Div(id={"type": "taskID-search-result", "index": "taskID"})
			 ]),
		parent_className="monitor-body", fullscreen=True),
	no_gutters=True)

detail = dbc.Row(
	dcc.Loading(
		html.Div(
			[html.H4("Job Details", className="underline"),
			 dcc.Dropdown(multi=True, id={"type": "job-detail-dropdown", "index": "taskID"}),
			 dbc.Row(id={"type": "job-detail", "index": "taskID"}, no_gutters=True)
			 ]),
		parent_className="monitor-body", fullscreen=True),
	no_gutters=True)

alert_taskID_search = dbc.Modal(
	children=[dbc.ModalHeader(id={"type": "taskID-search-alert-header", "index": "taskID"}, style={'color': "black"}),
			  dbc.ModalBody(id={"type": "taskID-search-alert-body", "index": "taskID"})],
	id={"type": "taskID-search-alert", "index": "taskID"}, is_open=False, keyboard=True, size="lg")

alert_job_detail = dbc.Modal(
	children=[dbc.ModalHeader(id={"type": "job-detail-alert-header", "index": "taskID"}, style={'color': "black"}),
			  dbc.ModalBody(id={"type": "job-detail-alert-body", "index": "taskID"}), 
			  html.Div(hidden=True, children=[], id={"type": "hidden-dropdown-value", "index": "taskID"}),],
	id={"type": "job-detail-alert", "index": "taskID"}, is_open=False, keyboard=True, size="lg")


@app.callback(
	Output({"type": "taskID-search-alert-header", "index": "taskID"}, "children"),
	Output({"type": "taskID-search-alert-body", "index": "taskID"}, "children"),
	Output({"type": "taskID-search-alert", "index": "taskID"}, "is_open"),
 	Output({"type": "taskID-search-result", "index": "taskID"}, "children"),
	Input({"type": "taskID-search-button", "index": "taskID"}, "n_clicks"),
	State("taskID", "value"),
	prevent_initial_call=True)
def check_taskID(signal, value):
	index=callback_context.inputs_list[0]['id']["index"]
	retriever=Retriever()
	retriever.get_username_from_conf()
	qr = []
	taskIDs = []
	try:
		inputs = value.split(",")
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
			value if value != "" else None), True, None
	for taskID in taskIDs:
		qr += retriever.retrieve_taskId(taskId=taskID)
	
	if len(qr) == 0:
		return "Query gets no response", "Could not get a meaningful response from BigPanda. The task ID is likely incorrect.", True, None
	
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
		id={"type": "taskID-search-result-table", "index": index},
		style_data_conditional=[
			{
				'if': {'row_index': 'odd'},
				'backgroundColor': 'rgba(50, 52, 56, 1)'
			}
		],
		style_cell={
			'padding': '5px',
			"backgroundColor": 'rgba(50, 52, 56, 0.2)',
			"color": "white",
			"font-size": "0.9rem",
			'height': 'auto' },
		style_header={
			'fontWeight': 'bold'
		},
		style_table={'overflowX': 'auto'},
		#selected_rows=[],
		row_selectable="single")
	return None, None, False, summary_table


@app.callback(
	Output({"type": "hidden-dropdown-value", "index": MATCH}, "children"),
	Input({"type": "job-detail-dropdown", "index": MATCH}, "value"),
	prevent_initial_call=True
)
def record_dropdown_value(value):
	if value:
		print(value)
		return value
	else:
		return []


@app.callback(
	Output({"type": "job-detail-alert-header", "index": MATCH}, "children"),
	Output({"type": "job-detail-alert-body", "index": MATCH}, "children"),
	Output({"type": "job-detail-alert", "index": MATCH}, "is_open"),
	Output({"type": "job-detail-dropdown", "index": MATCH}, "options"),
	Output({"type": "job-detail-dropdown", "index": MATCH}, "value"),
	Input({"type": "taskID-search-result-table", "index": MATCH}, "selected_rows"),
	State({"type": "taskID-search-result-table", "index": MATCH}, "data"),
	prevent_initial_call=True
)
def show_job_detail(row_ids, data):
	if row_ids == None or row_ids == []:
		return None, None, False, [], []
	taskID = data[row_ids[0]]["Task ID"]
	try:
		qr = Retriever.retrieve_jobs(taskId=taskID)
	except:
		return "Unable to retrieve jobs", "Cannot retrieve jobs with task ID %d. This might be due to bad connection. You can make another attempt to retrieve the jobs." % taskID, True, None, [], []
	jobs = qr[-1]["jobs"]
	if len(jobs) == 0:
		return "No Job Found", "Found no job for task ID %d" % taskID, True, [], []
	global df
	df = pd.DataFrame(jobs)
	if not ('computingsite' in df.columns and "jobstatus" in df.columns):
		return "Computing Sites Unavailable", "No information on computing site is available. Cannot plot the histogram", True, [], []
	
	df['durationhour'] = df["durationmin"] / 60
	
	return None, None, False, [{'label': col, 'value': col} for col in df.columns], ['computingsite', 'durationhour'] 

@app.callback(
	Output({"type": "job-detail", "index": MATCH}, "children"),
	Input({"type": "hidden-dropdown-value", "index": MATCH}, "children"),
	prevent_initial_call=True
)
def make_plots(plots):
	output = []
	for plot in plots:
		try:
			global df
			output.append(dbc.Col(dcc.Graph(figure=px.histogram(df, x=plot, color="jobstatus")), width=6))
		except:
			continue
	return output