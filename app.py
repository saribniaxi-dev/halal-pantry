import streamlit as st
import requests
from datetime import datetime, date

st.set_page_config(page_title="Halal Pantry", page_icon="🍳", layout="wide")

# 1. Setup Connection
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# 2. Database Functions
def get_inventory():
    url = f"{SUPABASE_URL}/rest/v1/inventory?select=*&order=name.asc"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def update_quantity(item_id, new_qty):
    url = f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item_id}"
    requests.patch(url, headers=HEADERS, json={"quantity": new_qty})
    st.rerun()

def delete_item(item_id):
    url = f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item_id}"
    requests.delete(url, headers=HEADERS)
    st.rerun()

# --- APP UI ---
st.title("🍳 My Halal Pantry")

inventory = get_inventory()

# 3. SMART ALERTS SECTION
st.subheader("⚠️ Smart Alerts")
cols = st.columns(3)
today = date.today()

# Logic for alerts
low_stock = [i for i in inventory if i['is_essential'] and i['quantity'] <= 1]
expiring_soon = [i for i in inventory if i['expiry_date'] and datetime.strptime(i['expiry_date'], '%Y-%m-%d').date() <= today]

with cols[0]:
    if low_stock:
        st.error(f"Restock Needed: {len(low_stock)} essential items are low!")
    else:
        st.success("Essentials are fully stocked.")

with cols[1]:
    if expiring_soon:
        st.warning(f"Expiry Alert: {len(expiring_soon)} items expire today or sooner!")
    else:
        st.success("No immediate expiries.")

# 4. INVENTORY MANAGEMENT
st.divider()
st.header("📋 Current Inventory")

if not inventory:
    st.info("Your pantry is empty.")
else:
    # Creating a table-like header
    h_col1, h_col2, h_col3 = st.columns([3, 2, 2])
    h_col1.write("**Item Name**")
    h_col2.write("**Quantity**")
    h_col3.write("**Manage**")

    for item in inventory:
        col1, col2, col3 = st.columns([3, 2, 2])
        
        # Column 1: Name and Expiry
        essential_tag = "⭐ " if item['is_essential'] else ""
        col1.write(f"{essential_tag}{item['name']}")
        col1.caption(f"Expires: {item['expiry_date']}")
        
        # Column 2: Quantity
        col2.write(f"{item['quantity']} {item['unit']}")
        
        # Column 3: Quick Buttons
        btn_col1, btn_col2, btn_col3 = col3.columns(3)
        if btn_col1.button("➖", key=f"min_{item['id']}"):
            update_quantity(item['id'], max(0, item['quantity'] - 1))
        if btn_col2.button("➕", key=f"add_{item['id']}"):
            update_quantity(item['id'], item['quantity'] + 1)
        if btn_col3.button("🗑️", key=f"del_{item['id']}"):
            delete_item(item['id'])

# 5. ADD NEW FOOD FORM (Simplified)
with st.expander("➕ Add New Item to Pantry"):
    with st.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Food Name")
        f_qty = st.number_input("Quantity", min_value=0.0, value=1.0)
        f_unit = st.selectbox("Unit", ["pieces", "kg", "grams", "liters", "packs"])
        f_date = st.date_input("Expiry Date")
        f_ess = st.checkbox("Essential (Always-Have)")
        
        if st.form_submit_button("Save to Database"):
            new_data = {"name": f_name, "quantity": f_qty, "unit": f_unit, "expiry_date": str(f_date), "is_essential": f_ess}
            requests.post(f"{SUPABASE_URL}/rest/v1/inventory", headers=HEADERS, json=new_data)
            st.rerun()