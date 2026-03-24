import requests
from datetime import date
# Note: Ensure these Secrets are added to GitHub Actions Settings
import os
URL = os.getenv('SUPABASE_URL')
KEY = os.getenv('SUPABASE_KEY')
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def check_pantry():
    r = requests.get(f"{URL}/rest/v1/inventory?select=*", headers=HEADERS)
    if r.status_code == 200:
        items = r.json()
        today = str(date.today())
        problems = [i['name'] for i in items if i['expiry_date'] == today]
        if problems:
            msg = f"Morning! Check your Halal Pantry—{', '.join(problems)} expire today."
            requests.post("https://ntfy.sh/sarib-pantry", data=msg.encode('utf-8'))

if __name__ == '__main__':
    check_pantry()
