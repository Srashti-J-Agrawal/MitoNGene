# testapp.py
import streamlit as st
import pandas as pd
import urllib.parse
from openai import OpenAI

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
    selected_func = st.selectbox("Filter by Mutation Type (FunctionalRef)", ["All"] + sorted(df["FunctionalRef"].dropna().unique().tolist()))

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
if selected_func != "All":
    filtered_df = filtered_df[filtered_df["FunctionalRef"] == selected_func]

if query:
    query = query.lower()
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]

st.write(f"### Showing {len(filtered_df)} variant(s)")

# Function to create external links
def create_links(row):
    links = []
    if pd.notna(row["dbSNP"]):
        links.append(("dbSNP", f"https://www.ncbi.nlm.nih.gov/snp/{urllib.parse.quote(str(row['dbSNP']))}"))
    if pd.notna(row["ClinvarID"]):
        links.append(("ClinVar", f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{urllib.parse.quote(str(row['ClinvarID']).split('.')[0])}"))
    if pd.notna(row["OMIM"]):
        omim_id = str(row["OMIM"]).split(".")[0]
        links.append(("OMIM", f"https://www.omim.org/entry/{urllib.parse.quote(omim_id)}"))
    return links

# AI summary using OpenAI (new API syntax for openai>=1.0.0)
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

# Generate compact card-style display with clickable buttons
for i, row in filtered_df.iterrows():
    st.markdown("---")
    st.markdown(f"### 🧬 {row['refGene']} | {row['Merged']}")
    st.markdown(f"**Chromosome:** {row['chr']} | **Start:** {row['Start']} | **Ref/Alt:** {row['Ref']}/{row['Alt']}")
    st.markdown(f"**Disease:** {row['Disease']}")
    summary = ai_summary(row["Comments"])
    st.markdown(f"**AI Summary:** _{summary}_")

    # Display external links as buttons
    links = create_links(row)
    cols = st.columns(len(links) + 1)
    for idx, (label, url) in enumerate(links):
        with cols[idx]:
            st.link_button(label, url)

    # View details button
    merged_id = urllib.parse.quote(row["Merged"])
    with cols[-1]:
        st.link_button("View Details", f"?merged={merged_id}")

# Route to full detail view based on URL query param
params = st.query_params
if "merged" in params:
    target = urllib.parse.unquote(params["merged"])
    st.markdown("---")
    st.subheader(f"📋 Full Details for Variant: {target}")
    full_detail = df[df["Merged"] == target]
    st.dataframe(full_detail, use_container_width=True)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data from UniqLiterature2018.xlsx")
