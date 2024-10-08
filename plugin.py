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
            'Davinci_API_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJEVkNBU1NJIiwic3ViIjoiRFNfQVJMTy5MSU5ATUVESUFURUsuQ09NIiwiYXVkIjpbIkRWQ0FTU0kiXSwiaWF0IjoxNzI0MjI4NzU0LCJqdGkiOiJjNjU2ZWI2ZC1kYjRjLTQ4NDAtYTU1Ny1mZjkxNmE4YzZjMDYifQ.XbCKaXNEYmJceyRM-jC1sK_NnwA77i0Z7BWJYI1xA9Q',
            'Composio_API_KEY': 'nz8dbhjwoibd3iee6l45b',
            'Entity_ID': 'Arlo',
            'App': ['YOUTUBE','GMAIL']})
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
