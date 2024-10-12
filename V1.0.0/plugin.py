import json
import asyncio
from pyodide.http import pyfetch

async def get_from_port(conversation):
    try:
        resp = await pyfetch(
            'http://127.0.0.1:5001',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps({"conversation": conversation,
            'Davinci_API_KEY': [DaVinci API Key],
            'Composio_API_KEY': [Composio API Key],
            'Entity_ID': [Entity ID],
            'App': [APP_List]})
        )

        if resp.status == 200:
            return await resp.json()
        else:
            return f"Error{resp.status}"

    except Exception as e:
        return f"Request failed{e}"

async def main():
    conversation = CURRENT_CONVERSATION
    # username = await get_user()
    result = await get_from_port(conversation)
    print("Received from port:", result)

await main()
