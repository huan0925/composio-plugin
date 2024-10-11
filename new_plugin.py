import json
import asyncio
from pyodide.http import pyfetch

async def get_from_port():
    try:
        resp = await pyfetch(
            'http://127.0.0.1:5001',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'Composio_API_KEY': 'nz8dbhjwoibd3iee6l45b',
            'Entity_ID': 'Arlo',
            'App': ['Gmail']})
        )

        if resp.status == 200:
            return await resp.json()
        else:
            return f"Error{resp.status}"

    except Exception as e:
        return f"Request failed{e}"

async def run_action(response):
    try:
        resp = await pyfetch(
            'http://127.0.0.1:5001/run',
            method="POST",
            headers={'Content-Type': 'application/json'},
            body=json.dumps({'Composio_API_KEY': 'nz8dbhjwoibd3iee6l45b',
            'Entity_ID': 'Arlo',
            'response': response})
        )

        if resp.status == 200:
            return await resp.json()
        else:
            return f"Error{resp.status}"

    except Exception as e:
        return f"Request failed{e}"

async def main():
    get_tools = await get_from_port()
    # print(type(get_tools))

    conversation = CURRENT_CONVERSATION + [
        {
            "role": "system",
            "content": "You are a super intelligent personal assistant, you can help me find what to do."
        }
    ]

    # print(get_tools['response']['function'])

    response = await chat(
        conversation=conversation,
        functions=[get_tools['response']['function']],
    )

    result = await run_action(response)
    print(result)

await main()
