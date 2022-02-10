from dash import html, dcc
import dash_bootstrap_components as dbc
from apps.components.utils import info_button_style, full_width_style, label_with_info_button

BUTTONS = [
    ("File Upload",  'file_upload'),
    ("Task Configurations", 'task_config'),
    ("Search Space", 'search_space'),
    ("Review", 'review')
]

def render_job_config(job_config):
	short_configurations = dbc.Container(
		dbc.Row(
			[
				dbc.Col(
					[
						html.Div([
							label_with_info_button("Number of parallel evaluations"),
							dbc.Input(
								className="input-element", 
								id='nParallelEvaluation', 
								type='number',
								min=1, 
								step=1, 
								value=job_config.nParallelEvaluation,
								required=True,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Max number of evaluation jobs"),
							# html.Div(className="label", children="Max evaluation jobs: "),
							dbc.Input(
								className="input-element", 
								id='maxEvaluationJobs', 
								type='number',
								min=1, 
								step=1, 
								value=job_config.maxEvaluationJobs,
								required=True,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Min number unevaluated jobs"),
							# html.Div(className="label", children="Min unevaluated jobs: "),
							dbc.Input(
								className="input-element", 
								id='minUnevaluatedPoints', 
								type='number',
								min=0, 
								step=1, 
								value=job_config.minUnevaluatedPoints,
								required=True,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Training dataset"),
							# html.Div(className="label", children="Training dataset: "),
							dbc.Input(
								className="input-element", 
								id='trainingDS', 
								value=job_config.trainingDS,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Evaluation output"),
							# html.Div(className="label", children="Evaluation output: "),
							dbc.Input(
								className="input-element", 
								id='evaluationOutput', 
								value=job_config.evaluationOutput,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Output dataset name"),
							# html.Div(className="label", children="Output dataset: "),
							dbc.Input(
								className="input-element", 
								id='customOutDS', 
								value=job_config.customOutDS,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
					],
					width=6,
					# style={'padding-right': '5%'}
				),

				dbc.Col(
					[
						html.Div([
							label_with_info_button("Max number of points"),
							# html.Div(className="label", children="Max points: "),
							dbc.Input(
								className="input-element", 
								id='maxPoints', 
								type='number',
								min=1, 
								step=1, 
								value=job_config.maxPoints,
								required=True,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Number of points per iterations"),
							# html.Div(className="label", children="Points per iterations: "),
							dbc.Input(
								className="input-element", 
								id='nPointsPerIteration', 
								type='number',
								min=1, 
								step=1, 
								value=job_config.nPointsPerIteration,
								required=True,
								persistence=True,
								persistence_type="memory",
								)
							]
						),
						html.Div([
							label_with_info_button("Evaluation input"),
							# html.Div(className="label", children="Evaluation input: "),
							dbc.Input(
								className="input-element", 
								id='evaluationInput', 
								value=job_config.evaluationInput,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Training data"),
							# html.Div(className="label", children="Training data: "),
							dbc.Input(
								className="input-element", 
								id='evaluationTrainingData', 
								value=job_config.evaluationTrainingData,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
						html.Div([
							label_with_info_button("Evaluation metrics"),
							# html.Div(className="label", children="Evaluation metrics: "),
							dbc.Input(
								className="input-element", 
								id='evaluationMetrics', 
								value=job_config.evaluationMetrics,
								persistence=True,
								persistence_type="memory"
								)
							]
						),
					]
				)
			]
		)
	)

	long_configurations = dbc.Container(
		[
			html.Div([
				label_with_info_button("Search algorithm"),
				# html.Div(["Search algorithm: ", dbc.Badge("info", color="dark")]),
				dcc.Dropdown(
					id='searchAlgorithm', 
					value=job_config.searchAlgorithm,
					options=[{'label': i, 'value': i} for i in job_config._searchAlgOptions],
					persistence=True,
					persistence_type="memory",
					clearable=False
					)
				]
			),
			html.Div([
				label_with_info_button("Grid sites"),
				# html.Div(className="label", children="Grid sites: "),
				dcc.Dropdown(
					id='sites', 
					value=job_config.sites,
					options=[{'label': i, 'value': i} for i in job_config._siteOptions],
					persistence=True,
					persistence_type="memory",
					clearable=False,
					multi=True
					)
				]
			),
			html.Div([
				label_with_info_button("Evaluation container"),
				# html.Div(className="label", children="Evaluation container: "),
				dbc.Input(
					className="input-element", 
					id='evaluationContainer', 
					value=job_config.evaluationContainer,
					required=True,
					persistence=True,
					persistence_type="memory",
					style=full_width_style
					)
				]
			),
			html.Div([
				label_with_info_button("Evaluation execution"),
				# html.Div(className="label", children="Evaluation execution: "),
				dcc.Textarea(
					className="input-element", 
					rows=5,
					id='evaluationExec', 
					contentEditable=True,
					required=True,
					value=job_config.evaluationExec,
					persistence=True,
					persistence_type="memory",
					style=full_width_style
					)
				]
			),	
		]
	)
	
	configurations = html.Div(
		[
			short_configurations,
			long_configurations
		]
	)

	return configurations

def submission(**kwargs):
	job_config = kwargs.get('config', {})
	hyperparameters = kwargs.get('hyperparameters', {})
	searchspace = kwargs.get('search_space',{})

	file_upload = html.Div(
		className = "tab-content",
		children=[
			html.Div("Select file: "),
			dcc.Upload(
				[
					'Drag and drop a search space json file or ',
					dbc.Button("Upload", outline=True, color='primary')
				], className="upload", id="upload-search-space", filename=[], contents=[], multiple=True
			),
			dcc.Upload(
				[
					'Drag and drop a configuration json file or ',
					dbc.Button("Upload", outline=True, color='primary')
				], className="upload", id="upload-task-conf", filename=[], contents=[], multiple=False
			),
			dbc.Offcanvas(
				html.P("Some offcanvas content..."),
				id="search-space-info",
				title="Search space loaded...",
				is_open=False,
			),
			dbc.Offcanvas(
				html.P("Some offcanvas content..."),
				id="task-conf-info",
				title="Task configurations loaded...",
				is_open=False,
			),
		]
	)

	search_space = dbc.Container(
		[
			dbc.Row(
				[
					dbc.Col(
						[
							hyperparameter.render() for hyperparameter in hyperparameters.values()
							# dbc.Button('Save Hyperparameter', id='save-button')
						],
						id='search-space-board',
						width=6
					),
					dbc.Col(
						[
							dbc.Accordion(
								[hp.display_search_space_element() for hp in searchspace.values()],
								flush=False,
								id='saved-search-space',
								start_collapsed=True,
							),
							dbc.Button('Add', id='add-button'),
						],
						id='display-saved-hps',
						width=6
					)
				]	
			)
		]
	)

	configurations = html.Div(render_job_config(job_config), id='configuration-container')

	review = dbc.Container(
		[
			dbc.Row(
				[
					html.H3("Search Space"),
					dbc.Accordion(
								[hp.display_search_space_element(review=True) for hp in searchspace.values()],
								flush=False,
								id='saved-search-space-review',
								start_collapsed=True,
							),
				]
			),
			dbc.Row(
				[
					html.H3("Task Configurations"),
					html.Div(id='task-config-review')
				]
			),
			dbc.Row(
				[
					html.H3('File Download'),
					dcc.Dropdown(
						id='download-dropdown',
						options=[
							{'label': 'search_space.json', 'value': 'search_space'},
							{'label': 'config.json', 'value': 'configuration'}
						],
						value=['search_space', 'configuration'],
						multi=True
					),
					dbc.Button('Download', color='success', outline=True, id='download-button'),
					dcc.Download(id='download-search-space'),
					dcc.Download(id='download-config')
				]
			)
		]
	)

	tab1_content = html.Div(
		className='tab-content-container',
        children=[
            file_upload,
			# dbc.Button('Save', id={'type': 'save-button', 'index':'1'}),
			dbc.Button('Next', id={'type': 'next-button', 'index':'1'})
        ]
	)

	tab2_content = html.Div(
		className='tab-content-container',
        children=[
            search_space,
			dbc.Button('Back', id={'type': 'back-button', 'index':'2'}),
			# dbc.Button('Save', id={'type': 'save-button', 'index':'2'}),
			dbc.Button('Save', id='save-button'),
			dbc.Button('Next', id={'type': 'next-button', 'index':'2'})
            # dcc.Loading(children=dbc.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tab3_content = html.Div(
		className='tab-content-container',
        children=[
            configurations,
			dbc.Button('Back', id={'type': 'back-button', 'index':'3'}),
			dbc.Button('Save', id={'type': 'save-button', 'index':'3'}),
			dbc.Button('Next', id={'type': 'next-button', 'index':'3'}),
			dbc.Toast(
				"sfg", 
				id='configuration-alert', 
				header="Please fix the following errors", 
				dismissable=True, 
				style={'position':'fixed', "top": 90, "right": 10, "width": 350}, 
				is_open=False)
            # dcc.Loading(children=dbc.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tab4_content = html.Div(
		className='tab-content-container',
        children=[
            review,
			dbc.Button('Back', id={'type': 'back-button', 'index':'4'}),
			dbc.Button("Submit", id="task-submit-button"),
			html.A('Click here to open OIDC Auth', href="#", hidden=True, className='btn btn-outline-primary', target='_blank', id="oidc-auth-window"),
			dbc.Button('Continue', id="task-submit-continue-after-auth-button")
            # dcc.Loading(children=dbc.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tabs = dcc.Tabs(
		className="tabs",
		id='submission-tabs',
		children=[
			dcc.Tab(tab1_content, label="File upload", style={'width': '25%'}, value='1'),
			dcc.Tab(tab2_content, label="Search space", style={'width': '25%'}, value='2'),
			dcc.Tab(tab3_content, label="Configurations", style={'width': '25%'}, value='3'),
			dcc.Tab(tab4_content, label="Review", style={'width': '25%'}, value='4'),
		],
		persistence=True,
		persistence_type="memory", 
		value='3'
	)

	# result = html.Div(
	# 	id="search-result-container",
	# 	children=[
	# 		dcc.Loading(children=html.H4(children="Search Result", id="taskID-result-title"), fullscreen=True),
	# 		html.Div(
	# 			id="taskID-search-result",
	# 			children=[]	
	# 		)
	# 	],
	# 	className="tab-content-container",
	# 	hidden=True
	# )

	# detail = html.Div(
	# 	id="detail-container",
	# 	children=[
	# 		html.H4("Job Details"),
	# 		dcc.Dropdown(multi=True, id="job-detail-dropdown"),
	# 		html.Div(id="job-detail")	
	# 	],
	# 	className="tab-content-container", 
	# 	hidden=True
	# )

	# alert_taskID_search = dbc.Modal(
	# 	children=[
	# 		dbc.ModalHeader(id="taskID-search-alert-header"),
	# 		dbc.ModalBody(id="taskID-search-alert-body")
	# 	],
	# 	id="taskID-search-alert", is_open=False, keyboard=True, size="lg"
	# )

	# alert_job_detail = dbc.Modal(
	# 	children=[
	# 		dbc.ModalHeader(id="job-detail-alert-header", style={'color': "black"}),
	# 		dbc.ModalBody(id="job-detail-alert-body"), 
	# 		html.Div(hidden=True, children=[], id="hidden-dropdown-value"),
	# 	],
	# 	id="job-detail-alert", is_open=False, keyboard=True, size="lg"
	# )

	submission = dbc.Container(
		children=[
			tabs,
			# result,
			# detail,
			# alert_job_detail,
			# alert_taskID_search
		],
		style={'padding': '30px 20px'}
	)
	
	return submission