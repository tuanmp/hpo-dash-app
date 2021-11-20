import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, MATCH, Output, State
from dash import callback_context
import re, yaml

from hpogui.dash.components.SearchSpace import Hyperparameter
from hpogui.dash.main import app, task

hyperparameters={}
search_space=task.HyperParameters

def checkInt(input: str):
    try:
        int(input)
        return True
    except: 
        return False
def checkFloat(input: str):
    try:
        float(input)
        return True
    except: 
        return False
def converInputDType(input, dtype):
    if dtype=="Int":
        return int(input)
    if dtype=="Float":
        return float(input)
    if dtype=="Boolean":
        return input=='true'
    return input

layout=html.Div(children=[html.H4("Define Hyperparameter Search", className="underline"), dbc.Row(no_gutters=True, id="searchspace-board", children=[hp.render() for hp in hyperparameters.values()])], className="searchspace-body")
sideLayout=html.Div([
    html.H4("Search Space", className="underline"),
    dbc.Col(children=
        [element.display_search_space_element for element in search_space],
        id="display-saved-hps"),
    dbc.Row([dbc.Col(dbc.Button("Add HP", color="info", id="add-button", n_clicks=0, block=True), width=6, style={"padding": "0 0.5rem"}),
    dbc.Col(dbc.Button("Save HPs", color="success", id="save-button", block=True), width=6, style={"padding": "0 0.5rem"})], no_gutters=True)
    ], className="searchspace-side")

# Add hyperparameters
@app.callback(Output("searchspace-board", "children"), 
            Output("display-saved-hps", "children"),
            Input("add-button", "n_clicks"), 
            Input("save-button", "n_clicks"),
            prevent_initial_call=True)
def add_hyperparameter(index, saveSignal):
    trigger=callback_context.triggered[0]["prop_id"]
    if "add-button" in trigger:
        hyperparameters[index]=Hyperparameter(index=index)
    else:
        # check the HPs in the editor for those that are valid
        for index, hp in hyperparameters.items():
            # check if it is possible to generate a search space element from the HP, this also checks if the HP is valid
            if not hp.isValid: continue
            if hp.name in [element.name for element in search_space.values()]: continue
            # add HP to search_space
            search_space[index]=hp
        for index in search_space:
            if index in hyperparameters:
                hyperparameters.pop(index)
    return [hp.render() for hp in hyperparameters.values()], [element.display_search_space_element() for element in search_space.values()]

# Remove hyperparameters
@app.callback(Output({"type": "display-searchspace-element", "index": MATCH}, "is_open"), 
            Input({"type": "display-searchspace-element", "index": MATCH}, "is_open"),
            prevent_initial_call=True)
def delete_hyperparameter(signal):
    index=callback_context.inputs_list[0]['id']["index"]
    try:
        search_space.pop(index)
    except:
        pass
    return False

# change title of hyperparameter when input
@app.callback(Output({"type": "hyperparameter-name", "index": MATCH}, "children"), 
            Output({"type": "hyperparameter-name-input", "index": MATCH}, "valid"), 
            Output({"type": "hyperparameter-name-input", "index": MATCH}, "invalid"), 
            Input({"type": "hyperparameter-name-input", "index": MATCH}, "value"), 
            prevent_initial_call=True)
def change_title(name):
    index=callback_context.inputs_list[0]['id']["index"]
    if name and (not bool(re.search(u"\W", name))):
        hyperparameters[index].name=name
        return name, True, False
    else:
        hyperparameters[index].name=None
        return "Undefined Hyperparameter", False, True

# Open the collapse to select method
@app.callback(Output({"type": "sampling-method-selector-collapse", "index": MATCH}, "is_open"),
                Input({"type": "sampling-method-selector", "index": MATCH}, "n_clicks"), 
                State({"type": "sampling-method-selector-collapse", "index": MATCH}, "is_open"), prevent_initial_call=True)
def show_method_collapse(n, is_open):
    return not is_open

@app.callback(Output({"type": "dtype-selector-collapse", "index": MATCH}, "is_open"), 
            Input({"type": "dtype-selector", "index": MATCH}, "n_clicks"), 
            State({"type": "dtype-selector-collapse", "index": MATCH}, "is_open"), prevent_initial_call=True)
def show_dtype_collapse(n, is_open):
    return not is_open

@app.callback(Output({"type": "method-info", "index": MATCH}, "header"), 
                Output({"type": "method-info", "index": MATCH}, "children"), 
                Output({"type": "method-info", "index": MATCH}, "icon"), 
                Output({"type": "method-info", "index": MATCH}, 'color'), 
                Output({"type": "method-selector-container", "index": MATCH}, "color"),
                Output({"type": "sampling-method-selector", "index": MATCH}, "color"),
                Output({"type": "sampling-method-selector", "index": MATCH}, "children"),
                Output({"type": "method-dimension-container", "index": MATCH}, "children"),
                Input({"type": "method-radio-selector", "index": MATCH}, "value"), prevent_initial_call=True)
def show_method_info(selected_method):
    index=callback_context.inputs_list[0]['id']["index"]
    messages={
        "Categorical": "The value of this hyperparameter in a hyperparameter point is uniformly picked from a list of values that you will specify.",
        'Normal': 'The numerical value of this hyperparameter or its logarithm is sampled over a Gaussian distribution defined by a mean \u03BC and variance \u03C3\u00B2 that you will specify.',
        'Uniform': 'The numberical value of this hyperparameter or logarithms is uniformly sampled from a range that you will specify'
    }
    hyperparameters[index].method=selected_method
    return selected_method, messages[selected_method], "success", "success", "success", "success", selected_method, hyperparameters[index].display_method

@app.callback(
    Output({"type": "dtype-selector-container", "index": MATCH}, "color"),
    Output({"type": "dtype-selector", "index": MATCH}, "color"), 
    Output({"type": "dtype-selector", "index": MATCH}, "children"), 
    Input({"type": "dtype-radio-selector", "index": MATCH}, "value"),
    Input({"type": "dtype-selector", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True)
def dtype_reaction(dtype, n):
    index=callback_context.inputs_list[0]['id']["index"]
    hyperparameters[index].dimensions["Categorical"]["dtype"]=dtype
    return "success", "success", dtype

@app.callback(
    Output({"type": "add-none", "index": MATCH}, "outline"),
    Output({"type": "add-none", "index": MATCH}, "style"),
    Output({"type": "add-none", "index": MATCH}, "color"),
    Input({"type": "add-none", "index": MATCH}, "n_clicks"),
    State({"type": "add-none", "index": MATCH}, "outline"),
    State({"type": "add-none", "index": MATCH}, "style"),
    State({"type": "add-none", "index": MATCH}, "color"),
    prevent_initial_call=True)
def change_add_none_style(n, outline, style, color):
    return not outline, {"font-weight": "bold"} if style != {"font-weight": "bold"}  else {}, "info" if color=="success" else "success"

@app.callback(
    Output({"type":"item-value-input", "index": MATCH}, "valid"),
    Output({"type":"item-value-input", "index": MATCH}, "invalid"),
    Input({"type":"item-value-input", "index": MATCH}, "value"),
    prevent_initial_call=True)
def change_input_value_valid(value):
    if not value:
        return False, False
    elif value and not (bool(re.search(u"[^a-zA-Z0-9[.]]", value))):
        return True, False
    else:
        return False, True

@app.callback(
    Output({"type": "display-items", "index": MATCH}, "options"),
    Output({"type": "display-items", "index": MATCH}, "value"),
    Output({"type":"item-value-input", "index": MATCH}, "value"),
    Input({"type":"add-item-button", "index": MATCH}, "n_clicks"),
    Input({"type": "dtype-radio-selector", "index": MATCH}, 'value'),
    Input({"type": "add-none", "index": MATCH}, 'outline'),
    Input({"type": "display-items", "index": MATCH}, "value"),
    State({"type":"item-value-input", "index": MATCH}, "value"),
    State({"type":"item-value-input", "index": MATCH}, "valid"),
    State({"type":"item-value-input", "index": MATCH}, "invalid"),
    State({"type": "display-items", "index": MATCH}, "options"),
    State({"type": "display-items", "index": MATCH}, "value"),
    prevent_initial_call=True)
def display_values(n1, dtype, noNull, activeValues, inputValue: str, inputValid, inputInvalid, options, values):
    addNull=not noNull
    index=callback_context.inputs_list[0]['id']["index"]
    triggeringInput="new-value"
    if "dtype-radio-selector" in callback_context.triggered[0]["prop_id"]: 
        triggeringInput="new-DType"
    elif "add-none" in callback_context.triggered[0]["prop_id"]: 
        triggeringInput="add-none"
    elif "display-items" in callback_context.triggered[0]["prop_id"]:
        triggeringInput="active-value"
    if triggeringInput=="new-value":
        inputValueReformat=re.sub("\s", "", inputValue)
        dtypeValid=True
        if dtype=="Int":
            dtypeValid=checkInt(inputValueReformat)
        if dtype=="Float":
            dtypeValid=checkFloat(inputValueReformat)
        if dtype=="Boolean" and inputValueReformat.lower() in ['true', 'false']:
            inputValueReformat=inputValueReformat.lower()
        if inputValid and dtypeValid and not inputInvalid and not {"label": inputValueReformat, "value": inputValueReformat} in options:
            hyperparameters[index].dimensions["Categorical"]["categories"][dtype].append(converInputDType(inputValueReformat, dtype))
            return options + [{"label": inputValueReformat, "value": inputValueReformat}], values+[inputValueReformat], ""
        else:
            return options, values, inputValue
    elif triggeringInput=='add-none':
        if addNull:
            if "None" not in hyperparameters[index].dimensions["Categorical"]["categories"][dtype]: 
                hyperparameters[index].dimensions["Categorical"]["categories"][dtype]+=["None"]
            if not {"label": "None", "value": "None"} in options:
                return options+[{"label": "None", "value": "None"}], values+["None"], inputValue
            else:
                return options, values, inputValue
        else:
            hyperparameters[index].dimensions["Categorical"]["categories"][dtype]=[value for value in hyperparameters[index].dimensions["Categorical"]["categories"][dtype] if value != "None"]
            if not {"label": "None", "value": "None"} in options: 
                return options, values, inputValue
            else: 
                return [option for option in options if option!={"label": "None", "value": "None"}], [value for value in values if value != "None"], inputValue
    elif triggeringInput=="new-DType":
        hyperparameters[index].dimensions["Categorical"]["dtype"]=dtype
        newOptions=[{"label": value, "value": value} for value in hyperparameters[index].dimensions["Categorical"]["categories"][dtype] if value != "None"]
        newValues=[value for value in hyperparameters[index].dimensions["Categorical"]["categories"][dtype] if value != "None"]
        if addNull: 
            newOptions.append({"label": "None", "value": "None"})
            if "None" in hyperparameters[index].dimensions["Categorical"]["categories"][dtype]: newValues.append("None")
        return newOptions, newValues, inputValue
    else: 
        hyperparameters[index].dimensions["Categorical"]['categories'][dtype]=activeValues
        return options, values, inputValue

@app.callback(Output({"type": "int-button", "index": MATCH}, "outline"),
            Output({"type": "int-button", "index": MATCH}, "color"),
            Output({"type": "int-button", "index": MATCH}, "style"),
            Output({"type": "q", "index": MATCH}, "disabled"),
            Output({"type": "q-button", "index": MATCH}, "outline"),
            Output({"type": "q-button", "index": MATCH}, "color"),
            Output({"type": "q-button", "index": MATCH}, "style"),
            Output({"type": "log", "index": MATCH}, "disabled"),
            Output({"type": "log-button", "index": MATCH}, "outline"),
            Output({"type": "log-button", "index": MATCH}, "color"),
            Output({"type": "log-button", "index": MATCH}, "style"),
            Input({"type": "int-button", "index": MATCH}, "n_clicks"),
            Input({"type": "q-button", "index": MATCH}, "n_clicks"),
            Input({"type": "log-button", "index": MATCH}, "n_clicks"),
            State({"type": "int-button", "index": MATCH}, "outline"),
            State({"type": "int-button", "index": MATCH}, "color"),
            State({"type": "int-button", "index": MATCH}, "style"),
            State({"type": "q-button", "index": MATCH}, "outline"),
            State({"type": "q-button", "index": MATCH}, "color"),
            State({"type": "q-button", "index": MATCH}, "style"),
            State({"type": "log-button", "index": MATCH}, "outline"),
            State({"type": "log-button", "index": MATCH}, "color"),
            State({"type": "log-button", "index": MATCH}, "style"),
            prevent_initial_call=True)
def activate_int_q_log(intNClicks, qNClicks, logNClicks, isIntDisabled, intColor, intStyle,  isQDisabled, qColor, qStyle, isLogDisabled, logColor, logStyle):
    triggeringInput="int"
    index=callback_context.inputs_list[0]['id']["index"]
    if "q-button" in callback_context.triggered[0]["prop_id"]:
        triggeringInput="q"
    if "log-button" in callback_context.triggered[0]["prop_id"]:
        triggeringInput="log"
    if triggeringInput=="int":
        hyperparameters[index].dimensions["Uniform"]["isInt"]=isIntDisabled
        return not isIntDisabled, "success" if isIntDisabled else "info", {"font-weight": "bold"} if isIntDisabled else {}, True, True, "info", {}, True, True, "info", {}
    if triggeringInput=="q":
        if not isIntDisabled:
            return isIntDisabled, intColor, intStyle, True, True, "info", {}, True, True, "info", {}
        else:
            return isIntDisabled, intColor, intStyle, not isQDisabled, not isQDisabled, "success" if isQDisabled else "info", {"font-weight": "bold"} if isQDisabled else {}, isLogDisabled, isLogDisabled, logColor, logStyle
    if triggeringInput=="log":
        if not isIntDisabled:
            return isIntDisabled, intColor, intStyle, True, True, "info", {}, True, True, "info", {}
        else: 
            return isIntDisabled, intColor, intStyle, isQDisabled, isQDisabled, qColor, qStyle, not isLogDisabled, not isLogDisabled, "success" if isLogDisabled else "info", {"font-weight": "bold"} if isLogDisabled else {}

@app.callback(Output({"type": "q-normal", "index": MATCH}, "disabled"),
            Output({"type": "q-button-normal", "index": MATCH}, "outline"),
            Output({"type": "q-button-normal", "index": MATCH}, "color"),
            Output({"type": "q-button-normal", "index": MATCH}, "style"),
            Output({"type": "log-normal", "index": MATCH}, "disabled"),
            Output({"type": "log-button-normal", "index": MATCH}, "outline"),
            Output({"type": "log-button-normal", "index": MATCH}, "color"),
            Output({"type": "log-button-normal", "index": MATCH}, "style"),
            Input({"type": "q-button-normal", "index": MATCH}, "n_clicks"),
            Input({"type": "log-button-normal", "index": MATCH}, "n_clicks"),
            State({"type": "q-button-normal", "index": MATCH}, "outline"),
            State({"type": "q-button-normal", "index": MATCH}, "color"),
            State({"type": "q-button-normal", "index": MATCH}, "style"),
            State({"type": "log-button-normal", "index": MATCH}, "outline"),
            State({"type": "log-button-normal", "index": MATCH}, "color"),
            State({"type": "log-button-normal", "index": MATCH}, "style"),
            prevent_initial_call=True)
def activate_q_log_normal(nQ, nLog, isQDisabled, qColor, qStyle, isLogDisabled, logColor, logStyle):
    triggeringInput="q" if "q-button-normal" in callback_context.triggered[0]["prop_id"] else "log"
    index=callback_context.inputs_list[0]['id']["index"]
    if triggeringInput=="q":
        return not isQDisabled, not isQDisabled, "success" if isQDisabled else "info", {"font-weight": "bold"} if isQDisabled else {}, isLogDisabled, isLogDisabled, logColor, logStyle
    if triggeringInput=="log":
        return isQDisabled, isQDisabled, qColor, qStyle, not isLogDisabled, not isLogDisabled, "success" if isLogDisabled else "info", {"font-weight": "bold"} if isLogDisabled else {}

@app.callback(Output({"type": "log", "index": MATCH}, "valid"),
            Output({"type": "log", "index": MATCH}, "invalid"),
            Input({"type": "log", "index": MATCH}, "value"),
            Input({"type": "log", "index": MATCH}, "disabled"), 
            State({"type": "method-radio-selector", "index": MATCH}, "value"))
def log_reaction(value: str, disabled, Method):
    enabled=not disabled
    index=callback_context.inputs_list[0]['id']["index"]
    if disabled:
        hyperparameters[index].dimensions[Method]["base"]=None
        #print(hyperparameters[index].dimensions[Method]["base"])
        return False, False
    if enabled and checkFloat(value) and value>0:
        hyperparameters[index].dimensions[Method]["base"]=value
        #print(hyperparameters[index].dimensions[Method]["base"])
        return True, False
    else:
        hyperparameters[index].dimensions[Method]["base"]=None
        #print(hyperparameters[index].dimensions[Method]["base"])
        return False, True

@app.callback(Output({"type": "q", "index": MATCH}, "valid"),
            Output({"type": "q", "index": MATCH}, "invalid"),
            Input({"type": "q", "index": MATCH}, "value"),
            Input({"type": "q", "index": MATCH}, "disabled"),
            State({"type": "method-radio-selector", "index": MATCH}, "value"))
def q_reaction(value: str, disabled, Method):
    enabled=not disabled
    index=callback_context.inputs_list[0]['id']["index"]
    if disabled:
        hyperparameters[index].dimensions[Method]["q"]=None
        return False, False
    if enabled and checkFloat(value) and value>0:
        hyperparameters[index].dimensions[Method]["q"]=value
        return True, False
    else:
        hyperparameters[index].dimensions[Method]["q"]=None
        return False, True

@app.callback(Output({"type": "log-normal", "index": MATCH}, "valid"),
            Output({"type": "log-normal", "index": MATCH}, "invalid"),
            Input({"type": "log-normal", "index": MATCH}, "value"),
            Input({"type": "log-normal", "index": MATCH}, "disabled"), 
            State({"type": "method-radio-selector", "index": MATCH}, "value"))
def log_normal_reaction(value: str, disabled, Method):
    enabled=not disabled
    index=callback_context.inputs_list[0]['id']["index"]
    if disabled:
        hyperparameters[index].dimensions[Method]["base"]=None
        return False, False
    if enabled and checkFloat(value) and value>0:
        hyperparameters[index].dimensions[Method]["base"]=value
        return True, False
    else:
        hyperparameters[index].dimensions[Method]["base"]=None
        return False, True

@app.callback(Output({"type": "q-normal", "index": MATCH}, "valid"),
            Output({"type": "q-normal", "index": MATCH}, "invalid"),
            Input({"type": "q-normal", "index": MATCH}, "value"),
            Input({"type": "q-normal", "index": MATCH}, "disabled"),
            State({"type": "method-radio-selector", "index": MATCH}, "value"))
def q_normal_reaction(value: str, disabled, Method):
    enabled=not disabled
    index=callback_context.inputs_list[0]['id']["index"]
    if disabled:
        hyperparameters[index].dimensions[Method]["q"]=None
        return False, False
    if enabled and checkFloat(value) and value>0:
        hyperparameters[index].dimensions[Method]["q"]=value
        return True, False
    else:
        hyperparameters[index].dimensions[Method]["q"]=None
        return False, True

@app.callback(Output({"type": "mu", "index": MATCH}, "valid"),
            Output({"type": "mu", "index": MATCH}, "invalid"),
            Input({"type": "mu", "index": MATCH}, "value"))
def mu_reaction(value):
    index=callback_context.inputs_list[0]['id']["index"]
    if checkFloat(value):
        hyperparameters[index].dimensions["Normal"]["mu"]=value
        return True, False
    else:
        hyperparameters[index].dimensions["Normal"]["mu"]=None
        return False, True

@app.callback(Output({"type": "sigma", "index": MATCH}, "valid"),
            Output({"type": "sigma", "index": MATCH}, "invalid"),
            Input({"type": "sigma", "index": MATCH}, "value"))
def sigma_reaction(value):
    index=callback_context.inputs_list[0]['id']["index"]
    if checkFloat(value):
        hyperparameters[index].dimensions["Normal"]["sigma"]=value
        return True, False
    else:
        hyperparameters[index].dimensions["Normal"]["sigma"]=None
        return False, True

@app.callback(Output({"type": "low", "index": MATCH}, "valid"),
            Output({"type": "low", "index": MATCH}, "invalid"),
            Output({"type": "high", "index": MATCH}, "valid"),
            Output({"type": "high", "index": MATCH}, "invalid"),
            Input({"type": "low", "index": MATCH}, "value"),
            Input({"type": "high", "index": MATCH}, "value"),
            Input({"type": "int-button", "index": MATCH}, "outline"))
def low_high_reaction(low, high, is_disabled):
    isInt=not is_disabled
    index=callback_context.inputs_list[0]['id']["index"]
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

