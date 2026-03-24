import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import date
import json

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Halal Pantry AI", page_icon="🌙", layout="wide")

# --- 2. SECURE API SETUP & MODEL FINDER ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # NEW: Automatically find the best "Flash" model available to you
    # This prevents the "404 Not Found" error
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Order of preference for 2026
    preferred = ['models/gemini-3-flash-preview', 'models/gemini-3-flash', 'models/gemini-2.5-flash']
    MODEL_NAME = next((m for m in preferred if m in available_models), 'models/gemini-2.0-flash')
    
    model = genai.GenerativeModel(MODEL_NAME)
    
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    HEADERS = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
except Exception as e:
    st.error(f"⚠️ API Setup Error: {e}")
    st.stop()

# --- 3. APP NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📋 My Dashboard", "📸 Scan Receipt", "👨‍🍳 AI Halal Chef"])

inventory = [] # Placeholder for the get_inventory() logic from before

with tab1:
    st.header("Pantry Status")
    st.write(f"Currently using: `{MODEL_NAME}`")
    # (Existing dashboard code here...)

with tab2:
    st.header("📸 Smart Receipt Scanner")
    img_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=400)
        
        if st.button("🤖 Sync to Database"):
            with st.spinner("Analyzing..."):
                prompt = """Analyze this receipt. Return ONLY a JSON list of dictionaries.
                Keys: 'name', 'quantity' (integer), 'unit'.
                Example: [{"name": "Chicken", "quantity": 1, "unit": "kg"}]"""
                
                try:
                    # Explicitly use the model found by our finder
                    response = model.generate_content([prompt, img])
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    new_items = json.loads(clean_text)
                    
                    for item in new_items:
                        requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                      headers=HEADERS, 
                                      json={**item, "expiry_date": str(date.today())})
                    st.success(f"Successfully added {len(new_items)} items!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing receipt: {e}")

with tab3:
    st.header("👨‍🍳 AI Halal Chef")
    # (Existing chef code here...)