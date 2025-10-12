import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
from usda_functions import fetch_category, extract_nutrients

# to test run:
# streamlit run app.py

# Local URL: http://localhost:8501
# Network URL: http://10.148.82.87:8501

# do NOT use ''' comments it will show up on the website

# page config
st.set_page_config(page_title="NEED PROTEIN", page_icon="assets/flexcat.png", layout="wide")

# header - image, title, description
st.image("assets/flexcat.png", width=200)
st.title("get your protein in")
st.markdown("find the most protein-efficient foods (using the USDA FoodData Central API)")

# api config
api_key = "XeQbGEzwfYOQQ5XDA6EL5ZAyuZCcpYeTHv3coBxZ"
base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

# sidebar for user inputs
st.sidebar.header("Filters")

# food categories
# perhaps expand later
available_categories = {
    "Protein Bars": "protein bars",
    "Greek Yogurt": "greek yogurt",
    "Chicken Breast": "chicken breast",
    "Cottage Cheese": "cottage cheese",
    "Tuna": "tuna",
    "Eggs": "eggs",
    "Salmon": "salmon",
    "Turkey Breast": "turkey breast",
    "Tofu": "tofu",
    "Protein Powder": "protein powder"
}

selected_category = st.sidebar.multiselect(
    "Select Food Categories",
    options=list(available_categories.keys()),
    default=['Chicken Breast', 'Greek Yogurt', 'Tuna', 'Cottage Cheese']
)

st.sidebar.subheader("Filters")
min_protein = st.sidebar.slider("Minimum Protein (g)", 0, 50, 10)
max_calories = st.sidebar.slider("Maximum Calories (kcal)", 0, 500, 300)
max_results = st.sidebar.slider("Results per Category", 10, 100, 50)

if st.sidebar.button("search foods", type="primary"):
    if not selected_categories:
        st.warning("please select at least one food category!")
    else:
        with st.spinner("fetching food data..."):
            all_food_data = []

            # progress bar :D
            progress_bar = st.progress(0)
            for i, category_name in enumerate(selected_categories):
                category_query = available_categories[category_name]
                st.info(f"fetching {category_name}...")

                foods = fetch_category(category_query, max_results)
                for food in foods:
                    food_data = extract_nutrients(food)
                    food_data['category'] = category_name
                    all_food_data.append(food_data)
                
                progress_bar.progress((i + 1) / len(selected_categories))
                time.sleep(0.5)  # to avoid overwhelming the api

            # dataframe
            df = pd.DataFrame(all_food_data)
            df = df.dropna(subset=['calories', 'protein'], how='all')

            df['protein_per_calorie'] = df.apply(
                lambda row: round(row['protein_g'] / row['calories'], 3)
                if pd.notna(row['calories']) and pd.notna(row['protein_g']) and row['calories'] > 0
                else None,
                axis=1
            )

            # apply filters
            df_filtered = df[
                (df['protein_g'] >= min_protein) &
                (df['calories'] <= max_calories) &
                (df['protein_per_calorie'].notna())
            ].copy()

            # store in session state
            st.session_state['df'] = df_filtered
            st.session_state['searched'] = True

