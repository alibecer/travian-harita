import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

MIN_LIMIT = -200
MAX_LIMIT = 200

SHEET_URL = "https://docs.google.com/spreadsheets/d/1PG1WgRzAW2NkHKEhKzTQocggxCMG_UVZsLJx4GgTp4k/gviz/tq?tqx=out:csv&gid=112640639"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    d = df.iloc[:, 10:14].copy()
    d.columns = ["Tip", "İsim", "X", "Y"]
    d["X"] = pd.to_numeric(d["X"], errors="coerce")
    d["Y"] = pd.to_numeric(d["Y"], errors="coerce")
    d = d.dropna(subset=["X", "Y"])
    return d

st.sidebar.title("Kontrol Paneli")
if st.sidebar.button("🔄 Veriyi yenile"):
    st.cache_data.clear()

# Görünüm ayarları
show_grid = st.sidebar.checkbox("Grid çizgileri göster", True)
tick_step = st.sidebar.selectbox("Grid yoğunluğu (tick step)", [5, 10, 20, 25, 50], index=1)
marker_size = st.sidebar.slider("Nokta boyutu", 4, 20, 9)
marker_opacity = st.sidebar.slider("Nokta opaklığı", 30, 100, 95) / 100.0

# Filtreler
df2 = load_data()
tip_options = sorted(df2["Tip"].unique().tolist())
tip_filter = st.sidebar.multiselect("Tip seç", tip_options, default=tip_options)
search_text = st.sidebar.text_input("İsim ara (contains)", "").strip()

dfv = df2[df2["Tip"].isin(tip_filter)].copy()
if search_text:
    dfv = dfv[dfv["İsim"].str.contains(search_text, case=False, na=False)]

# Mesafe
st.sidebar.markdown("---")
st.sidebar.subheader("Mesafe Hesapla")
names_all = sorted(df2["İsim"].unique().tolist())
p1 = st.sidebar.selectbox("1. Nokta", names_all, index=0, key="p1")
p2 = st.sidebar.selectbox("2. Nokta", names_all, index=min(1, len(names_all)-1), key="p2")

if p1 != p2:
    a = df2[df2["İsim"] == p1].iloc[0]
    b = df2[df2["İsim"] == p2].iloc[0]
    dist = float(np.sqrt((a["X"] - b["X"])**2 + (a["Y"] - b["Y"])**2))
    st.sidebar.success(f"Mesafe: {dist:.2f} kare")

# Reset butonu (sınır sabitlemek için pratik çözüm)
reset_view = st.sidebar.button("🔁 Görünümü sıfırla (-200..200)")

# Figure
fig = go.Figure()

color_map = {"Oyuncu": "#4C78FF", "Hedef": "#FF4B4B"}

for tip in sorted(dfv["Tip"].unique()):
    sub = dfv[dfv["Tip"] == tip]
    fig.add_trace(
        go.Scatter(
            x=sub["X"],
            y=sub["Y"],
            mode="markers",
            name=str(tip),
            marker=dict(
                size=marker_size,
                opacity=marker_opacity,
                color=color_map.get(str(tip), None),
            ),
            text=sub["İsim"],
            hovertemplate="<b>%{text}</b><br>X=%{x}<br>Y=%{y}<extra></extra>",
        )
    )

# Layout (dark + zoom only)
fig.update_layout(
    title="Travian Haritası",
    template="plotly_dark",
    height=850,
    dragmode=False,  # ✅ pan kapalı, sürükleme yok
    margin=dict(l=50, r=30, t=70, b=50),
    legend_title_text="Tip",
)

# Axes + grid (zoom works)
x_range = [MIN_LIMIT, MAX_LIMIT]
y_range = [MIN_LIMIT, MAX_LIMIT]
if not reset_view:
    # İlk yüklemede de sabit göster
    pass

fig.update_xaxes(
    range=x_range,
    autorange=False,
    fixedrange=False,              # ✅ zoom çalışsın
    showgrid=show_grid,
    gridcolor="rgba(255,255,255,0.15)",
    zeroline=True,
    zerolinecolor="rgba(255,255,255,0.25)",
    dtick=tick_step,
)

fig.update_yaxes(
    range=y_range,
    autorange=False,
    fixedrange=False,              # ✅ zoom çalışsın
    showgrid=show_grid,            # ✅ Y grid
    gridcolor="rgba(255,255,255,0.15)",
    zeroline=True,
    zerolinecolor="rgba(255,255,255,0.25)",
    dtick=tick_step,
    scaleanchor="x",
    scaleratio=1
)

st.title("Travian Haritası")

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "scrollZoom": True,        # ✅ mouse tekerleği zoom
        "displayModeBar": False,   # toolbar yok
        "doubleClick": False
    }

)
