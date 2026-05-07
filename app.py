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
st.write("距離とアンテナ利得から受信電力を予測します（自由空間損失モデル）")

# --- 入力セクション ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 A地点 (送信側)")
    freq = st.number_input("周波数 (MHz)", value=70.0, step=1.0)
    tx_power_w = st.number_input("送信機出力 (W)", value=1.0, step=0.1, format="%.2f")
    tx_ant_gain = st.number_input("送信アンテナ利得 (dBi)", value=2.15, step=0.1, help="半波長ダイポールなら2.15dBi")
    tx_height = st.number_input("送信アンテナ地上高 (m)", value=10.0, step=1.0)

with col2:
    st.subheader("🎯 B地点 (受信側)")
    distance_km = st.number_input("地点間距離 (km)", value=5.0, step=0.1, format="%.2f")
    rx_ant_gain = st.number_input("受信アンテナ利得 (dBi)", value=2.15, step=0.1)
    rx_height = st.number_input("受信アンテナ地上高 (m)", value=5.0, step=1.0)

st.markdown("---")

# --- 計算ロジック ---
# 1. 送信電力をdBmに換算 (dBm = 10 * log10(mW))
tx_power_dbm = 10 * math.log10(tx_power_w * 1000)

# 2. 自由空間伝搬損失 (FSPL) の計算
# Loss(dB) = 20*log10(d[km]) + 20*log10(f[MHz]) + 32.44
if distance_km > 0 and freq > 0:
    fspl = 20 * math.log10(distance_km) + 20 * math.log10(freq) + 32.44
else:
    fspl = 0

# 3. 受信電力 (dBm) = 送信出力 + 送信利得 - 伝搬損失 + 受信利得
rx_power_dbm = tx_power_dbm + tx_ant_gain - fspl + rx_ant_gain

# 4. dBμV (50Ω系) への換算
rx_power_dbuv = rx_power_dbm + 107

# --- 結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.subheader("📊 シミュレーション結果")

res_col1, res_col2 = st.columns(2)
res_col1.metric("受信電力 (dBm)", f"{rx_power_dbm:.2f} dBm")
res_col2.metric("受信電圧 (dBμV)", f"{rx_power_dbuv:.2f} dBμV")

st.write(f"**【内訳】**")
st.write(f"・送信出力: {tx_power_dbm:.2f} dBm")
st.write(f"・空間損失: {fspl:.2f} dB")
st.write(f"・実効輻射電力(EIRP): {tx_power_dbm + tx_ant_gain:.2f} dBm")
st.markdown('</div>', unsafe_allow_html=True)

# --- 解説 ---
with st.expander("📌 計算の前提条件と補足"):
    st.write("""
    * **自由空間損失**: 障害物が一切ない理想的な空間での減衰です。
    * **アンテナ高さ**: このツールではFSPLモデルを使用しているため、高さは計算式に直接反映されませんが、実際の現場では高さがあるほど障害物の影響（フレネルゾーン）を回避できます。
    * **実際の現場では**: 地形や建物による遮蔽、地面からの反射があるため、計算結果より **10〜20dB程度低くなる** ことが一般的です。
    """)
