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

# Top navigation bar
st.markdown("""
    <style>
        .top-nav {
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #003349;
            padding: 0.8rem 2rem;
            color: white;
            font-weight: bold;
        }
        .top-nav a {
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            font-size: 16px;
        }
        .top-nav a:hover {
            text-decoration: underline;
        }
        .logo-header {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
    </style>
    <div class='top-nav'>
        <div class='logo-header'>
            <a href='/?page=Home'><img src='MainLogo.PNG' width='50' height='50' alt='MitoNGene Logo'></a>
            <span>MitoNGene</span>
        </div>
        <div>
            <a href='#about'>About</a>
            <a href='#vcf-parse'>Vcf Parse</a>
            <a href='#help'>Help</a>
            <a href='#contact'>Contact Us</a>
        </div>
    </div>
    <div style='margin-top: 80px'></div>
""", unsafe_allow_html=True)

# Load main data
df = load_data()

# Calculate metrics
total_variants = df["Merged"].nunique()
total_genes = df["refGene"].nunique()
total_diseases = df["Disease"].nunique()
total_publications = df["PMID"].nunique() if "PMID" in df.columns else "-"

# Load logo image safely
logo_url = "MainLogo.PNG"
if not os.path.exists(logo_url):
    st.warning("Logo file 'MainLogo.PNG' not found. Please upload it to the app directory.")

# Sidebar navigation
st.sidebar.title("🔍 Navigate")
page = st.sidebar.radio("Go to", ["Home", "About", "VCF Parse", "Help", "Contact Us", "Browse All Variants", "By Gene", "By Disease", "By Phenotype", "Gene Diagram", "Bubble & Heatmaps"])




if page == "Home":
    query = st.text_input("🔍 Search Variant / Gene / Disease / Phenotype", placeholder="Phenotype/Gene/Variant/Disease")
    if query:
        query = query.lower()
        filtered_df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
        st.write(f"### Showing {len(filtered_df)} matching result(s)")
        st.dataframe(filtered_df, use_container_width=True)
    if os.path.exists(logo_url):
        st.markdown(f"""
        <style>
            .home-header {{
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(to bottom right, #00a8e8, #0077b6);
                color: white;
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }}
            .home-header img {{
                width: 90px;
                margin-right: 1.5rem;
            }}
            .home-header h1 {{
                font-size: 32px;
                margin: 0;
                line-height: 1.3;
            }}
        </style>
        <div class='home-header'>
            <a href='/?page=Home'><img src='{logo_url}' alt='Logo'></a>
            <h1>Nuclear-encoded Mitochondrial Disease<br>Variants Database</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### Nuclear-encoded Mitochondrial Disease Variants Database")
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-title'>Total number of genes</div>", unsafe_allow_html=True)
        st.metric(label="", value=total_genes)
    with col2:
        st.markdown("<div class='metric-title'>Total number of diseases</div>", unsafe_allow_html=True)
        st.metric(label="", value=total_diseases)
    with col3:
        st.markdown("<div class='metric-title'>Total number of variants</div>", unsafe_allow_html=True)
        st.metric(label="", value=total_variants)
    with col4:
        st.markdown("<div class='metric-title'>Total number of publications</div>", unsafe_allow_html=True)
        st.metric(label="", value=total_publications)

    

    st.markdown("### 📊 Breakdown")
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

        st.markdown("""
        <style>
            .variant-card {
                background-color: #f0f9ff;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
            }
            .variant-card h4 {
                margin-bottom: 0.2rem;
            }
            .variant-card a {
                text-decoration: none;
                font-weight: bold;
                color: #0077b6;
            }
        </style>
        """, unsafe_allow_html=True)

        for i, row in phenotype_df.iterrows():
            unique_id = urllib.parse.quote(str(row['Merged']))
            with st.container():
                st.markdown(f"""
                <div class='variant-card'>
                    <h4>{row['refGene']} – {row['Merged']}</h4>
                    <p><b>Disease:</b> {row['Disease']}<br>
                       <b>Phenotype:</b> {row['Phenotype']}<br>
                       <b>Mutation:</b> {row['FunctionalRef']}<br>
                       <a href='/?entry={unique_id}'>🔗 View full entry</a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
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

elif page == "About":
    st.title("📘 About")
    st.markdown("""
    This database presents curated variants in nuclear-encoded genes associated with mitochondrial diseases.
    It is designed for researchers, clinicians, and bioinformaticians to explore genotype-phenotype relationships
    across curated literature and ClinVar sources.
    """)

elif page == "VCF Parse":
    st.title("🧬 VCF Parse (Coming Soon)")
    st.markdown("""
    Functionality for parsing VCF files and automated annotation will be added soon.
    """)

elif page == "Help":
    st.title("❓ Help")
    st.markdown("""
    To browse variants, select a category from the sidebar (e.g., by Gene, Disease, Phenotype).
    Use the search bar on the homepage to quickly query by gene, SNP ID, or disease name.
    Use the charts to explore top genes and associated diseases.
    """)

elif page == "Contact Us":
    st.title("📬 Contact Us")
    st.markdown("""
    For questions or collaborations, please contact:

    📧 srashti.agrawal@igib.in  
    👨‍🔬 Dr. Vivek T. Natarajan, Scientist, CSIR-IGIB  
    👨‍🔬 Dr. Sridhar Sivasubbu, Scientist, CSIR-IGIB  
    🏢 CSIR-Institute of Genomics and Integrative Biology, Mathura Road, New Delhi
    """)

elif 'entry' in st.query_params:
    entries = st.query_params.get('entry')
    if isinstance(entries, str):
        entries = [entries]
    for entry_id in entries:
        entry_id = urllib.parse.unquote(entry_id)
        entry_df = df[df['Merged'] == entry_id]
        if not entry_df.empty:
            st.markdown(f"## 🧬 Entry: {entry_id}")
            with st.expander(f"Details for {entry_id}", expanded=True):
                for col in entry_df.columns:
                    st.markdown(f"**{col}**: {entry_df.iloc[0][col]}")
        else:
            st.warning(f"No entry found for ID: {entry_id}")

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
