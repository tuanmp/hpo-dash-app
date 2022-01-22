from dash import html, dcc
import dash_bootstrap_components as dbc
import yaml
from .utils import make_options_from_list, label_with_info_button, info_button

class Hyperparameter:
    def __init__(self, index, name=None, method=None):
        self._index=index
        self._name=name
        self._dimensions={
            "Categorical": {"categories": []},
            "Uniform": {"low": 0, "high": 1, "base": None, "q": None, "isInt": False},
            "Normal": {"mu": 0, "sigma": 1, "base": None, "q": None}}
        self._method=method
        pass

    def __repr__(self):
        return f"hyperparameter(name={self.name}, index={self.index}, method={self.method})"
    
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
            if self._dimensions["Uniform"]["base"] is not None and self._dimensions["Uniform"]["q"] is not None: 
                return "qloguniform"
            if self._dimensions["Uniform"]["base"] is not None:
                return "loguniform"
            if self._dimensions["Uniform"]["q"] is not None:
                return "quniform"
            return "uniform"
        if self.method=="Normal":
            if self._dimensions["Normal"]["base"] is not None and self._dimensions["Normal"]["q"] is not None: 
                return "qlognormal"
            if self._dimensions["Normal"]["base"] is not None:
                return "lognormal"
            if self._dimensions["Normal"]["q"] is not None:
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
            dimension=dimensions
        elif self.method=="Uniform":
            if dimensions["isInt"]: 
                dimension={"low": dimensions["low"], "high": dimensions["high"]}
            else:
                dimension={key: dimensions[key] for key in dimensions if (key!="isInt" and dimensions[key] is not None)}
        else: 
            dimension={key: dimensions[key] for key in dimensions if dimensions[key] is not None}
        return {"method": opt_method, "dimension": dimension}

    def render(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        return html.Div(
            [
                html.H3("Undefined Hyperparameter" if self.name==None else self.name, id={"type": "hyperparameter-name", "index": self.index}, style={"font-weight": "normal"}),
                html.P(
                    "Specify a name and a sampling method to define this hyperparameter",
                    style={"font-weight": "normal"}
                ),
                # html.Hr(className="my-2"),
                dbc.Row(
                    [
                        dbc.Label('Name'),
                        dbc.Input(
                            className="input-element", 
                            id={"type": "hyperparameter-name-input", "index": self.index}, 
                            value=self.name
                        )
                    ]
                ),  
                dbc.Row(
                    [
                        dbc.Label('Method'),
                        dcc.Dropdown(
                            id={"type": "sampling-method-selector", "index": self.index},
                            options=make_options_from_list(list(self._dimensions)),
                            value=self._method,
                            # persistence=True,
                            # persistence_type="memory",
                            clearable=False
                        ),
                    ]
                ),
                html.Div(children=self.display_method, id={"type": "method-dimension-container", "index": self.index})
            ], 
            id={"type": "hyperparameter", "index": self.index}
        )

    @property
    def display_method(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        if self.method==None:
            return None
        dimensions=self.dimensions[self.method]
        if self.method=="Uniform":
            return [
                html.Div(
                    [
                        label_with_info_button(dbc.Label('Min'), id={"type": 'search-space-method-uniform-min-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["low"],
                            type="number", 
                            id={"type": "min", "index": self.index}
                        ),
                        label_with_info_button(dbc.Label('Max'), id={"type": 'search-space-method-uniform-max-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["high"], 
                            type="number", 
                            id={"type": "max", "index": self.index}
                        ),
                        dbc.Row(
                            [
                                dbc.Switch(
                                    id={"type": "isInt", "index": self.index},
                                    label="Uniform integer",
                                    value=False,
                                ),
                                info_button(id={"type": 'search-space-method-uniform-isInt-info', "index": self.index})
                            ]
                        ),                            
                        label_with_info_button(dbc.Label('Log base'), id={"type": 'search-space-method-uniform-base-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["base"], 
                            type="number", 
                            id={"type": "log", "index": self.index},
                            min=0
                        ),
                        label_with_info_button(dbc.Label('q'), id={"type": 'search-space-method-uniform-q-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["q"], 
                            type="number", 
                            id={"type": "q", "index": self.index},
                            min=0
                        )
                    ]
                )
            ]
        elif self.method=="Normal":
            return [
                html.Div(
                    [
                        label_with_info_button(dbc.Label('Center'), id={"type": 'search-space-method-normal-center-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["mu"], 
                            type="number", 
                            id={"type": "mu", "index": self.index}
                        ),
                        label_with_info_button(dbc.Label('Width'), id={"type": 'search-space-method-normal-width-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["sigma"], 
                            type="number", 
                            id={"type": "sigma", "index": self.index},
                            min=0
                        ),
                        label_with_info_button(dbc.Label('Log base'), id={"type": 'search-space-method-normal-base-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["base"], 
                            type="number", 
                            id={"type": "log", "index": self.index},
                            min=0),
                        label_with_info_button(dbc.Label('q'), id={"type": 'search-space-method-normal-q-info', "index": self.index}),
                        dbc.Input(
                            value=dimensions["q"], 
                            type="number", 
                            id={"type": "q", "index": self.index}, 
                            min=0
                        )
                    ]
                )
            ]
        elif self.method=="Categorical":
            return [
                html.Div(
                    [
                        label_with_info_button(dbc.Label('Values'), id={"type": 'search-space-method-category-info', "index": self.index}),
                        dbc.Input(
                            className="input-element", 
                            id={"type":"item-value-input", "index": self.index}, 
                            value="",
                            persistence=True,
                            persistence_type="memory"
                        ),
                        dbc.Button('Add Value', id={"type":"add-item-button", "index": self.index}, color='success', outline=True),
                        dbc.Checklist(
                            value=self._dimensions['Categorical']['categories'], 
                            options=self._dimensions['Categorical']['categories'], 
                            switch=True, 
                            inline=False, 
                            id={"type": "display-items", "index": self.index}
                        )
                    ]
                )
            ]
        else:
            return None

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
            if dimensions["categories"]:
                return True
        if self.method=="Uniform":
            if dimensions["low"]!=None and dimensions["high"]!=None:
                return True
        if self.method=="Normal":
            if dimensions["mu"]!=None and dimensions["sigma"]!=None:
                return True
        return False

    def display_search_space_element(self, review=False):
        content=[]
        for line in yaml.dump(self.search_space_element, sort_keys=False).split("\n"):
            content.append(line)
            content.append(html.Br())
        content.pop(-1)
        if not review:
            output=dbc.AccordionItem(
                    [
                        html.P(children=content),
                        dbc.Button(
                            'Mark for removal', 
                            color='danger', 
                            outline=True, 
                            id={"type": "display-searchspace-element-delete", "index": self.index}
                        ),
                    ], 
                    id={"type": "display-searchspace-element", "index": self.index}, 
                    title=self.name
                )
        else:
            output=dbc.AccordionItem(
                    [
                        html.P(children=content),
                    ], 
                    # id={"type": "display-searchspace-element", "index": self.index}, 
                    title=self.name
                )        
        return output
        


  