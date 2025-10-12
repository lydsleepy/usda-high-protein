import streamlit as st
import requests
import pandas as pd
import time
# import plotly.express as px
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

selected_categories = st.sidebar.multiselect(
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
                # time.sleep(0.5)  # to avoid overwhelming the api

            # dataframe
            df = pd.DataFrame(all_food_data)
            df = df.dropna(subset=['calories', 'protein_g'], how='all')

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

# display results
if 'searched' in st.session_state and st.session_state['searched']:
    df = st.session_state['df']

    if df.empty:
        st.warning("no foods found matching your criteria. try adjusting the filters!")
    else:
        # summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("total foods found", len(df))
        with col2:
            st.metric("max protein (g)", f"{df['protein_g'].max():.1f}")
        with col3:
            st.metric("avg calories (kcal)", f"{df['calories'].mean():.1f}")
        with col4:
            st.metric("best protein/calorie ratio", f"{df['protein_per_calorie'].max():.3f}")
        
        st.divider()

        # top 10 most efficient
        st.subheader("top 10 most protein-efficient foods")
        top10 = df.nlargest(10, 'protein_per_calorie')

        # interactive chart
        fig = px.bar(
            top10,
            y='description',
            x='protein_per_calorie',
            color='category',
            orientation='h',
            title='protein per calorie (g/kcal)',
            labels={'protein_per_calorie': 'protein per calorie',
                    'description': 'food item'},
            height=500
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

        # detailed table
        st.subheader("top results (detailed)")
        display_cols = ['description', 'category', 'calories',
            'protein_g', 'fat_g', 'carbs_g', 'protein_per_calorie',
            'brand_owner']
        display_df = top10[display_cols].copy()
        display_df.columns = ['food', 'category', 'calories (kcal)',
            'protein (g)', 'fat (g)', 'carbs (g)', 'protein/calorie (g/kcal)',
            'brand']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # download button for csv file
        csv = df.to_csv(index=False)
        st.download_button(
            label='download full results as CSV',
            data=csv,
            file_name='usda_protein_results.csv',
            mime='text/csv'
        )

        # all results table
        # expandable
        with st.expander("view all results"):
            st.dataframe(
                df[display_cols].sort_values('protein_per_calorie', ascending=False),
                use_container_width=True,
                hide_index=True
            )
    
else:
    st.info("select food categories and filters in the sidebar, then click **search foods** to begin!")

    st.markdown("""
    ### how to use:
    1. **select categories**: choose which food types you want to analyze
    2. **set filters**: adjust minimum or maximum values for protein & calories
    3. **search**: click the search button to fetch data from USDA
    4. **analyze**: view top results, charts, and download data)
    """)