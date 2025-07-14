import openai
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import google.generativeai as genai

# import google.generativeai as genai # Removed as per requirement

st.set_page_config(page_title="AI Food Waste Reduction", layout="wide")

IMAGE_URL = 'https://cdn.photoroom.com/v2/image-cache?path=gs://background-7ef44.appspot.com/backgrounds_v3/food/46_food.jpg'
custom_css = f"""
<style>
.stApp {{
    background-image: url("{IMAGE_URL}");
    background-size: cover; /* This makes the image cover the entire background */
    background-position: center; /* Centers the image */
    background-repeat: no-repeat; /* Prevents the image from tiling */
    background-attachment: fixed; /* Keeps the background fixed when scrolling */
}}
</style>"""
st.markdown(custom_css, unsafe_allow_html=True)
genai.configure(api_key="AIzaSyAbYwAOzAJzALzpcsoSQTn8bS6CdUJ80qA")
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
# Modified GenerateResponse to be a placeholder
def GenerateResponse(input_text=None, image=None):
    if not input_text and not image:
        return "Please enter a message or upload an image"
    
    # Simple placeholder response for recipe generation
    parts = []
    if input_text:
        parts.append(input_text.lower())
    if image:
        parts.append(image)
    response = model.generate_content(parts)
    return response.text


def leftover_transformation_tab():
    st.title("🧠 Leftover Transformation (AI-Powered)")
    st.write("Enter your leftover ingredients and let AI suggest creative recipes!")

    ingredients = st.text_input("Enter your leftover ingredients (comma-separated):")

    if st.button("Generate Recipes"):
        if not ingredients:
            st.warning("Please enter some ingredients.")
            return

        prompt = (
            f"I have the following leftover ingredients: {ingredients}. "
            f"Suggest 3 creative, simple recipes I can make with them. "
            f"Use easy-to-understand language, and list the ingredients and steps for each recipe."
        )

        try:
            with st.spinner("Thinking..."):
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                st.markdown("### 📝 AI Recipe Suggestions:")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Error: {e}")

# Placeholder for Leftover Transformation
def generate_leftover_idea(ingredients):
    if not ingredients:
        return "Please tell me what leftovers you have!"
    
    ideas = {
        "chicken": "Turn your leftover chicken into chicken salad sandwiches, a quick chicken stir-fry, or chicken and veggie quesadillas!",
        "rice": "Make fried rice, rice pudding, or add it to a soup for extra body.",
        "vegetables": "Chop them up for an omelette, blend into a soup, or roast them with some herbs.",
        "bread": "Make croutons, breadcrumbs, or a savory bread pudding.",
        "pasta": "Reheat with new sauce, make a pasta salad, or bake into a frittata.",
        "potatoes": "Mash them into potato cakes, add to a hash, or make loaded baked potatoes.",
        "fruit": "Blend into a smoothie, bake into a crumble, or make fruit skewers.",
        "soup": "Add some pasta or rice to make it heartier, or blend for a creamy texture.",
        # Add more ideas here
    }
    
    matched_ideas = []
    for ingredient in ingredients.lower().split(','):
        ingredient = ingredient.strip()
        found_match = False
        for key, value in ideas.items():
            if key in ingredient:
                matched_ideas.append(f"- For your '{ingredient}': {value}")
                found_match = True
                break
        if not found_match:
            matched_ideas.append(f"- For your '{ingredient}': Try searching for recipes online that include this ingredient, or combine it with other leftovers!")
            
    if matched_ideas:
        return "Here are some ideas for your leftovers:\n\n" + "\n".join(matched_ideas)
    else:
        return f"I need more specific ingredients to give you transformation ideas for '{ingredients}'. Try listing them out!"

# Initializing Session State Variables
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = []
if 'waste_log' not in st.session_state:
    st.session_state.waste_log = []
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'badges' not in st.session_state:
    st.session_state.badges = set()
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Guest"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False
if 'manual_shopping_list' not in st.session_state:
    st.session_state.manual_shopping_list = []
if 'community_posts' not in st.session_state:
    st.session_state.community_posts = []
if 'custom_reminders' not in st.session_state: # New: Custom Reminders
    st.session_state.custom_reminders = []
if 'pantry_challenge_active' not in st.session_state: # New: Pantry Challenge
    st.session_state.pantry_challenge_active = False
if 'pantry_challenge_start_date' not in st.session_state:
    st.session_state.pantry_challenge_start_date = None
if 'pantry_challenge_end_date' not in st.session_state: # New: Pantry Challenge End Date
    st.session_state.pantry_challenge_end_date = None
if 'sustainability_tip_index' not in st.session_state:
    st.session_state.sustainability_tip_index = 0

donation_centers = [
    {"name": "Local Food Bank A", "address": "123 Charity St", "distance_km": 1.2},
    {"name": "Community Soup Kitchen", "address": "456 Helping Rd", "distance_km": 2.5},
    {"name": "Neighborhood Shelter", "address": "789 Care Ave", "distance_km": 3.1},
]

# Sustainability Tips (New Feature)
sustainability_tips = [
    "Plan your meals ahead to avoid impulse buys and reduce waste.",
    "Store food properly to extend its shelf life. Check storage guides!",
    "Compost your food scraps if possible. It enriches the soil!",
    "Use up leftovers creativey. Don't let them go to waste!",
    "Understand 'best by' vs. 'use by' dates. Many foods are safe past 'best by'.",
    "Donate edible excess food to local food banks or shelters.",
    "Shop smart: Make a list and stick to it to avoid overbuying.",
    "Freeze food before it spoils if you can't eat it in time.",
    "Repurpose food scraps, like making vegetable broth from peels.",
    "Share excess produce with neighbors, friends, or a community garden."
]

def add_inventory_item(name, qty, expiry):
    new_id = len(st.session_state.inventory) + 1
    st.session_state.inventory.append({
        "id": new_id,
        "name": name.title(),
        "qty": qty,
        "expiry": expiry.strftime("%Y-%m-%d")
    })
    st.session_state.points += 5
    st.session_state.notifications.append(f"Added {qty} x {name.title()} to inventory (+5 points)")

def update_inventory_qty(item_id, new_qty):
    for item in st.session_state.inventory:
        if item["id"] == item_id:
            item["qty"] = new_qty
            st.session_state.notifications.append(f"Updated {item['name']} quantity to {new_qty}")
            break

def remove_inventory_item(item_id):
    st.session_state.inventory = [item for item in st.session_state.inventory if item["id"] != item_id]
    st.session_state.notifications.append(f"Removed item with ID {item_id} from inventory")

def log_consumption(name, qty):
    today = datetime.today().date()
    st.session_state.consumption_log.append({"name": name.title(), "qty": qty, "date": today})
    st.session_state.points += 3
    st.session_state.notifications.append(f"Logged consumption of {qty} x {name.title()} (+3 points)")

def log_waste(name, qty, reason):
    today = datetime.today().date()
    st.session_state.waste_log.append({"name": name.title(), "qty": qty, "reason": reason, "date": today})
    st.session_state.points -= 10 # Decreased points for waste
    st.session_state.notifications.append(f"Logged waste of {qty} x {name.title()} due to {reason} (-10 points)")

def get_inventory_df():
    if not st.session_state.inventory:
        return pd.DataFrame(columns=["ID", "Name", "Quantity", "Expiry Date"])
    return pd.DataFrame(st.session_state.inventory).rename(columns={"id":"ID", "name":"Name", "qty":"Quantity", "expiry":"Expiry Date"})

def get_consumption_df():
    if not st.session_state.consumption_log:
        return pd.DataFrame(columns=["Name", "Quantity", "Date"])
    return pd.DataFrame(st.session_state.consumption_log).rename(columns={"name":"Name","qty":"Quantity","date":"Date"})

def get_waste_df():
    if not st.session_state.waste_log:
        return pd.DataFrame(columns=["Name", "Quantity", "Reason", "Date"])
    return pd.DataFrame(st.session_state.waste_log).rename(columns={"qty":"Quantity","reason":"Reason","date":"Date"})

def forecast_consumption(name):
    df = get_consumption_df()
    today = datetime.today().date()
    window_start = today - timedelta(days=14)
    df_recent = df[(df["Name"] == name.title()) & (df["Date"] >= window_start)]
    if df_recent.empty:
        return 0
    return round(df_recent["Quantity"].mean(), 2)

def generate_menu(inv_df):
    if inv_df.empty:
        return pd.DataFrame(columns=["ID", "Name", "Quantity", "Expiry Date"]) # Return empty DataFrame if input is empty
    inv_df["Expiry Date"] = pd.to_datetime(inv_df["Expiry Date"])
    today = datetime.today().date()
    soon_expiry_date = today + timedelta(days=7)
    soon_expiring = inv_df[
        (inv_df["Expiry Date"].dt.date <= soon_expiry_date) &
        (inv_df["Quantity"] > 0)
    ].copy()
    soon_expiring = soon_expiring.sort_values(by="Expiry Date")
    return soon_expiring

def generate_auto_shopping_list():
    inv_df = get_inventory_df()
    inv_map = {}
    for _, row in inv_df.iterrows():
        inv_map[row["Name"]] = row["Quantity"]
    forecast_items = {}
    for item in inv_map.keys():
        forecast_items[item] = forecast_consumption(item)
    shopping_list = {}
    for item, forecast_qty in forecast_items.items():
        current_qty = inv_map.get(item, 0)
        diff = forecast_qty - current_qty
        if diff > 0:
            shopping_list[item] = round(diff, 2)
    return shopping_list

def add_to_manual_shopping_list(name, qty):
    found = False
    for item in st.session_state.manual_shopping_list:
        if item["name"].lower() == name.lower():
            item["qty"] += qty
            st.session_state.notifications.append(f"Updated {name.title()} in manual shopping list to {item['qty']} units.")
            found = True
            break
    if not found:
        st.session_state.manual_shopping_list.append({"name": name.title(), "qty": qty})
    st.session_state.notifications.append(f"Added {qty} x {name.title()} to manual shopping list.")

def remove_from_manual_shopping_list(name):
    st.session_state.manual_shopping_list = [item for item in st.session_state.manual_shopping_list if item["name"].lower() != name.lower()]
    st.session_state.notifications.append(f"Removed {name.title()} from manual shopping list.")

def check_expiry_alerts():
    inv_df = get_inventory_df()
    alerts = []
    today = datetime.today().date()
    soon = today + timedelta(days=3)
    for _, row in inv_df.iterrows():
        expiry_date = pd.to_datetime(row["Expiry Date"]).date()
        if row["Quantity"] > 0 and expiry_date <= soon:
            alerts.append(f"Item '{row['Name']}' is expiring on {row['Expiry Date']}")
    return alerts

def award_badges():
    badges = st.session_state.badges
    pts = st.session_state.points
    new_badges = []
    
    # Define badge thresholds
    badge_thresholds = {
        "Waste Warrior": 20,
        "Green Guardian": 50,
        "Zero Waste Hero": 100
    }

    for badge_name, threshold in badge_thresholds.items():
        if pts >= threshold and badge_name not in badges:
            badges.add(badge_name)
            new_badges.append(badge_name)
            
    return new_badges

def plot_waste_over_time():
    df = get_waste_df()
    if df.empty:
        st.write("No waste data to display.")
        return
    
    # Ensure 'Date' column is datetime objects for plotting
    df['Date'] = pd.to_datetime(df['Date'])
    waste_by_date = df.groupby("Date")["Quantity"].sum()
    
    fig, ax = plt.subplots()
    ax.plot(waste_by_date.index, waste_by_date.values, marker='o', linestyle='-')
    ax.set_title("Waste Quantity Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Quantity")
    plt.xticks(rotation=45) # Rotate x-axis labels for better readability
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free up memory

def show_notifications():
    if st.session_state.notifications:
        st.info("🔔 Notifications:")
        # Display latest 5 notifications
        for note in st.session_state.notifications[-5:]:
            st.write(f"- {note}")

def inventory_tab():
    st.header("Inventory Management")
    if st.session_state.inventory:
        st.write("Current Inventory:")
        st.dataframe(get_inventory_df())
    else:
        st.info("Inventory is empty.")
    st.markdown("---")
    with st.form("add_inventory_form"):
        st.subheader("Add New Inventory Item")
        name = st.text_input("Item Name")
        qty = st.number_input("Quantity", min_value=1, step=1)
        expiry = st.date_input("Expiry Date", min_value=datetime.today().date()) # Ensure expiry date is not in the past
        submitted = st.form_submit_button("Add Item")
        if submitted:
            if name.strip() == "":
                st.error("Item name cannot be empty.")
            else:
                add_inventory_item(name.strip(), qty, expiry)
                st.success(f"Added {qty} x {name.strip()} to inventory.")
                st.rerun() # Rerun to update the dataframe immediately
    st.markdown("---")

    if st.session_state.inventory:
        st.subheader("Update Inventory Quantity")
        inv_df = get_inventory_df()
        
        # Create a list of (item_name, id) tuples for display and internal use, filter for qty > 0
        item_options_update = [f"{item['name']} (ID: {item['id']})" for item in st.session_state.inventory if item['qty'] > 0]
        if not item_options_update:
            st.info("No available items to update.")
        else:
            selected_item_display = st.selectbox("Select Item to Update", options=item_options_update, key="update_select_item")
            
            # Extract item_id from the selected display string
            selected_item_id = int(selected_item_display.split('(ID: ')[1][:-1]) if selected_item_display else None
            
            current_qty = 0
            selected_item_name = ""
            for item in st.session_state.inventory:
                if item["id"] == selected_item_id:
                    current_qty = item["qty"]
                    selected_item_name = item["name"]
                    break

            new_qty = st.number_input(f"New Quantity for {selected_item_name}", min_value=0, step=1, value=int(current_qty), key="update_qty")
            if st.button("Update Quantity", key="update_qty_button"):
                if selected_item_id is not None:
                    update_inventory_qty(selected_item_id, new_qty)
                    st.success(f"Updated quantity of {selected_item_name} to {new_qty}")
                    st.rerun()
                else:
                    st.error("Please select an item to update.")
        
        st.subheader("Remove Inventory Item")
        item_options_remove = [f"{item['name']} (ID: {item['id']})" for item in st.session_state.inventory]
        if not item_options_remove:
            st.info("No items to remove.")
        else:
            selected_item_display_remove = st.selectbox("Select Item to Remove", options=item_options_remove, key="remove_item_select")
            selected_item_id_remove = int(selected_item_display_remove.split('(ID: ')[1][:-1]) if selected_item_display_remove else None

            if st.button("Remove Item", key="remove_item_button"):
                if selected_item_id_remove is not None:
                    remove_inventory_item(selected_item_id_remove)
                    st.success(f"Removed item from inventory.")
                    st.rerun()
                else:
                    st.error("Please select an item to remove.")
    else:
        st.info("No items to update or remove.")


def consumption_logging_tab():
    st.header("Log Consumption")
    inv_df = get_inventory_df()
    
    # Filter for items with quantity > 0
    available_items_df = inv_df[inv_df["Quantity"] > 0]
    item_names = available_items_df["Name"].tolist()
    
    if available_items_df.empty:
        st.warning("Inventory is empty or all items have zero quantity. Add items before logging consumption.")
        return

    item = st.selectbox("Select Item Consumed", item_names, key="consume_select_item")
    
    max_qty = available_items_df[available_items_df["Name"] == item]["Quantity"].values[0] if item else 0
    
    qty = st.number_input("Quantity Consumed", min_value=1, max_value=int(max_qty), step=1, key="consume_qty_input")
    
    if st.button("Log Consumption", key="log_consumption_button"):
        if qty > 0 and item:
            log_consumption(item, qty)
            for i in st.session_state.inventory:
                if i["name"] == item:
                    i["qty"] -= qty
            st.success(f"Logged consumption of {qty} x {item}.")
            st.rerun()
        else:
            st.error("Quantity consumed must be greater than 0 and an item must be selected.")

def waste_logging_tab():
    st.header("Log Food Waste")
    inv_df = get_inventory_df()
    
    # Filter for items with quantity > 0
    available_items_df = inv_df[inv_df["Quantity"] > 0]
    item_names = available_items_df["Name"].tolist()

    if available_items_df.empty:
        st.warning("Inventory is empty or all items have zero quantity. Add items before logging waste.")
        return
    
    item = st.selectbox("Select Item Wasted", item_names, key="waste_select_item")
    max_qty = available_items_df[available_items_df["Name"] == item]["Quantity"].values[0] if item else 0
    
    qty = st.number_input("Quantity Wasted", min_value=1, max_value=int(max_qty), step=1, key="waste_qty_input")
    reason = st.selectbox("Reason for Waste", ["Expired", "Spoiled", "Leftover", "Other"], key="waste_reason_select")
    
    if st.button("Log Waste", key="log_waste_button"):
        if qty > 0 and item:
            log_waste(item, qty, reason)
            for i in st.session_state.inventory:
                if i["name"] == item:
                    i["qty"] -= qty
            st.success(f"Logged waste of {qty} x {item} due to {reason}.")
            st.rerun()
        else:
            st.error("Quantity wasted must be greater than 0 and an item must be selected.")

def waste_analytics_tab():
    st.header("Waste Analytics Dashboard")
    plot_waste_over_time()
    waste_df = get_waste_df()
    if not waste_df.empty:
        st.markdown("### Waste by Reason")
        waste_by_reason = waste_df.groupby("Reason")["Quantity"].sum()
        
        fig_reason, ax_reason = plt.subplots()
        waste_by_reason.plot(kind='bar', ax=ax_reason)
        ax_reason.set_title("Waste Quantity by Reason")
        ax_reason.set_xlabel("Reason")
        ax_reason.set_ylabel("Quantity")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig_reason)
        plt.close(fig_reason)

        st.markdown("### Top Wasted Items")
        top_wasted_items = waste_df.groupby("Name")["Quantity"].sum().nlargest(5)
        if not top_wasted_items.empty:
            fig_top_wasted, ax_top_wasted = plt.subplots()
            top_wasted_items.plot(kind='bar', ax=ax_top_wasted)
            ax_top_wasted.set_title("Top 5 Wasted Items")
            ax_top_wasted.set_xlabel("Item Name")
            ax_top_wasted.set_ylabel("Total Quantity Wasted")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_top_wasted)
            plt.close(fig_top_wasted)
        else:
            st.info("No data for top wasted items.")
    else:
        st.info("No waste data to display analytics.")

def menu_planning_tab():
    st.title("🍳 Recipe Generator Chatbot")
    st.info("This is a simple recipe generator. For more advanced features, consider connecting to a real AI model.")
    user_input = st.text_input("Enter a dish or ingredient to get a recipe:", "", key="recipe_input")
    if st.button("Get Recipe", key="get_recipe_button"):
        if not user_input.strip():
            st.warning("Please enter a dish or ingredient!")
        else:
            with st.spinner("Generating your recipe..."):
                reply = GenerateResponse(user_input)
            st.markdown("### Recipe:")
            st.write(reply)

def meal_prep_planner_tab():
    st.header("📅 Meal Prep Planner")
    st.write("Plan your meals for the week using your current inventory, especially items expiring soon.")
    st.markdown("---")
    
    inv_df = get_inventory_df()
    if inv_df.empty or inv_df["Quantity"].sum() == 0:
        st.info("Your inventory is empty. Add items to your inventory to start planning meals!")
        return

    st.subheader("Items to Prioritize (Expiring Soon)")
    soon_expiring_items = generate_menu(inv_df)
    if not soon_expiring_items.empty:
        st.dataframe(soon_expiring_items[["Name", "Quantity", "Expiry Date"]])
        st.info("Focus on these items for your meal planning to minimize waste!")
    else:
        st.success("No items are expiring soon. Great job managing your inventory!")

    st.markdown("---")
    st.subheader("Plan Your Week")
    
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    if 'meal_plan' not in st.session_state:
        st.session_state.meal_plan = {day: {meal: "" for meal in meal_types} for day in days_of_week}

    # Use a dictionary to store inputs for form submission
    meal_plan_inputs = {}

    with st.form("meal_plan_form"):
        for day in days_of_week:
            st.markdown(f"#### {day}")
            cols = st.columns(len(meal_types))
            for i, meal_type in enumerate(meal_types):
                with cols[i]:
                    meal_plan_inputs[(day, meal_type)] = st.text_input(
                        f"{meal_type}",
                        value=st.session_state.meal_plan[day][meal_type],
                        key=f"{day}_{meal_type}_input" # Unique key for each input
                    )
        submit_plan = st.form_submit_button("Save Meal Plan")
        if submit_plan:
            for day in days_of_week:
                for meal_type in meal_types:
                    st.session_state.meal_plan[day][meal_type] = meal_plan_inputs[(day, meal_type)]
            st.success("Meal plan saved!")
            st.rerun() # Rerun to update the displayed plan

    st.markdown("---")
    st.subheader("Your Meal Plan Summary")
    meal_plan_data = []
    for day, meals in st.session_state.meal_plan.items():
        for meal_type, dish in meals.items():
            if dish: # Only add if a dish is planned
                meal_plan_data.append({"Day": day, "Meal Type": meal_type, "Dish": dish})
    
    if meal_plan_data:
        meal_plan_df = pd.DataFrame(meal_plan_data)
        st.dataframe(meal_plan_df)
    else:
        st.info("No meals planned yet. Start filling out your weekly plan!")


def donation_suggestions_tab():
    st.header("Donation Suggestions")
    st.write("Nearby donation centers you can contribute to:")
    for center in donation_centers:
        st.markdown(f"{center['name']}** - {center['address']} ({center['distance_km']} km away)")
    
    inv_df = get_inventory_df()
    today = datetime.today().date()
    soon_expiry = today + timedelta(days=7) # Changed to 7 days for more donation opportunities
    
    # Filter for items with quantity > 0 and expiring soon
    to_donate = inv_df[(inv_df["Quantity"] > 0) & (pd.to_datetime(inv_df["Expiry Date"]).dt.date <= soon_expiry)]
    
    if to_donate.empty:
        st.success("No items suitable for donation right now.")
    else:
        st.subheader("Items recommended for donation (expiring soon):")
        st.dataframe(to_donate[["Name", "Quantity", "Expiry Date"]])
        st.info("Consider donating these items to reduce waste and help others!")

def shopping_list_tab():
    st.header("Smart Shopping List")
    st.subheader("Add Items to Your Shopping List Manually")
    with st.form("manual_shopping_form"):
        item_name = st.text_input("Item Name (e.g., Milk, Bread)", key="manual_item_name")
        item_qty = st.number_input("Quantity", min_value=1, step=1, key="manual_item_qty")
        add_item_button = st.form_submit_button("Add to Shopping List")
        if add_item_button:
            if item_name.strip():
                add_to_manual_shopping_list(item_name.strip(), item_qty)
                st.rerun() # Rerun to update the shopping list display
            else:
                st.error("Please enter an item name.")

    st.markdown("---")
    display_items = {}
    
    # Combine forecasted list and manual list
    forecasted_list = generate_auto_shopping_list()
    for item_name, qty in forecasted_list.items():
        display_items[item_name] = display_items.get(item_name, 0) + qty
    
    for item in st.session_state.manual_shopping_list:
        display_items[item["name"]] = display_items.get(item["name"], 0) + item["qty"]
    
    if not display_items:
        st.success("Your shopping list is empty. You're all set!")
    else:
        st.subheader("Your Combined Shopping List")
        # Convert dictionary to a list of tuples and sort for consistent display
        sorted_display_items = sorted(display_items.items())

        # Create a DataFrame for display
        shopping_df = pd.DataFrame([{"Item": item, "Quantity": qty} for item, qty in sorted_display_items])
        
        # Display the shopping list with buttons for each item
        for idx, row in shopping_df.iterrows():
            item_name = row["Item"]
            qty = row["Quantity"]
            
            with st.container(border=True):
                cols = st.columns([0.5, 0.5, 1.5])
                with cols[0]:
                    st.write(item_name)
                with cols[1]:
                    st.write(f"{int(qty)}")
                with cols[2]:
                    # Generate unique keys for each date_input and button
                    expiry_date_key = f"expiry_date_{item_name.replace(' ', '')}{idx}"
                    buy_button_key = f"buy_button_{item_name.replace(' ', '')}{idx}"
                    remove_button_key = f"remove_button_{item_name.replace(' ', '')}{idx}"
                    
                    default_expiry = datetime.now().date() + timedelta(days=7)
                    chosen_expiry = st.date_input("Expiry Date", value=default_expiry, key=expiry_date_key, label_visibility="collapsed") # collapsed label

                    if st.button(f"🛒 Buy {item_name}", key=buy_button_key):
                        add_inventory_item(item_name, int(qty), chosen_expiry)
                        # Remove from manual shopping list if it was manually added
                        st.session_state.manual_shopping_list = [item for item in st.session_state.manual_shopping_list if item["name"].lower() != item_name.lower()]
                        st.success(f"Added {int(qty)} x {item_name} to inventory with expiry {chosen_expiry}.")
                        st.rerun()
                    
                    # Only show remove button for items that were manually added
                    # This check needs to be against the original manual_shopping_list, not the combined display_items
                    if any(item_m["name"].lower() == item_name.lower() for item_m in st.session_state.manual_shopping_list):
                        if st.button(f"❌ Remove {item_name}", key=remove_button_key):
                            remove_from_manual_shopping_list(item_name)
                            st.rerun()

def custom_alerts_reminders_tab():
    st.header("⏰ Custom Alerts & Reminders")
    st.write("Set personalized reminders for your inventory items or anything else!")
    st.markdown("---")

    st.subheader("Add New Reminder")
    with st.form("add_reminder_form"):
        reminder_text = st.text_input("Reminder Message (e.g., 'Use the milk by tomorrow!')", key="reminder_text_input")
        reminder_date = st.date_input("Remind me on...", min_value=datetime.today().date(), key="reminder_date_input")
        reminder_time = st.time_input("At time (optional)", value=datetime.now().time(), key="reminder_time_input")
        add_reminder_button = st.form_submit_button("Set Reminder")

        if add_reminder_button:
            if reminder_text.strip():
                st.session_state.custom_reminders.append({
                    "text": reminder_text.strip(),
                    "date": reminder_date,
                    "time": reminder_time,
                    "set_at": datetime.now()
                })
                st.success("Reminder set successfully!")
                st.rerun()
            else:
                st.error("Please enter a reminder message.")
    
    st.markdown("---")
    st.subheader("Your Active Reminders")
    if not st.session_state.custom_reminders:
        st.info("No custom reminders set.")
    else:
        # Sort reminders by date and then time
        sorted_reminders = sorted(st.session_state.custom_reminders, key=lambda x: (x['date'], x['time']))
        
        current_datetime = datetime.now()
        
        for i, reminder in enumerate(sorted_reminders):
            reminder_dt = datetime.combine(reminder['date'], reminder['time'])
            is_overdue = reminder_dt < current_datetime
            
            status_emoji = "⚠" if is_overdue else "✅"
            status_text = "Overdue" if is_overdue else "Active"

            st.markdown(f"{status_emoji} {reminder['text']}")
            st.write(f"Due: {reminder['date'].strftime('%Y-%m-%d')} at {reminder['time'].strftime('%H:%M')} ({status_text})")
            
            # Button to dismiss reminder
            if st.button(f"Dismiss Reminder {i+1}", key=f"dismiss_reminder_{i}"):
                st.session_state.custom_reminders.pop(st.session_state.custom_reminders.index(reminder))
                st.success("Reminder dismissed!")
                st.rerun()
            st.markdown("---")

def pantry_challenge_tab():
    st.header("🏆 Pantry Challenge")
    st.write("Challenge yourself to use only what you have in your pantry for a set period!")
    st.markdown("---")

    if not st.session_state.pantry_challenge_active:
        st.subheader("Start a New Challenge")
        challenge_duration = st.selectbox(
            "Select Challenge Duration",
            options=["3 Days", "5 Days", "7 Days", "Custom"],
            key="challenge_duration"
        )
        custom_days = 0
        if challenge_duration == "Custom":
            custom_days = st.number_input("Enter custom days", min_value=1, step=1, value=7, key="custom_challenge_days")
        
        if st.button("Start Pantry Challenge!", key="start_challenge_button"):
            days = 0
            if challenge_duration == "3 Days": days = 3
            elif challenge_duration == "5 Days": days = 5
            elif challenge_duration == "7 Days": days = 7
            else: days = custom_days # Correctly assign custom days

            if days > 0:
                st.session_state.pantry_challenge_active = True
                st.session_state.pantry_challenge_start_date = datetime.now().date()
                st.session_state.pantry_challenge_end_date = datetime.now().date() + timedelta(days=days)
                st.success(f"Pantry Challenge started! Try to use only your inventory for the next {days} days.")
                st.info("Remember: The goal is to avoid buying new groceries during the challenge period.")
                st.balloons()
                st.rerun()
            else:
                st.error("Please select a valid challenge duration.")
    else:
        st.subheader("Current Pantry Challenge")
        start_date = st.session_state.pantry_challenge_start_date
        end_date = st.session_state.pantry_challenge_end_date
        today = datetime.now().date()
        
        days_left = (end_date - today).days
        
        if days_left >= 0:
            st.info(f"Your Pantry Challenge is active!")
            st.write(f"Started: *{start_date.strftime('%Y-%m-%d')}*")
            st.write(f"Ends: *{end_date.strftime('%Y-%m-%d')}*")
            st.write(f"{days_left} days left!** Keep going!")
            
            if st.button("End Challenge Early", key="end_challenge_early"):
                st.session_state.pantry_challenge_active = False
                st.session_state.pantry_challenge_start_date = None
                st.session_state.pantry_challenge_end_date = None
                st.warning("Pantry Challenge ended early.")
                st.rerun()
        else:
            st.success("🎉 Your Pantry Challenge has ended!")
            st.write(f"You completed a challenge from *{start_date.strftime('%Y-%m-%d')}* to *{end_date.strftime('%Y-%m-%d')}*.")
            st.info("Great job on trying to reduce your food waste!")
            # Optionally award points/badge for completion here if desired
            # e.g., if st.session_state.points >= 50: st.session_state.badges.add("Pantry Master")
            if st.button("Reset Challenge", key="reset_completed_challenge"):
                st.session_state.pantry_challenge_active = False
                st.session_state.pantry_challenge_start_date = None
                st.session_state.pantry_challenge_end_date = None
                st.rerun()

def community_forum_tab():
    st.header("🤝 Community Forum")
    st.write("Share tips, ask questions, and connect with other users!")
    st.markdown("---")

    st.subheader("New Post")
    with st.form("new_post_form"):
        post_title = st.text_input("Post Title", key="post_title_input")
        post_content = st.text_area("Your Message", key="post_content_input")
        submit_post = st.form_submit_button("Submit Post")

        if submit_post:
            if post_title.strip() and post_content.strip():
                st.session_state.community_posts.append({
                    "author": st.session_state.user_name,
                    "title": post_title.strip(),
                    "content": post_content.strip(),
                    "timestamp": datetime.now()
                })
                st.success("Your post has been shared!")
                st.rerun()
            else:
                st.error("Please enter both a title and a message for your post.")
    
    st.markdown("---")
    st.subheader("Recent Posts")
    if not st.session_state.community_posts:
        st.info("No posts yet. Be the first to share something!")
    else:
        # Display posts in reverse chronological order
        for i, post in enumerate(reversed(st.session_state.community_posts)):
            st.markdown(f"{post['title']}** by *{post['author']}* on {post['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            st.write(post['content'])
            st.markdown("---")


def settings_tab():
    st.header("⚙ Application Settings")
    st.write("Manage your application preferences and data.")
    st.markdown("---")
    st.subheader("User Information")
    current_user_name = st.session_state.user_name
    new_user_name = st.text_input("Change your display name:", value=current_user_name, key="settings_username_input")
    if new_user_name.strip() != current_user_name and st.button("Save Name", key="save_username_button"):
        st.session_state.user_name = new_user_name.strip()
        st.success(f"Your display name has been updated to '{st.session_state.user_name}'.")
    st.markdown("---")
    st.subheader("Data Management")
    st.warning("🚨 Caution: Resetting data will permanently delete all your inventory, consumption, and waste logs. This action cannot be undone.")
    if st.button("Reset All Data", key="reset_all_data_button"):
        st.session_state.confirm_reset = True
    if st.session_state.get('confirm_reset', False):
        st.info("Are you sure you want to delete all data? This cannot be undone.")
        col_confirm_yes, col_confirm_no = st.columns(2)
        with col_confirm_yes:
            if st.button("Yes, Reset Data Permanently", key="confirm_reset_yes"):
                st.session_state.inventory = []
                st.session_state.consumption_log = []
                st.session_state.waste_log = []
                st.session_state.points = 0
                st.session_state.badges = set()
                st.session_state.notifications.append("All application data has been reset.")
                st.session_state.confirm_reset = False
                st.session_state.manual_shopping_list = []
                st.session_state.community_posts = []
                st.session_state.custom_reminders = [] # Reset custom reminders
                st.session_state.pantry_challenge_active = False # Reset pantry challenge
                st.session_state.pantry_challenge_start_date = None
                st.session_state.pantry_challenge_end_date = None
                if 'meal_plan' in st.session_state:
                    del st.session_state.meal_plan
                st.success("All data has been reset successfully!")
                st.rerun()
        with col_confirm_no:
            if st.button("No, Cancel Reset", key="confirm_reset_no"):
                st.session_state.confirm_reset = False
                st.info("Data reset cancelled.")
                st.rerun()
    st.markdown("---")
    st.subheader("About This Application")
    st.info("""
    This AI Food Waste Reduction System helps you manage your food inventory, track consumption and waste,
    and provides insights to minimize food waste.

    Features:
    - Inventory Management: Add, update, and remove food items.
    - Consumption & Waste Logging: Keep a record of what you eat and what goes to waste.
    - Waste Analytics: Visualize your waste patterns.
    - Menu Planning (AI-powered): Get recipe suggestions based on your input.
    - Meal Prep Planner: Plan your weekly meals focusing on expiring items.
    - Leftover Transformation: Get creative ideas for using up leftovers.
    - Custom Alerts & Reminders: Set personalized notifications for anything you need.
    - Pantry Challenge: A fun way to use up your existing groceries.
    - Donation Suggestions: Find nearby places to donate expiring food.
    - Smart Shopping List: Generate a list based on your consumption forecasts and allow manual additions.
    - Gamification: Earn points and badges for your waste reduction efforts!
    - Community Forum: Share tips and connect with other users.
    - Sustainability Tips: Get daily tips to live more sustainably.
    """)
    st.markdown("Version: 1.2.0")
    st.markdown("Developed by: CL Codinglab")

def main():
    st.title("🍅 AI Food Waste Reduction System")
    st.markdown(
        """
        <style>
        .st-emotion-cache-vk32hr.eczokc11 { /* Targeting the sidebar container */
            background-color: #1A1A1A; /* Very dark background */
            color: #E0E0E0; /* Light gray text */
            padding-top: 20px; /* Space at the top */
        }
        .st-emotion-cache-vk32hr.eczokc11 h1, .st-emotion-cache-vk32hr.eczokc11 h2,
        .st-emotion-cache-vk32hr.eczokc11 h3, .st-emotion-cache-vk32hr.eczokc11 h4,
        .st-emotion-cache-vk32hr.eczokc11 h5, .st-emotion-cache-vk32hr.eczokc11 h6,
        .st-emotion-cache-vk32hr.eczokc11 p, .st-emotion-cache-vk32hr.eczokc11 span,
        .st-emotion-cache-vk32hr.eczokc11 label { /* Include labels for text inputs */
            color: #E0E0E0 !important; /* Light gray text for all sidebar elements */
        }
        .st-emotion-cache-vk32hr.eczokc11 .st-emotion-cache-fxbcv5 {
            margin-bottom: 25px;
            padding: 0 20px;
        }
        .st-emotion-cache-vk32hr.eczokc11 .st-emotion-cache-1ft0bsa {
            background-color: #2D2D2D;
            border: none;
            border-radius: 8px;
            color: #E0E0E0;
            padding: 10px 15px 10px 40px;
            box-shadow: none;
            font-size: 16px;
            position: relative;
        }
        .st-emotion-cache-vk32hr.eczokc11 .st-emotion-cache-1ft0bsa::placeholder {
            color: #AAAAAA;
        }
        .st-emotion-cache-vk32hr.eczokc11 .st-emotion-cache-1ft0bsa:focus {
            outline: none;
            box-shadow: 0 0 0 2px #4CAF50;
        }
        .search-icon-container {
            position: relative;
            width: 100%;
        }
        .search-icon-container .st-emotion-cache-1ft0bsa {
            padding-left: 40px;
        }
        .search-icon {
            position: absolute;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            color: #AAAAAA;
            font-size: 18px;
            z-index: 1;
        }
        .stButton>button {
            width: calc(100% - 40px); /* Adjust for padding on sides */
            margin-left: 20px; /* Push from left */
            margin-right: 20px; /* Push from right */
            text-align: left;
            background: none;
            border: none;
            padding: 12px 15px; /* Padding inside the button */
            color: #E0E0E0; /* Light gray text */
            font-size: 16px;
            margin-bottom: 5px; /* Space between buttons */
            transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out, border-radius 0.2s ease-in-out;
            border-radius: 8px; /* More rounded corners */
            display: flex; /* Allow icon and text to be side by side */
            align-items: center;
        }
        .stButton>button:hover {
            background-color: #2D2D2D; /* Darker grey on hover, similar to input background */
            color: #90EE90; /* Lighter green on hover */
            cursor: pointer;
        }
        .stButton>button.active-nav {
            background-color: #2D2D2D !important; /* Darker grey background for active, as per image */
            color: #4CAF50 !important; /* Green text for active */
            font-weight: bold;
            border-radius: 8px;
        }
        .stButton>button svg { /* Targets the SVG for the icon */
            margin-right: 12px; /* Space between icon and text */
            font-size: 20px; /* Make icons slightly larger */
        }
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 h2,
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stText,
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stMarkdown {
            color: #E0E0E0 !important;
            padding-left: 20px;
        }
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stTextInput {
            background-color: #2D2D2D;
            border: none;
            border-radius: 8px;
            color: #E0E0E0;
        }
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stButton {
            width: calc(100% - 40px);
            margin-left: 20px;
            margin-right: 20px;
        }
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stButton>button {
            width: 100%;
            text-align: center;
            background-color: #444444;
            color: #E0E0E0;
            margin-top: 15px;
        }
        section[data-testid="stSidebarV1"] .st-emotion-cache-vk32hr.eczokc11 .stButton>button:hover {
            background-color: #555555;
            color: #FFFFFF;
        }
        .logout-button-container {
            margin-top: 50px; /* Push it down */
            border-top: 1px solid #333333; /* Separator line */
            padding-top: 20px;
            padding-bottom: 20px; /* Space below logout */
        }
        .logout-button-container .stButton>button {
            width: calc(100% - 40px);
            margin-left: 20px;
            margin-right: 20px;
            color: #E0E0E0; /* Keep logout button white */
            background: none;
            border-radius: 8px;
        }
        .logout-button-container .stButton>button:hover {
            background-color: #2D2D2D; /* Same as hover for other buttons */
            color: #FF6347; /* Reddish on hover for logout */
        }
        /* Custom CSS for Points and Badges */
        .points-badge-container {
            padding: 10px 20px 20px 20px;
            border-bottom: 1px solid #333333;
            margin-bottom: 20px;
            color: #E0E0E0;
            text-align: center;
        }
        .points-text {
            font-size: 24px;
            font-weight: bold;
            color: #90EE90; /* Light green for points */
            margin-bottom: 5px;
        }
        .badges-text {
            font-size: 14px;
            color: #ADD8E6; /* Light blue for badges */
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background-color: #212121; /* Darker grey background for the main app area */
            color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Display Points and Badges in Sidebar
    # Convert set to sorted list for consistent display, or to 'None' if empty
    display_badges = ', '.join(sorted(list(st.session_state.badges))) if st.session_state.badges else 'None'

    st.sidebar.markdown(
        """
        <div class="points-badge-container">
            <div class="points-text">🏆 Points: {points}</div>
            <div class="badges-text">🏅 Badges: {badges}</div>
        </div>
        """.format(
            points=st.session_state.points,
            badges=display_badges
        ),
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<div style='margin-top: 30px; font-size: 20px; font-weight: bold; color: white; padding-left: 20px;'>MENU</div>", unsafe_allow_html=True)
    nav_options = {
        "Home": "🏠 Home",
        "Inventory Management": "📦 Inventory Management",
        "Log Consumption": "🍽 Log Consumption",
        "Log Food Waste": "🗑 Log Food Waste",
        "Waste Analytics": "📊 Waste Analytics",
        "Menu Planning": "🍳 Menu Planning",
        "Meal Prep Planner": "📅 Meal Prep Planner", # New navigation option
        "Leftover Transformation": "♻ Leftover Transformation", # New navigation option
        "Custom Alerts & Reminders": "⏰ Custom Alerts & Reminders", # New navigation option
        "Pantry Challenge": "🏆 Pantry Challenge", # New navigation option
        "Donation Suggestions": "❤ Donation Suggestions",
        "Shopping List": "🛒 Shopping List",
        "Community Forum": "🤝 Community Forum", # New navigation option
        "Settings": "⚙ Settings",
    }
    for page_name, icon_label in nav_options.items():
        if st.sidebar.button(icon_label, key=f"nav_{page_name}"):
            st.session_state.current_page = page_name
        if st.session_state.current_page == page_name:
            st.sidebar.markdown(f"""
                <style>
                div[data-testid="stSidebar"] button[key="nav_{page_name}"] {{
                    background-color: #2D2D2D !important;
                    color: #4CAF50 !important;
                    font-weight: bold;
                }}
                </style>
            """, unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    if st.sidebar.button("➡ Log Out", key="nav_Logout"):
        st.info("You have been logged out.")
        st.session_state.clear() # Clear all session state
        st.rerun() # Rerun the app to reset everything
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.current_page == "Home":
        st.header("Welcome to the AI Food Waste Reduction System!")
        st.write("Use the sidebar to navigate through the features.")
        st.markdown("---")
        st.subheader(f"👋 Hello, {st.session_state.user_name}!")
        user_name_input = st.text_input("Change your display name (optional):", value=st.session_state.user_name, key="home_username_input")
        if user_name_input.strip() != st.session_state.user_name:
            st.session_state.user_name = user_name_input.strip() if user_name_input.strip() else "Guest"
            st.success(f"Your name has been updated to {st.session_state.user_name}!")
            st.rerun() # Rerun to update sidebar display

        st.markdown("---")
        
        # Display Sustainability Tip of the Day
        st.subheader("💡 Sustainability Tip of the Day")
        today_date = datetime.now().date()
        # Use a consistent daily index based on date
        tip_index = today_date.day % len(sustainability_tips)
        st.info(sustainability_tips[tip_index])
        
        st.markdown("---")
        show_notifications()
        new_badges = award_badges()
        if new_badges:
            for badge in new_badges:
                st.balloons() # This should now trigger when a new badge is earned
                st.success(f"🎉 Congratulations, {st.session_state.user_name}! You earned the '{badge}' badge!")
        
        alerts = check_expiry_alerts()
        if alerts:
            st.warning("⚠ Expiry Alerts:")
            for alert in alerts:
                st.write(f"- {alert}")
        
        # Display custom reminders if any are due today or overdue
        active_custom_reminders = [
            rem for rem in st.session_state.custom_reminders
            if datetime.combine(rem['date'], rem['time']) <= datetime.now()
        ]
        if active_custom_reminders:
            st.error("⏰ Active Reminders!")
            for rem in active_custom_reminders:
                st.write(f"- {rem['text']} (Due: {rem['date'].strftime('%Y-%m-%d')} at {rem['time'].strftime('%H:%M')})")
            st.info("Visit 'Custom Alerts & Reminders' to manage them.")

        if st.button("Clear Notifications", key="clear_notifications_home"):
            st.session_state.notifications.clear()
            st.success("Notifications cleared!")
            st.rerun()
    elif st.session_state.current_page == "Inventory Management":
        inventory_tab()
    elif st.session_state.current_page == "Log Consumption":
        consumption_logging_tab()
    elif st.session_state.current_page == "Log Food Waste":
        waste_logging_tab()
    elif st.session_state.current_page == "Waste Analytics":
        waste_analytics_tab()
    elif st.session_state.current_page == "Menu Planning":
        menu_planning_tab()
    elif st.session_state.current_page == "Meal Prep Planner":
        meal_prep_planner_tab()
    elif st.session_state.current_page == "Leftover Transformation": # New tab
        leftover_transformation_tab()
    elif st.session_state.current_page == "Custom Alerts & Reminders": # New tab
        custom_alerts_reminders_tab()
    elif st.session_state.current_page == "Pantry Challenge": # New tab
        pantry_challenge_tab()
    elif st.session_state.current_page == "Donation Suggestions":
        donation_suggestions_tab()
    elif st.session_state.current_page == "Shopping List":
        shopping_list_tab()
    elif st.session_state.current_page == "Community Forum":
        community_forum_tab()
    elif st.session_state.current_page == "Settings":
        settings_tab()

if __name__ == "__main__":
    main()