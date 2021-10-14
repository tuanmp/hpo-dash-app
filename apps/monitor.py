import dash_bootstrap_components as dbc
from dash import html, dcc
from .components.TaskRetriever import Retriever

def monitor(**kwargs):

	query_by_id = html.Div(
		className = "tab-content",
		children=[
			html.Div(className="label", children="Task ID(s): "),
			dcc.Input(
				className="input-element", 
				id='taskID', 
			)
		]
	)

	query_by_user = html.Div(
		className = "tab-content",
		children=[
			html.Div([
				html.Div(className="label", children="Username: "),
				dcc.Input(
					className="input-element", 
					id='criteria-username', 
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Age (days): "),
				dcc.Input(
					className="input-element", 
					id='criteria-age', 
					type='number'
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Task Name: "),
				dcc.Input(
					className="input-element", 
					id='criteria-taskname', 
					)
				]
			),
		]
	)

	tab1_content = html.Div(
		className='tab-content-container',
        children=[
            query_by_id,
            dcc.Loading(children=html.Button("Search", id= "taskID-search-button"), fullscreen=True),
        ]
	)

	tab2_content = html.Div(
		className='tab-content-container',
        children=[
            query_by_user,
            dcc.Loading(children=html.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tabs = dbc.Tabs(
		className="tabs",
		children=[
			dbc.Tab(tab1_content, label="Search by ID"),
			dbc.Tab(tab2_content, label="Advanced search"),
		]
	)

	result = html.Div(
		id="search-result-container",
		children=[
			dcc.Loading(children=html.H4(children="Search Result", id="taskID-result-title"), fullscreen=True),
			html.Div(
				id="taskID-search-result",
				children=[]	
			)
		],
		className="tab-content-container",
		hidden=True
	)

	detail = html.Div(
		id="detail-container",
		children=[
			html.H4("Job Details"),
			dcc.Dropdown(multi=True, id="job-detail-dropdown"),
			html.Div(id="job-detail")	
		],
		className="tab-content-container", 
		hidden=True
	)

	alert_taskID_search = dbc.Modal(
		children=[
			dbc.ModalHeader(id="taskID-search-alert-header"),
			dbc.ModalBody(id="taskID-search-alert-body")
		],
		id="taskID-search-alert", is_open=False, keyboard=True, size="lg"
	)

	alert_job_detail = dbc.Modal(
		children=[
			dbc.ModalHeader(id="job-detail-alert-header", style={'color': "black"}),
			dbc.ModalBody(id="job-detail-alert-body"), 
			html.Div(hidden=True, children=[], id="hidden-dropdown-value"),
		],
		id="job-detail-alert", is_open=False, keyboard=True, size="lg"
	)

	query = html.Div(
		className="content-container bright-background",
		children=[
			tabs,
			result,
			detail,
			alert_job_detail,
			alert_taskID_search
		]
	)
	
	return query
