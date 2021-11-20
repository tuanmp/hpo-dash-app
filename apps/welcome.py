import base64
import json

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from hpogui.dash.components.SearchSpace import Hyperparameter
from hpogui.dash.components.utils import searchAlgorithmOptions
from hpogui.dash.main import app, task

layout = html.Div(
	[
		html.Div(
			children=[
				dcc.Upload(
					[
						'Drag and drop a search space json file or ',
						dbc.Button('Select', color="success")
					], className="upload", id="upload-search-space", filename=[], contents=[], multiple=True),
				dbc.Alert(children="", color="primary", is_open=False, duration=5000, id="search-space-info")
			], className="task-conf-body"),
		html.Div(
			children=[
				dcc.Upload(
					[
						'Drag and drop a task configuration json file or ',
						dbc.Button('Select', color="success")
					], className="upload", id="upload-task-conf"),
				dbc.Alert(children="", color="primary", is_open=False, duration=5000, id="task-conf-info")
			], className="task-conf-body")
	], className="task-conf-main-body")


@app.callback(
	Output("search-space-info", "children"),
	Output("search-space-info", "color"),
	Output("search-space-info", "is_open"),
	Input("upload-search-space", "contents"),
	Input("upload-search-space", "filename"),
	prevent_initial_call=True
)
def load_search_space(contents, filenames):
	def getMethod(optMethod):
		if "uniform" in optMethod:
			return "Uniform"
		if "normal" in optMethod:
			return "Normal"
		if "categorical" in optMethod:
			return "Categorical"
		else:
			return None
	
	def getDType(instance):
		if isinstance(instance, int):
			return "Int"
		if isinstance(instance, float):
			return "Float"
		if isinstance(instance, str):
			return "Text"
		if isinstance(instance, bool):
			return "Boolean"
		return None
	
	n = 0
	for content, filename in zip(contents, filenames):
		if not filename.endswith(".json"):
			continue
		content_type, content_string = content.split(",")
		search_space = json.loads(base64.b64decode(content_string))
		for name in search_space:
			try:
				element = search_space[name]
				index = len(task.HyperParameters)
				tmp = Hyperparameter(index=index, name=name, method=getMethod(element["method"]))
				if tmp.method == "Categorical":
					dtype = getDType(element["dimension"]["categories"][0])
					tmp.dimensions["Categorical"]["dtype"] = dtype
					if dtype:
						tmp.dimensions["Categorical"]["categories"][dtype] = element["dimension"]["categories"]
				else:
					for key in element["dimension"]:
						tmp.dimensions[tmp.method][key] = element["dimension"][key]
					if "int" in element["method"]:
						tmp.dimensions["Uniform"]["isInt"] = True
				if tmp.isValid and tmp.name not in [hp.name for hp in task.HyperParameters.values()]:
					task.HyperParameters[index] = tmp
					n += 1
			except:
				continue
	if n > 0:
		return "%d elements were successfully loaded from the provided search space file." % n, "info", True
	else:
		return "None of the elements in the provided file were loaded to the search space.", "danger", True


@app.callback(
	Output("task-conf-info", "children"),
	Output("task-conf-info", "color"),
	Output("task-conf-info", "is_open"),
	Input("upload-task-conf", "contents"),
	Input("upload-task-conf", "filename"),
	prevent_initial_call=True
)
def load_search_space(content, filename):
	if not filename.endswith(".json"):
		return "Task configration input file must be in .json format.", "danger", True
	content_type, content_string = content.split(",")
	configs = json.loads(base64.b64decode(content_string))
	failList = []
	for config in configs:
		value = configs[config]
		if config == "steeringExec":
			if value.split("-l=")[-1] in searchAlgorithmOptions:
				task.JobConfig.searchAlgorithm = value.split("-l=")[-1]
		else:
			if hasattr(task.JobConfig, config):
				try:
					setattr(task.JobConfig, config, value)
				except:
					failList += config
					pass
	
	if len(failList) > 0:
		return "The following configurations cannot be set from the input file. Please manually set them in the Configuration" % ", ".join(
			failList), "info", True
	else:
		return "All configurations successfully set.", "info", True
