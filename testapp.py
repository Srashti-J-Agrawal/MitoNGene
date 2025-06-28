# testapp.py
import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("UniqLiterature2018.xlsx")

df = load_data()

st.title("Genetic Variant & Phenotype Database")

# Search bar
query = st.text_input("Search by Gene, Disease, or dbSNP ID")

# Filtered display
if query:
    query = query.lower()
    filtered = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
    st.write(f"### {len(filtered)} results found:")
    st.dataframe(filtered)
else:
    st.write("### Showing all records:")
    st.dataframe(df)

# Show raw download option
st.download_button("Download Full Dataset", data=df.to_csv(index=False), file_name="variants.csv", mime="text/csv")