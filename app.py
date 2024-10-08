from flask import Flask, render_template, request
from flask_cors import CORS

import os
from openai import OpenAI
from composio_openai import ComposioToolSet, App
from composio.client.exceptions import NoItemsFound
 
def run_composio(msg, Davinci_API_KEY, Composio_API_KEY, Entity_ID, App_list):
    # 初始化 OpenAI 客戶端
    openai_client = OpenAI(
        base_url = "https://prod.dvcbot.net/api/assts/v1",
        api_key = Davinci_API_KEY
    )

    # 初始化 Composio 工具集

    # Youtube
    # composio_toolset = ComposioToolSet(api_key="nz8dbhjwoibd3iee6l45b", entity_id="default")
    #Gmail
    composio_toolset = ComposioToolSet(api_key=Composio_API_KEY, entity_id=Entity_ID)
   
    # 步驟 3：通過 Composio 獲取所有 GitHub 工具
    App_list_attr = []
    
    for app in App_list:
        print(app)
        app_enum = getattr(App, app.upper(), None)
        if app_enum is None:
            raise ValueError(f'Invalid name')
        else:
            App_list_attr.append(app_enum)
    tool = composio_toolset.get_tools(apps=App_list_attr)
    # tool = composio_toolset.get_tools(apps=[App.YOUTUBE, App.GMAIL])
    # tool = composio_toolset.get_tools(apps=[App.GMAIL, App.YOUTUBE])
    my_task = msg # 在達哥輸入的內容

    # Setup openai assistant
    assistant_instruction = "You are a super intelligent personal assistant, you can help me find what to do."

    assistant = openai_client.beta.assistants.create(
        name="Personal Assistant",
        instructions=assistant_instruction,
        model="aide-gpt-4o", 
        tools=tool,  # 使用之前獲取的 GitHub 操作
        metadata = {"backend_id": "default"}
    )

    # create a thread
    thread = openai_client.beta.threads.create()
    message = openai_client.beta.threads.messages.create(thread_id=thread.id,role="user",content=my_task)
    
    # Execute Agent with integrations
    run = openai_client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id) # choose action
    response_after_tool_calls = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread,
    )
    
    while run.status in ["queued", "in_progress"]:
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id = run.id)
        print(run.status)

    if run.status == "requires_action":
        print(run)
    elif run.status == "failed":
        print(run)
    else:
        messages = openai_client.beta.threads.messages.list(thread_id=thread.id).data
        print(messages[0])
    
    return messages[0].content[0].text.value

# def integration(entity_id):
#     toolset = ComposioToolSet()
#     integration_id = "edf69af4-69a1-48c9-a827-4a971ffc88b1" # Gmail integration id
#     entity = toolset.get_entity(id=entity_id)

#     integration = toolset.client.integrations.get_by_id(integration_id=integration_id)

#     try:    
#         connection = entity.get_connection(app=App.GMAIL)
#         # Connection Already exist with Github. 
#         # Now we can check if it's using the correct integration

#         if connection:
#             connection_integration_id = connection.integrationId
#             if connection_integration_id == integration_id:
#                 # Connection is already active with the correct integration
#                 print(f"User is already authenticated with GitHub")
#             else:
#                 # Connection is active with a different integration
#                 # TODO: Choose between the following options:
#                 # 1. Create a new connection with the correct integration
#                 # 2. Ignore as it's fine
#                 print(f"User is already authenticated with GitHub but with a different integration")
        
#         # print(f"User is already authenticated with GitHub")
#         return "connected"

#     except NoItemsFound as e:
#         # Create a request to initiate connection
#         request = entity.initiate_connection(App.GMAIL,integration=integration)

#         return {'url': request.redirectUrl}
#         # return f"Please authenticate {App.GMAIL} in the browser and come back here. URL: {request.redirectUrl}"
        
#         # return request.redirectUrl
#         # Poll until the connection is active
#         # connected_account = request.wait_until_active(client=toolset.client, timeout=100)
        

app = Flask(__name__)
# Enable CORS for all domains on all routes
CORS(app)
 
@app.route('/', methods=['POST'])
def home():
    data = request.get_json()
    headers={
      "Content-Type":"application/json"
    }
    # entity_id = data['username']
    # confirm = integration(entity_id)
    # if confirm == 'connected':
    #     return data
    # else:
    #     print("please connect first")
    #     return confirm
    print(data)
    msg = data['conversation'][-1]['content']
    Davinci_API_KEY = data['Davinci_API_KEY']
    Composio_API_KEY = data['Composio_API_KEY']
    Entity_ID = data['Entity_ID']
    App_list = data['App']
    # print(msg)
    response = run_composio(msg, Davinci_API_KEY, Composio_API_KEY, Entity_ID, App_list)
    # print(response)
    response_data = {"response": response}
    
    return response_data
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
