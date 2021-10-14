import dash_html_components as html
import dash_bootstrap_components as dbc
import yaml

class Hyperparameter():
    def __init__(self, index, name=None, method=None):
        self._index=index
        self._name=name
        self._dimensions={
            "Categorical": {"categories": {"Text": [], "Int": [], "Float": [], "Boolean": []}, "dtype": "Text"},
            "Uniform": {"low": 0, "high": 1, "base": None, "q": None, "isInt": False},
            "Normal": {"mu": 0, "sigma": 1, "base": None, "q": None}}
        self._method=method
        pass
    
    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, newname):
        self._name=newname
    
    @property
    def dimensions(self):
        return self._dimensions
    
    @property
    def method(self):
        return self._method
    @method.setter
    def method(self, newmethod):
        if newmethod in ["Categorical", "Uniform", "Normal"]:
            self._method=newmethod
        else:
            raise ValueError('method must be one of ("Categorical", "Uniform", "Normal")')
    
    @property
    def opt_method(self):
        if self.method=="Categorical": 
            return "categorical"
        if self.method=="Uniform": 
            if self._dimensions["Uniform"]["isInt"]: 
                return "uniformint"
            if self._dimensions["Uniform"]["base"]!=None and self._dimensions["Uniform"]["q"]!=None: 
                return "qloguniform"
            if self._dimensions["Uniform"]["base"]!=None:
                return "loguniform"
            if self._dimensions["Uniform"]["q"]!=None:
                return "quniform"
            return "uniform"
        if self.method=="Normal":
            if self._dimensions["Normal"]["base"]!=None and self._dimensions["Normal"]["q"]!=None: 
                return "qlognormal"
            if self._dimensions["Normal"]["base"]!=None:
                return "lognormal"
            if self._dimensions["Normal"]["q"]!=None:
                return "qnormal"
            return "normal"
        return None
    
    @property
    def search_space_element(self):
        if not self.isValid:
            return None
        dimensions = self.dimensions[self.method]
        opt_method=self.opt_method
        if self.method=="Categorical":
            dimension={"categories": dimensions["categories"][dimensions["dtype"]]}
        elif self.method=="Uniform":
            if dimensions["isInt"]: 
                dimension={"low": dimensions["low"], "high": dimensions["high"]}
            else:
                dimension={key: dimensions[key] for key in dimensions if (key!="isInt" and dimensions[key]!=None)}
        else: 
            dimension={key: dimensions[key] for key in dimensions if dimensions[key]!=None}
        return {"method": opt_method, "dimension": dimension}

    def render(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        return dbc.Col(dbc.Jumbotron([
            html.H3("Undefined Hyperparameter" if self.name==None else self.name, id={"type": "hyperparameter-name", "index": self.index}, style={"font-weight": "normal"}),
            html.P(
                "Specify a name and a sampling method to define this hyperparameter",
                style={"font-weight": "normal"}
            ),
            html.Hr(className="my-2"),
            dbc.FormGroup(row=True, children=[
                dbc.Label("Name", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col([dbc.Input(value=self.name, id={"type": "hyperparameter-name-input", "index": self.index}, bs_size="sm", debounce=False)])
            ]),
            dbc.FormGroup(row=True, children=[
                dbc.Label("Method", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col([dbc.Button("Select a sampling method" if self.method==None else self.method, id={"type": "sampling-method-selector", "index": self.index}, color="danger" if self.method==None else "success", block=True, size="sm", style={"font-weight": "bold"})])
            ]),
            dbc.Collapse(self.method_selector, id={"type": "sampling-method-selector-collapse", "index": self.index}, is_open=False),
            html.Div(children=self.display_method, id={"type": "method-dimension-container", "index": self.index})
        ], id={"type": "hyperparameter", "index": self.index}),
        width=6, style={"padding-right": "0rem"})

    @property
    def display_method(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        if self.method==None:
            return None
        dimensions=self.dimensions[self.method]
        if self.method=="Uniform":
            return [dbc.FormGroup(row=True, children=[
                dbc.Label("Range", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col(dbc.InputGroup([
                    dbc.InputGroupAddon("low", addon_type="prepend"), 
                    dbc.Input(value= dimensions["low"],type="number", bs_size="sm", valid=True, invalid=False, id={"type": "low", "index": self.index}),
                    dbc.InputGroupAddon("high"),
                    dbc.Input(value=dimensions["high"], type="number", bs_size="sm", valid=True, invalid=False, id={"type": "high", "index": self.index}),
                    dbc.InputGroupAddon(dbc.Button("int", color="info", outline=(not dimensions["isInt"]), id={"type": "int-button", "index": self.index}), addon_type="append"),
                ], size='sm'))
            ]), dbc.FormGroup(row=True, children=[
                dbc.Label("Scaling", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col(dbc.InputGroup([
                    dbc.InputGroupAddon(dbc.Button("log", color="info", outline=True if dimensions["base"]==None else False, id={"type": "log-button", "index": self.index}, n_clicks=0), addon_type="prepend"), 
                    dbc.Input(value=dimensions["base"], type="number",  bs_size="sm", valid=False, invalid=False, id={"type": "log", "index": self.index}, disabled=True),
                    dbc.InputGroupAddon(dbc.Button("q", color="info", outline=True if dimensions["q"]==None else False, id={"type": "q-button", "index": self.index}, n_clicks=0)),
                    dbc.Input(value=dimensions["q"], type="number",  bs_size="sm", valid=False, invalid=False, id={"type": "q", "index": self.index}, disabled=True)
                ], size='sm'))
            ])]
        elif self.method=="Normal":
            return [dbc.FormGroup(row=True, children=[
                dbc.Label("Gaussian", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col(dbc.InputGroup([
                    dbc.InputGroupAddon("\u03BC", addon_type="prepend"), 
                    dbc.Input(value=dimensions["mu"], type="number", bs_size="sm", valid=False, invalid=False, id={"type": "mu", "index": self.index}),
                    dbc.InputGroupAddon("\u03C3"),
                    dbc.Input(value=dimensions["sigma"], type="number", bs_size="sm", valid=False, invalid=False, id={"type": "sigma", "index": self.index})
                ], size='sm'))
            ]), dbc.FormGroup(row=True, children=[
                dbc.Label("Scaling", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col(dbc.InputGroup([
                    dbc.InputGroupAddon(dbc.Button("log", color="info", outline=True if dimensions["base"]==None else False, id={"type": "log-button-normal", "index": self.index}, n_clicks=0), addon_type="prepend"), 
                    dbc.Input(value=dimensions["base"], type="number",  bs_size="sm", valid=False, invalid=False, id={"type": "log-normal", "index": self.index}, disabled=True),
                    dbc.InputGroupAddon(dbc.Button("q", color="info", outline=True if dimensions["q"]==None else False, id={"type": "q-button-normal", "index": self.index}, n_clicks=0)),
                    dbc.Input(value=dimensions["q"], type="number",  bs_size="sm", valid=False, invalid=False, id={"type": "q-normal", "index": self.index}, disabled=True)
                ], size='sm'))
            ])]
        elif self.method=="Categorical":
            return [dbc.FormGroup(row=True, children=[
                dbc.Label("Format", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                dbc.Col(dbc.InputGroup([
                    dbc.ButtonGroup([dbc.Button("Data Type", color="danger", id={"type": "dtype-selector", "index": self.index}, style={"font-weight": "bold"}), dbc.Button(children="Add Null Value", color="info", outline=(None not in dimensions["categories"][dimensions["dtype"]]), id={"type": "add-none", "index": self.index})], style={"width": "100%"}, size="sm")
                ], size='sm'))
            ]), 
                dbc.Collapse([self.dtype_selector], is_open=False, id={"type": "dtype-selector-collapse", "index": self.index}),
                dbc.FormGroup(row=True, children=[
                    dbc.Label("Values", size=labelSize, width=labelWidth, align=labelAlign, style={"padding": "0 1em"}),
                    dbc.Col([dbc.InputGroup([
                        dbc.Input(value="",  bs_size="sm", id={"type":"item-value-input", "index": self.index}, valid=False, invalid=False),
                        dbc.InputGroupAddon(dbc.Button("Add value", color="info", style={"font-weight": "bold"}, id={"type":"add-item-button", "index": self.index}), addon_type='append')
                    ], size='sm'),
                    dbc.Col(children=dbc.Checklist(value=[], options=[], switch=True, inline=True, id={"type": "display-items", "index": self.index}))
                ])
            ])]
        else:
            return None

    @property
    def dtype_selector(self):
        return dbc.Card(children=[
                dbc.CardHeader("Select a data type for elements of the value list"), 
                dbc.CardBody([
                    dbc.RadioItems(options=[
                    {"label": "Text", "value": "Text"},
                    {"label": "Int", "value": "Int"},
                    {"label": "Float", "value": "Float"},
                    {"label": "Boolean", "value": "Boolean"},],
                value=self.dimensions["Categorical"]["dtype"],
                inline=True,
                id={"type": "dtype-radio-selector", "index": self.index})
            ])], outline=True, color="success", id={"type": "dtype-selector-container", "index": self.index}) 

    @property
    def method_selector(self):
        messages={
        "Categorical": "The value of this hyperparameter in a hyperparameter point is uniformly picked from a list of values that you will specify.",
        'Normal': 'The numerical value of this hyperparameter or its logarithm is sampled over a Gaussian distribution defined by a mean \u03BC and variance \u03C3\u00B2 that you will specify.',
        'Uniform': 'The numberical value of this hyperparameter or logarithms is uniformly sampled from a range that you will specify'
        }
        return dbc.Card([
                dbc.CardHeader("Select a sampling method"), 
                dbc.CardBody([
                    dbc.RadioItems(options=[
                    {"label": "Categorical", "value": "Categorical"},
                    {"label": "Normal", "value": "Normal"},
                    {"label": "Uniform", "value": "Uniform"},
                ],
                value=self.method,
                inline=True,
                id={"type": "method-radio-selector", "index": self.index}), 
                    html.Hr(), 
                    dbc.Toast(children=None if self.method==None else messages[self.method], header="No method selected" if self.method==None else self.method, icon="danger" if self.method==None else "success", id={"type": "method-info", "index": self.index}, is_open=True, style={"maxWidth": "100%"}) ])
            ], outline=True, color="danger" if self.method==None else "success", id={"type": "method-selector-container", "index": self.index})

    @property
    def isValid(self):
        if not self.name: 
            return False
        if not self.method: 
            return False
        dimensions=self.dimensions[self.method]
        if self.method=="Categorical":
            dtype=dimensions['dtype']
            if dimensions["categories"][dtype]:
                return True
        if self.method=="Uniform":
            if dimensions["low"]!=None and dimensions["high"]!=None:
                return True
        if self.method=="Normal":
            if dimensions["mu"]!=None and dimensions["sigma"]!=None:
                return True
        return False

    def display_search_space_element(self):
        content=[]
        for line in yaml.dump(self.search_space_element, sort_keys=False).split("\n"):
            content.append(line)
            content.append(html.Br())
        content.pop(-1)
        return dbc.Toast(children=[
            html.P(children=content)
        ], id={"type": "display-searchspace-element", "index": self.index}, className="HP-toast", bodyClassName="HP-toast-body", headerClassName="HP-toast-header", dismissable=True, header=self.name, icon="success", is_open=True)
        


  