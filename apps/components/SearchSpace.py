from dash import html, dcc
import dash_bootstrap_components as dbc
import yaml
from .utils import make_options_from_list, label_with_info_button, info_button

class Hyperparameter:
    def __init__(self, index, name=None, method='categorical'):
        self._index=index
        self._name=name
        self._dimensions={
            "categorical": {"categories": []},
            "uniform": {"low": 0, "high": 1},
        }
        self._method=method

    def __repr__(self):
        return f"hyperparameter(name={self.name}, index={self.index}, method={self.method})"
    
    def parse(self, name, value):
        try:
            self.name=name
            self.method=value['method']
            self._dimensions['categorical']['categories']=value['dimension']['categories']
            self._dimensions['uniform']['low']=value['dimension']['low']
            self._dimensions['uniform']['high']=value['dimension']['high']
            return True
        except Exception as e:
            print(e)
            return False

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
        if newmethod in self._dimensions.keys():
            self._method=newmethod
        else:
            raise ValueError('method must be one of ("categorical", "uniform")')
    
    @property
    def opt_method(self):
        return self.method
    
    @property
    def search_space_element(self):
        return {"method": self.method, "dimension": self._dimensions[self.method]}

    def render(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        return dbc.Col(
            [
                html.H3("Undefined Hyperparameter" if self.name==None else self.name, id={"type": "hyperparameter-name", "index": self.index}, style={"font-weight": "normal"}), 
                dbc.Row(
                    [
                        dbc.Label('Search method'),
                        dcc.Dropdown(
                            id={"type": "sampling-method-selector", "index": self.index},
                            options=make_options_from_list(list(self.dimensions.keys())),
                            value=self.method,
                            persistence=True,
                            persistence_type="memory",
                            clearable=False
                        ),
                    ]
                ),
                html.Div(children=self.display_method, id={"type": "method-dimension-container", "index": self.index})
            ], 
            id={"type": "hyperparameter", "index": self.index},
            width=6
        )

    @property
    def display_method(self):
        labelWidth=3
        labelSize="sm"
        labelAlign="center"
        if self.method is None:
            return None
        dimensions=self._dimensions[self.method]
        # print(self._dimensions)
        return [
            html.Div(
                [
                    dbc.Row(label_with_info_button(dbc.Label('Categories'), id={"type": 'search-space-method-category-info', "index": self.index})),
                    dbc.Row(
                        [    
                            dbc.Col(
                                [
                                    dbc.Textarea(
                                        # className="input-element", 
                                        id={"type":"item-value-input", "index": self.index}, 
                                        value=",".join(self._dimensions["categorical"]['categories']),
                                        debounce=False,
                                        rows=5,
                                        placeholder="A comma-separated list of catgegories"
                                        # persistence=True,
                                        # persistence_type="memory"
                                    )
                                ],
                            ),
                            # dbc.Col(dbc.Button('+', id={"type":"add-item-button", "index": self.index}, color='success', outline=True), width=3),
                        ]
                    ),
                    # dbc.Checklist(
                    #     value=self._dimensions["categorical"]['categories'], 
                    #     options=self._dimensions["categorical"]['categories'], 
                    #     # switch=True, 
                    #     inline=False, 
                    #     id={"type": "display-items", "index": self.index}
                    # )
                ],
                hidden=(self.method!='categorical')
            ),
            html.Div(
                [
                    label_with_info_button(dbc.Label('Low'), id={"type": 'search-space-method-uniform-min-info', "index": self.index}),
                    dbc.Input(
                        value=self._dimensions["uniform"]["low"],
                        type="number", 
                        placeholder='Lower bound of uniform distribution',
                        id={"type": "min", "index": self.index}
                    ),
                    label_with_info_button(dbc.Label('High'), id={"type": 'search-space-method-uniform-max-info', "index": self.index}),
                    dbc.Input(
                        value=self._dimensions["uniform"]["high"], 
                        type="number", 
                        placeholder='Lower bound of uniform distribution',
                        id={"type": "max", "index": self.index}
                    ),
                ],
                hidden=(self.method!='uniform')
            ),
            dbc.Row(    
                dbc.Col(    
                    dbc.Button(
                        'Remove', 
                        color='danger', 
                        outline=True, 
                        id={"type": "delete-button", "index": self.index}
                    ),
                    width=3,
                    style={'margin': '1rem'}
                ),
                justify='center'
            ),
        ]


    # @property
    # def method_selector(self):
    #     messages={
    #     "Categorical": "The value of this hyperparameter in a hyperparameter point is uniformly picked from a list of values that you will specify.",
    #     'Normal': 'The numerical value of this hyperparameter or its logarithm is sampled over a Gaussian distribution defined by a mean \u03BC and variance \u03C3\u00B2 that you will specify.',
    #     'Uniform': 'The numberical value of this hyperparameter or logarithms is uniformly sampled from a range that you will specify'
    #     }
    #     return dbc.Card([
    #             dbc.CardHeader("Select a sampling method"), 
    #             dbc.CardBody([
    #                 dbc.RadioItems(options=[
    #                 {"label": "Categorical", "value": "Categorical"},
    #                 {"label": "Normal", "value": "Normal"},
    #                 {"label": "Uniform", "value": "Uniform"},
    #             ],
    #             value=self.method,
    #             inline=True,
    #             id={"type": "method-radio-selector", "index": self.index}), 
    #                 html.Hr(), 
    #                 dbc.Toast(children=None if self.method==None else messages[self.method], header="No method selected" if self.method==None else self.method, icon="danger" if self.method==None else "success", id={"type": "method-info", "index": self.index}, is_open=True, style={"maxWidth": "100%"}) ])
    #         ], outline=True, color="danger" if self.method==None else "success", id={"type": "method-selector-container", "index": self.index})

    @property
    def is_valid(self):
        if self.method not in ['categorical', 'uniform']: 
            return False, f'Check {self.name}: method'
        dimensions=self.dimensions[self.method]
        if self.method=="categorical":
            if not (isinstance(dimensions["categories"], list) and len(dimensions['categories']) > 0):
                return False, f'Check {self.name}: categories'
        else:
            if not (isinstance(dimensions["low"], (int, float)) and isinstance(dimensions["high"], (int, float)) and dimensions['high'] > dimensions['low']):
                return False, f'Check {self.name}: min and max'
        return True, None

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
    
    @property
    def memory_element(self):
        return {
            'name': self.name, 
            'method': self.method, 
            'dimension': {
                "categories": self._dimensions['categorical']['categories'], 
                "low": self._dimensions['uniform']['low'], 
                'high': self._dimensions['uniform']['high']
            }
        }
        
class SearchSpace:
    def __init__(self):
        self.search_space = {}
    
    @property
    def new_id(self):
        id=0
        while id in self.search_space.keys():
            id+=1
        return id
    
    @property
    def name_list(self):
        return [h['name'] for h in self.search_space.values()]

    def parse_from_memory(self, memory):
        for id, element in memory.items():
            try:
                index = int(id)
                tmp = Hyperparameter(index)
                tmp.parse(element['name'], {'method': element['method'], 'dimension': element['dimension']})
                self.search_space[index] = tmp.memory_element
            except Exception as e:
                print(f'Parsing error: {e}')
                continue
    
    def add_hyperparameter(self, name, value=None):
        if name in self.name_list:
            return 
        index = self.new_id
        new_hp = Hyperparameter(index, name)
        if isinstance(value, dict):
            try:
                new_hp.method=value.get('method', 'categorical')
                new_hp._dimensions['categorical']['categories']=value.get('dimension', {}).get('categories', [])
                new_hp._dimensions['uniform']['low']=value.get('dimension', {}).get('low', 0)
                new_hp._dimensions['uniform']['high']=value.get('dimension', {}).get('high', 1)
            except Exception as e:
                print(e)
                pass
        self.search_space[index] = new_hp.memory_element

    @property
    def search_space_objects(self):
        objects = {}
        for index, element in self.search_space.items():
            tmp = Hyperparameter(index)
            tmp.parse(element['name'], {'method': element['method'], 'dimension': element['dimension']})
            objects[index] = tmp
        return objects

    @property
    def is_valid(self):
        return [hp.is_valid for hp in self.search_space_objects.values()]
    
    @property
    def json_search_space(self):
        return {element.name: element.search_space_element for element in self.search_space_objects.values()}

class Hyperparameters(SearchSpace):
    def __init__(self):
        super().__init__()

    def parse_from_memory(self, memory):
        for id, element in memory.items():
            try:
                index = int(id)
                tmp = Hyperparameter(index)
                tmp.parse(element['name'], {'method': element['method'], 'dimension': element['dimension']})
                self.search_space[index] = element
                self.search_space_object.append(tmp)
            except Exception as e:
                print(e)
                continue


  