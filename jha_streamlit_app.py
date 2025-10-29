import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="JHA Interactive (Prototype)", layout="wide")

@st.cache_data
def load_data(path="/mnt/data/JHA by Division.xlsx"):
    xls = pd.ExcelFile(path)
    sheet_name = next((s for s in xls.sheet_names if "Key JHAs" in s or "Key JHA" in s), xls.sheet_names[0])
    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]
    div_col = next((c for c in df.columns if "division" in c.lower()), None)
    if div_col:
        df[div_col] = df[div_col].ffill()
    return df, xls.sheet_names

df, sheets = load_data()

st.title("JHA Interactive — Streamlit Prototype")
st.markdown("Filter the Job Hazard Analysis data, search, view charts, and download filtered CSV.")

q = st.sidebar.text_input("Search (matches any text)")
div_col = next((c for c in df.columns if "division" in c.lower()), None)
divisions = ["All"] + sorted(df[div_col].dropna().unique().tolist()) if div_col else ["All"]
sel_div = st.sidebar.selectbox("Division", divisions)

filtered = df.copy()
if div_col and sel_div != "All":
    filtered = filtered[filtered[div_col] == sel_div]
if q:
    qlow = q.lower()
    mask = filtered.apply(lambda row: row.astype(str).str.lower().str.contains(qlow, na=False).any(), axis=1)
    filtered = filtered[mask]

st.sidebar.write(f"Filtered rows: {len(filtered)}")

def convert_df_to_csv(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

csv_bytes = convert_df_to_csv(filtered)
st.sidebar.download_button("Download filtered CSV", data=csv_bytes, file_name="jha_filtered.csv", mime="text/csv")

st.subheader("Data Preview")
st.write(f"Showing {len(filtered)} rows from sheet: **{sheets[0]}**")
st.dataframe(filtered, use_container_width=True)

st.subheader("Counts by Division")
if div_col:
    counts = df[div_col].fillna("Unknown").value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(6, max(3, 0.3*len(counts))))
    counts.plot(kind="barh", ax=ax)
    ax.set_xlabel("Number of JHAs")
    ax.set_ylabel("Division")
    ax.set_title("JHAs by Division")
    st.pyplot(fig)
else:
    st.info("No Division-like column detected for chart.")

st.sidebar.subheader("Available sheets")
for s in sheets:
    st.sidebar.write(s)

st.markdown("""
**Notes:**
- To run locally: `pip install streamlit pandas openpyxl matplotlib` then `streamlit run jha_streamlit_app.py`.
""")
