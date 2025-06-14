import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="H1 Returns per Evento",
    layout="wide"
)
st.title("Report H1 dei ritorni pre- e post-evento")

def parse_value(x):
    """Da “1.9%”→0.019, “231K”→231000, “6.888M”→6888000, “54.1”→54.1"""
    if pd.isna(x):
        return float("nan")
    s = str(x).strip()
    if s.endswith('%'):
        return float(s[:-1]) / 100.0
    if s.endswith('K'):
        return float(s[:-1]) * 1_000
    if s.endswith('M'):
        return float(s[:-1]) * 1_000_000
    try:
        return float(s)
    except:
        return float("nan")

@st.cache_data
def load_data():
    # 1) Macro multi‐indicatore
    df_macro = pd.read_csv("macro_multi_2019.csv", parse_dates=["datetime"])
    for col in ["actual", "forecast", "previous"]:
        df_macro[col + "_val"] = df_macro[col].map(parse_value)

    # 2) Pre e post returns
    df_pre  = pd.read_csv("pre_h1_returns_2019_2.csv", parse_dates=["datetime"])
    df_post = pd.read_csv("post_h1_returns_2019_filtered.csv", parse_dates=["datetime"])

    # 3) Unisco i valori numerici originali
    df_pre = df_pre.merge(
        df_macro[["datetime","event","previous_val","forecast_val","actual_val"]],
        on=["datetime","event"], how="left"
    )
    df_post = df_post.merge(
        df_macro[["datetime","event","previous_val","forecast_val","actual_val"]],
        on=["datetime","event"], how="left"
    )

    # 4) Calcolo i nuovi delta numerici
    df_pre["delta_prev"] = df_pre["forecast_val"] - df_pre["previous_val"]
    df_post["delta_act"]  = df_post["actual_val"]   - df_post["forecast_val"]

    # 5) Colonna data-only per raggruppamento
    df_pre["date"]  = df_pre["datetime"].dt.date
    df_post["date"] = df_post["datetime"].dt.date

    return df_pre, df_post

df_pre, df_post = load_data()

# --------------------- RITORNI PRE-NEWS ---------------------
st.subheader("Ritorni Pre-News (H1)")
st.markdown("""
- **event**: nome dell’indicatore macro  
- **delta_prev**: forecast − previous  
- **pre_pips**: movimento in pips da 00:00 fino all’ora dell’uscita  
- **pre_max_pips, pre_min_pips, pre_mean_pips, pre_sum_pips**: max, min, media e somma dei movimenti  
- **previous_val, forecast_val, actual_val**: valori raw di riferimento  
- **date**: data del giorno (per eventuale raggruppamento)
""")

cols_pre = [
    "datetime", "event",
    "pre_pips", "pre_max_pips", "pre_min_pips", "pre_mean_pips", "pre_sum_pips",
    "previous_val", "forecast_val", "actual_val",
    "date"
]
st.dataframe(df_pre[cols_pre], height=400)

# --------------------- RITORNI POST-NEWS ---------------------
st.subheader("Ritorni Post-News (H1)")
st.markdown("""
- **event**: nome dell’indicatore macro  
- **delta_act**: actual − forecast  
- **post_pips**: movimento in pips dall’ora dell’uscita fino a mezzanotte  
- **post_max_pips, post_min_pips, post_mean_pips, post_sum_pips**: max, min, media e somma dei movimenti  
- **previous_val, forecast_val, actual_val**: valori raw di riferimento  
- **date**: data del giorno (per eventuale raggruppamento)
""")

cols_post = [
    "datetime", "event",
    "post_pips", "post_max_pips", "post_min_pips", "post_mean_pips", "post_sum_pips",
    "previous_val", "forecast_val", "actual_val",
    "date"
]
st.dataframe(df_post[cols_post], height=400)
