import streamlit as st
import requests
from google import genai
from PIL import Image
from datetime import date
import json

# --- 0. HELPER FUNCTIONS ---

def _supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY and HEADERS)


@st.cache_data(ttl=60)
def get_inventory():
    """Fetch inventory from Supabase, fallback to local session storage."""
    if not _supabase_configured():
        st.warning("Supabase not configured. Using local inventory fallback.")
        return st.session_state.get("local_inventory", [])

    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/inventory?select=*&order=name", headers=HEADERS, timeout=12)
        if response.status_code == 200:
            inventory = response.json()
            # Keep a local copy for offline fallback
            st.session_state["local_inventory"] = inventory
            return inventory
        else:
            st.error(f"Failed to fetch inventory from Supabase: {response.status_code}")
            return st.session_state.get("local_inventory", [])
    except Exception as e:
        st.error(f"Error fetching inventory: {e} — using local cache.")
        return st.session_state.get("local_inventory", [])

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
    
    body {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeInUp 1s ease-out;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.4rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInUp 1.2s ease-out;
        font-weight: 400;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .intro-text {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInUp 1.4s ease-out;
        line-height: 1.7;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        padding: 1rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.2rem;
        margin-top: 1rem;
    }

    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #eff6ff 100%);
        border: 1px solid #cbd5e1;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.12);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.18);
    }

    .feature-card h3 {
        margin: 0 0 0.5rem 0;
        color: #1e293b;
        font-size: 1.1rem;
    }

    .feature-card p {
        margin: 0;
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .nav-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid transparent;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .nav-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .nav-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    .nav-card:hover::before {
        left: 100%;
    }
    
    .nav-card.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-4px);
    }
    
    .nav-card.active .nav-icon,
    .nav-card.active .nav-title,
    .nav-card.active .nav-desc {
        color: white !important;
    }
    
    .nav-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .nav-card:hover .nav-icon {
        transform: scale(1.1);
    }
    
    .nav-title {
        font-weight: 700;
        font-size: 1.5rem;
        color: #1e293b;
        margin-bottom: 0.5rem;
        transition: color 0.3s ease;
    }
    
    .nav-desc {
        color: #64748b;
        font-size: 1rem;
        line-height: 1.5;
        transition: color 0.3s ease;
    }
    
    .content-section {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideUp 0.6s ease-out;
    }
    
    .section-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .inventory-list {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .inventory-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        font-size: 0.9rem;
    }
    
    .inventory-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
    }
    
    .item-checkbox {
        margin-right: 1rem;
    }
    
    .item-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        flex: 1;
    }
    
    .item-name {
        font-weight: 600;
        font-size: 1rem;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    
    .item-details {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .item-details {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .item-price {
        font-weight: 600;
        color: #059669;
        font-size: 1rem;
    }
    
    .item-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .bulk-actions {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 1.75rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .delete-btn button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
    }
    
    .delete-btn button:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
    }
    
    .success-msg {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .error-msg {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    .info-msg {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .receipt-preview {
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .receipt-preview:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
    }
    
    .recipe-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    
    .recipe-category {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .recipe-category:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.8);
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    .stFileUploader>div>div>div {
        border-radius: 12px;
        border: 2px dashed #667eea;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader>div>div>div:hover {
        border-color: #764ba2;
        background: rgba(118, 75, 162, 0.1);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1.2rem;
        }
        .intro-text {
            font-size: 1rem;
            padding: 1.5rem;
        }
        .nav-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        .nav-card {
            padding: 1.5rem;
        }
        .content-section {
            padding: 2rem 1.5rem;
            margin: 1rem;
        }
        .section-header {
            font-size: 2rem;
        }
        .inventory-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .item-actions {
            align-self: flex-end;
        }
        .bulk-actions {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SECURE API SETUP & MODEL FINDER ---
ai_configured = False
AI_CLIENT = None
MODEL_NAME = None
SUPABASE_URL = None
SUPABASE_KEY = None
HEADERS = None

MODEL_CANDIDATES = [
    'gemini-2.5-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-1.5'
]

def find_available_model():
    if AI_CLIENT is None:
        return MODEL_CANDIDATES[0]

    try:
        # new SDK client.models.list() returns iterable of Model
        available_names = []
        for m in AI_CLIENT.models.list():
            if m.name:
                available_names.append(m.name)
                # handle "models/gemini-1.5-flash" naming
                available_names.append(m.name.split("/")[-1])

        for candidate in MODEL_CANDIDATES:
            if candidate in available_names:
                return candidate
        if available_names:
            return available_names[0]
    except Exception:
        pass

    return MODEL_CANDIDATES[0]


def parse_ai_text(response):
    if response is None:
        return ''
    if hasattr(response, 'text'):
        return response.text
    return str(response)


def generate_ai_text(prompt, image=None):
    if not ai_configured or AI_CLIENT is None or not MODEL_NAME:
        raise RuntimeError('AI model is not configured')

    contents = [prompt]
    if image is not None:
        contents.append(image)

    resp = AI_CLIENT.models.generate_content(
        model=MODEL_NAME, 
        contents=contents
    )
    
    return parse_ai_text(resp)


try:
    api_key = st.secrets.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not set')

    # Initialize new genai client
    AI_CLIENT = genai.Client(api_key=api_key)

    MODEL_NAME = find_available_model()
    ai_configured = True
except Exception as e:
    ai_configured = False
    st.warning(f'Gemini AI setup failed: {e}. Some features may not work.')

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
<div class="intro-text">
    <h2>Transform your grocery shopping experience</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <h3>🧠 AI Receipt Scanner</h3>
            <p>Upload receipts and watch advanced AI extract items, prices, and quantities with 95%+ accuracy, plus halal verification guidance.</p>
        </div>
        <div class="feature-card">
            <h3>📊 Smart Dashboard</h3>
            <p>Real-time inventory tracking, bulk operations, manual entries, and expiry alerts to reduce waste and save money.</p>
        </div>
        <div class="feature-card">
            <h3>👨‍🍳 Halal AI Chef</h3>
            <p>Personalized recipe recommendations based on pantry contents, with budget-aware ingredient suggestions for every meal.</p>
        </div>
        <div class="feature-card">
            <h3>🎯 Ideal for You</h3>
            <p>Great for students, busy professionals, and halal-conscious families who want time savings, better budgeting, and compliance peace of mind.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Navigation Cards
st.markdown('<div class="nav-grid">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True, 
                 type="secondary" if st.session_state.current_page != "dashboard" else "primary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

with col2:
    if st.button("📸 Scan Receipt", key="nav_scanner", use_container_width=True,
                 type="secondary" if st.session_state.current_page != "scanner" else "primary"):
        st.session_state.current_page = "scanner"
        st.rerun()

with col3:
    if st.button("👨‍🍳 AI Chef", key="nav_chef", use_container_width=True,
                 type="secondary" if st.session_state.current_page != "chef" else "primary"):
        st.session_state.current_page = "chef"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Content Sections
if st.session_state.current_page == "dashboard":
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📊 Pantry Dashboard</h2>', unsafe_allow_html=True)
    
    inventory = get_inventory()
    
    if inventory:
        # Bulk actions bar
        selected_items = []
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
        
        # Display items in a compact list
        st.markdown('<div class="inventory-list">', unsafe_allow_html=True)
        for item in inventory:
            selected = st.checkbox(
                "Select item", 
                key=f"select_{item.get('id', item.get('name', 'unknown'))}",
                label_visibility="collapsed"
            )
            if selected:
                selected_items.append(item)
            
            st.markdown(f"""
            <div class="inventory-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="item-checkbox"></div>
                    <div class="item-info">
                        <div class="item-name">{item['name']}</div>
                        <div class="item-details">{item['quantity']} {item['unit']} • Expires: {item.get('expiry_date', 'N/A')}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="item-price">£{item.get('price', 0):.2f}</div>
                    <div class="item-actions">
                        <button class="delete-btn" onclick="deleteItem('{item.get('id', item['name'])}')">🗑️</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual delete button
            if st.button("🗑️", key=f"del_{item.get('id', item['name'])}", help="Delete this item"):
                if 'id' in item:
                    delete_response = requests.delete(f"{SUPABASE_URL}/rest/v1/inventory?id=eq.{item['id']}", headers=HEADERS)
                    if delete_response.status_code == 204:
                        st.success(f"Removed {item['name']}")
                        st.rerun()
                    else:
                        st.error("Failed to remove item")
        st.markdown('</div>', unsafe_allow_html=True)
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
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "scanner":
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📸 Smart Receipt Scanner</h2>', unsafe_allow_html=True)
    st.markdown("Upload a receipt to automatically add items to your pantry with AI-powered extraction")
    
    img_file = st.file_uploader("Choose receipt image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=300, caption="Receipt Preview", use_column_width=False, clamp=True, output_format="auto")
        
        if st.button("🤖 Analyze & Sync", type="primary"):
            if not ai_configured:
                st.error("AI model not configured.")
            elif not HEADERS or not SUPABASE_URL:
                st.error("Database not configured.")
            else:
                with st.spinner("Analyzing receipt with AI..."):
                    prompt = """Analyze this receipt. Return ONLY a JSON list of dictionaries.
Keys: 'name', 'quantity' (integer), 'unit', 'price' (float).
Example: [{"name": "Chicken", "quantity": 1, "unit": "kg", "price": 5.99}]"""
                    
                    try:
                        response_text = generate_ai_text(prompt, image=img)
                        clean_text = response_text.replace("```json", "").replace("```", "").strip()
                        new_items = json.loads(clean_text)
                        
                        success_count = 0
                        for item in new_items:
                            post_response = requests.post(f"{SUPABASE_URL}/rest/v1/inventory", 
                                          headers=HEADERS, 
                                          json={**item, "expiry_date": str(date.today()), "price": item.get("price", 0)})
                            if post_response.status_code in [200, 201]:
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"✅ Successfully added {success_count} items from receipt!")
                            st.balloons()
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("❌ Failed to parse receipt. Please try a clearer image.")
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "chef":
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">👨‍🍳 AI Halal Chef</h2>', unsafe_allow_html=True)
    st.markdown("Get personalized recipe suggestions based on your pantry with budget-conscious additions")
    
    if not ai_configured or not MODEL_NAME:
        st.error("AI model not configured. Please set GEMINI_API_KEY and ensure a supported model is available.")
    else:
        inventory = get_inventory()
        if not inventory:
            st.info("📦 Add some ingredients to your pantry first to get recipe suggestions!")
        else:
            st.info(f"🍳 Using {len(inventory)} items from your pantry for recipe suggestions")
            
            budget = st.slider("Budget for additional ingredients (£)", 0.0, 20.0, 5.0, 0.5)
            
            if st.button("🍳 Generate Recipe Ideas", type="primary"):
                with st.spinner("Creating personalized recipe suggestions..."):
                    try:
                        inventory_text = ", ".join([f"{item['name']} ({item['quantity']} {item['unit']})" for item in inventory])
                        
                        chef_prompt = f"""Based on these pantry ingredients: {inventory_text}

Create 3 categorized recipe suggestions for a halal-conscious person:
1. ⚡ QUICK & EASY (15-30 min prep/cook, minimal effort, perfect for busy days)
2. 🍽️ CLASSIC COMFORT (30-45 min, balanced effort, family favorites)  
3. ✨ GOURMET SPECIAL (45+ min, high effort, impressive meals for special occasions)

For each category, provide:
- Recipe name and brief description
- Key ingredients used from pantry
- 2-3 additional affordable items needed (total under £{budget})
- Step-by-step cooking instructions
- Total estimated cost breakdown
- Why it fits the category and dietary notes

Focus on practical, delicious halal recipes with clear instructions."""
                        
                        recipes = generate_ai_text(chef_prompt)
                        
                        st.markdown('<div class="recipe-section">', unsafe_allow_html=True)
                        st.markdown("### 🍳 Your Personalized Recipe Suggestions")
                        
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
    
    st.markdown('</div>', unsafe_allow_html=True)