import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="H1 Returns per Evento",
    layout="wide"
)
st.title("Report H1 dei ritorni pre- e post-evento")

def parse_value(x):
    """Da “1.9%”→0.019, “231K”→231000, “6.888M”→6888000, “54.1”→54.1"""
    if pd.isna(x):
        return np.nan
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
        return np.nan

@st.cache_data
def load_data():
    # 1) macro
    df_macro = pd.read_csv("macro_multi_2019_EU_fixed.csv", parse_dates=["datetime"])
    for col in ["actual", "forecast", "previous"]:
        df_macro[col + "_val"] = df_macro[col].map(parse_value)

    # 2) returns pre / post
    df_pre  = pd.read_csv("pre_m1_returns_eu_5.csv", parse_dates=["datetime"])
    df_post = pd.read_csv("post_m1_returns_eu_5.csv", parse_dates=["datetime"])

    # 3) merge per event+timestamp
    df_pre  = df_pre.merge(
        df_macro[["datetime", "event", "previous_val", "forecast_val", "actual_val"]],
        on=["datetime", "event"], how="left"
    )
    df_post = df_post.merge(
        df_macro[["datetime", "event", "previous_val", "forecast_val", "actual_val"]],
        on=["datetime", "event"], how="left"
    )

    # 4) colonna data per raggruppare
    df_pre["date"]  = df_pre["datetime"].dt.date
    df_post["date"] = df_post["datetime"].dt.date

    # 5) elimino le colonne textual deltas e sum_pips
    drop_cols = ["delta_prev_fc", "delta_act_fc", "delta_act_prev",
                 "pre_sum_pips", "post_sum_pips"]
    df_pre  = df_pre.drop(columns=[c for c in drop_cols if c in df_pre.columns])
    df_post = df_post.drop(columns=[c for c in drop_cols if c in df_post.columns])

    return df_pre, df_post

df_pre, df_post = load_data()

st.subheader("Ritorni Pre-News (H1)")
st.markdown("""
- **event**: nome dell’indicatore macro  
- **delta_prev**: forecast − previous  
- **pre_pips**: movimento in pips da 00:00 fino all’ora dell’uscita  
- **pre_max_pips, pre_min_pips, pre_mean_pips**: max, min e media  
- **date**: data del giorno (per eventuale raggruppamento)
""")
st.dataframe(df_pre, height=400)

st.subheader("Ritorni Post-News (H1)")
st.markdown("""
- **event**: nome dell’indicatore macro  
- **delta_act**: actual − forecast  
- **post_pips**: movimento in pips dall’ora dell’uscita fino a mezzanotte  
- **post_max_pips, post_min_pips, post_mean_pips**: max, min e media  
- **date**: data del giorno (per eventuale raggruppamento)
""")
st.dataframe(df_post, height=400)
