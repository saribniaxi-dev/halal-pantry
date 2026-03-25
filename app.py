import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
from datetime import date
import json

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="Halal Pantry AI", 
    page_icon="🌙", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E3440;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4C566A;
        margin-bottom: 1rem;
    }
    .card {
        background: #F8F9FA;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #5E81AC;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-msg {
        background: #A3BE8C;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .error-msg {
        background: #BF616A;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .recipe-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #E5E9F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .recipe-title {
        font-weight: 600;
        color: #2E3440;
        margin-bottom: 0.5rem;
    }
    .recipe-meta {
        color: #4C566A;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background: #5E81AC;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background: #4C6B8A;
    }
</style>
""", unsafe_allow_html=True)

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
st.markdown('<h1 class="main-header">🌙 Halal Pantry AI</h1>', unsafe_allow_html=True)
st.markdown("Your intelligent halal food management assistant")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📸 Scan Receipt", "👨‍🍳 AI Chef"])

def get_inventory():
    if not HEADERS or not SUPABASE_URL:
        st.error("Database not configured.")
        return []
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*", headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch inventory")
            return []
    except Exception as e:
        st.error(f"Error fetching inventory: {e}")
        return []

inventory = get_inventory()

with tab1:
    st.markdown('<h2 class="tab-header">📊 Pantry Dashboard</h2>', unsafe_allow_html=True)
    
    inventory = get_inventory()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Inventory")
        if inventory:
            # Group by category (we'll assume a category field or add one)
            for item in inventory:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    with col_a:
                        st.write(f"**{item['name']}**")
                    with col_b:
                        st.write(f"{item['quantity']} {item['unit']}")
                    with col_c:
                        if st.button("🗑️", key=f"del_{item['id'] if 'id' in item else item['name']}"):
                            # Delete item
                            if 'id' in item:
                                delete_response = requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
                                if delete_response.status_code == 204:
                                    st.success(f"Removed {item['name']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove item")
        else:
            st.info("No items in inventory. Add some manually or scan a receipt!")
    
    with col2:
        st.subheader("Add Item Manually")
        with st.form("add_item"):
            name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
            unit_options = ["pieces", "kg", "lbs", "liters", "cups", "cans", "bottles"]
            unit = st.selectbox("Unit", unit_options)
            price = st.number_input("Price (£)", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("Add Item")
            if submitted and name:
                new_item = {
                    "name": name,
                    "quantity": quantity,
                    "unit": unit,
                    "price": price,
                    "expiry_date": str(date.today())
                }
                add_response = requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                           headers=HEADERS, 
                                           json=new_item)
                if add_response.status_code in [200, 201]:
                    st.success(f"Added {name}!")
                    st.rerun()
                else:
                    st.error("Failed to add item")

with tab2:
    st.markdown('<h2 class="tab-header">📸 Smart Receipt Scanner</h2>', unsafe_allow_html=True)
    st.markdown("Upload a receipt to automatically add items to your pantry")
    img_file = st.file_uploader("Choose receipt image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300, caption="Receipt Preview")
        
        if st.button("🤖 Analyze & Sync", type="primary"):
            if not model:
                st.error("AI model not configured. Please set up Gemini API key or ADC.")
            elif not HEADERS or not SUPABASE_URL:
                st.error("Database not configured. Please set up Supabase secrets.")
            else:
                with st.spinner("Analyzing receipt..."):
                    prompt = """Analyze this receipt. Return ONLY a JSON list of dictionaries.
                Keys: 'name', 'quantity' (integer), 'unit', 'price' (float).
                Example: [{"name": "Chicken", "quantity": 1, "unit": "kg", "price": 5.99}]"""
                    try:
                        # Explicitly use the model found by our finder
                        response = model.generate_content([prompt, img])
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        new_items = json.loads(clean_text)
                        
                        success_count = 0
                        for item in new_items:
                            post_response = requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                          headers=HEADERS, 
                                          json={**item, "expiry_date": str(date.today()), "price": item.get("price", 0)})
                            if post_response.status_code in [200, 201]:
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"✅ Successfully added {success_count} items!")
                            st.balloons()
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Failed to parse receipt. Please try a clearer image.")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

with tab3:
    st.markdown('<h2 class="tab-header">👨‍🍳 AI Halal Chef</h2>', unsafe_allow_html=True)
    st.markdown("Get personalized recipe suggestions based on your pantry")
    if not model:
        st.error("AI model not configured. Please set up Gemini API key or ADC.")
    else:
        inventory = get_inventory()
        if not inventory:
            st.info("Add some ingredients to your pantry first!")
        else:
            # Don't show the raw list, just show count
            st.info(f"📦 Using {len(inventory)} items from your pantry")
            
            budget = st.slider("Budget for additional ingredients (£)", 0.0, 20.0, 5.0, 0.5)
            
            if st.button("🍳 Generate Recipe Ideas", type="primary"):
                with st.spinner("Creating recipe suggestions..."):
                    try:
                        inventory_text = ", ".join([f"{item['name']} ({item['quantity']} {item['unit']})" for item in inventory])
                        
                        chef_prompt = f"""Based on these pantry ingredients: {inventory_text}

Create 3 categorized recipe suggestions:
1. ⚡ QUICK & EASY (15-30 min, minimal effort)
2. 🍽️ CLASSIC COMFORT (30-45 min, balanced effort)  
3. ✨ GOURMET SPECIAL (45+ min, high effort/chic)

For each category, provide:
- Recipe name
- Key ingredients used from pantry
- 2-3 additional affordable items needed (under £{budget} total)
- Brief cooking method
- Total estimated cost
- Why it fits the category

Keep all recipes halal and culturally appropriate. Focus on practical, delicious meals."""
                        
                        recipe_response = model.generate_content(chef_prompt)
                        recipes = recipe_response.text
                        
                        # Parse and display in cards
                        st.markdown("### 🍳 Your Recipe Suggestions")
                        
                        # Split by categories (this is a simple approach)
                        categories = recipes.split("⚡ QUICK & EASY")[1:] if "⚡ QUICK & EASY" in recipes else [recipes]
                        
                        for i, category in enumerate(categories[:3]):
                            category_names = ["⚡ Quick & Easy", "🍽️ Classic Comfort", "✨ Gourmet Special"]
                            with st.container():
                                st.markdown(f"#### {category_names[i] if i < len(category_names) else f'Option {i+1}'}")
                                st.markdown(category.strip())
                                st.markdown("---")
                        
                    except Exception as e:
                        st.error(f"Recipe generation failed: {e}")