import datetime
import itertools
import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash import callback_context
import plotly.express as px

from hpogui.dash.components.TaskRetriever import Retriever
from hpogui.dash.main import app

df = pd.DataFrame()

popover_children = {
	'username': [
    dbc.PopoverHeader("Username"),
    dbc.PopoverBody("This field is optional if you have done the grid authentication."),
],
	'age': [
    dbc.PopoverHeader("(Optional) Maximum task age."),
    dbc.PopoverBody("Return all tasks that are less than or equal to this number of days in age."),
],
	'taskname': [
    dbc.PopoverHeader("(Optional) Name submitted task"),
    dbc.PopoverBody("Partial task name. Return all tasks whose name contains this value."),
],
}

query = dbc.Row(
	html.Div(
		children=[html.H4("Search by criteria", className="underline"),
				  dbc.FormGroup(
					  [
						dbc.Label(
							"Username", width=2, align="center",
							color="white", size="lg", style={"padding": "0 0.5rem"}),
						dbc.Col(
							dbc.Input(id="criteria-username"), width=4),
						dbc.Label(
							"Age (days)", width=2, align="center",
							color="white", size="lg", style={"padding": "0 0.5rem"}),
						dbc.Col(
							dbc.Input(id="criteria-age", type='number'), width=4),
						dbc.Popover(popover_children['username'], target="criteria-username", trigger="focus"),
						dbc.Popover(popover_children["age"], target="criteria-age", trigger="focus")
					  ], row=True, className="no-gutters"),
				dbc.FormGroup(
					  [
						dbc.Label(
							"Taskname", width=2, align="center",
							color="white", size="lg", style={"padding": "0 0.5rem"}),
						dbc.Col(
							dbc.Input(id="criteria-taskname"), width=4),
						dbc.Popover(popover_children['taskname'], target="criteria-taskname", trigger="focus")
					  ], row=True, className="no-gutters"),
				  dbc.Row(dbc.Button(
					  "Make Query", id={"type": "taskID-search-button", "index": "criteria"},
					  color="info"), no_gutters=True, justify="end")
				  ], className="monitor-body"), no_gutters=True)

result = dbc.Row(
	dcc.Loading(
		html.Div(
			[html.H4("Search Result", className="underline"),
			 html.Div(id={"type": "taskID-search-result", "index": "criteria"})
			 ]),
		parent_className="monitor-body", fullscreen=True),
	no_gutters=True)

detail = dbc.Row(
	dcc.Loading(
		html.Div(
			[html.H4("Job Details", className="underline"),
			 dcc.Dropdown(multi=True, id={"type": "job-detail-dropdown", "index": "criteria"}),
			 dbc.Row(id={"type": "job-detail", "index": "criteria"}, no_gutters=True)
			 ]),
		parent_className="monitor-body", fullscreen=True),
	no_gutters=True)

alert_taskID_search = dbc.Modal(
	children=[dbc.ModalHeader(id={"type": "taskID-search-alert-header", "index": "criteria"}, style={'color': "black"}),
			  dbc.ModalBody(id={"type": "taskID-search-alert-body", "index": "criteria"})],
	id={"type": "taskID-search-alert", "index": "criteria"}, is_open=False, keyboard=True, size="lg")

alert_job_detail = dbc.Modal(
	children=[dbc.ModalHeader(id={"type": "job-detail-alert-header", "index": "criteria"}, style={'color': "black"}),
			  dbc.ModalBody(id={"type": "job-detail-alert-body", "index": "criteria"}), 
			  html.Div(hidden=True, children=[], id="hidden-dropdown-value"),],
	id={"type": "job-detail-alert", "index": "criteria"}, is_open=False, keyboard=True, size="lg")



@app.callback(
	Output({"type": "taskID-search-alert-header", "index": "criteria"}, "children"),
	Output({"type": "taskID-search-alert-body", "index": "criteria"}, "children"),
	Output({"type": "taskID-search-alert", "index": "criteria"}, "is_open"),
 	Output({"type": "taskID-search-result", "index": "criteria"}, "children"),
	Input({"type": "taskID-search-button", "index": "criteria"}, "n_clicks"),
	State("criteria-username", "value"),
	State("criteria-age", "value"),
	State("criteria-taskname", "value"),
	prevent_initial_call=True)
def query_user(signal, username, age, taskname):
	index=callback_context.inputs_list[0]['id']["index"]
	retriever=Retriever()
	retriever.get_username_from_conf()
	qr = []
	qr+=retriever.retrieve_all_taskId(username=username, days=age, taskname="*{}*".format(taskname) if taskname!=None else None)
	if age:
		qr=[task for task in qr if task['age']<age]
	
	if len(qr) == 0:
		return "Query gets no response", "Could not get a meaningful response from BigPanda. The task ID is likely incorrect.", True, None
	
	columns = [
		("Task ID", "jeditaskid"),
		("Username", "username"),
		("Creation Date", "creationdate"),
		("Start Time", "starttime"),
		("End Time", "endtime"),
		("Status", "status"),
		("Super Status", "superstatus")]
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

