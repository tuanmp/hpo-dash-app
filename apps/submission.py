from dash import html, dcc
import dash_bootstrap_components as dbc

BUTTONS = [
    ("File Upload",  'file_upload'),
    ("Task Configurations", 'task_config'),
    ("Search Space", 'search_space'),
    ("Review", 'review')
]
# <ul id="progressbar">
#                         <li class="active" id="account"><strong>Account</strong></li>
#                         <li id="personal"><strong>Personal</strong></li>
#                         <li id="payment"><strong>Image</strong></li>
#                         <li id="confirm"><strong>Finish</strong></li>
#                     </ul>

def submission(**kwargs):
	job_config = kwargs.get('config', {})
	file_upload = html.Div(
		className = "tab-content",
		children=[
			html.Div(className="label", children="Select file: "),
			dcc.Upload(
				[
					'Drag and drop a search space json file or ',
					html.Button("Upload")
				], className="upload", id="upload-search-space", filename=[], contents=[], multiple=True
			)
		]
	)

	search_space = html.Div(
		className = "tab-content",
		children=[
			html.Div([
				html.Div(className="label", children="Username: "),
				dcc.Input(
					className="input-element", 
					# id='criteria-username', 
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Age (days): "),
				dcc.Input(
					className="input-element", 
					# id='criteria-age', 
					type='number'
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Task Name: "),
				dcc.Input(
					className="input-element", 
					# id='criteria-taskname', 
					)
				]
			),
		]
	)

	control_configuration = html.Div(
		className = "tab-content",
		children=[
			html.Div([
				html.Div(className="label", children="Parallel evaluations: "),
				dcc.Input(
					className="input-element", 
					id='nParallelEvaluations', 
					type='number',
					min=1, 
					step=1, 
					value=job_config.nParallelEvaluation,
					required=True,
					persistence=True,
					persistence_type="memory"
					),
				html.Button('Info')
				]
			),
			html.Div([
				html.Div(className="label", children="Max points: "),
				dcc.Input(
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
				html.Div(className="label", children="Max evaluation jobs: "),
				dcc.Input(
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
				html.Div(className="label", children="Points per iterations: "),
				dcc.Input(
					className="input-element", 
					id='nPointsPerIteration', 
					type='number',
					min=1, 
					step=1, 
					value=job_config.nPointsPerIteration,
					required=True,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Min unevaluated jobs: "),
				dcc.Input(
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
				html.Div(className="label", children="Search algorithm: "),
				dcc.Dropdown(
					# className="input-element", 
					id='searchAlgorithm', 
					value=job_config._searchAlgOptions[0],
					options=[{'label': i, 'value': i} for i in job_config._searchAlgOptions],
					persistence=True,
					persistence_type="memory",
					clearable=False
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Grid sites: "),
				dcc.Dropdown(
					# className="input-element", 
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
		]
	)

	eval_configuration = html.Div(
		className = "tab-content",
		children=[
			html.Div([
				html.Div(className="label", children="Evaluation container: "),
				dcc.Input(
					className="input-element", 
					id='evaluationContainer', 
					value=job_config.evaluationContainer,
					required=True,
					persistence=True,
					persistence_type="memory"
					),
				html.Button('Info')
				]
			),
			html.Div([
				html.Div(className="label", children="Evaluation execution: "),
				dcc.Textarea(
					className="input-element", 
					rows=5,
					id='evaluationExec', 
					contentEditable=True,
					required=True,
					value=job_config.evaluationExec,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			# html.Div([
			# 	html.Div(className="label", children="Max number of jobs: "),
			# 	dcc.Input(
			# 		className="input-element", 
			# 		id='maxEvaluationJobs', 
			# 		type='number',
			# 		min=1, 
			# 		step=1, 
			# 		value=job.max,
			# 		required=True,
			# 		persistence=True,
			# 		persistence_type="memory"
			# 		)
			# 	]
			# ),
			html.Div([
				html.Div(className="label", children="Evaluation input: "),
				dcc.Input(
					className="input-element", 
					id='evaluationInput', 
					value=job_config.evaluationInput,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Training dataset: "),
				dcc.Input(
					className="input-element", 
					id='trainingDS', 
					value=job_config.trainingDS,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Training data: "),
				dcc.Input(
					className="input-element", 
					id='evaluationTrainingData', 
					value=job_config.evaluationTrainingData,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Evaluation output: "),
				dcc.Input(
					className="input-element", 
					id='evaluationOutput', 
					value=job_config._evaluationOutput,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Evaluation metrics: "),
				dcc.Input(
					className="input-element", 
					id='evaluationMetrics', 
					value=job_config.evaluationMetrics,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Output dataset: "),
				dcc.Input(
					className="input-element", 
					id='customOutDS', 
					value=job_config.customOutDS,
					persistence=True,
					persistence_type="memory"
					)
				]
			),
		]
	)
	
	configurations = html.Div(
		[
			control_configuration,
			eval_configuration
		]
	)

	review = html.Div(
		className = "tab-content",
		children=[
			html.Div([
				html.Div(className="label", children="Username: "),
				dcc.Input(
					className="input-element", 
					# id='criteria-username', 
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Age (days): "),
				dcc.Input(
					className="input-element", 
					# id='criteria-age', 
					type='number'
					)
				]
			),
			html.Div([
				html.Div(className="label", children="Task Name: "),
				dcc.Input(
					className="input-element", 
					# id='criteria-taskname', 
					)
				]
			),
		]
	)

	tab1_content = html.Div(
		className='tab-content-container',
        children=[
            file_upload,
			html.Button('Save', id={'type': 'save-button', 'index':'1'}),
			html.Button('Next', id={'type': 'next-button', 'index':'1'})
        ]
	)

	tab2_content = html.Div(
		className='tab-content-container',
        children=[
            search_space,
			html.Button('Back', id={'type': 'back-button', 'index':'2'}),
			html.Button('Save', id={'type': 'save-button', 'index':'2'}),
			html.Button('Next', id={'type': 'next-button', 'index':'2'})
            # dcc.Loading(children=html.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tab3_content = html.Div(
		className='tab-content-container',
        children=[
            configurations,
			html.Button('Back', id={'type': 'back-button', 'index':'3'}),
			html.Button('Save', id={'type': 'save-button', 'index':'3'}),
			html.Button('Next', id={'type': 'next-button', 'index':'3'}),
			dbc.Toast(
				"sfg", 
				id='configuration-alert', 
				header="Please fix the following errors", 
				dismissable=True, 
				style={'position':'fixed', "top": 90, "right": 10, "width": 350}, 
				is_open=False)
            # dcc.Loading(children=html.Button("Search", id="criteria-search-button"), fullscreen=True),
        ]
	)

	tab4_content = html.Div(
		className='tab-content-container',
        children=[
            review,
			html.Button('Back', id={'type': 'back-button', 'index':'4'}),
			# html.Button('Save and Continue', id={'type': 'next-button', 'index':'upload'})
            # dcc.Loading(children=html.Button("Search", id="criteria-search-button"), fullscreen=True),
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

	submission = html.Div(
		className="content-container blue-background",
		children=[
			tabs,
			# result,
			# detail,
			# alert_job_detail,
			# alert_taskID_search
		]
	)
	
	return submission