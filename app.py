import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import datetime, date

st.set_page_config(page_title="Halal Pantry AI", page_icon="🌙", layout="wide")

# 1. API Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# 2. Sidebar - Strategy Logic
st.sidebar.title("🍱 Shopping Strategy")
shopping_mode = st.sidebar.radio(
    "Select Mode:", 
    ["Economy (Lidl/Aldi Focus)", "Value (Tesco/Halal Grocers)", "Premium (Waitrose/Organic)"],
    help="Changes AI suggestions and shopping tips."
)

# 3. Database Function
def get_inventory():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*&order=name.asc", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

inventory = get_inventory()

# 4. THE NAVIGATION TABS (This is what you were missing!)
tab1, tab2, tab3 = st.tabs(["📋 My Dashboard", "📸 Scan Receipt", "👨‍🍳 AI Halal Chef"])

with tab1:
    st.header("Pantry Status")
    if not inventory:
        st.info("Your pantry is empty. Use the scanner to add items!")
    for item in inventory:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{item['name']}** ({item['quantity']} {item['unit']})")
        if col2.button("🗑️", key=f"del_{item['id']}"):
            requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

with tab2:
    st.header("📸 Smart Receipt Scanner")
    img_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300)
        if st.button("🤖 Sync to Database"):
            with st.spinner("AI is analyzing and saving..."):
                # We ask Gemini for a specific format so the code can read it
                prompt = """Analyze this receipt. Return ONLY a Python-style list of dictionaries 
                for food items with keys: 'name', 'quantity' (as number), 'unit' (e.g. kg, pieces, liters). 
                Example: [{'name': 'Chicken', 'quantity': 2, 'unit': 'kg'}]"""
                
                response = model.generate_content([prompt, img])
                
                try:
                    # This converts the AI text into actual data
                    new_items = eval(response.text.strip().replace("```python", "").replace("```", ""))
                    for item in new_items:
                        requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                      headers=HEADERS, 
                                      json={**item, "expiry_date": str(date.today()), "is_essential": False})
                    st.success(f"Added {len(new_items)} items to your pantry!")
                    st.rerun()
                except:
                    st.error("AI list format was slightly off. Try again or check the text output.")
                    st.write(response.text)

with tab3:
    st.header("👨‍🍳 AI Halal Chef")
    if st.button("What can I cook right now?"):
        if not inventory:
            st.warning("Your pantry is empty! Add ingredients first so the AI knows what you have.")
        else:
            # This line gets your actual list of food from Supabase
            items = [i['name'] for i in inventory]
            
            with st.spinner("The AI Chef is looking at your pantry..."):
                # This prompt tells the AI exactly what you have
                prompt = f"I have these ingredients: {', '.join(items)}. Please suggest 3 Halal recipes. Match the style to: {shopping_mode}."
                
                # This line actually calls the Gemini Brain
                response = model.generate_content(prompt)
                
                # This displays the AI's real answer
                st.markdown(response.text)

# 5. LOCAL SHOPPING LOGIC
st.divider()
st.header("🛒 Smart Shopping List")
to_buy = [i for i in inventory if i['quantity'] <= 1]
if to_buy:
    for item in to_buy:
        if "Economy" in shopping_mode:
            tip = "💡 Tip: Check Lidl on Muller Road for the best price."
        elif "Premium" in shopping_mode:
            tip = "💡 Tip: Check Waitrose or M&S for organic options."
        else:
            tip = "💡 Tip: Try the Eastville Tesco or Stapleton Road butchers."
        st.warning(f"**Restock: {item['name']}** — {tip}")

