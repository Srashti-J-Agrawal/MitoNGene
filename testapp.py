# testapp.py
import streamlit as st
import pandas as pd
import urllib.parse
import openai

# Load data
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    return pd.read_excel("UniqLiterature2018.xlsx")

st.set_page_config(page_title="Genetic Variant & Phenotype DB", layout="wide")
st.title("🧬 Genetic Variant & Phenotype Database")

# Admin Upload Panel
with st.expander("⚙️ Admin: Upload Updated Dataset"):
    uploaded_file = st.file_uploader("Upload a new Excel file to update the database", type=["xlsx"])
    if uploaded_file:
        st.success("New file uploaded successfully.")

df = load_data(uploaded_file if 'uploaded_file' in locals() else None)

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter Options")
    selected_gene = st.selectbox("Filter by Gene", ["All"] + sorted(df["refGene"].dropna().unique().tolist()))
    selected_disease = st.selectbox("Filter by Disease", ["All"] + sorted(df["Disease"].dropna().unique().tolist()))
    selected_chr = st.selectbox("Filter by Chromosome", ["All"] + sorted(df["chr"].dropna().unique().tolist()))

# Search box in main view
query = st.text_input("🔎 Search for keyword in all fields (e.g., SNP ID, phenotype, gene, comment)")

# Apply filters
filtered_df = df.copy()
if selected_gene != "All":
    filtered_df = filtered_df[filtered_df["refGene"] == selected_gene]
if selected_disease != "All":
    filtered_df = filtered_df[filtered_df["Disease"] == selected_disease]
if selected_chr != "All":
    filtered_df = filtered_df[filtered_df["chr"] == selected_chr]

if query:
    query = query.lower()
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]

st.write(f"### Showing {len(filtered_df)} variant(s)")

# Function to create external links
def create_links(row):
    links = []
    if pd.notna(row["dbSNP"]):
        links.append(f"[dbSNP](https://www.ncbi.nlm.nih.gov/snp/{urllib.parse.quote(str(row['dbSNP']))})")
    if pd.notna(row["ClinvarID"]):
        links.append(f"[ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/variation/{urllib.parse.quote(str(row['ClinvarID']).split('.')[0])})")
    if pd.notna(row["OMIM"]):
        omim_id = str(row["OMIM"]).split(".")[0]
        links.append(f"[OMIM](https://www.omim.org/entry/{urllib.parse.quote(omim_id)})")
    return " | ".join(links)

# AI summary using OpenAI (new API syntax for openai>=1.0.0)
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai_api_key"])

def ai_summary(comment):
    if pd.isna(comment) or comment.strip() == "":
        return "No comment to summarize."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize this genetic variant comment in one sentence."},
                {"role": "user", "content": comment}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error summarizing] {str(e)}"

# Generate final view DataFrame
styled_df = filtered_df[["refGene", "chr", "Start", "Ref", "Alt", "Disease", "dbSNP", "ClinvarID", "OMIM", "Comments"]].copy()
styled_df["Links"] = filtered_df.apply(create_links, axis=1)
styled_df["AI Summary"] = filtered_df["Comments"].apply(ai_summary)

# Add simple severity tagging (mockup)
def tag_severity(disease):
    if pd.isna(disease):
        return "🟢 Mild"
    disease_lower = disease.lower()
    if any(keyword in disease_lower for keyword in ["lethal", "severe", "neurodegenerative"]):
        return "🔴 Severe"
    elif any(keyword in disease_lower for keyword in ["progressive", "chronic"]):
        return "🟠 Moderate"
    else:
        return "🟢 Mild"

styled_df["Severity"] = filtered_df["Disease"].apply(tag_severity)

# Multi-row selection
selected_rows = st.multiselect("Select row indices to export:", styled_df.index.tolist())
if selected_rows:
    export_df = styled_df.loc[selected_rows]
    st.download_button(
        label="📥 Export Selected Rows",
        data=export_df.to_csv(index=False),
        file_name="selected_variants.csv",
        mime="text/csv"
    )

# Display table
st.data_editor(
    styled_df[["refGene", "chr", "Start", "Ref", "Alt", "Disease", "Severity", "Links", "AI Summary"]],
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic"
)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data from UniqLiterature2018.xlsx")
