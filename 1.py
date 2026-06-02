# ==============================================================================
# 🛡️ ULTIMATE SMART MONEY TERMINAL v2
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import nselib
from nselib import capital_market

# ૧. પેજ સેટિંગ્સ (Wide Layout)
st.set_page_config(
    layout="wide", 
    page_title="Ultimate Smart Money Terminal v2", 
    page_icon="🛡️"
)
# પેજ સેટિંગ્સની નીચે આ લોગ-ઈન લોજિક ઉમેરો
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 સિક્યોર લૉગ-ઈન")
    user_password = st.text_input("પાસવર્ડ લખો:", type="password")

    if st.button("પ્રવેશ કરો 🚀"):
        if user_password == "420":  # અહીં તમારો મનપસંદ પાસવર્ડ લખો
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ ખોટો પાસવર્ડ!")
    st.stop() # પાસવર્ડ સાચો ન હોય ત્યાં સુધી આગળનો કોડ નહીં ખુલે
    
st.title("🛡️ Ultimate Automated Smart Money Terminal v2")

# ==============================================================================
# 🛠️ સાઇડબાર સેટિંગ્સ (All original sliders fully restored)
# ==============================================================================
st.sidebar.header("📥 Data Downloader / ડેટા ડાઉનલોડ")

default_date = datetime.now()
if default_date.hour < 18:  # સાંજના ૬ વાગ્યા પહેલા ગઈકાલનો ડેટા લેવો
    default_date = default_date - timedelta(days=1)

selected_date = st.sidebar.date_input("📆 End Date / કઈ તારીખ સુધીનો ડેટા જોઈએ છે?", default_date)
days_to_fetch = st.sidebar.slider("⏳ Days to Fetch / કેટલા દિવસનો ડેટા ફેચ કરવો છે?", 1, 30, 10) # SMA ગણતરી માટે રેન્જ ૩૦ સુધી વધારી

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Professional Filters / ફિલ્ટર્સ")

market_segment = st.sidebar.selectbox("🎯 Segment Filter / માર્કેટ સેગમેન્ટ ફિલ્ટર", ["All Stocks"])

u_del = st.sidebar.slider("Min Delivery % / મિનિમમ ડિલિવરી %", 0, 100, 45)
u_gain = st.sidebar.slider("Min Price Change % / મિનિમમ તેજી %", -10.0, 20.0, 1.0, 0.5)
u_min_val = st.sidebar.slider("Min Delivery Value (₹ Cr) / મિનિમમ વેલ્યુ કરોડમાં", 0.0, 500.0, 0.0, 1.0)
u_vol_mult = st.sidebar.slider("Min Volume Multiplier / મિનિમમ વોલ્યુમ મલ્ટિપ્લાયર", 1.0, 10.0, 1.5, 0.1)
u_consecutive = st.sidebar.slider("Min Consecutive Days / સળંગ સિગ્નલના દિવસો", 1, 10, 3)

# ડેટા ફેચિંગ ફંક્શન
@st.cache_data(ttl=3600)
def fetch_nse_data(end_date, num_days):
    combined_data = []
    current_date = end_date
    days_gathered = 0
    attempts = 0
    
    progress_bar = st.progress(0, text="📡 Connecting to NSE Server... / NSE સર્વર કનેક્શન થઈ રહ્યું છે...")
    
    while days_gathered < num_days and attempts < 60: # અટેમ્પટ વધાર્યા જેથી પૂરો SMA ડેટા મળે
        if current_date.weekday() >= 5: # શનિ-રવિ સ્કીપ કરવા
            current_date -= timedelta(days=1)
            continue
            
        date_str = current_date.strftime("%d-%m-%Y")
        try:
            progress_bar.progress(
                int((days_gathered / num_days) * 100), 
                text=f"📥 Fetching Date / ડેટા ફેચિંગ તારીખ: {date_str}"
            )
            df = capital_market.bhav_copy_with_delivery(date_str)
            if df is not None and not df.empty:
                df['FILE_NAME'] = date_str
                df['DATE_OBJ'] = datetime.strptime(date_str, '%d-%m-%Y')
                combined_data.append(df)
                days_gathered += 1
        except Exception as e:
            pass
        current_date -= timedelta(days=1)
        attempts += 1
        
    progress_bar.empty()
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    return None

# ડેટા મેળવવાનું ટ્રિગર
if st.sidebar.button("🚀 Fetch Data From NSE / ડેટા મેળવો"):
    raw_df = fetch_nse_data(selected_date, days_to_fetch)
    if raw_df is not None:
        st.session_state['nse_combined_data'] = raw_df
        st.sidebar.success("✅ Data Loaded Successfully! / ડેટા લોડ થઈ ગયો!")

# મેન્યુઅલ CSV અપલોડર
st.sidebar.markdown("---")
st.sidebar.header("📂 CSV Upload / મેન્યુઅલ ફાઇલ")
uploaded_files = st.sidebar.file_uploader("Upload CSV Files / CSV ફાઇલો અપલોડ કરો", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    manual_data = []
    for f in uploaded_files:
        temp_df = pd.read_csv(f, skipinitialspace=True)
        temp_df.columns = temp_df.columns.str.strip().str.upper()
        temp_df['FILE_NAME'] = f.name
        try:
            date_str = f.name.replace('.csv', '')
            temp_df['DATE_OBJ'] = datetime.strptime(date_str, '%d-%m-%Y')
        except:
            temp_df['DATE_OBJ'] = datetime.now()
        manual_data.append(temp_df)
    st.session_state['nse_combined_data'] = pd.concat(manual_data, ignore_index=True)

# ==============================================================================
# 🧠 કોર એન્જિન પ્રોસેસિંગ  (Core Processing Engine)
# ==============================================================================
if 'nse_combined_data' in st.session_state:
    df = st.session_state['nse_combined_data'].copy()
    df.columns = df.columns.str.strip().str.upper()
    
    # જો DATE_OBJ કૉલમ ન હોય તો જનરેટ કરવી
    if 'DATE_OBJ' not in df.columns:
        df['DATE_OBJ'] = pd.to_datetime(df['FILE_NAME'], format='%d-%m-%Y', errors='coerce')
    else:
        df['DATE_OBJ'] = pd.to_datetime(df['DATE_OBJ'])
        
    # ક્રોનોલોજિકલ ઓર્ડરમાં સોર્ટ કરવું (ઇન્ડિકેટર્સ માટે જરૂરી)
    df = df.sort_values(by=['SYMBOL', 'DATE_OBJ']).reset_index(drop=True)
    
    # કોલમ ઓટો-ડિટેક્શન
    sym_col = next((c for c in df.columns if 'SYMBOL' in c), None)
    close_col = next((c for c in df.columns if 'CLOSE_PRICE' in c or 'CLOSE_PRC' in c or 'CLOSE' in c and 'PREV' not in c), None)
    prev_close_col = next((c for c in df.columns if 'PREV_CLOSE' in c or 'PREV' in c), None)
    del_col = next((c for c in df.columns if 'DELIV_PER' in c or 'DELIV_QTY_TO_TRD_QTY' in c or 'DELIVERY_PCT' in c), None)
    vol_col = next((c for c in df.columns if 'TTL_TRD_QNTY' in c or 'TOTAL_VOLUME' in c or 'VOLUME' in c or 'TRADED_QTY' in c), None)
    del_qty_col = next((c for c in df.columns if 'DELIV_QTY' in c or 'DELIVERY_QTY' in c), None)
    series_col = next((c for c in df.columns if 'SERIES' in c), None)

    # સફાઈ અને ન્યુમેરિક કન્વર્ઝન
    df[close_col] = pd.to_numeric(df[close_col], errors='coerce')
    df[prev_close_col] = pd.to_numeric(df[prev_close_col], errors='coerce')
    df[del_col] = pd.to_numeric(df[del_col].astype(str).str.replace('%', '').str.strip(), errors='coerce')
    if vol_col: df[vol_col] = pd.to_numeric(df[vol_col], errors='coerce')
    if del_qty_col: df[del_qty_col] = pd.to_numeric(df[del_qty_col], errors='coerce')

    if not del_qty_col and vol_col:
        df['DELIV_QTY'] = (df[vol_col] * df[del_col]) / 100
        del_qty_col = 'DELIV_QTY'

    # મૂળ કેલ્ક્યુલેશન્સ
    df['PRICE_CHG_PCT'] = ((df[close_col] - df[prev_close_col]) / df[prev_close_col]) * 100
    df['DELIVERY_VALUE_CR'] = (df[del_qty_col] * df[close_col]) / 10000000

    if series_col:
        df = df[df[series_col].astype(str).str.strip().str.upper().isin(['EQ', 'BE', 'NIFTY50'])]
    df = df.dropna(subset=['PRICE_CHG_PCT', del_col, close_col])

    # 🚀 ORIGINAL SIGNAL ENGINE
    def get_signal(row):
        p = row['PRICE_CHG_PCT']
        d = row[del_col]
        if p >= 4 and d >= 60: return "🔥 BREAKOUT"
        elif p >= 2 and d >= 60: return "⭐ JACKPOT"
        elif p > 0 and d >= 45: return "🟢 LONG BUILDUP"
        elif p < 0 and d >= 45: return "🔴 SHORT BUILDUP"
        elif p > 0 and d < 20: return "⚠️ SHORT COVERING TRAP"
        elif p > 0 and d < 45: return "🟡 SHORT COVERING"
        else: return "⚪ NORMAL"

    df['SIGNAL_ALERTS'] = df.apply(get_signal, axis=1)

    # એવરેજ વોલ્યુમ અને ડિલિવરી સ્પાઈક ગણતરીઓ
    avg_vol = df.groupby(sym_col)[vol_col].mean().reset_index().rename(columns={vol_col: 'AVG_VOLUME'})
    avg_del = df.groupby(sym_col)[del_col].mean().reset_index().rename(columns={del_col: 'AVG_DEL'})
    df = pd.merge(df, avg_vol, on=sym_col, how='left')
    df = pd.merge(df, avg_del, on=sym_col, how='left')
    
    df['VOLUME_MULTIPLIER'] = df[vol_col] / df['AVG_VOLUME']
    df['DELIVERY_SPIKE'] = df[del_col] - df['AVG_DEL']

    # v4 એડવાન્સ સબ-એન્જિન્સ
    df['VOLUME_CLASSIFICATION'] = df.apply(lambda r: "🟢 Bullish Volume" if r['PRICE_CHG_PCT'] > 0 and r['VOLUME_MULTIPLIER'] >= 2 else ("🔴 Bearish Volume" if r['PRICE_CHG_PCT'] < 0 and r['VOLUME_MULTIPLIER'] >= 2 else ("⚪ Weak Volume" if r['VOLUME_MULTIPLIER'] < 1 else "🟡 Neutral Volume")), axis=1)
    df['DIVERGENCE_SIGNAL'] = df.apply(lambda r: "💎 Hidden Accumulation" if r['PRICE_CHG_PCT'] < 0 and r['DELIVERY_SPIKE'] > 10 else ("⚠️ Weak Rally" if r['PRICE_CHG_PCT'] > 0 and r['DELIVERY_SPIKE'] < -10 else ("🧠 Silent Buying" if abs(r['PRICE_CHG_PCT']) < 1 and r['DELIVERY_SPIKE'] > 10 else "NORMAL")), axis=1)
    df['TRAP_SIGNAL'] = df.apply(lambda r: "🚨 OPERATOR TRAP" if r['PRICE_CHG_PCT'] > 5 and r[del_col] < 25 and r['VOLUME_MULTIPLIER'] > 3 else ("⚠️ WEAK BREAKOUT" if r['PRICE_CHG_PCT'] > 3 and r[del_col] < 20 else ("🔻 DISTRIBUTION" if r['PRICE_CHG_PCT'] < -4 and r[del_col] > 60 else ("🔥 EXHAUSTION RALLY" if r['PRICE_CHG_PCT'] > 7 and r['VOLUME_MULTIPLIER'] > 5 else "NORMAL"))), axis=1)
    df['BREAKOUT_SCORE'] = ((df[del_col] * 0.4) + (df['VOLUME_MULTIPLIER'] * 20) + (df['PRICE_CHG_PCT'] * 5)).clip(0, 100)

    # સળંગ સિગ્નલ ટ્રેકર
    signal_counts = df[df['SIGNAL_ALERTS'].isin(['⭐ JACKPOT', '🔥 BREAKOUT'])].groupby([sym_col, 'SIGNAL_ALERTS']).size().reset_index(name='COUNT')

    # ==============================================================================
    # 📊 ૧. માર્કેટ મૂડ ડેશબોર્ડ (Original KPI Dashboard + Pie Chart from File 2)
    # ==============================================================================
    st.markdown("### 📊 Market Mood Dashboard / માર્કેટ લાઈવ સેન્ટિમેન્ટ રિપોર્ટ")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("🔥 Breakouts / બ્રેકઆઉટ", len(df[df['SIGNAL_ALERTS'] == '🔥 BREAKOUT']))
    with k2: st.metric("⭐ Jackpot Stocks / જેકપોટ", len(df[df['SIGNAL_ALERTS'] == '⭐ JACKPOT']))
    with k3: st.metric("🚨 Operator Traps / ટ્રેપ્સ", len(df[df['TRAP_SIGNAL'] != 'NORMAL']))
    with k4: st.metric("💎 Hidden Accum. / છુપી ખરીદી", len(df[df['DIVERGENCE_SIGNAL'] == '💎 Hidden Accumulation']))
    with k5: st.metric("📈 Volume Shockers / વોલ્યુમ શોકર્સ", len(df[df['VOLUME_MULTIPLIER'] >= 2]))

    st.markdown("---")
    
    col_pie1, col_pie2 = st.columns([1, 2])
    with col_pie1:
        counts = df['SIGNAL_ALERTS'].value_counts().reset_index()
        counts.columns = ['SIGNAL', 'COUNT']
        fig_pie = px.pie(counts, values='COUNT', names='SIGNAL', 
                         color='SIGNAL',
                         color_discrete_map={
                             "🔥 BREAKOUT": "#FF4B4B",
                             "⭐ JACKPOT": "#FF1493",
                             "🟢 LONG BUILDUP": "#00CC96",
                             "🔴 SHORT BUILDUP": "#EF553B",
                             "⚠️ SHORT COVERING TRAP": "#FECB52",
                             "🟡 SHORT COVERING": "#FFA500",
                             "⚪ NORMAL": "#AB63FA"
                         }, title="માર્કેટ પોઝિશન્સ પાઇ ચાર્ટ (Market Mood)")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_pie2:
        st.markdown("##### 🔥 જેકપોટ અને બ્રેકઆઉટ રાડાર સ્ટોક્સ (High Conviction Radar)")
        special_alerts = ["🔥 BREAKOUT", "⭐ JACKPOT"]
        jackpot_df = df[df['SIGNAL_ALERTS'].isin(special_alerts)].sort_values(by=['DATE_OBJ', 'DELIVERY_VALUE_CR'], ascending=[False, False])
        if not jackpot_df.empty:
            st.dataframe(jackpot_df[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].round(2), use_container_width=True)
        else:
            st.warning("પસંદ કરેલા દિવસોમાં કોઈ સ્ટોક જેકપોટ કે બ્રેકઆઉટ કન્ડિશનમાં મેચ થયો નથી.")

    st.markdown("---")

    # ==============================================================================
    # 🗂️ એડવાન્સ ટેબ્સ સિસ્ટમ (All original + File 2 specific tabs)
    # ==============================================================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "🎯 Best Stocks",
        "📊 Cumulative Summary",
        "📈 Volume Shockers",
        "💎 Institutional Radar",
        "🚨 Trap Detection",
        "📉 Divergence Radar",
        "🔁 Consecutive Tracker સળંગ સિગ્નલ",
        "🧠 Breakout Score",
        "⚡ Price-Volume Action",  
        "📈 SMA Crossover Scanner",       
        "🔍 Stock Search"
    ])

    # યુનિવર્સલ ડાઉનલોડ બટન
    def download_csv(df_target, title_name):
        csv_bytes = df_target.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Excel/CSV / ફાઇલ ડાઉનલોડ કરો", csv_bytes, f"{title_name}.csv", "text/csv")

    # ------------------------------------------------------------------------------
    # TAB 1: બેસ્ટ ફિલ્ટર સ્ટોક્સ (સુધારેલું: BREAKOUT_SCORE અને VOLUME_MULTIPLIER બંને સાથે)
    # ------------------------------------------------------------------------------
    with tab1:
        st.subheader("🎯 Smart Money Stocks / ફિલ્ટર કરેલા બેસ્ટ સ્ટોક્સ")
        final_filtered = df[(df['PRICE_CHG_PCT'] >= u_gain) & (df[del_col] >= u_del) & (df['DELIVERY_VALUE_CR'] >= u_min_val)].sort_values(by='DELIVERY_VALUE_CR', ascending=False)
        
        # તમારી નવી શરત મુજબ: BREAKOUT_SCORE પણ રાખ્યું છે અને VOLUME_MULTIPLIER ને પણ ઉમેરી દીધું છે.
        exact_display_cols = [sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'VOLUME_MULTIPLIER', 'BREAKOUT_SCORE', 'SIGNAL_ALERTS', 'FILE_NAME']
        st.dataframe(final_filtered[exact_display_cols].round(2), use_container_width=True)
        download_csv(final_filtered[exact_display_cols], "Best_Stocks")

        # Consolidation Breakout લોજિક
        st.markdown("#### 📦 Consolidation Breakout Alerts")
        if len(df['FILE_NAME'].unique()) >= 3:
            grouped_p = df.groupby(sym_col).agg(MIN_P=(close_col, 'min'), MAX_P=(close_col, 'max'), LATEST_P=(close_col, 'last'), LATEST_C=('PRICE_CHG_PCT', 'last'), LATEST_D=(del_col, 'last')).reset_index()
            grouped_p['RANGE_PCT'] = ((grouped_p['MAX_P'] - grouped_p['MIN_P']) / grouped_p['MIN_P']) * 100
            cons_break = grouped_p[(grouped_p['RANGE_PCT'] <= 4.0) & (grouped_p['LATEST_C'] >= 2.0) & (grouped_p['LATEST_D'] >= 50.0)].sort_values(by='LATEST_C', ascending=False)
            if not cons_break.empty:
                st.success("🚀 Tight Consolidation Breakouts found! / સાંકડી રેન્જમાંથી બ્રેકઆઉટ શેરો મળ્યા છે!")
                st.dataframe(cons_break.round(2), use_container_width=True)
            else:
                st.info("અત્યારે સાંકડી રેન્જમાંથી બહાર નીકળતો કોઈ બ્રેકઆઉટ સ્ટોક મળ્યો નથી.")

    # TAB 2: ક્યુમ્યુલેટિવ સમરી (અકબંધ છે)
    with tab2:
        st.subheader("📊 Cumulative Market Summary / ભેગો નીચોડ રિપોર્ટ")
        summary_df = df.groupby(sym_col).agg({close_col: 'last', 'PRICE_CHG_PCT': 'sum', del_col: 'mean', 'DELIVERY_VALUE_CR': 'sum', vol_col: 'sum'}).reset_index()
        summary_filtered = summary_df[summary_df[del_col] >= u_del].sort_values(by='DELIVERY_VALUE_CR', ascending=False)
        st.dataframe(summary_filtered.round(2), use_container_width=True)
        download_csv(summary_filtered, "Cumulative_Summary")

    # TAB 3: વોલ્યુમ શોકર્સ (અકબંધ છે)
    with tab3:
        st.subheader("📈 Volume Shockers / અસાધારણ વોલ્યુમ એનાલિસિસ")
        st.markdown("### 📊 ટોપ ટ્રેડેડ વોલ્યુમ સ્ટોક્સ")
        high_vol_df_old = df.sort_values(by=['DATE_OBJ', vol_col], ascending=[False, False]).head(20)
        st.dataframe(high_vol_df_old[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', vol_col, 'SIGNAL_ALERTS', 'FILE_NAME']].round(2), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🚀 અચાનક વોલ્યુમમાં ઉછાળો આવ્યો હોય તેવા સ્ટોક્સ (Volume Multiplier)")
        shockers = df[df['VOLUME_MULTIPLIER'] >= u_vol_mult].sort_values(by='VOLUME_MULTIPLIER', ascending=False)
        st.dataframe(shockers[[sym_col, 'VOLUME_MULTIPLIER', 'SIGNAL_ALERTS', 'BREAKOUT_SCORE', 'FILE_NAME']].round(2), use_container_width=True)
        download_csv(shockers, "Volume_Shockers")

    # TAB 4: ઇન્સ્ટિટ્યુશનલ રાડાર (અકબંધ છે)
    with tab4:
        st.subheader("💎 Institutional Radar / સંસ્થાકીય એક્યુમ્યુલેશન")
        high_del_days = df[df[del_col] >= 50.0]
        accumulation_count = high_del_days.groupby(sym_col)['FILE_NAME'].count().reset_index().rename(columns={'FILE_NAME': 'STRONG_DELIVERY_DAYS'})
        mega_accumulated = accumulation_count[accumulation_count['STRONG_DELIVERY_DAYS'] >= 3].sort_values(by='STRONG_DELIVERY_DAYS', ascending=False)
        
        if not mega_accumulated.empty:
            st.markdown("#### 🔗 Continuous Institutional Accumulation (સળંગ ખરીદી ધરાવતા સ્ટોક્સ)")
            latest_dates = df.groupby(sym_col)['FILE_NAME'].max().reset_index()
            latest_info = pd.merge(df, latest_dates, on=[sym_col, 'FILE_NAME'])
            final_accum_df = pd.merge(mega_accumulated, latest_info, on=sym_col).sort_values(by='STRONG_DELIVERY_DAYS', ascending=False)
            st.dataframe(final_accum_df[[sym_col, 'STRONG_DELIVERY_DAYS', close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR']].round(2), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### ⚡ Single-Day High Delivery Radar")
        institutional = df[(df[del_col] >= 50) & (df['DELIVERY_VALUE_CR'] >= u_min_val)].sort_values(by='DELIVERY_VALUE_CR', ascending=False)
        st.dataframe(institutional[[sym_col, del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].round(2), use_container_width=True)
        download_csv(institutional, "Institutional_Radar")

    # TAB 5: ટ્રેપ ડિટેક્શન (અકબંધ છે)
    with tab5:
        st.subheader("🚨 Operator Trap Detection Engine / ઓપરેટર ટ્રેપ સ્કેનર")
        traps = df[df['TRAP_SIGNAL'] != 'NORMAL'].sort_values(by='PRICE_CHG_PCT', ascending=False)
        st.dataframe(traps[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'TRAP_SIGNAL', 'FILE_NAME']].round(2), use_container_width=True)
        download_csv(traps, "Operator_Traps")

    # TAB 6: ડાયવર્જન્સ રાડાર (અકબંધ છે)
    with tab6:
        st.subheader("📉 Divergence Radar (Hidden Accumulation) / ડાયવર્જન્સ અને છુપી ખરીદી")
        divergence = df[df['DIVERGENCE_SIGNAL'] != 'NORMAL'].sort_values(by='DELIVERY_SPIKE', ascending=False)
        st.dataframe(divergence[[sym_col, close_col, 'PRICE_CHG_PCT', 'DELIVERY_SPIKE', 'DIVERGENCE_SIGNAL', 'FILE_NAME']].round(2), use_container_width=True)
        download_csv(divergence, "Divergence_Report")

    # TAB 7: સળંગ સિગ્નલ ટ્રેકર (અકબંધ છે)
    with tab7:
        st.subheader("🔁 Consecutive Signal Tracker / સળંગ જેકપોટ અને બ્રેકઆઉટ દિવસો")
        filtered_counts = signal_counts[signal_counts['COUNT'] >= u_consecutive].sort_values(by='COUNT', ascending=False)
        st.dataframe(filtered_counts, use_container_width=True)
        download_csv(filtered_counts, "Consecutive_Signals")

    # TAB 8: બ્રેકઆઉટ પ્રોબેબિલિટી સ્કોર (અકબંધ છે)
    with tab8:
        st.subheader("🧠 Breakout Probability Score Quadrant / સ્કોર એનાલિસિસ")
        breakout_ranked = df.sort_values(by='BREAKOUT_SCORE', ascending=False).head(20)
        
        fig_score = px.bar(breakout_ranked, x=sym_col, y='BREAKOUT_SCORE', color='BREAKOUT_SCORE', title="Top Breakout Probability Stocks", color_continuous_scale='Turbo')
        st.plotly_chart(fig_score, use_container_width=True)
        st.dataframe(breakout_ranked[[sym_col, close_col, 'BREAKOUT_SCORE', 'SIGNAL_ALERTS', 'VOLUME_MULTIPLIER', del_col]].round(2), use_container_width=True)
        download_csv(breakout_ranked, "Breakout_Scores")

    # TAB 9: Price-Volume Action Matrix (અકબંધ છે)
    with tab9:
        st.subheader("⚡ Price-Volume Action Matrix (Professional Quadrant Screen)")
        if vol_col and not df.empty:
            matrix_avg_vol = df.groupby(sym_col)[vol_col].mean().reset_index().rename(columns={vol_col: 'MATRIX_AVG_VOL'})
            latest_date_m = df['FILE_NAME'].max()
            latest_df_m = df[df['FILE_NAME'] == latest_date_m].copy()
            
            matrix_df = pd.merge(latest_df_m, matrix_avg_vol, on=sym_col)
            
            def classify_matrix(row):
                p_chg = row['PRICE_CHG_PCT']
                curr_vol = row[vol_col]
                avg_v = row['MATRIX_AVG_VOL']
                
                if p_chg > 0 and curr_vol > avg_v:
                    return "🟢 High Volume + High Price (Pure Bullish)"
                elif p_chg < 0 and curr_vol > avg_v:
                    return "🔴 High Volume + Low Price (Aggressive Shorting)"
                elif p_chg > 0 and curr_vol <= avg_v:
                    return "🟡 Low Volume + High Price (Lack of Follow-up)"
                else:
                    return "⚪ Low Volume + Low Price (Profit Booking / Dull)"
            
            matrix_df['MATRIX_QUADRANT'] = matrix_df.apply(classify_matrix, axis=1)
            selected_quadrant = st.selectbox("🎯 ક્વાડ્રન્ટ ફિલ્ટર પસંદ કરો:", [
                "🟢 High Volume + High Price (Pure Bullish)",
                "🔴 High Volume + Low Price (Aggressive Shorting)",
                "🟡 Low Volume + High Price (Lack of Follow-up)",
                "⚪ Low Volume + Low Price (Profit Booking / Dull)"
            ])
            filtered_matrix = matrix_df[matrix_df['MATRIX_QUADRANT'] == selected_quadrant].sort_values(by='DELIVERY_VALUE_CR', ascending=False)
            
            st.dataframe(filtered_matrix[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', vol_col, 'MATRIX_AVG_VOL']].rename(columns={
                sym_col: 'STOCK_NAME', close_col: 'PRICE', 'PRICE_CHG_PCT': 'CHANGE_%', del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'VALUE_(CR)', vol_col: 'TODAY_VOLUME', 'MATRIX_AVG_VOL': 'AVG_VOLUME'
            }).round(2), use_container_width=True)
        else:
            st.info("વોલ્યુમ મેટ્રિક્સ લોડ કરવા માટે પૂરતો ડેટા નથી.")

    # TAB 10: SMA Crossover Scanner (અકબંધ છે)
    with tab10:
        st.subheader("📈 Daily Timeframe SMA Crossover Terminal")
        st.write("આ સેક્શન ક્લોઝિંગ પ્રાઈઝ અને અગાઉના દિવસના ડેટાના આધારે કરંટ લાઈવ ક્રોસઓવર્સ ટ્રેક કરે છે. સચોટ પરિણામ માટે ડાબી બાજુ સાઇડબારમાંથી 'Days to Fetch' ફિલ્ટર વધારીને ૧૦ થી ૩૦ દિવસ સેટ કરો.")
        
        df['SMA_9'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=9).mean())
        df['SMA_21'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=21).mean())
        df['SMA_50'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=50).mean())
        
        df['PREV_CLOSE_LIVE'] = df.groupby(sym_col)[close_col].shift(1)
        df['PREV_SMA_9'] = df.groupby(sym_col)['SMA_9'].shift(1)
        df['PREV_SMA_21'] = df.groupby(sym_col)['SMA_21'].shift(1)
        df['PREV_SMA_50'] = df.groupby(sym_col)['SMA_50'].shift(1)
        
        latest_date_s = df['DATE_OBJ'].max()
        sma_latest_df = df[df['DATE_OBJ'] == latest_date_s].copy()
        
        def display_sma_table(filtered_df, title_text, success_mode=True):
            st.markdown(f"##### {title_text}")
            if not filtered_df.empty:
                out_df = filtered_df[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR']].rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'CURRENT_PRICE', 'PRICE_CHG_PCT': 'CHANGE_%', del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_(CR)'
                }).round(2)
                if success_mode:
                    st.dataframe(out_df.style.background_gradient(cmap='Greens', subset=['CHANGE_%']), use_container_width=True)
                else:
                    st.dataframe(out_df.style.background_gradient(cmap='Reds', subset=['CHANGE_%']), use_container_width=True)
            else:
                st.caption("આ ક્રોસઓવરમાં અત્યારે કોઈ સ્ટોક ઉપલબ્ધ નથી.")

        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🔹 SMA 9 Filters", "🔹 SMA 21 Filters", "🔹 SMA 50 Filters"])
        
        with sub_tab1:
            col_b1, col_r1 = st.columns(2)
            with col_b1:
                bullish_9 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_9']) & (sma_latest_df[close_col] > sma_latest_df['SMA_9'])]
                display_sma_table(bullish_9, "🟢 SMA 9: નીચેથી ઉપર (Bullish Crossover)", True)
            with col_r1:
                bearish_9 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_9']) & (sma_latest_df[close_col] < sma_latest_df['SMA_9'])]
                display_sma_table(bearish_9, "🔴 SMA 9: ઉપરથી નીચે (Bearish Crossover)", False)
                
        with sub_tab2:
            col_b2, col_r2 = st.columns(2)
            with col_b2:
                bullish_21 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_21']) & (sma_latest_df[close_col] > sma_latest_df['SMA_21'])]
                display_sma_table(bullish_21, "🟢 SMA 21: નીચેથી ઉપર (Bullish Crossover)", True)
            with col_r2:
                bearish_21 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_21']) & (sma_latest_df[close_col] < sma_latest_df['SMA_21'])]
                display_sma_table(bearish_21, "🔴 SMA 21: ઉપરથી નીચે (Bearish Crossover)", False)

        with sub_tab3:
            col_b3, col_r3 = st.columns(2)
            with col_b3:
                bullish_50 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_50']) & (sma_latest_df[close_col] > sma_latest_df['SMA_50'])]
                display_sma_table(bullish_50, "🟢 SMA 50: નીચેથી ઉપર (Bullish Crossover)", True)
            with col_r3:
                bearish_50 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_50']) & (sma_latest_df[close_col] < sma_latest_df['SMA_50'])]
                display_sma_table(bearish_50, "🔴 SMA 50: ઉપરથી નીચે (Bearish Crossover)", False)

    # TAB 11: સ્માર્ટ સર્ચ અને ઇન્ટરેક્ટિવ ડ્યુઅલ ચાર્ટ (અકબંધ છે)
    with tab11:
        st.subheader("🔍 Smart Stock Search & Multi-Day Chart / સ્માર્ટ સર્ચ હિસ્ટ્રી")
        
        st.markdown("#### 🏹 Swing Trading Radar (Price Down, Delivery Up)")
        unique_dates = sorted(df['FILE_NAME'].unique(), key=lambda x: datetime.strptime(x, '%d-%m-%Y') if '-' in x else x)
        if len(unique_dates) >= 3:
            d3, d2, d1 = unique_dates[-3], unique_dates[-2], unique_dates[-1]
            df_d3 = df[df['FILE_NAME'] == d3][[sym_col, close_col, del_col]].rename(columns={close_col: 'P3', del_col: 'D3'})
            df_d2 = df[df['FILE_NAME'] == d2][[sym_col, close_col, del_col]].rename(columns={close_col: 'P2', del_col: 'D2'})
            df_d1 = df[df['FILE_NAME'] == d1][[sym_col, close_col, del_col]].rename(columns={close_col: 'P1', del_col: 'D1'})
            
            swing_m = pd.merge(pd.merge(df_d1, df_d2, on=sym_col), df_d3, on=sym_col)
            swing_candidates = swing_m[(swing_m['P3'] > swing_m['P2']) & (swing_m['P2'] > swing_m['P1']) & (swing_m['D1'] > swing_m['D2']) & (swing_m['D2'] > swing_m['D3']) & (swing_m['D1'] >= 45.0)]
            if not swing_candidates.empty:
                st.success("💎 Hidden Swing Accumulation Zone Detected! (કિંમત ઘટી રહી છે પણ સંસ્થાઓ નીચા ભાવે માલ એકઠો કરે છે)")
                st.dataframe(swing_candidates.round(2), use_container_width=True)
            else:
                st.info("અત્યારે શરતો મુજબ 'Price Down, Delivery Up' વાળો કોઈ પણ છુપો સ્ટોક મળ્યો નથી.")

        search_query = st.text_input("Enter Stock Symbol (e.g. RELIANCE) / શેરનું નામ લખો:").strip().upper()
        if search_query:
            s_res = df[df[sym_col].astype(str).str.contains(search_query, na=False)].sort_values(by='DATE_OBJ')
            if not s_res.empty:
                st.dataframe(s_res[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].round(2), use_container_width=True)
                
                fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
                fig_dual.add_trace(go.Scatter(x=s_res['FILE_NAME'], y=s_res[close_col], name="Price / ભાવ", mode='lines+markers', line=dict(color='#FF4B4B', width=3)), secondary_y=False)
                fig_dual.add_trace(go.Bar(x=s_res['FILE_NAME'], y=s_res[del_col], name="Delivery % / ડિલિવરી %", opacity=0.3, marker_color='#00CC96'), secondary_y=True)
                
                fig_dual.update_layout(title_text=f"📈 {search_query} : ભાવ (Line) અને ડિલિવરી % (Bar) નો મલ્ટી-ડે ટ્રેન્ડ", hovermode="x unified")
                fig_dual.update_yaxes(title_text="Stock Price (₹)", secondary_y=False)
                fig_dual.update_yaxes(title_text="Delivery Percentage (%)", secondary_y=True)
                st.plotly_chart(fig_dual, use_container_width=True)
            else:
                st.error("આ નામનો કોઈ સ્ટોક મળ્યો નથી.")
                
        st.markdown("---")
        st.info("💡 **પ્રોફેશનલ માર્કેટ એનાલિસિસ ટિપ:**")
        st.markdown("""
        * **SMA Crossover Scanner:** ટૂંકા ગાળાના ટ્રેન્ડ રિવર્સલ પકડવા માટે SMA 9 અને SMA 21 જુઓ. જો કોઈ શેર સિંગલ ડે માં જ શક્તિશાળી સંસ્થાકીય ડિલિવરી વોલ્યુમ સાથે **SMA 50 બ્રેકઆઉટ** આપે, તો મોટો અપટ્રેન્ડ શરૂ થવાની પ્રબળ સંભાવના રહે છે.
        * **Consolidation Breakout:** જો કોઈ સ્ટોક ટેબ ૧ માં સાંકડી રેન્જમાંથી બહાર નીકળતો દેખાય, તો તેમાં મોટી મુવમેન્ટ આવવાની શક્યતા ખૂબ વધારે હોય છે.
        * **Price-Volume Action Matrix:** ટ્રેડિંગ કરતી વખતે હંમેશા **Pure Bullish ક્વાડ્રન્ટ** ના સ્ટોક્સ લોન્ગ પોઝિશન માટે અને **Aggressive Shorting ક્વાડ્રન્ટ** ના સ્ટોક્સ શોર્ટ સેલિંગ માટે વોચલિસ્ટમાં રાખવા.
        """)
else:
    st.info("👋 Please fetch data from sidebar or upload CSV to start. / શરૂ કરવા માટે સાઇડબારમાંથી ડેટા ફેચ કરો અથવા CSV અપલોડ કરો.")
