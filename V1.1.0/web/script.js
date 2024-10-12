async function loadPyodideAndPackages() {
    window.pyodide = await loadPyodide({
        indexURL : "https://cdn.jsdelivr.net/pyodide/v0.21.0/full/"
    });
}

async function submitForm() {
    const fields = [
        { id: 'composioApiKey', name: 'Composio API Key' },
        { id: 'entityId', name: 'Entity ID' },
        { id: 'pluginId', name: 'Plugin ID' },
        { id: 'schemaVersion', name: 'Schema Version' },
        { id: 'nameForHuman', name: 'Name for Human' },
        { id: 'nameForModel', name: 'Name for Model' },
        { id: 'descriptionForHuman', name: 'Description for Human' },
        { id: 'descriptionForModel', name: 'Description for Model' }
    ];

    let isValid = true;
    let errorMessage = '以下欄位是必填的:\n';

    fields.forEach(field => {
        const element = document.getElementById(field.id);
        if (!element.value) {
            element.classList.add('is-invalid');
            errorMessage += `- ${field.name}\n`;
            isValid = false;
        } else {
            element.classList.remove('is-invalid');
        }
    });

    if (!isValid) {
        alert(errorMessage);
        return;
    }

    const selectedApps = Array.from(document.querySelectorAll('input[name="app"]:checked')).map(checkbox => checkbox.value);

    const data = {
        composioApiKey: document.getElementById('composioApiKey').value,
        entityId: document.getElementById('entityId').value,
        pluginId: document.getElementById('pluginId').value,
        schemaVersion: document.getElementById('schemaVersion').value,
        nameForHuman: document.getElementById('nameForHuman').value,
        nameForModel: document.getElementById('nameForModel').value,
        descriptionForHuman: document.getElementById('descriptionForHuman').value,
        descriptionForModel: document.getElementById('descriptionForModel').value,
        app: selectedApps
    };
    await loadPyodideAndPackages();

    const pythonCode = `
import json

data = ${JSON.stringify(data)}

data_template = {
    'id': data['pluginId'],
    'schema_version': data['schemaVersion'],
    'name_for_human': data['nameForHuman'],
    'name_for_model': data['nameForModel'],
    'description_for_human': data['descriptionForHuman'],
    'description_for_model': data['descriptionForModel'],
    'auth': {
        'type': 'none'
    },
    'api': {
        'type': 'python',
        'python': {
            'source': f"""
import json
import asyncio
from pyodide.http import pyfetch

async def get_from_port():
    try:
        resp = await pyfetch(
            'http://127.0.0.1:5001',
            method="POST",
            headers={{'Content-Type': 'application/json'}},
            body=json.dumps({{
                'Composio_API_KEY': '{data['composioApiKey']}',
                'Entity_ID': '{data['entityId']}',
                'App': {data['app']}
            }})
        )

        if resp.status == 200:
            return await resp.json()
        else:
            return f"Error{{resp.status}}"

    except Exception as e:
        return f"Request failed{{e}}"

async def run_action(response):
    try:
        resp = await pyfetch(
            'http://127.0.0.1:5001/run',
            method="POST",
            headers={{'Content-Type': 'application/json'}},
            body=json.dumps({{'Composio_API_KEY': '{data['composioApiKey']}',
            'Entity_ID': '{data['entityId']}',
            'response': response}})
        )

        if resp.status == 200:
            return await resp.json()
        else:
            return f"Error{{resp.status}}"

    except Exception as e:
        return f"Request failed{{e}}"

async def main():
    get_tools = await get_from_port()
    # print(type(get_tools))

    conversation = CURRENT_CONVERSATION + [
        {{
            "role": "system",
            "content": "You are a super intelligent personal assistant, you can help me find what to do."
        }}
    ]

    # print(get_tools['response']['function'])

    response = await chat(
        conversation=conversation,
        functions=[get_tools['response']['function']],
    )

    result = await run_action(response)
    print(result)

await main()
"""
        }
    }
}

with open('/plugin.json', 'w', encoding='utf8') as file:
    json.dump(data_template, file, ensure_ascii=False, indent=2)
    `;

    await pyodide.runPythonAsync(pythonCode);

    const output = pyodide.FS.readFile('/plugin.json', { encoding: 'utf8' });
    const blob = new Blob([output], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'plugin.json';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);

    // 檔案下載完畢後顯示提示訊息並刷新頁面
    alert('檔案下載完畢');
    location.reload();
}