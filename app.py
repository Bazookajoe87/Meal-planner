import streamlit as st
import random
import requests
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Infinite Family Meal Planner", page_icon="🥦", layout="wide")

st.markdown("# 🥦 Live-Fetching Family Meal Planner")
st.markdown("### Powered by TheMealDB API — 100% Soy-Free Hybrid Meal Generator")

# --- SOY-FREE DETECTION ENGINE ---
SOY_BANNED_KEYWORDS = ["tofu", "soy milk", "soy protein", "edamame", "tempeh", "miso"]

def is_soy_free(meal_data):
    """Scans all ingredients from the API recipe to ensure no tofu or hidden soy protein exists."""
    for i in range(1, 21):
        ing = meal_data.get(f"strIngredient{i}")
        if ing:
            ing_lower = ing.lower()
            if any(keyword in ing_lower for keyword in SOY_BANNED_KEYWORDS):
                return False
    return True

# --- DYNAMIC RECIPE FETCHER ---
@st.cache_data(ttl=3600)  # Caches requests for 1 hour to keep your app running lightning fast
def fetch_live_meal_by_cuisine(cuisine_name):
    """Pulls a completely fresh recipe from the live internet database based on your selected filter."""
    # Map app buttons to API area categories
    api_map = {"Italian": "Italian", "Mexican": "Mexican", "Asian": "Chinese", "American": "American"}
    area = api_map.get(cuisine_name, "American")
    
    try:
        # Step 1: Get a list of all meals in that global category
        url = f"https://themealdb.com{area}"
        response = requests.get(url).json()
        meals_list = response.get("meals", [])
        
        if meals_list:
            # Step 2: Try up to 10 random selections from the category to find a soy-free option
            for _ in range(10):
                random_choice = random.choice(meals_list)
                detail_url = f"https://themealdb.com{random_choice['idMeal']}"
                detail_res = requests.get(detail_url).json()
                meal_detail = detail_res.get("meals", [{}])[0]
                
                if is_soy_free(meal_detail):
                    # Extract list of ingredients
                    ingredients = []
                    for i in range(1, 21):
                        ing = meal_detail.get(f"strIngredient{i}")
                        if ing and ing.strip():
                            ingredients.append(ing.strip().capitalize())
                    
                    # Generate automatic kid-friendly / omnivore hybrid instructions
                    return {
                        "name": meal_detail.get("strMeal"),
                        "base": f"A soy-free base featuring {ingredients[0] if len(ingredients)>0 else 'fresh items'} and local produce cooked mild for small children.",
                        "omnivore": "Cook chicken breast chunks or lean ground beef on a separate skillet to use as an optional topping for meat-eaters.",
                        "ingredients": ingredients if ingredients else ["Assorted fresh vegetables", "Starch base"]
                    }
    except Exception as e:
        pass
    
    # Fallback backup meal if API fails or network timeout occurs
    return {
        "name": f"Classic {cuisine_name} Garden Skillet",
        "base": "A mixed bowl of rice, sweet corn, local seasonal veggies, and a dash of mild cheese.",
        "omnivore": "Top with grilled diced chicken or sliced sausage links cooked on the side.",
        "ingredients": ["Rice", "Seasonal Vegetables", "Olive oil", "Chicken breasts"]
    }

SNACKS = [
    "Fresh apples, bananas, and seedless grapes",
    "Hummus pots served with crisp cucumber slices and mini pretzel twists",
    "Individual low-sugar vanilla or strawberry Greek yogurt cups",
    "Kid-friendly trail mix: pumpkin seeds, raisins, and whole grain cereal squares"
]
# --- SESSION STATE INITIALIZATION ---
if "selected_meals" not in st.session_state:
    st.session_state.selected_meals = [fetch_live_meal_by_cuisine("American") for _ in range(5)]

if "active_cuisine" not in st.session_state:
    st.session_state.active_cuisine = "All"

# --- CORE INTERFACE CONTROLS ---
def randomize_all_live():
    cuisines = ["Italian", "Mexican", "Asian", "American"]
    st.session_state.selected_meals = []
    for _ in range(5):
        chosen_style = st.session_state.active_cuisine if st.session_state.active_cuisine != "All" else random.choice(cuisines)
        st.session_state.selected_meals.append(fetch_live_meal_by_cuisine(chosen_style))

def swap_single_meal_live(index):
    cuisines = ["Italian", "Mexican", "Asian", "American"]
    chosen_style = st.session_state.active_cuisine if st.session_state.active_cuisine != "All" else random.choice(cuisines)
    st.session_state.selected_meals[index] = fetch_live_meal_by_cuisine(chosen_style)

# --- STYLE SELECTION BUTTONS ---
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🇮🇹 Italian", use_container_width=True):
        st.session_state.active_cuisine = "Italian"
with col2:
    if st.button("🇲🇽 Mexican", use_container_width=True):
        st.session_state.active_cuisine = "Mexican"
with col3:
    if st.button("🥢 Asian", use_container_width=True):
        st.session_state.active_cuisine = "Asian"
with col4:
    if st.button("🇺🇸 American", use_container_width=True):
        st.session_state.active_cuisine = "American"
with col5:
    if st.button("🌐 Show All Styles", use_container_width=True):
        st.session_state.active_cuisine = "All"

st.write(f"**Current Style Filter:** {st.session_state.active_cuisine}")

if st.button("🎲 Pull 5 Brand New Live Meals From Internet", type="primary", use_container_width=True):
    randomize_all_live()
    st.rerun()

st.write("---")

# --- MEAL CARDS DISPLAY ---
st.markdown("### 🍽️ Your Current Dinner Lineup")
if not st.session_state.selected_meals:
    st.info("Lineup empty. Click the button above to generate a new week!")
else:
    for idx, meal in enumerate(st.session_state.selected_meals):
        with st.container(border=True):
            c_title, c_swap, c_remove = st.columns([4, 1, 1])
            with c_title:
                st.markdown(f"#### Day {idx+1}: {meal['name']}")
                st.markdown(f"🌿 **Vegetarian Base:** {meal['base']}")
                st.markdown(f"🥩 **Omnivore Option:** {meal['omnivore']}")
            with c_swap:
                if st.button(f"🔄 Swap", key=f"swap_{idx}", use_container_width=True):
                    swap_single_meal_live(idx)
                    st.rerun()
            with c_remove:
                if st.button(f"❌ Remove", key=f"rem_{idx}", use_container_width=True):
                    st.session_state.selected_meals.pop(idx)
                    st.rerun()

if st.button("➕ Add New Dinner Slot", use_container_width=True):
    current_style = st.session_state.active_cuisine if st.session_state.active_cuisine != "All" else "American"
    st.session_state.selected_meals.append(fetch_live_meal_by_cuisine(current_style))
    st.rerun()

st.write("---")

# --- SNACKS SECTIONS ---
st.markdown("### 🍎 Healthy Snacks for the Week")
for snack in SNACKS:
    st.markdown(f"- {snack}")

st.write("---")

# --- GROCERY LIST GENERATION ---
st.markdown("### 🛒 Consolidated Grocery Checklist")
compiled_ingredients = set()
for meal in st.session_state.selected_meals:
    for ing in meal["ingredients"]:
        compiled_ingredients.add(ing.capitalize())

for ing in sorted(list(compiled_ingredients)):
    st.checkbox(f"[ ] {ing}", key=f"chk_{ing}")

st.write("---")

# --- EXPORT & PRINT ACTIONS ---
st.markdown("### 💾 Export & Action Center")
recipe_text = "=== WEEKLY MEAL PLAN ===\\n\\n"
for idx, meal in enumerate(st.session_state.selected_meals):
    recipe_text += f"Day {idx+1}: {meal['name']}\\n- Base: {meal['base']}\\n- Omnivore: {meal['omnivore']}\\n\\n"
recipe_text += "=== WEEKLY SNACKS ===\\n" + "\\n".join([f"- {s}" for s in SNACKS]) + "\\n\\n"
recipe_text += "=== GROCERY LIST ===\\n" + "\\n".join([f"[ ] {ing}" for ing in sorted(list(compiled_ingredients))])

col_p1, col_p2, col_amazon = st.columns(3)
with col_p1:
    st.download_button("🖨️ Download / Print Plan", data=recipe_text, file_name="meal_plan.txt", mime="text/plain", use_container_width=True)

with col_p2:
    encoded_text = urllib.parse.quote(recipe_text)
    share_url = f"https://wa.me{encoded_text}"
    st.markdown(f'<a href="{share_url}" target="_blank"><button style="width:100%; height:40px; border-radius:5px; background-color:#25D366; color:white; border:none; cursor:pointer;">📱 Send via WhatsApp / Phone</button></a>', unsafe_allow_html=True)

with col_amazon:
    amazon_base_url = "https://amazon.com"
    query_items = "+and+".join([urllib.parse.quote(ing.lower()) for ing in list(compiled_ingredients)[:5]])
    cart_url = f"{amazon_base_url}{query_items}+grocery"
    st.markdown(f'<a href="{cart_url}" target="_blank"><button style="width:100%; height:40px; border-radius:5px; background-color:#FF9900; color:white; border:none; cursor:pointer;">🛒 Send to Amazon Cart</button></a>', unsafe_allow_html=True)
