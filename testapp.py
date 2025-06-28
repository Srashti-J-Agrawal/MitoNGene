# testapp.py
import streamlit as st
import pandas as pd
import urllib.parse
from openai import OpenAI
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

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

# Load logo image
logo = Image.open("mito_white.PNG")

# Sidebar navigation
st.sidebar.title("🔍 Navigate")
page = st.sidebar.radio("Go to", ["Home", "Browse All Variants", "By Gene", "By Disease", "By Phenotype", "Gene Diagram", "Bubble & Heatmaps"])

# Home Page
if page == "Home":
    st.image(logo, width=150)
    st.markdown("""
    <h1 style='color:#0288D1; font-size: 38px;'>Nuclear-encoded Mitochondrial Disease <br>Variants Database</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top: 30px; font-size: 16px;'>
    Search genetic variants associated with nuclear-encoded mitochondrial diseases by phenotype, gene, variant, or disease name.
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("🔍 Search Variant / Gene / Disease / Phenotype", placeholder="Phenotype/Gene/Variant/Disease")

    if query:
        query = query.lower()
        filtered_df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
        st.write(f"### Showing {len(filtered_df)} matching result(s)")
        st.dataframe(filtered_df, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧬 Total number of variants", f"{total_variants}")
    col2.metric("🧪 Total number of genes", f"{total_genes}")
    col3.metric("🦠 Total number of diseases", f"{total_diseases}")
    col4.metric("📚 Total number of publications", f"{total_publications}")

    st.markdown("### 📊 Dataset Overview")
    disease_count = df["Disease"].value_counts().reset_index().rename(columns={"index": "Disease", "Disease": "Count"})
    st.plotly_chart(px.pie(disease_count.head(10), names='Disease', values='Count', title='Top 10 Diseases by Variant Count'), use_container_width=True)

    gene_count = df["refGene"].value_counts().reset_index().rename(columns={"index": "Gene", "refGene": "Count"})
    st.plotly_chart(px.bar(gene_count.head(10), x='Gene', y='Count', title='Top 10 Genes by Variant Count'), use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <small>Built with ❤️ using Streamlit | Data from UniqLiterature2018.xlsx</small>
    """, unsafe_allow_html=True)

elif page == "Browse All Variants":
    st.title("🧬 Browse All Variants")
    st.dataframe(df, use_container_width=True)

elif page == "By Gene":
    st.title("🧪 Gene-wise Summary")
    selected_gene = st.selectbox("Select Gene", sorted(df["refGene"].dropna().unique()))
    gene_df = df[df["refGene"] == selected_gene]
    st.write(f"### {len(gene_df)} variant(s) found for {selected_gene}")
    st.dataframe(gene_df, use_container_width=True)
    disease_chart = gene_df["Disease"].value_counts().reset_index().rename(columns={"index": "Disease", "Disease": "Count"})
    st.plotly_chart(px.pie(disease_chart, names='Disease', values='Count', title='Associated Diseases'), use_container_width=True)

elif page == "By Disease":
    st.title("🦠 Disease-wise Summary")
    selected_disease = st.selectbox("Select Disease", sorted(df["Disease"].dropna().unique()))
    dis_df = df[df["Disease"] == selected_disease]
    st.write(f"### {len(dis_df)} variant(s) found for {selected_disease}")
    st.dataframe(dis_df, use_container_width=True)
    gene_chart = dis_df["refGene"].value_counts().reset_index().rename(columns={"index": "Gene", "refGene": "Count"})
    st.plotly_chart(px.bar(gene_chart, x='Gene', y='Count', title='Associated Genes'), use_container_width=True)

elif page == "By Phenotype":
    st.title("📖 Phenotype-wise Summary")
    if "Phenotype" in df.columns:
        selected_pheno = st.selectbox("Select Phenotype", sorted(df["Phenotype"].dropna().unique()))
        pheno_df = df[df["Phenotype"] == selected_pheno]
        st.write(f"### {len(pheno_df)} variant(s) associated with {selected_pheno}")
        st.dataframe(pheno_df, use_container_width=True)
    else:
        st.warning("Phenotype data not available in this dataset.")

elif page == "Gene Diagram":
    st.title("🧬 Gene Diagram Viewer")
    selected_gene = st.selectbox("Select Gene for Diagram", sorted(df["refGene"].dropna().unique()))
    gene_data = df[df["refGene"] == selected_gene]
    if not gene_data.empty:
        st.write(f"Rendering intron/exon-style layout for {selected_gene}...")
        st.plotly_chart(px.timeline(
            gene_data,
            x_start="Start",
            x_end="End",
            y="Merged",
            color="FunctionalRef",
            title=f"Genomic Range of Variants in {selected_gene}"
        ), use_container_width=True)
    else:
        st.info("No data found for the selected gene.")

elif page == "Bubble & Heatmaps":
    st.title("📊 Variant-Level Bubble & Heatmaps")
    if "refGene" in df.columns and "Disease" in df.columns:
        grouped = df.groupby(["refGene", "Disease"]).size().reset_index(name="Count")
        st.plotly_chart(px.scatter(
            grouped, x="refGene", y="Disease", size="Count", color="Count",
            title="Variant Counts by Gene and Disease (Bubble Plot)",
            height=700
        ), use_container_width=True)

        heatmap_data = grouped.pivot(index="Disease", columns="refGene", values="Count").fillna(0)
        st.plotly_chart(px.imshow(
            heatmap_data,
            labels=dict(x="Gene", y="Disease", color="Variant Count"),
            title="Heatmap of Variants by Gene and Disease"
        ), use_container_width=True)
    else:
        st.warning("Required fields for visualization not found.")
