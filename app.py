import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import date

st.set_page_config(page_title="Halal Pantry AI", page_icon="🌙")

# 1. Secure API Setup
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
except KeyError:
    st.error("🔑 API Keys missing! Please add them to the Streamlit Secrets dashboard.")
    st.stop()

# 2. Database Sync
def get_inventory():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

inventory = get_inventory()
tab1, tab2, tab3 = st.tabs(["📋 Dashboard", "📸 Scan", "👨‍🍳 Chef"])

with tab1:
    st.header("My Pantry")
    for item in inventory:
        st.write(f"✅ {item['name']} - {item['quantity']} {item['unit']}")

with tab2:
    st.header("📸 Scan Receipt")
    img_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        if st.button("🤖 Sync to Database"):
            with st.spinner("AI is reading receipt..."):
                prompt = "List food items in this format: [{'name': 'Chicken', 'quantity': 1, 'unit': 'kg'}]"
                try:
                    # The 'models/' prefix helps avoid the NotFound error
                    response = genai.GenerativeModel('models/gemini-1.5-flash').generate_content([prompt, img])
                    items = eval(response.text.strip().replace("```python", "").replace("```", ""))
                    for i in items:
                        requests.post(f"{SUPABASE_URL}/rest/v1/inventory", headers=HEADERS, json={**i, "expiry_date": str(date.today())})
                    st.success("Pantry Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")

with tab3:
    st.header("👨‍🍳 AI Chef")
    if st.button("Generate Recipes"):
        names = [i['name'] for i in inventory]
        response = model.generate_content(f"I have {names}. Suggest 3 Halal recipes.")
        st.markdown(response.text)