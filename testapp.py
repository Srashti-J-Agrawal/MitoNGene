# testapp.py
import streamlit as st
import pandas as pd
import urllib.parse
from openai import OpenAI
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import os

# Load data
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    return pd.read_excel("UniqLiterature2018.xlsx")

st.set_page_config(page_title="Genetic Variant & Phenotype DB", layout="wide")

# Load main data
df = load_data()

# Calculate metrics
total_variants = df["Merged"].nunique()
total_genes = df["refGene"].nunique()
total_diseases = df["Disease"].nunique()
total_publications = df["PMID"].nunique() if "PMID" in df.columns else "-"

# Load logo image safely
if os.path.exists("mito_white.PNG"):
    logo = Image.open("mito_white.PNG")
    st.image(logo, width=150)
else:
    st.warning("Logo file 'mito_white.PNG' not found. Please upload it to the app directory.")

# Sidebar navigation
st.sidebar.title("🔍 Navigate")
page = st.sidebar.radio("Go to", ["Home", "Browse All Variants", "By Gene", "By Disease", "By Phenotype", "Gene Diagram", "Bubble & Heatmaps"])

# (rest of app remains unchanged)
