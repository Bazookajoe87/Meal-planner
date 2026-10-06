import streamlit as st
import random
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Family Meal Planner & Grocery Generator", page_icon="🥦", layout="wide")

st.markdown("# 🥦 Kid-Friendly, Soy-Free Family Meal Planner")
st.markdown("### Tailored for a family of 3 (1 Strict Vegetarian, 2 Omnivores)")

# --- RECIPE DATABASE ---
# All bases are 100% vegetarian, dairy is allowed, NO tofu/soy protein. Soy sauce allowed for Asian style.
RECIPES = {
    "Italian": [
        {
            "name": "Creamy Tomato & Spinach Pasta",
            "base": "Short ridged pasta (penne/rotini) tossed in a mild, velvety tomato-parmesan cream sauce with tender baby spinach.",
            "omnivore": "Top individual portions with sliced grilled Italian sausage or chicken breasts cooked on the side.",
            "ingredients": ["penne pasta", "passata sauce", "heavy cream", "parmesan cheese", "baby spinach", "Italian sausage links", "chicken breasts"]
        },
        {
            "name": "Sheet-Pan Gnocchi & Roasted Veggies",
            "base": "Pillowy potato gnocchi roasted on a baking sheet with cherry tomatoes, zucchini slices, garlic, and olive oil until plump.",
            "omnivore": "Add sliced pepperoni or diced pancetta to a separate corner of the baking sheet to toss into omnivore bowls.",
            "ingredients": ["potato gnocchi", "cherry tomatoes", "zucchini", "garlic", "olive oil", "pepperoni"]
        },
        {
            "name": "Build-Your-Own French Bread Pizzas",
            "base": "Soft French bread halves topped with smooth pizza sauce and shredded mozzarella cheese.",
            "omnivore": "Load omnivore halves with cooked Italian sausage or mini pepperoni before baking.",
            "ingredients": ["French bread", "pizza sauce", "shredded mozzarella cheese", "Italian sausage links", "mini pepperoni"]
        },
        {
            "name": "Creamy Parmesan Orzo with Peas",
            "base": "Tiny, rice-shaped orzo pasta cooked in vegetable broth and swirled with butter, sweet green peas, and plenty of mild Parmesan cheese.",
            "omnivore": "Top individual bowls with sliced, pan-seared chicken cutlets.",
            "ingredients": ["orzo pasta", "vegetable broth", "butter", "frozen peas", "parmesan cheese", "chicken breasts"]
        }
    ],
    "Mexican": [
        {
            "name": "Deconstructed Burrito Bowls",
            "base": "Fluffy cilantro-lime rice, sweet corn, black beans, shredded cheddar cheese, sour cream, and mild salsa.",
            "omnivore": "Add lean seasoned ground beef or shredded chicken served from a separate bowl.",
            "ingredients": ["long-grain white rice", "cilantro", "lime", "canned corn", "black beans", "shredded cheddar cheese", "sour cream", "mild salsa", "ground beef", "rotisserie chicken"]
        },
        {
            "name": "Mild Loaded Cheese Quesadillas",
            "base": "Crispy flour tortillas filled with melted Monterey Jack cheese, black beans, and fine-diced mild bell peppers.",
            "omnivore": "Add seasoned shredded chicken or ground beef to the omnivore quesadillas.",
            "ingredients": ["flour tortillas", "shredded Monterey Jack cheese", "black beans", "bell peppers", "rotisserie chicken", "ground beef"]
        }
    ],
    "Asian": [
        {
            "name": "Sweet Teriyaki Rice Bowls",
            "base": "A sweet kid-friendly teriyaki glaze (made with real soy sauce, brown sugar, and ginger) over a base of fluffy white rice, broccoli florets, and carrots.",
            "omnivore": "Top with grilled chicken breast tossed in the teriyaki glaze cooked separately.",
            "ingredients": ["soy sauce", "brown sugar", "ginger", "white rice", "broccoli", "carrots", "chicken breasts"]
        },
        {
            "name": "Twirly Lo Mein Noodle Night",
            "base": "Soft egg noodles tossed in a mild, savory soy-sesame sauce with crisp shredded cabbage, carrots, and sweet snap peas.",
            "omnivore": "Add sliced stir-fry beef cooked separately on the side for the meat-eaters.",
            "ingredients": ["egg noodles", "soy sauce", "sesame oil", "cabbage", "carrots", "sugar snap peas", "stir-fry beef"]
        }
    ],
    "American": [
        {
            "name": "Rainbow Veggie & Chicken Kabobs",
            "base": "Skewers of colorful bell peppers, red onion, zucchini chunks, and whole button mushrooms brushed with a mild garlic-herb olive oil.",
            "omnivore": "Separate skewers of diced chicken breast grilled on the side to slide onto the omnivore plates.",
            "ingredients": ["bell peppers", "red onion", "zucchini", "button mushrooms", "garlic", "olive oil", "chicken breasts"]
        },
        {
            "name": "Build-Your-Own Black Bean Burgers",
            "base": "Hearty homemade soy-free black bean patties (mashed black beans, breadcrumbs, mild seasonings) on soft brioche buns with lettuce and tomato.",
            "omnivore": "Lean ground beef patties grilled separately for the meat-eaters.",
            "ingredients": ["black beans", "breadcrumbs", "brioche buns", "lettuce", "vine tomatoes", "ground beef"]
        },
        {
            "name": "Cozy Vegetable Pot Pie with Biscuits",
            "base": "Carrots, peas, and potatoes simmered in a rich vegetable gravy, baked under golden flaky drop biscuits.",
            "omnivore": "Stir pre-cooked shredded rotisserie chicken into the omnivore individual baking dishes before topping with dough.",
            "ingredients": ["carrots", "frozen peas", "potatoes", "vegetable broth", "butter", "flour", "refrigerated biscuit dough", "rotisserie chicken"]
        }
    ]
}

SNACKS = [
    "Fresh apples, bananas, and seedless grapes",
    "Hummus pots served with crisp cucumber slices and mini pretzel twists",
    "Individual low-sugar vanilla or strawberry Greek yogurt cups",
    "Kid-friendly trail mix: pumpkin seeds, raisins, and whole grain cereal squares"
]
# --- SESSION STATE INITIALIZATION ---
if "selected_meals" not in st.session_state:
    all_flat = [meal for cat in RECIPES.values() for meal in cat]
    st.session_state.selected_meals = random.sample(all_flat, 5)

if "active_cuisine" not in st.session_state:
    st.session_state.active_cuisine = "All"

# --- HELPER FUNCTIONS ---
def get_filtered_meals():
    if st.session_state.active_cuisine == "All":
        return [meal for cat in RECIPES.values() for meal in cat]
    return RECIPES.get(st.session_state.active_cuisine, [])

def randomize_all():
    pool = get_filtered_meals()
    if len(pool) >= 5:
        st.session_state.selected_meals = random.sample(pool, 5)
    else:
        st.session_state.selected_meals = random.choices(pool, k=5)

def swap_meal(index):
    pool = get_filtered_meals()
    current_names = [m["name"] for m in st.session_state.selected_meals]
    fresh_pool = [m for m in pool if m["name"] not in current_names]
    if not fresh_pool:
        fresh_pool = pool
    st.session_state.selected_meals[index] = random.choice(fresh_pool)

def remove_meal(index):
    st.session_state.selected_meals.pop(index)

def add_meal_slot():
    pool = get_filtered_meals()
    st.session_state.selected_meals.append(random.choice(pool))

# --- INTERFACE CUISINE BUTTONS ---
# FIXED: Added the number 5 inside st.columns() to fix the crash
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

if st.button("🎲 Randomize All 5 Dinners", type="primary", use_container_width=True):
    randomize_all()

st.write("---")

# --- MEAL CARDS GRID ---
st.markdown("### 🍽️ Your Current Dinner Lineup")
if not st.session_state.selected_meals:
    st.info("No meals in your lineup. Click below to add a slot!")
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
                    swap_meal(idx)
                    st.rerun()
            with c_remove:
                if st.button(f"❌ Remove", key=f"rem_{idx}", use_container_width=True):
                    remove_meal(idx)
                    st.rerun()

if st.button("➕ Add New Dinner Slot", use_container_width=True):
    add_meal_slot()
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
