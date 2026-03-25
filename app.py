import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import date
import json

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Halal Pantry AI", page_icon="🌙", layout="wide")

# --- 2. SECURE API SETUP & MODEL FINDER ---
model = None
SUPABASE_URL = None
SUPABASE_KEY = None
HEADERS = None

try:
    # Try to get API key from secrets, fallback to ADC
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    # NEW: Automatically find the best "Flash" model available to you
    # This prevents the "404 Not Found" error
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Order of preference for 2026
    preferred = ['models/gemini-3-flash-preview', 'models/gemini-3-flash', 'models/gemini-2.5-flash']
    MODEL_NAME = next((m for m in preferred if m in available_models), 'models/gemini-2.0-flash')
    
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.warning(f"Gemini AI setup failed: {e}. Some features may not work.")

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    HEADERS = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
except Exception as e:
    st.warning(f"Supabase setup failed: {e}. Database features may not work.")

# --- 3. APP NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📋 My Dashboard", "📸 Scan Receipt", "👨‍🍳 AI Halal Chef"])

def get_inventory():
    if not HEADERS or not SUPABASE_URL:
        st.error("Database not configured. Please set up Supabase secrets.")
        return []
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*", headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch inventory: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching inventory: {e}")
        return []

inventory = get_inventory()

with tab1:
    st.header("Pantry Status")
    st.write(f"Currently using: `{MODEL_NAME}`")
    if inventory:
        st.subheader("Current Inventory")
        st.table(inventory)
    else:
        st.write("No items in inventory.")
    if st.button("🔄 Refresh Inventory"):
        st.rerun()

with tab2:
    st.header("📸 Smart Receipt Scanner")
    img_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=400)
        
        if st.button("🤖 Sync to Database"):
            if not model:
                st.error("AI model not configured. Please set up Gemini API key or ADC.")
            elif not HEADERS or not SUPABASE_URL:
                st.error("Database not configured. Please set up Supabase secrets.")
            else:
                with st.spinner("Analyzing..."):
                    prompt = """Analyze this receipt. Return ONLY a JSON list of dictionaries.
                Keys: 'name', 'quantity' (integer), 'unit', 'price' (float).
                Example: [{"name": "Chicken", "quantity": 1, "unit": "kg", "price": 5.99}]"""
                    try:
                        # Explicitly use the model found by our finder
                        response = model.generate_content([prompt, img])
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        st.write(f"Raw AI response: {clean_text}")  # Debug: show raw response
                        new_items = json.loads(clean_text)
                        
                        for item in new_items:
                            post_response = requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                          headers=HEADERS, 
                                          json={**item, "expiry_date": str(date.today()), "price": item.get("price", 0)})
                            if post_response.status_code not in [200, 201]:
                                st.error(f"Failed to add {item['name']}: {post_response.status_code} - {post_response.text}")
                            else:
                                st.success(f"Added {item['name']}")
                        st.success(f"Successfully added {len(new_items)} items!")
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse AI response as JSON: {e}. Raw response: {clean_text}")
                    except Exception as e:
                        st.error(f"Error during sync: {e}")

with tab3:
    st.header("👨‍🍳 AI Halal Chef")
    if not model:
        st.error("AI model not configured. Please set up Gemini API key or ADC.")
    else:
        inventory = get_inventory()
        if not inventory:
            st.warning("No inventory available. Please scan some receipts first.")
        else:
            st.subheader("Current Inventory")
            inventory_text = ", ".join([f"{item['name']} ({item['quantity']} {item['unit']})" for item in inventory])
            st.write(f"Available ingredients: {inventory_text}")
            
            budget = st.number_input("Budget for additional ingredients (£)", min_value=0.0, value=10.0, step=1.0)
            
            if st.button("Generate Recipe Ideas"):
                with st.spinner("Cooking up recipe ideas..."):
                    try:
                        chef_prompt = f"""Based on these available ingredients: {inventory_text}

Generate 2-3 halal recipe suggestions that can be made with the current inventory. For each recipe, include:
1. Recipe name
2. Ingredients needed (from inventory)
3. Simple instructions
4. Estimated cost (based on typical prices)

If the budget allows (£{budget}), also suggest 1-2 additional ingredients to buy that would enable a more impressive recipe. Include the additional cost and the enhanced recipe.

Keep recipes halal, healthy, and suitable for a student budget."""
                        
                        recipe_response = model.generate_content(chef_prompt)
                        st.write(recipe_response.text)
                    except Exception as e:
                        st.error(f"Error generating recipes: {e}")