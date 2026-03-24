import requests
from datetime import date

# These will be pulled from GitHub's secret vault later
URL = "YOUR_SUPABASE_URL"
KEY = "YOUR_SUPABASE_KEY"
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def check_pantry():
    r = requests.get(f"{URL}/rest/v1/inventory?select=*", headers=HEADERS)
    items = r.json()
    today = str(date.today())
    
    # Logic: Find items expiring today or essentials that are low
    problems = [i['name'] for i in items if i['expiry_date'] == today or (i['is_essential'] and i['quantity'] <= 1)]
    
    if problems:
        msg = f"Morning Sarib! Quick update: {', '.join(problems)} need your attention today."
        requests.post("https://ntfy.sh/sarib-pantry", data=msg.encode('utf-8'))

if __name__ == "__main__":
    check_pantry()