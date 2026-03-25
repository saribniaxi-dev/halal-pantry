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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeInUp 1s ease-out;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInUp 1.2s ease-out;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .tab-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .inventory-item {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .inventory-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .item-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .item-name {
        font-weight: 600;
        color: #1e293b;
    }
    
    .item-details {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .item-price {
        font-weight: 500;
        color: #059669;
    }
    
    .item-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .bulk-actions {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .delete-btn button {
        background: #dc2626 !important;
    }
    
    .delete-btn button:hover {
        background: #b91c1c !important;
    }
    
    .success-msg {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .error-msg {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .receipt-preview {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .receipt-preview:hover {
        transform: scale(1.02);
    }
    
    .recipe-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .recipe-category {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .recipe-category:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .feature-grid {
            grid-template-columns: 1fr;
        }
        .tab-header {
            font-size: 1.5rem;
        }
        .inventory-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .item-actions {
            align-self: flex-end;
        }
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
st.markdown('<p class="subtitle">Your intelligent halal food management assistant powered by AI</p>', unsafe_allow_html=True)

# Feature Overview
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Smart Dashboard</div>
        <div class="feature-desc">Real-time inventory tracking with manual add/remove, bulk operations, and visual item management.</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📸</div>
        <div class="feature-title">AI Receipt Scanner</div>
        <div class="feature-desc">Upload receipts for automatic item extraction with prices, powered by Gemini AI vision.</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">👨‍🍳</div>
        <div class="feature-title">Halal AI Chef</div>
        <div class="feature-desc">Get personalized recipes from your pantry with budget suggestions and categorized meal ideas.</div>
    </div>
</div>
""", unsafe_allow_html=True)

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
    
    if inventory:
        # Bulk actions bar
        selected_items = []
        with st.container():
            st.markdown('<div class="bulk-actions">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                select_all = st.checkbox("Select All", key="select_all")
            with col2:
                st.write(f"📦 {len(inventory)} items in pantry")
            with col3:
                if selected_items and st.button("🗑️ Delete Selected", type="secondary"):
                    # Bulk delete selected items
                    deleted_count = 0
                    for item in selected_items:
                        if 'id' in item:
                            delete_response = requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
                            if delete_response.status_code == 204:
                                deleted_count += 1
                    if deleted_count > 0:
                        st.success(f"Deleted {deleted_count} items!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display items with selection
        for item in inventory:
            with st.container():
                selected = st.checkbox("", key=f"select_{item.get('id', item['name'])}", label_visibility="collapsed")
                if selected:
                    selected_items.append(item)
                
                st.markdown(f"""
                <div class="inventory-item">
                    <div class="item-info">
                        <div class="item-name">{item['name']}</div>
                        <div class="item-details">{item['quantity']} {item['unit']}</div>
                        <div class="item-price">£{item.get('price', 0):.2f}</div>
                    </div>
                    <div class="item-actions">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Individual delete button
                col_a, col_b = st.columns([10, 1])
                with col_b:
                    if st.button("🗑️", key=f"del_{item.get('id', item['name'])}", help="Delete this item"):
                        if 'id' in item:
                            delete_response = requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
                            if delete_response.status_code == 204:
                                st.success(f"Removed {item['name']}")
                                st.rerun()
                            else:
                                st.error("Failed to remove item")
    else:
        st.info("📦 No items in inventory. Add some manually or scan a receipt!")
    
    # Add item form
    with st.expander("➕ Add New Item", expanded=False):
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
            with col2:
                unit_options = ["pieces", "kg", "lbs", "liters", "cups", "cans", "bottles", "packs"]
                unit = st.selectbox("Unit", unit_options)
                price = st.number_input("Price (£)", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("Add Item", type="primary")
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
                    st.success(f"✅ Added {name}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to add item")

with tab2:
    st.markdown('<h2 class="tab-header">📸 Smart Receipt Scanner</h2>', unsafe_allow_html=True)
    st.markdown("Upload a receipt to automatically add items to your pantry")
    img_file = st.file_uploader("Choose receipt image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300, caption="Receipt Preview", use_column_width=False, clamp=True, output_format="auto")
        
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
                        
                        # Display recipes in styled sections
                        st.markdown('<div class="recipe-section">', unsafe_allow_html=True)
                        st.markdown("### 🍳 Your Recipe Suggestions")
                        
                        # Split by categories
                        categories = recipes.split("⚡ QUICK & EASY")[1:] if "⚡ QUICK & EASY" in recipes else [recipes]
                        
                        for i, category in enumerate(categories[:3]):
                            category_names = ["⚡ Quick & Easy", "🍽️ Classic Comfort", "✨ Gourmet Special"]
                            st.markdown(f"""
                            <div class="recipe-category">
                                <h4>{category_names[i] if i < len(category_names) else f'Option {i+1}'}</h4>
                            """, unsafe_allow_html=True)
                            st.markdown(category.strip())
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Recipe generation failed: {e}")