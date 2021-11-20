import re

from dash.dependencies import Input, Output, State
from hpogui.dash.apps.submission import *
from hpogui.dash.components.utils import (parameterDetails,
                                          searchAlgorithmOptions, siteOptions)
from hpogui.dash.main import *

config = task.JobConfig


def check_set(att, value, obj=config):
    try:
        setattr(obj, att, value)
        return True
    except:
        return False


def jobConfigPage(config):
    labelWidth = 3
    popOvers = [
        dbc.Popover(
            [dbc.PopoverHeader("Number of parallel evaluations"),
             dbc.PopoverBody(parameterDetails["nParallelEvalulations"]), dbc.Toast(
                [html.P("Parallel evaluation must be positive.")], id="nParallelEvalulations-warning-toast",
                header="WARNING", icon="danger", is_open=False)], target="nParallelEvalulations", trigger="focus",
            placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Max evaluation jobs"), dbc.PopoverBody(parameterDetails["maxEvaluationJobs"]),
             dbc.Toast(
                [html.P(
                    "Max evaluation jobs must be positive and larger than max points.")],
                id="maxEvaluationJobs-warning-toast", header="WARNING", icon="danger", is_open=False)],
            target="maxEvaluationJobs", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Max points"), dbc.PopoverBody(parameterDetails["maxPoints"]), dbc.Toast(
                [html.P("Max points must be positive and less than max evaluation jobs.")],
                id="maxPoints-warning-toast", header="WARNING", icon="danger", is_open=False)], target="maxPoints",
            trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Number of points per iteration"),
             dbc.PopoverBody(parameterDetails["nPointsPerIteration"]), dbc.Toast(
                [html.P(
                    "The number of points per iteration must be positive and exceed min unevaluated points.")],
                id="nPointsPerIteration-warning-toast", header="WARNING", icon="danger", is_open=False)],
            target="nPointsPerIteration", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Min unevaluated points"), dbc.PopoverBody(parameterDetails["minUnevaluatedPoints"]),
             dbc.Toast(
                [html.P(
                    "Min unevaluated points must be non-negative and less than the number of points per iteration.")],
                id="minUnevaluatedPoints-warning-toast", header="WARNING", icon="danger", is_open=False)],
            target="minUnevaluatedPoints", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Check point interval"), dbc.PopoverBody(
                parameterDetails["checkPointInterval"])],
            target="checkPointInterval", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Save check points"), dbc.PopoverBody(
                parameterDetails["checkPointToSave"])],
            target="checkPointToSave", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Load check points"), dbc.PopoverBody(
                parameterDetails["checkPointToLoad"])],
            target="checkPointToLoad", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation container"), dbc.PopoverBody(
                parameterDetails["evaluationContainer"])],
            target="evaluationContainer", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation exec"), dbc.PopoverBody(
                parameterDetails["evaluationExec"])],
            target="evaluationExec", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Training dataset"), dbc.PopoverBody(
                parameterDetails["trainingDS"])],
            target="trainingDS", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Output dataset"), dbc.PopoverBody(parameterDetails["outDS"])], target="outDS-custom",
            trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation training data"),
             dbc.PopoverBody(parameterDetails["evaluationTrainingData"])], target="evaluationTrainingData",
            trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation output"), dbc.PopoverBody(
                parameterDetails["evaluationOutput"])],
            target="evaluationOutput", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation metrics"), dbc.PopoverBody(
                parameterDetails["evaluationMetrics"])],
            target="evaluationMetrics", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Evaluation meta"), dbc.PopoverBody(
                parameterDetails["evaluationMeta"])],
            target="evaluationMeta", trigger="focus", placement="bottom-end"),
        dbc.Popover(
            [dbc.PopoverHeader("Steering container"), dbc.PopoverBody(
                parameterDetails["steeringContainer"])],
            target="steeringContainer", trigger="focus", placement="bottom-end")
    ]
    controlConfigurations = dbc.FormGroup(
        [
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Parallel Evaluations".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="nParallelEvalulations",
                            value=config.nParallelEvaluation, bs_size="sm", style=inputStyle), width=5 - labelWidth),
                    dbc.Col(width=2),
                    dbc.Label(
                        "max Points".capitalize(), html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="maxPoints",
                            value=config.maxPoints, bs_size="sm", style=inputStyle)], width=5 - labelWidth),
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "max Evaluation Jobs".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="maxEvaluationJobs",
                            value=config.maxEvaluationJobs, bs_size="sm", style=inputStyle)], width=5 - labelWidth),
                    dbc.Col(width=2),
                    dbc.Label(
                        "Points Per Iteration".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="nPointsPerIteration",
                            value=config.nPointsPerIteration, bs_size="sm", style=inputStyle)], width=5 - labelWidth),
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "min Unevaluated Points".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="minUnevaluatedPoints",
                            value=config.minUnevaluatedPoints, bs_size="sm", style=inputStyle)], width=5 - labelWidth),
                    dbc.Col(width=2),
                    dbc.Label(
                        "Search algorithm", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Select(
                            id="searchAlgorithm", persistence=True, persistence_type="memory",
                            options=[{"label": option, 'value': option}
                                     for option in searchAlgorithmOptions],
                            value=config.searchAlgorithm, bs_size="sm")], width=5 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Select grid sites", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Button(
                            "Grid sites", id="collapse-button", color="primary", block=True, size="sm", style=inputStyle)],
                        width=12 - labelWidth),
                ], row=True, className="no-gutters"),
            dbc.Collapse(
                dbc.Card(
                    children=[
                        dbc.CardHeader(
                            "Select one or more of the following computing sites", className="site-header"),
                        dbc.CardBody(
                            dbc.Checklist(
                                id='sites', options=[{'label': site, 'value': site} for site in siteOptions],
                                value=config.site, persistence=True, persistence_type="memory"),
                            className="site-body")], color="primary", outline=True, id="collapse-card"), is_open=False,
                id="collapse")
        ])
    evalationConfigurations = dbc.FormGroup(
        [
            dbc.FormGroup(
                [
                    dbc.Label(
                        "evaluation Container".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Textarea(
                            id="evaluationContainer", persistence=True, persistence_type="memory",
                            value=config.evaluationContainer, rows=2, bs_size="sm", style=inputStyle)],
                        width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "evaluation Exec".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Textarea(
                            id="evaluationExec", persistence=True, persistence_type="memory", value=config.evaluationExec,
                            rows=2, bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Training DS", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="trainingDS", value=config.trainingDS, persistence=True, persistence_type="memory",
                            valid=False, bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Evaluation training data", html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="evaluationTrainingData", value=config.evaluationTrainingData, persistence=True,
                            persistence_type="memory", bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Evaluation output", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="evaluationOutput", value=config.evaluationOutput, persistence=True,
                            persistence_type="memory", bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Evaluation metrics", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="evaluationMetrics", value=config.evaluationMetrics, persistence=True,
                            persistence_type="memory", bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters")
        ])
    optionalConfigurations = dbc.FormGroup(
        children=[
            dbc.FormGroup(
                [
                    dbc.Label(
                        "save check point".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Textarea(
                            id="checkPointToSave", persistence=True, persistence_type="memory",
                            value=config.checkPointToSave, rows=2, bs_size="sm", style=inputStyle)], width=5 - labelWidth),
                    dbc.Col(width=2),
                    dbc.Label(
                        "load check point".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Textarea(
                            id="checkPointToLoad", persistence=True, persistence_type="memory",
                            value=config.checkPointToLoad, rows=2, bs_size="sm", style=inputStyle)], width=5 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Check Point Interval".capitalize(), html_for="example-email-row", width=labelWidth,
                        align=labelAlignment, color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            type="number", persistence=True, persistence_type="memory", step=1, id="checkPointInterval",
                            value=config.checkPointInterval, bs_size="sm", style=inputStyle)], width=5 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Evaluation meta", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="evaluationMeta", value=config.evaluationMeta, persistence=True, persistence_type="memory",
                            bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Steering Container", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"), dbc.Col(
                        [dbc.Input(
                            id="steeringContainer", value=config.steeringContainer, persistence=True,
                            persistence_type="memory", bs_size="sm", style=inputStyle)], width=12 - labelWidth)
                ], row=True, className="no-gutters"),
            dbc.FormGroup(
                [
                    dbc.Label(
                        "Out DS", html_for="example-email-row", width=labelWidth, align=labelAlignment,
                        color=labelColor, size=labelSize, className="task-conf-label"),
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupAddon(
                                    "user.{}".format(config.user), id="outDS-prefix", addon_type='prepend'),
                                dbc.Input(
                                    id="outDS-custom", persistence=True, persistence_type="memory",
                                    value=config.customOutDS, style=inputStyle),
                                dbc.InputGroupAddon(".{}".format(
                                    config.uuid), addon_type='append')
                            ], size="sm"), width=12 - labelWidth)
                ], row=True, className="no-gutters"),
        ])
    layout = html.Div(
        children=[
            html.Div(
                [
                    html.H4("Control Configurations", style=linkStyle),
                    controlConfigurations], className="task-conf-body"),
            html.Div(
                [
                    html.H4("Evaluation Configurations", style=linkStyle),
                    evalationConfigurations], className="task-conf-body"),
            html.Div(
                [
                    html.H4("Optional Configurations", style=linkStyle),
                    optionalConfigurations], className="task-conf-body"),
            *popOvers
        ], className="task-conf-main-body")
    # layout.children+=popOvers
    return layout


# layout=jobConfigPage(config=config)

@app.callback(Output("collapse", "is_open"), Input("collapse-button", "n_clicks"), State("collapse", "is_open"))
def collapse_site(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@app.callback(
    Output("outDS-prefix", 'children'),
    Output("outDS-custom", 'valid'),
    Input("outDS-custom", "value"),
    State("outDS-prefix", 'children'))
def outDS_format(custom: str, prefix: str):
    config.customOutDS = custom
    if custom:
        if prefix.endswith("."):
            return prefix, True
        else:
            return prefix + ".", True
    else:
        return re.sub("\.$", "", prefix), False


@app.callback(
    Output("nPointsPerIteration", "valid"),
    Output("minUnevaluatedPoints", "valid"),
    Output("nPointsPerIteration", "invalid"),
    Output("minUnevaluatedPoints", "invalid"),
    Output("nPointsPerIteration-warning-toast", "is_open"),
    Output("minUnevaluatedPoints-warning-toast", "is_open"),
    Input("nPointsPerIteration", "value"),
    Input("minUnevaluatedPoints", "value"))
def link_nPointsPerIteration_minUnevaluatedPoints(nPointsPerIteration, minUnevaluatedPoints):
    nPointsPerIteration_valid, minUnevaluatedPoints_valid, nPointsPerIteration_invalid, minUnevaluatedPoints_invalid, nPointsPerIteration_warning_toast, minUnevaluatedPoints_warning_toast = True, True, False, False, False, False
    if nPointsPerIteration == None or nPointsPerIteration <= 0:
        nPointsPerIteration_valid, nPointsPerIteration_invalid, nPointsPerIteration_warning_toast = False, True, True
    if minUnevaluatedPoints == None or minUnevaluatedPoints < 0:
        minUnevaluatedPoints_valid, minUnevaluatedPoints_invalid, minUnevaluatedPoints_warning_toast = False, True, True
    if nPointsPerIteration != None and minUnevaluatedPoints != None and nPointsPerIteration <= minUnevaluatedPoints:
        nPointsPerIteration_valid, nPointsPerIteration_invalid = False, True
        minUnevaluatedPoints_valid, minUnevaluatedPoints_invalid = False, True
        nPointsPerIteration_warning_toast, minUnevaluatedPoints_warning_toast = True, True
    if nPointsPerIteration_valid:
        config.nPointsPerIteration = nPointsPerIteration
    if minUnevaluatedPoints_valid:
        config.minUnevaluatedPoint = minUnevaluatedPoints
    return nPointsPerIteration_valid, minUnevaluatedPoints_valid, nPointsPerIteration_invalid, minUnevaluatedPoints_invalid, nPointsPerIteration_warning_toast, minUnevaluatedPoints_warning_toast


@app.callback(
    Output("maxEvaluationJobs", "valid"),
    Output("maxPoints", "valid"),
    Output("maxEvaluationJobs", "invalid"),
    Output("maxPoints", "invalid"),
    Output("maxEvaluationJobs-warning-toast", "is_open"),
    Output("maxPoints-warning-toast", "is_open"),
    Input("maxEvaluationJobs", "value"),
    Input("maxPoints", "value"))
def link_maxEvaluationJobs_maxPoints(maxEvaluationJobs, maxPoints):
    maxEvaluationJobs_valid, maxPoints_valid, maxEvaluationJobs_invalid, maxPoints_invalid, maxEvaluationJobs_warning_toast, maxPoints_warning_toast = True, True, False, False, False, False
    if maxEvaluationJobs == None or maxEvaluationJobs <= 0:
        maxEvaluationJobs_valid, maxEvaluationJobs_invalid, maxEvaluationJobs_warning_toast = False, True, True
    if maxPoints == None or maxPoints < 0:
        maxPoints_valid, maxPoints_invalid, maxPoints_warning_toast = False, True, True
    if maxEvaluationJobs != None and maxPoints != None and maxEvaluationJobs < maxPoints:
        maxEvaluationJobs_valid, maxEvaluationJobs_invalid = False, True
        maxPoints_valid, maxPoints_invalid = False, True
        maxEvaluationJobs_warning_toast, maxPoints_warning_toast = True, True
    if maxPoints_valid:
        config.maxPoints = maxPoints
    if maxEvaluationJobs_valid:
        config.maxEvaluationJobs = maxEvaluationJobs
    return maxEvaluationJobs_valid, maxPoints_valid, maxEvaluationJobs_invalid, maxPoints_invalid, maxEvaluationJobs_warning_toast, maxPoints_warning_toast


@app.callback(
    Output("collapse-button", "color"),
    Output("collapse-card", "color"),
    Input("sites", "value"))
def change_collapse_button_color(sites):
    config.site = sites
    if sites:
        return "success", "success"
    else:
        return "warning", "warning"


@app.callback(
    Output("nParallelEvalulations", "valid"),
    Output("nParallelEvalulations", "invalid"),
    Output("nParallelEvalulations-warning-toast", "is_open"),
    Input("nParallelEvalulations", "value"))
def check_nParallelEvaluations(nParallelEvalulations):
    if check_set("nParallelEvalulations", nParallelEvalulations):
        return True, False, False
    else:
        return False, True, True


@app.callback(
    Output("evaluationContainer", "valid"),
    Output("evaluationContainer", "invalid"),
    Input("evaluationContainer", "value")
)
def check_evaluationContainer(evaluationContainer):
    if check_set("evaluationContainer", evaluationContainer):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationExec", "valid"),
    Output("evaluationExec", "invalid"),
    Input("evaluationExec", "value")
)
def check_evaluationExec(evaluationExec):
    if check_set("evaluationExec", evaluationExec):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationInput", "valid"),
    Output("evaluationInput", "invalid"),
    Input("evaluationInput", "value")
)
def check_evaluationInput(evaluationInput):
    if check_set("evaluationInput", evaluationInput):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationTrainingData", "valid"),
    Output("evaluationTrainingData", "invalid"),
    Input("evaluationTrainingData", "value")
)
def check_evaluationTrainingData(evaluationTrainingData):
    if check_set("evaluationTrainingData", evaluationTrainingData):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationOutput", "valid"),
    Output("evaluationOutput", "invalid"),
    Input("evaluationOutput", "value")
)
def check_evaluationOutput(evaluationOutput):
    if check_set("evaluationOutput", evaluationOutput):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationMeta", "valid"),
    Output("evaluationMeta", "invalid"),
    Input("evaluationMeta", "value"),
    prevent_initial_call=True
)
def check_evaluationMeta(evaluationMeta):
    if check_set("evaluationMeta", evaluationMeta):
        return True, False
    else:
        return False, True


@app.callback(
    Output("evaluationMetrics", "valid"),
    Output("evaluationMetrics", "invalid"),
    Input("evaluationMetrics", "value")
)
def check_evaluationMetrics(evaluationMetrics):
    if check_set("evaluationMetrics", evaluationMetrics):
        return True, False
    else:
        return False, True


@app.callback(
    Output("trainingDS", "valid"),
    Output("trainingDS", "invalid"),
    Input("trainingDS", "value"),
    prevent_initial_call=True
)
def check_trainingDS(trainingDS):
    if check_set("trainingDS", trainingDS):
        return True, False
    else:
        return False, True


@app.callback(
    Output("checkPointToSave", "valid"),
    Output("checkPointToSave", "invalid"),
    Input("checkPointToSave", "value"),
    prevent_initial_call=True
)
def check_checkPointToSave(checkPointToSave):
    if check_set("checkPointToSave", checkPointToSave):
        return True, False
    else:
        return False, True


@app.callback(
    Output("checkPointToLoad", "valid"),
    Output("checkPointToLoad", "invalid"),
    Input("checkPointToLoad", "value"),
    prevent_initial_call=True
)
def check_checkPointToLoad(checkPointToLoad):
    if check_set("checkPointToLoad", checkPointToLoad):
        return True, False
    else:
        return False, True


@app.callback(
    Output("checkPointInterval", "valid"),
    Output("checkPointInterval", "invalid"),
    Input("checkPointInterval", "value")
)
def check_checkPointInterval(checkPointInterval):
    if check_set("checkPointInterval", checkPointInterval):
        return True, False
    else:
        return False, True


@app.callback(
    Output("searchAlgorithm", "valid"),
    Input("searchAlgorithm", "value")
)
def check_searchAlgorithm(searchAlgorithm):
    return check_set("searchAlgorithm", searchAlgorithm)


@app.callback(
    Output("steeringContainer", "valid"),
    Input("steeringContainer", "value")
)
def check_searchAlgorithm(steeringContainer):
    return check_set("steeringContainer", steeringContainer)
