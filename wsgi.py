import os
from apps.headers import header
import dash
from dash import dcc
from dash import html
from dash import callback_context
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH
import plotly.express as px

from apps.submission import submission
from apps.monitor import monitor
from apps.homepage import homepage
from apps.footer import footer
import dash_bootstrap_components as dbc
from apps.components.TaskRetriever import Retriever
import time

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

application = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css", rel="stylesheet"),
    html.Link(href="https://codepen.io/rmarren1/pen/mLqGRg.css", rel="stylesheet"),
    header(),
    html.Div(
        id='app-page-content',
        children=[
        ]
    ),
    footer()
], style={'height': "100vh"})

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
        return submission()
    elif pathname=='/monitor':
        return monitor()
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

if __name__ == '__main__':
    app.run_server(debug=True)
