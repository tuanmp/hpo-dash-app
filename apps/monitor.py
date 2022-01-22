import dash_bootstrap_components as dbc
from dash import html, dcc
from .components.TaskRetriever import Retriever

def monitor(**kwargs):
	transition_style={'transition': 'opacity 1000ms ease'}
	SIDEBAR_STYLE = {
		# "position": "fixed",
		# "top": 0,
		# "right": 0,
		# "bottom": 0,
		'height': '100vh',
		# "width": "16rem",
		"padding": "2rem rem",
		"background-color": "#f8f9fa",
	}
	query_by_id = html.Div(
		[
			html.Div(className="label", children="Task ID(s): "),
			dcc.Input(
				className="input-element", 
				id='taskID', 
			)
		]
	)

	query_by_user = html.Div(
		[
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

	tab1_content = dcc.Tab(
        [
            query_by_id,
            dcc.Loading(children=dbc.Button("Search", id= "taskID-search-button"), fullscreen=True),
        ],
		id='query-by-id',
		label='Search by JEDI task ID'
	)

	tab2_content = dcc.Tab(
		className='tab-content-container',
        children=[
            query_by_user,
            dcc.Loading(children=dbc.Button("Search", id="criteria-search-button"), fullscreen=True),
        ],
		id='query-by-user',
		label='Advanced Search'
	)

	tabs = dcc.Tabs(
		[
			tab1_content,
			tab2_content,
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

	alert_taskID_search = dbc.Offcanvas(
		children=[
			dbc.ModalHeader(id="taskID-search-alert-header"),
			dbc.ModalBody(id="taskID-search-alert-body")
		],
		id="taskID-search-alert", is_open=False, keyboard=True
	)

	alert_job_detail = dbc.Offcanvas(
		children=[
			dbc.ModalHeader(id="job-detail-alert-header", style={'color': "black"}),
			dbc.ModalBody(id="job-detail-alert-body"), 
			html.Div(hidden=True, children=[], id="hidden-dropdown-value"),
		],
		id="job-detail-alert", is_open=False, keyboard=True
	)

	query = dbc.Container(
		[
			tabs,
			result,
			detail,
			alert_job_detail,
			alert_taskID_search
		],
		style={'padding': '30px 20px'}
	)
	
	return query
