import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
import 

'''
to test run:
streamlit run app.py

Local URL: http://localhost:8501
Network URL: http://10.148.82.87:8501
'''

st.title("Protein Analyzer")

st.sidebar.header("Filters")
