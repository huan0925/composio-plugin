from flask import Flask, render_template, request
from flask_cors import CORS

import os
from openai import OpenAI
from composio_openai import ComposioToolSet, App
from composio import Action
from composio.client.exceptions import NoItemsFound
 
app = Flask(__name__)
# Enable CORS for all domains on all routes
CORS(app)

def run_composio(Composio_API_KEY, Entity_ID, App_list):
    # Initialize ComposioToolSet
    composio_toolset = ComposioToolSet(api_key=Composio_API_KEY, entity_id=Entity_ID)
   
    # Check if the app is valid
    App_list_attr = []
    for app in App_list:
        # print(app)
        app_enum = getattr(App, app.upper(), None)
        if app_enum is None:
            raise ValueError(f'Invalid name')
        else:
            App_list_attr.append(app_enum)
    tool = composio_toolset.get_tools(apps=App_list_attr)
    # tool = composio_toolset.get_tools(apps=[App.GMAIL])

    # return app all action to DaVinci
    return tool[0]
        

def run_action(response, Composio_API_KEY, Entity_ID):
    # Initialize ComposioToolSet
    composio_toolset = ComposioToolSet(api_key=Composio_API_KEY, entity_id=Entity_ID)
    
    # convert string to python object
    if response['arguments'].find('true') != -1:
        res_pre = response['arguments'].replace('true', 'True')
        res = eval(res_pre)
    elif response['arguments'].find('false') != -1:
        res_pre = response['arguments'].replace('false', 'False')
        res = eval(res_pre)
    else:
        res = eval(response['arguments'])

    # get app action
    app_enum = getattr(Action, response['name'].upper(), None)
    print(app_enum)

    # execute app action
    result = composio_toolset.execute_action(action = app_enum, params = res, entity_id= Entity_ID)
    return result
 
# get app action
@app.route('/', methods=['POST'])
def home():
    data = request.get_json()
    Composio_API_KEY = data['Composio_API_KEY']
    Entity_ID = data['Entity_ID']
    App_list = data['App']
    response = run_composio(Composio_API_KEY, Entity_ID, App_list)
    response_data = {"response": response}
    
    return response_data


@app.route('/run', methods=['POST'])
def run_app():
    data = request.get_json()
    Composio_API_KEY = data['Composio_API_KEY']
    Entity_ID = data['Entity_ID']
    response = data['response']['function_call']
    # print(data)
    res = run_action(response, Composio_API_KEY, Entity_ID)
    response_data = {"response": res}
    
    return response_data   

 
if __name__ == '__main__':
    app.run(debug=True, port=5001)
