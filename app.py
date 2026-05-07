import streamlit as st
import math

st.set_page_config(page_title="無線回線設計ツール", layout="centered")

st.markdown("""
<style>
.stNumberInput label { font-size: 16px !important; font-weight: 800 !important; color: #2E8B57 !important; }
.result-box { background-color: #f0fff4; padding: 20px; border-radius: 10px; border-left: 5px solid #2E8B57; margin-top: 20px; }
.credit { text-align: right; font-size: 14px; color: #666; margin-bottom: -20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📡 無線回線設計シミュレーター")

# --- 同軸ケーブルデータ ---
cable_data = {
    "5D-2V": 0.19,  # 100MHz付近の目安(dB/m)
    "8D-2V": 0.13,
    "10D-2V": 0.10,
    "5D-FB": 0.08,
    "8D-FB": 0.06,
    "10D-FB": 0.05,
    "その他（直接入力）": 0.0
}

# --- 1. 送信側設定 ---
st.subheader("🚀 A地点 (送信側) 設定")
col1, col2 = st.columns(2)

with col1:
    freq = st.number_input("周波数 (MHz)", value=70.0, step=1.0)
    tx_pwr_w = st.number_input("送信機出力 (W)", value=1.0, step=0.1)
    tx_ant_gain = st.number_input("送信アンテナ利得 (dBi)", value=2.15)
    tx_height = st.number_input("送信アンテナ地上高 (m)", value=10.0)

with col2:
    cable_type = st.selectbox("同軸ケーブル種類", list(cable_data.keys()))
    if cable_type == "その他（直接入力）":
        cable_loss_per_m = st.number_input("ケーブル損失 (dB/m)", value=0.1)
    else:
        cable_loss_per_m = cable_data[cable_type]
    
    cable_len = st.number_input("ケーブル長さ (m)", value=10.0)
    
    sw_check = st.checkbox("同軸切替器・中継コネクタあり")
    sw_loss = 0.0
    if sw_check:
        sw_loss = st.number_input("切替器・中継損失 (dB)", value=0.5, step=0.1)

# --- 2. 受信側設定 ---
st.markdown("---")
st.subheader("🎯 B地点 (受信側) 設定")
col3, col4 = st.columns(2)

with col3:
    distance_km = st.number_input("地点間距離 (km)", value=5.0, step=0.1)
    rx_ant_gain = st.number_input("受信アンテナ利得 (dBi)", value=2.15)

with col4:
    rx_height = st.number_input("受信アンテナ地上高 (m)", value=5.0)

# --- 計算ロジック ---
# 送信電力dBm
tx_dbm = 10 * math.log10(tx_pwr_w * 1000)
# ケーブル合計損失
total_cable_loss = (cable_loss_per_m * cable_len) + sw_loss
# 実効輻射電力 (EIRP)
eirp = tx_dbm - total_cable_loss + tx_ant_gain

# 自由空間損失 (FSPL)
if distance_km > 0 and freq > 0:
    fspl = 20 * math.log10(distance_km) + 20 * math.log10(freq) + 32.44
else:
    fspl = 0

# 受信電力
rx_dbm = eirp - fspl + rx_ant_gain
rx_dbuv = rx_dbm + 107

# --- 3. 結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.subheader("📊 設計計算結果")
r1, r2 = st.columns(2)
r1.metric("受信電力 (dBm)", f"{rx_dbm:.2f} dBm")
r2.metric("受信電圧 (dBμV)", f"{rx_dbuv:.2f} dBμV")

st.write(f"**【詳細内訳】**")
col_inf1, col_inf2 = st.columns(2)
with col_inf1:
    st.write(f"・送信機出力: {tx_dbm:.2f} dBm")
    st.write(f"・同軸＋切替器損失: -{total_cable_loss:.2f} dB")
    st.write(f"・送信アンテナ直下電力: {tx_dbm - total_cable_loss:.2f} dBm")
with col_inf2:
    st.write(f"・空間伝搬損失: -{fspl:.2f} dB")
    st.write(f"・実効輻射電力(EIRP): {eirp:.2f} dBm")
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. アンテナ高さを考慮したアドバイス ---
st.markdown("---")
st.subheader("🔍 アンテナ高さと見通しの確認")

# 第1フレネルゾーンの計算 (目安)
f1 = 17.3 * math.sqrt((distance_km/4) / (freq/1000))
h_required = f1 # 簡易的に中心部での必要高さ

st.info(f"""
**現場判断のヒント:**
* 現在の距離({distance_km}km)における第1フレネルゾーン半径は約 **{f1:.1f}m** です。
* 送受信アンテナの高さがこの半径以下だと、地面や障害物の影響で計算値より大幅に（最大20dB程度）落ち込む可能性があります。
* 特に70MHz帯は波長が長いため、アンテナを高く上げるほど安定します。
""")
