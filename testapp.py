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
if os.path.exists("MainLogo.PNG"):
    logo = Image.open("MainLogo.PNG")
    st.image(logo, width=150)
else:
    st.warning("Logo file 'MainLogo.PNG' not found. Please upload it to the app directory.")

# Sidebar navigation
st.sidebar.title("🔍 Navigate")
page = st.sidebar.radio("Go to", ["Home", "Browse All Variants", "By Gene", "By Disease", "By Phenotype", "Gene Diagram", "Bubble & Heatmaps"])

if page == "Home":
    st.title("🧬 Nuclear-encoded Mitochondrial Variant Database")
    query = st.text_input("Search by gene, disease, phenotype, or variant:")
    if query:
        query = query.lower()
        filtered_df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
        st.dataframe(filtered_df, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Variants", total_variants)
    col2.metric("Total Genes", total_genes)
    col3.metric("Total Diseases", total_diseases)
    col4.metric("Total Publications", total_publications)

    st.markdown("### Overview Charts")
    if "Disease" in df.columns:
        disease_chart = df["Disease"].value_counts().reset_index()
        disease_chart.columns = ["Disease", "Count"]
        st.plotly_chart(px.pie(disease_chart.head(10), names="Disease", values="Count", title="Top 10 Diseases"))

    if "refGene" in df.columns:
        gene_chart = df["refGene"].value_counts().reset_index()
        gene_chart.columns = ["Gene", "Count"]
        st.plotly_chart(px.bar(gene_chart.head(10), x="Gene", y="Count", title="Top 10 Genes"))

elif page == "Browse All Variants":
    st.title("📋 All Variants")
    st.dataframe(df, use_container_width=True)

elif page == "By Gene":
    st.title("🔍 Search by Gene")
    gene = st.selectbox("Select Gene", sorted(df["refGene"].dropna().unique()))
    gene_df = df[df["refGene"] == gene]
    st.dataframe(gene_df, use_container_width=True)

elif page == "By Disease":
    st.title("🧬 Search by Disease")
    disease = st.selectbox("Select Disease", sorted(df["Disease"].dropna().unique()))
    disease_df = df[df["Disease"] == disease]
    st.dataframe(disease_df, use_container_width=True)

elif page == "By Phenotype":
    st.title("🧠 Search by Phenotype")
    if "Phenotype" in df.columns:
        phenotype = st.selectbox("Select Phenotype", sorted(df["Phenotype"].dropna().unique()))
        phenotype_df = df[df["Phenotype"] == phenotype]
        st.dataframe(phenotype_df, use_container_width=True)
    else:
        st.warning("No phenotype data available.")

elif page == "Gene Diagram":
    st.title("🧬 Gene Diagram")
    gene = st.selectbox("Select Gene for Visualization", sorted(df["refGene"].dropna().unique()))
    gene_data = df[df["refGene"] == gene]
    if not gene_data.empty:
        fig = px.timeline(
            gene_data,
            x_start="Start",
            x_end="End",
            y="Merged",
            color="FunctionalRef",
            title=f"Variants in {gene}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No variant data for selected gene.")

elif page == "Bubble & Heatmaps":
    st.title("📊 Bubble Plot & Heatmap")
    if "refGene" in df.columns and "Disease" in df.columns:
        grouped = df.groupby(["refGene", "Disease"]).size().reset_index(name="Count")
        st.plotly_chart(px.scatter(
            grouped, x="refGene", y="Disease", size="Count", color="Count",
            title="Gene-Disease Variant Bubbles"
        ), use_container_width=True)

        heatmap_data = grouped.pivot(index="Disease", columns="refGene", values="Count").fillna(0)
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Gene", y="Disease", color="Variants"),
            title="Heatmap of Variants"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Necessary columns not found for plotting.")
