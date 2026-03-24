import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import date
import json

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Halal Pantry AI", page_icon="🌙", layout="wide")

# --- 2. SECURE API SETUP ---
try:
    # Using Gemini 3 Flash (the 2026 standard)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash')
    
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    HEADERS = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
except Exception as e:
    st.error("⚠️ Secrets Missing! Go to Streamlit Cloud > Settings > Secrets and paste your keys.")
    st.stop()

# --- 3. DATABASE FUNCTIONS ---
def get_inventory():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*&order=name.asc", headers=HEADERS)
        return r.json() if r.status_code == 200 else []
    except:
        return []

inventory = get_inventory()

# --- 4. SIDEBAR STRATEGY ---
st.sidebar.title("🍱 Shopping Strategy")
shopping_mode = st.sidebar.radio(
    "Select Mode:", 
    ["Economy (Lidl/Aldi Focus)", "Value (Tesco/Halal Grocers)", "Premium (Waitrose/Organic)"],
    help="Adjusts AI recipe suggestions and shopping tips for Bristol stores."
)

# --- 5. APP NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📋 My Dashboard", "📸 Scan Receipt", "👨‍🍳 AI Halal Chef"])

# TAB 1: DASHBOARD
with tab1:
    st.header("Pantry Status")
    if not inventory:
        st.info("Pantry is empty. Start by scanning a receipt!")
    
    for item in inventory:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{item['name']}** ({item['quantity']} {item['unit']})")
        if col2.button("🗑️", key=f"del_{item['id']}"):
            requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

# TAB 2: RECEIPT SCANNER
with tab2:
    st.header("📸 Smart Receipt Scanner")
    st.write("Upload a photo of your receipt to auto-fill your pantry.")
    img_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=400, caption="Uploaded Receipt")
        
        if st.button("🤖 Sync to Database"):
            with st.spinner("Gemini 3 is analyzing..."):
                prompt = """Analyze this receipt. Return ONLY a valid JSON list of dictionaries.
                Keys: 'name', 'quantity' (integer), 'unit' (e.g. kg, pack, liters).
                Example: [{"name": "Chicken", "quantity": 1, "unit": "kg"}]
                Exclude any text before or after the JSON."""
                
                try:
                    response = model.generate_content([prompt, img])
                    # Clean the response text for any markdown formatting
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    new_items = json.loads(clean_text)
                    
                    for item in new_items:
                        requests.post(
                            f"{SUPABASE_URL}/rest/v1/inventory", 
                            headers=HEADERS, 
                            json={**item, "expiry_date": str(date.today()), "is_essential": False}
                        )
                    st.success(f"Successfully added {len(new_items)} items!")
                    st.rerun()
                except Exception as e:
                    st.error("AI couldn't parse the receipt. Try a clearer photo.")
                    st.info(f"Technical Error: {e}")

# TAB 3: AI CHEF
with tab3:
    st.header("👨‍🍳 AI Halal Chef")
    if st.button("What can I cook right now?"):
        if not inventory:
            st.warning("Please add items to your pantry first!")
        else:
            item_list = [i['name'] for i in inventory]
            with st.spinner("Checking your ingredients..."):
                prompt = f"I have {', '.join(item_list)}. Suggest 3 Halal recipes. Style: {shopping_mode}."
                response = model.generate_content(prompt)
                st.markdown(response.text)

# --- 6. LOCAL SHOPPING TIPS ---
st.divider()
st.subheader("🛒 Local Shopping Tips")
if "Economy" in shopping_mode:
    st.info("💡 Check the Lidl on Muller Road or Aldi at Union Gate for the best deals this week.")
elif "Value" in shopping_mode:
    st.info("💡 Visit the Eastville Tesco or the Halal butchers on Stapleton Road.")
else:
    st.info("💡 Better Food Co. or Waitrose on Queens Road will have the premium organic items you're looking for.")