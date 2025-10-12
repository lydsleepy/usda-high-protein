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

st.set_page_config(page_title="Protein Analyzer", page_icon="assets/flexcat.png", layout="wide")
st.title("Protein Analyzer")

st.sidebar.header("Filters")

