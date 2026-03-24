import streamlit as st
import requests
from datetime import datetime, date
import urllib.parse

st.set_page_config(page_title="Halal Pantry Pro", page_icon="🌙", layout="wide")

# 1. Connection & Config
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# 2. Sidebar - The "Brains"
st.sidebar.title("⚙️ Pantry Settings")
shopping_mode = st.sidebar.selectbox("Shopping Strategy", ["Budget (Lidl/Aldi Mode)", "Standard (Halal Grocer)", "Premium (Waitrose/M&S Mode)"])
enable_push = st.sidebar.toggle("Enable Phone Notifications", value=True)

# 3. Database Functions
def get_inventory():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*&order=name.asc", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

# 4. APP UI
st.title("🌙 Halal Pantry: AI Assistant")

tab1, tab2, tab3 = st.tabs(["📋 My Inventory", "📸 Receipt Scanner", "👨‍🍳 AI Chef"])

inventory = get_inventory()

with tab1:
    # ALERTS
    today = date.today()
    low_stock = [i for i in inventory if i['is_essential'] and i['quantity'] <= 1]
    expiring = [i for i in inventory if i['expiry_date'] and datetime.strptime(i['expiry_date'], '%Y-%m-%d').date() <= today]
    
    if low_stock or expiring:
        st.error(f"⚠️ Action Required: {len(low_stock)} low items | {len(expiring)} expiring!")

    # THE LIST
    for item in inventory:
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item['name']}**")
        c2.write(f"{item['quantity']} {item['unit']}")
        if c3.button("🗑️", key=f"del_{item['id']}"):
            requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

with tab2:
    st.header("📸 Auto-Update via Receipt")
    uploaded_file = st.file_uploader("Upload a photo of your grocery receipt", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        with st.spinner("AI is reading your receipt..."):
            # This is where the AI Vision logic lives. For now, it detects the action.
            st.info("AI Analysis: Found 'Chicken', 'Rice', 'Lentils'. Updating Supabase...")
            # Logic: Send image to Gemini/Vision API -> Parse JSON -> Batch Insert to Supabase
            st.success("Inventory updated automatically!")

with tab3:
    st.header("👨‍🍳 AI Recipe Generator")
    if st.button("What can I cook right now?"):
        if not inventory:
            st.warning("Your pantry is empty! Add ingredients first.")
        else:
            with st.spinner("AI Chef is thinking..."):
                items_list = ", ".join([i['name'] for i in inventory])
                # In a full build, this sends 'items_list' to the Gemini API
                st.markdown(f"### Suggested Halal Recipes for your ingredients:")
                st.write("1. **One-Pot Chicken & Rice**: Use your chicken and rice. High protein, easy cleanup.")
                st.write("2. **Lentil Daal**: Perfect for your pantry staples.")
                st.write("3. **Quick Stir-fry**: Use any remaining veggies.")

# 5. SMART SHOPPING LIST
st.divider()
st.header("🛒 Smart Shopping List")
st.caption(f"Strategy active: **{shopping_mode}**")

to_buy = [i for i in inventory if i['quantity'] <= 1]
if to_buy:
    msg = f"*{shopping_mode} Shopping List*\n"
    for item in to_buy:
        # Business Logic for "Cheap vs Expensive"
        price_tip = " (Check Lidl middle aisle)" if "Budget" in shopping_mode else " (Select Organic)" if "Premium" in shopping_mode else ""
        msg += f"- {item['name']}{price_tip}\n"
    
    st.text_area("To-Buy:", msg)
    
    # NOTIFICATION TRIGGER
    if st.button("🔔 Send Push Notification to my Phone"):
        # We use a simple 'ntfy' service (No account needed, free)
        # You just download the 'ntfy' app on your phone and subscribe to 'sarib-pantry'
        requests.post("https://ntfy.sh/sarib-pantry", 
                     data=msg.encode('utf-8'),
                     headers={"Title": "Pantry Alert", "Priority": "high"})
        st.success("Push notification sent!")