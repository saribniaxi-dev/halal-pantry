import requests

try:
    with open('.streamlit/secrets.toml', 'r') as f:
        content = f.read()
    
    supabase_url = ''
    supabase_key = ''
    
    for line in content.splitlines():
        if "SUPABASE_URL" in line:
            supabase_url = line.split('=')[1].strip().strip('"').strip("'")
        if "SUPABASE_KEY" in line:
            supabase_key = line.split('=')[1].strip().strip('"').strip("'")
            
    if not supabase_url or not supabase_key:
        print('Missing SUPABASE_URL or SUPABASE_KEY in secrets.')
        exit(1)

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}'
    }

    url = f'{supabase_url}/rest/v1/inventory?select=*'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        items = response.json()
        print(f'Connection Successful! HTTP 200.')
        print(f'Inventory items count: {len(items)}')
    else:
        print(f'Connection Failed! HTTP {response.status_code}')
        print(response.text)
except Exception as e:
    print(f'Error checking Supabase connection: {e}')