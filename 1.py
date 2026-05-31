import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import nselib
from nselib import capital_market

# ૧. પેજ સેટિંગ્સ (Wide Layout)
st.set_page_config(layout="wide", page_title="Ultimate Smart Money Terminal v1", page_icon="🛡️")

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

# ટાઈટલ અને વર્ણન
st.title("🛡️ અલ્ટીમેટ ઓટોમેટેડ સ્માર્ટ મની ટ્રેકર અને ટ્રેન્ડ એનાલિસિસ ટર્મિનલ v1")
st.write("NSE સર્વર પરથી ઓટોમેટીક મલ્ટી-ડે ડેટા ફેચિંગ, જેકપોટ રાડાર, એડવાન્સ વોલ્યુમ શૉકર્સ, સ્માર્ટ ડિલિવરી વેલ્યુ ટ્રેકિંગ અને પ્રોફેશનલ ક્યુમ્યુલેટિવ એનાલિસિસ સિસ્ટમ.")

# 🛠️ સાઇડબાર ઓટોમેશન સેક્શન
st.sidebar.header("📥 ઓટોમેટિક મલ્ટી-ડે ડેટા ડાઉનલોડ")

# બાય-ડિફોલ્ટ ગઈકાલની અથવા આજની તારીખ સેટિંગ
default_date = datetime.now()
if default_date.hour < 18:  # સાંજના ૬ વાગ્યા પહેલા ગઈકાલનો ડેટા લેવો
    default_date = default_date - timedelta(days=1)

selected_date = st.sidebar.date_input("કઈ તારીખ સુધીનો ડેટા જોઈએ છે?", default_date)
days_to_fetch = st.sidebar.slider("કેટલા દિવસનો ડેટા એકસાથે ફેચ કરવો છે?", 1, 30, 10) # SMA ગણવા માટે દિવસો વધાર્યા છે

# ગ્લોબલ ડેટા લિસ્ટ
all_data = []

# બટન ક્લિક થતાં ઓટોમેટિક ડેટા ફેચિંગ
if st.sidebar.button("🚀 NSE માંથી મલ્ટી-ડે ડેટા મેળવો"):
    with st.spinner(f"NSE સર્વર પરથી છેલ્લા {days_to_fetch} ટ્રેડિંગ દિવસોનો ડેટા ઓટોમેટિક ડાઉનલોડ થઈ રહ્યો છે..."):
        current_check_date = selected_date
        fetched_days_count = 0
        attempts = 0
        
        while fetched_days_count < days_to_fetch and attempts < 60: # વધારે અટેમ્પટ રાખ્યા છે જેથી પૂરતો ડેટા મળે
            date_str = current_check_date.strftime('%d-%m-%Y')
            try:
                data = capital_market.bhav_copy_with_delivery(date_str)
                if data is not None and not data.empty:
                    temp_df = data.copy()
                    temp_df.columns = temp_df.columns.str.strip().str.upper()
                    temp_df['FILE_NAME'] = date_str  # તારીખનું લેબલ
                    # સોર્ટિંગ માટે સાચી ડેટ ઓબ્જેક્ટ બનાવવી
                    temp_df['DATE_OBJ'] = datetime.strptime(date_str, '%d-%m-%Y')
                    all_data.append(temp_df)
                    fetched_days_count += 1
            except Exception as e:
                pass
            current_check_date = current_check_date - timedelta(days=1)
            attempts += 1
            
        if all_data:
            main_df = pd.concat(all_data, ignore_index=True)
            st.session_state['nse_combined_data'] = main_df
            st.sidebar.success(f"✅ સફળતાપૂર્વક {fetched_days_count} દિવસનો લાઈવ ડેટા લોડ થઈ ગયો!")
        else:
            st.sidebar.error("❌ કોઈ ડેટા મળ્યો નથી. કૃપા કરીને રજાઓ ચેક કરો.")

# 📂 મેન્યુઅલ મલ્ટી-ફાઇલ બેકઅપ અપલોડર
st.sidebar.markdown("---")
st.sidebar.header("📂 મેન્યુઅલ ફાઇલ બેકઅપ (Multi-Upload)")
uploaded_files = st.sidebar.file_uploader("અથવા ડાઉનલોડ કરેલી એકથી વધુ CSV ફાઇલો અહીં ડ્રોપ કરો", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    manual_data = []
    for f in uploaded_files:
        temp_df = pd.read_csv(f, skipinitialspace=True)
        temp_df.columns = temp_df.columns.str.strip().str.upper()
        temp_df['FILE_NAME'] = f.name
        # ફાઇલના નામમાંથી અથવા અન્ય કોઈ રીતે ડેટ ઓબ્જેક્ટ સેટ કરવી (જો ફોર્મેટ DD-MM-YYYY હોય)
        try:
            date_str = f.name.replace('.csv', '')
            temp_df['DATE_OBJ'] = datetime.strptime(date_str, '%d-%m-%Y')
        except:
            temp_df['DATE_OBJ'] = datetime.now() # ફોલબેક
        manual_data.append(temp_df)
    st.session_state['nse_combined_data'] = pd.concat(manual_data, ignore_index=True)

# ⚙️ મેઇન લિસ્ટ સેટિંગ્સ ફિલ્ટર્સ (સાઇડબાર નીચે)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ મેઇન લિસ્ટ સેટિંગ્સ")

market_segment = st.sidebar.selectbox("🎯 માર્કેટ સેગમેન્ટ ફિલ્ટર", ["All Stocks"])

u_del = st.sidebar.slider("ટેબલ માટે મિનિમમ ડિલિવરી %", 0, 100, 45)
u_gain = st.sidebar.slider("ટેબલ માટે મિનિમમ તેજી %", -10.0, 20.0, 1.0, 0.5)
u_min_val = st.sidebar.slider("મિનિમમ ડિલિવરી વેલ્યુ (₹ કરોડમાં)", 0.0, 100.0, 0.0, 0.5)

# 📊 ડેટા પ્રોસેસિંગ અને એનાલિસિસ શરૂ
if 'nse_combined_data' in st.session_state:
    df = st.session_state['nse_combined_data'].copy()
    
    # જો DATE_OBJ કૉલમ ન હોય તો જનરેટ કરવી
    if 'DATE_OBJ' not in df.columns:
        df['DATE_OBJ'] = pd.to_datetime(df['FILE_NAME'], format='%d-%m-%Y', errors='coerce')
    else:
        df['DATE_OBJ'] = pd.to_datetime(df['DATE_OBJ'])
        
    # ક્રોનોલોજિકલ ઓર્ડરમાં સોર્ટ કરવું (ઇન્ડિકેટર્સ ગણવા માટે જરૂરી)
    df = df.sort_values(by=['SYMBOL', 'DATE_OBJ']).reset_index(drop=True)
    
    # સાચી કૉલમ્સ ઓટો-ડિટેક્ટ કરવી
    sym_col = next((c for c in df.columns if 'SYMBOL' in c), None)
    close_col = next((c for c in df.columns if 'CLOSE_PRICE' in c or 'CLOSE_PRC' in c or 'CLOSE' in c and 'PREV' not in c), None)
    prev_close_col = next((c for c in df.columns if 'PREV_CLOSE' in c or 'PREV' in c), None)
    del_col = next((c for c in df.columns if 'DELIV_PER' in c or 'DELIV_QTY_TO_TRD_QTY' in c or 'DELIVERY_PCT' in c or '⚡' in str(c)), None)
    vol_col = next((c for c in df.columns if 'TTL_TRD_QNTY' in c or 'TOTAL_VOLUME' in c or 'VOLUME' in c or 'TRADED_QTY' in c), None)
    del_qty_col = next((c for c in df.columns if 'DELIV_QTY' in c or 'DELIVERY_QTY' in c or 'DELIVERY_QUANTITY' in c), None)
    series_col = next((c for c in df.columns if 'SERIES' in c), None)
    
    if sym_col and close_col and prev_close_col and del_col:
        # ડેટા ક્લીનિંગ અને કન્વર્ઝન
        df[close_col] = pd.to_numeric(df[close_col], errors='coerce')
        df[prev_close_col] = pd.to_numeric(df[prev_close_col], errors='coerce')
        df[del_col] = pd.to_numeric(df[del_col].astype(str).str.replace('%', '').str.strip(), errors='coerce')
        
        if vol_col:
            df[vol_col] = pd.to_numeric(df[vol_col], errors='coerce')
        if del_qty_col:
            df[del_qty_col] = pd.to_numeric(df[del_qty_col], errors='coerce')
        else:
            if vol_col:
                df['DELIV_QTY'] = (df[vol_col] * df[del_col]) / 100
                del_qty_col = 'DELIV_QTY'
                
        # Delivery Value in Crores
        if del_qty_col:
            df['DELIVERY_VALUE_CR'] = (df[del_qty_col] * df[close_col]) / 10000000
        else:
            df['DELIVERY_VALUE_CR'] = 0.0
            
        df['PRICE_CHG_PCT'] = ((df[close_col] - df[prev_close_col]) / df[prev_close_col]) * 100
        
        # માત્ર સાચા ઇક્વિટી (EQ) સ્ટોક્સ ફિલ્ટર કરવા
        if series_col:
            df = df[df[series_col].astype(str).str.strip().str.upper().isin(['EQ', 'BE', 'NIFTY50'])]
            
        df = df.dropna(subset=['PRICE_CHG_PCT', del_col, close_col])
        
        # 🧠 કમ્બાઈન્ડ સુપર એડવાન્સ લોજિક (સિગ્નલો)
        def get_ultimate_signals(row):
            p_chg = row['PRICE_CHG_PCT']
            d_per = row[del_col]
            
            if p_chg >= 4.0 and d_per >= 60.0:
                return "🔥 BREAKOUT CANDIDATE (મોટો બ્રેકઆઉટ)"
            elif p_chg >= 2.0 and d_per >= 60.0:
                return "⭐ JACKPOT RADAR (બ્લાસ્ટ માટે તૈયાર)"
            elif p_chg > 0 and d_per >= 45.0:
                return "🟢 Long Buildup (મજબૂત તેજી)"
            elif p_chg < 0 and d_per >= 45.0:
                return "🔴 Short Buildup (મોટી મંદી)"
            elif p_chg > 0 and d_per < 20.0:
                return "⚠️ Short Covering Trap (નબળી તેજી)"
            elif p_chg > 0 and d_per < 45.0:
                return "🟡 Short Covering (સામાન્ય રિકવરી)"
            else:
                return "⚪ Normal Action / Profit Booking"

        df['SIGNAL_ALERTS'] = df.apply(get_ultimate_signals, axis=1)

        # 🔍 સેક્શન ૧: મલ્ટી-ડે સ્ટોક સ્માર્ટ સર્ચ હિસ્ટ્રી ટ્રેકર + એડવાન્સ ડ્યુઅલ ચાર્ટ
        st.subheader("🔍 સ્ટોક સ્માર્ટ સર્ચ (Multi-Day History Tracker & Interactive Chart)")
        search_query = st.text_input("કોઈપણ શેરનું નામ લખો (દા.ત. RELIANCE, TCS) અને જુઓ મલ્ટી-ડે ટ્રેન્ડ હિસ્ટ્રી:").strip().upper()
        if search_query:
            s_res = df[df[sym_col].astype(str).str.contains(search_query, na=False)].sort_values(by='DATE_OBJ')
            if not s_res.empty:
                st.success(f"📌 '{search_query}' નો દિવસ વાઇઝ હિસ્ટોરિકલ રિપોર્ટ:")
                
                st.dataframe(s_res[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].rename(columns={
                    sym_col: 'STOCK', close_col: 'PRICE', 'PRICE_CHG_PCT': 'CHANGE_%', del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_(CR)', 'FILE_NAME': 'DATE'
                }).round(2), use_container_width=True)
                
                fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
                fig_dual.add_trace(go.Scatter(x=s_res['FILE_NAME'], y=s_res[close_col], name="Close Price (ભાવ)", mode='lines+markers', line=dict(color='#FF4B4B', width=3)), secondary_y=False)
                fig_dual.add_trace(go.Bar(x=s_res['FILE_NAME'], y=s_res[del_col], name="Delivery %", opacity=0.3, marker_color='#00CC96'), secondary_y=True)
                
                fig_dual.update_layout(title_text=f"📈 {search_query} : ભાવ (Line) અને ડિલિવરી % (Bar) નો મલ્ટી-ડે ટ્રેન્ડ", hovermode="x unified")
                fig_dual.update_yaxes(title_text="Stock Price (₹)", secondary_y=False)
                fig_dual.update_yaxes(title_text="Delivery Percentage (%)", secondary_y=True)
                st.plotly_chart(fig_dual, use_container_width=True)
            else:
                st.error("આ નામનો કોઈ સ્ટોક મળ્યો નથી.")

        # 📊 સેક્શન ૨: ઓવરઓલ માર્કેટ સેન્ટિમેન્ટ
        st.markdown("---")
        st.subheader("📊 ઓવરઓલ માર્કેટ સેન્ટિમેન્ટ (Market Mood - All Combined Days)")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            counts = df['SIGNAL_ALERTS'].value_counts().reset_index()
            counts.columns = ['SIGNAL', 'COUNT']
            fig_pie = px.pie(counts, values='COUNT', names='SIGNAL', 
                             color='SIGNAL',
                             color_discrete_map={
                                 "🔥 BREAKOUT CANDIDATE (મોટો બ્રેકઆઉટ)": "#FF4B4B",
                                 "⭐ JACKPOT RADAR (બ્લાસ્ટ માટે તૈયાર)": "#FF1493",
                                 "🟢 Long Buildup (મજબૂત તેજી)": "#00CC96",
                                 "🔴 Short Buildup (મોટી મંદી)": "#EF553B",
                                 "⚠️ Short Covering Trap (નબળી તેજી)": "#FECB52",
                                 "🟡 Short Covering (સામાન્ય રિકવરી)": "#FFA500",
                                 "⚪ Normal Action / Profit Booking": "#AB63FA"
                             }, title="માર્કેટ પોઝિશન્સ પાઇ ચાર્ટ")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            special_alerts = ["🔥 BREAKOUT CANDIDATE (મોટો બ્રેકઆઉટ)", "⭐ JACKPOT RADAR (બ્લાસ્ટ માટે તૈયાર)"]
            jackpot_df = df[df['SIGNAL_ALERTS'].isin(special_alerts)].sort_values(by=['DATE_OBJ', 'DELIVERY_VALUE_CR'], ascending=[False, False])
            
            st.markdown("### 🔥 જેકપોટ અને બ્રેકઆઉટ રાડાર સ્ટોક્સ (High Conviction Radar)")
            if not jackpot_df.empty:
                st.dataframe(jackpot_df[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'CLOSE_PRICE', 'PRICE_CHG_PCT': 'CHANGE_%', del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_(CR)', 'SIGNAL_ALERTS': 'SIGNAL', 'FILE_NAME': 'DATE'
                }).round(2), use_container_width=True)
            else:
                st.warning("પસંદ કરેલા દિવસોમાં કોઈ સ્ટોક જેકપોટ કે બ્રેકઆઉટ કન્ડિશનમાં મેચ થયો નથી.")

        # 🎯 સેક્શન ૩: પ્રોફેશનલ મલ્ટી-ટેબ સિસ્ટમ (તમારી માંગણી મુજબ નવું મોટું SMA Scanner ટેબ ઉમેરેલ છે)
        st.markdown("---")
        tab1, tab2, tab3, tab4, tab6, tab7, tab8, tab5 = st.tabs([
            "🎯 ફિલ્ટર કરેલા બેસ્ટ સ્ટોક્સ", 
            "📊 મલ્ટી-ડે ક્યુમ્યુલેટિવ સમરી", 
            "📈 વોલ્યુમ શૉકર્સ (Volume Activity)", 
            "💎 ઇન્સ્ટિટ્યુશનલ એક્યુમ્યુલેશન રાડાર",
            "⚡ Price-Volume Action Matrix",
            "🎯 Swing Trading Scanner",
            "📈 SMA Crossover Scanner (New)", # નવું મુખ્ય ટૅબ
            "💡 પ્રોફેશનલ ટ્રેડિંગ ગાઈડ"
        ])
        
        with tab1:
            final_filtered = df[(df['PRICE_CHG_PCT'] >= u_gain) & (df[del_col] >= u_del) & (df['DELIVERY_VALUE_CR'] >= u_min_val)].sort_values(by='DELIVERY_VALUE_CR', ascending=False)
            st.subheader(f"🎯 સ્માર્ટ મની ફિલ્ટર લિસ્ટ (ડિલિવરી > {u_del}%, તેજી > {u_gain}% અને વેલ્યુ > {u_min_val} Cr)")
            
            st.markdown("#### 📦 Consolidation Breakout Alerts")
            unique_dates = df['FILE_NAME'].unique()
            if len(unique_dates) >= 3:
                grouped_prices = df.groupby(sym_col).agg(
                    MIN_PRICE=(close_col, 'min'),
                    MAX_PRICE=(close_col, 'max'),
                    LATEST_PRICE=(close_col, 'last'),
                    LATEST_CHG=('PRICE_CHG_PCT', 'last'),
                    LATEST_DEL=(del_col, 'last')
                ).reset_index()
                
                grouped_prices['RANGE_PCT'] = ((grouped_prices['MAX_PRICE'] - grouped_prices['MIN_PRICE']) / grouped_prices['MIN_PRICE']) * 100
                
                consolidation_breakouts = grouped_prices[
                    (grouped_prices['RANGE_PCT'] <= 4.0) & 
                    (grouped_prices['LATEST_CHG'] >= 2.0) & 
                    (grouped_prices['LATEST_DEL'] >= 50.0)
                ].sort_values(by='LATEST_CHG', ascending=False)
                
                if not consolidation_breakouts.empty:
                    st.success("🚀 નીચેના સ્ટોક્સ છેલ્લા કેટલાક દિવસોથી એક સાંકડી રેન્જમાં હતા અને આજે ભારે વોલ્યુમ/ડિલિવરી સાથે બ્રેકઆઉટ આપ્યો છે!")
                    st.dataframe(consolidation_breakouts.rename(columns={
                        sym_col: 'STOCK_NAME', 'MIN_PRICE': 'MIN_PRICE_ZONE', 'MAX_PRICE': 'MAX_PRICE_ZONE',
                        'LATEST_PRICE': 'CURRENT_PRICE', 'LATEST_CHG': 'TODAY_GAIN_%', 'LATEST_DEL': 'TODAY_DELIVERY_%', 'RANGE_PCT': 'CONSOLIDATION_RANGE_%'
                    }).round(2), use_container_width=True)
                else:
                    st.info("अત્યારે સાંકડી રેન્જમાંથી બહાર નીકળતો કોઈ બ્રેકઆઉટ સ્ટોક મળ્યો નથી.")
            else:
                st.info("ℹ️ Consolidation Breakout ગણવા માટે મિનિમમ ૩ કે તેથી વધુ દિવસનો ડેટા ફેચ કરો.")
            st.markdown("---")

            if not final_filtered.empty:
                disp_df = final_filtered[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'SIGNAL_ALERTS', 'FILE_NAME']].rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'PRICE', 'PRICE_CHG_PCT': 'CHANGE_%', del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_(CR)', 'SIGNAL_ALERTS': 'MARKET_ACTION', 'FILE_NAME': 'DATE'
                }).round(2)
                
                csv = disp_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 આ ફિલ્ટર કરેલો મલ્ટી-ડે ડેટા Excel/CSV તરીકે ડાઉનલોડ કરો", csv, "Ultimate_Smart_Money_Data.csv", "text/csv")
                
                st.dataframe(disp_df.style.background_gradient(subset=['DELIV_VALUE_(CR)'], cmap='YlGnBu').format(subset=['PRICE', 'CHANGE_%', 'DELIVERY_%', 'DELIV_VALUE_(CR)'], formatter="{:.2f}"), use_container_width=True)
                
                fig_bar = px.bar(disp_df.head(20), x='STOCK_NAME', y='DELIV_VALUE_(CR)', color='CHANGE_%',
                                 color_continuous_scale='Turbo', title="ટોપ ૨૦ હાઇ ડિલિવરી વેલ્યુ સ્ટોક્સ (₹ કરોડમાં)")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("આ ફિલ્ટર શરતો મુજબ કોઈ સ્ટોક્સ નથી. સાઇડબાર સ્લાઇડર્સ થોડા ઓછા કરો.")
                
        with tab2:
            st.subheader("📊 છેલ્લા બધા જ દિવસોનો ભેગો (Cumulative) નીચોડ રિપોર્ટ")
            
            agg_dict = {
                close_col: 'last', 
                'PRICE_CHG_PCT': 'sum', 
                del_col: 'mean',
                'DELIVERY_VALUE_CR': 'sum'
            }
            if vol_col:
                agg_dict[vol_col] = 'sum'
                
            summary_df = df.groupby(sym_col).agg(agg_dict).reset_index()
            
            renamed_summary = summary_df.rename(columns={
                sym_col: 'STOCK_NAME', close_col: 'LAST_PRICE', 
                'PRICE_CHG_PCT': 'TOTAL_GAIN_%', del_col: 'AVG_DELIVERY_%',
                'DELIVERY_VALUE_CR': 'CUMULATIVE_DELIV_VALUE_CR'
            })
            if vol_col:
                renamed_summary = renamed_summary.rename(columns={vol_col: 'TOTAL_VOLUME'})
                
            renamed_summary = renamed_summary[renamed_summary['AVG_DELIVERY_%'] >= u_del].sort_values(by='CUMULATIVE_DELIV_VALUE_CR', ascending=False)
            
            csv_summary = renamed_summary.to_csv(index=False).encode('utf-8')
            st.download_button("📥 ક્યુમ્યુલેટિવ રિપોર્ટ Excel તરીકે ડાઉનલોડ કરો", csv_summary, "Cumulative_Market_Summary.csv", "text/csv")
            st.dataframe(renamed_summary.style.bar(subset=['AVG_DELIVERY_%'], color='#636EFA').format(subset=['LAST_PRICE', 'TOTAL_GAIN_%', 'AVG_DELIVERY_%', 'CUMULATIVE_DELIV_VALUE_CR'], formatter="{:.2f}"), use_container_width=True)

        with tab3:
            if vol_col and not df.empty:
                st.subheader("📈 અસાધારણ વોલ્યુમ એનાલિસિસ રાડાર (Volume Activity)")
                st.markdown("### 📊 ટોપ ટ્રેડેડ વોલ્યુમ સ્ટોક્સ (તમારું જૂનું માર્કેટ લોજિક)")
                high_vol_df_old = df.sort_values(by=['DATE_OBJ', vol_col], ascending=[False, False]).head(20).copy()
                high_vol_df_old = high_vol_df_old.rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'CLOSE_PRICE', 'PRICE_CHG_PCT': 'PRICE_CHANGE_%', 
                    del_col: 'DELIVERY_%', vol_col: 'TOTAL_VOLUME', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_CR', 'FILE_NAME': 'DATE'
                })
                st.dataframe(high_vol_df_old[['STOCK_NAME', 'CLOSE_PRICE', 'PRICE_CHANGE_%', 'DELIVERY_%', 'DELIV_VALUE_CR', 'TOTAL_VOLUME', 'SIGNAL_ALERTS', 'DATE']].round(2), use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 🚀 અચાનક વોલ્યુમમાં ઉછાળો આવ્યો હોય તેવા સ્ટોક્સ (Volume Multiplier)")
                avg_vol_df = df.groupby(sym_col)[vol_col].mean().reset_index().rename(columns={vol_col: 'AVG_VOLUME'})
                latest_file_name = df['FILE_NAME'].max()
                latest_day_df = df[df['FILE_NAME'] == latest_file_name].copy()
                
                shocker_df = pd.merge(latest_day_df, avg_vol_df, on=sym_col)
                shocker_df['VOLUME_SHOCK_MULTIPLIER'] = shocker_df[vol_col] / shocker_df['AVG_VOLUME']
                
                high_vol_df_new = shocker_df.sort_values(by='VOLUME_SHOCK_MULTIPLIER', ascending=False).head(20)
                
                disp_shocker = high_vol_df_new[[sym_col, close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR', 'VOLUME_SHOCK_MULTIPLIER', 'FILE_NAME']].rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'CLOSE_PRICE', 'PRICE_CHG_PCT': 'PRICE_CHANGE_%', 
                    del_col: 'DELIVERY_%', 'DELIVERY_VALUE_CR': 'DELIV_VALUE_CR', 'FILE_NAME': 'DATE'
                })
                st.dataframe(disp_shocker.style.bar(subset=['VOLUME_SHOCK_MULTIPLIER'], color='#FFA500').format(subset=['CLOSE_PRICE', 'PRICE_CHANGE_%', 'DELIVERY_%', 'DELIV_VALUE_CR', 'VOLUME_SHOCK_MULTIPLIER'], formatter="{:.2f}"), use_container_width=True)
            else:
                st.info("વોલ્યુમ ડેટા ઉપલબ્ધ નથી અથવા ફાઇલ સપોર્ટેડ નથી.")
                
        with tab4:
            st.subheader("💎 ઇન્સ્ટિટ્યુશનલ કંટીન્યુઅસ એક્યુમ્યુલેશન રાડાર")
            high_del_days = df[df[del_col] >= 50.0]
            accumulation_count = high_del_days.groupby(sym_col)['FILE_NAME'].count().reset_index().rename(columns={'FILE_NAME': 'STRONG_DELIVERY_DAYS'})
            mega_accumulated = accumulation_count[accumulation_count['STRONG_DELIVERY_DAYS'] >= 3].sort_values(by='STRONG_DELIVERY_DAYS', ascending=False)
            
            if not mega_accumulated.empty:
                latest_dates = df.groupby(sym_col)['FILE_NAME'].max().reset_index()
                latest_info = pd.merge(df, latest_dates, on=[sym_col, 'FILE_NAME'])
                final_accum_df = pd.merge(mega_accumulated, latest_info, on=sym_col)
                
                disp_accum = final_accum_df[[sym_col, 'STRONG_DELIVERY_DAYS', close_col, 'PRICE_CHG_PCT', del_col, 'DELIVERY_VALUE_CR']].rename(columns={
                    sym_col: 'STOCK_NAME', close_col: 'LATEST_PRICE', 'PRICE_CHG_PCT': 'LATEST_CHANGE_%', del_col: 'LATEST_DELIVERY_%', 'DELIVERY_VALUE_CR': 'LATEST_VALUE_(CR)'
                }).round(2)
                st.dataframe(disp_accum.style.background_gradient(subset=['STRONG_DELIVERY_DAYS'], cmap='Greens'), use_container_width=True)
            else:
                st.info("સળંગ ૩ કે તેથી વધુ દિવસ ૫૦% થી વધુ ડિલિવરી ધરાવતો કોઈ શેર મળ્યો નથી. ડેટાના દિવસો (Slider) વધારો.")

        with tab6:
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

        with tab7:
            st.subheader("🎯 Swing Trading Scanner (Smart Accumulation on Dips)")
            unique_dates_sorted = sorted(df['FILE_NAME'].unique(), key=lambda x: datetime.strptime(x, '%d-%m-%Y') if '-' in x else x)
            
            if len(unique_dates_sorted) >= 3:
                d3, d2, d1 = unique_dates_sorted[-3], unique_dates_sorted[-2], unique_dates_sorted[-1]
                
                df_d3 = df[df['FILE_NAME'] == d3][[sym_col, close_col, del_col]].rename(columns={close_col: 'P3', del_col: 'D3'})
                df_d2 = df[df['FILE_NAME'] == d2][[sym_col, close_col, del_col]].rename(columns={close_col: 'P2', del_col: 'D2'})
                df_d1 = df[df['FILE_NAME'] == d1][[sym_col, close_col, del_col]].rename(columns={close_col: 'P1', del_col: 'D1'})
                
                swing_merge = pd.merge(df_d1, df_d2, on=sym_col)
                swing_merge = pd.merge(swing_merge, df_d3, on=sym_col)
                
                swing_candidates = swing_merge[
                    (swing_merge['P3'] > swing_merge['P2']) & (swing_merge['P2'] > swing_merge['P1']) &
                    (swing_merge['D1'] > swing_merge['D2']) & (swing_merge['D2'] > swing_merge['D3']) &
                    (swing_merge['D1'] >= 45.0)
                ]
                
                if not swing_candidates.empty:
                    st.success("💎 **Buy on Dips Radar Detected!** નીચેના સ્ટોક્સમાં કિંમત ઘટી રહી છે પણ ડિલિવરી વોલ્યુમ સતત વધી રહ્યું છે.")
                    st.dataframe(swing_candidates.rename(columns={
                        sym_col: 'STOCK_NAME', 'P1': 'LATEST_PRICE', 'P2': 'YESTERDAY_PRICE', 'P3': 'DAY_BEFORE_PRICE',
                        'D1': 'LATEST_DELIVERY_%', 'D2': 'YESTERDAY_DEL_%', 'D3': 'DAY_BEFORE_DEL_%'
                    }).round(2), use_container_width=True)
                else:
                    st.info("અત્યારે શરતો મુજબ 'Price Down, Delivery Up' વાળો કોઈ પણ છુપો સ્ટોક મળ્યો નથી.")
            else:
                st.info("ℹ专 સ્વીંગ ટ્રેડિંગ સ્કેનર ચલાવવા માટે મિનિમમ ૩ કે તેથી વધુ દિવસનો ડેટા સેટ કરો.")

        # 🆕 📈 નવું એડવાન્સ ટેબ ૮: SMA Crossover Scanner (તમારા ૬ નવા ટેબલ અહીં છે)
        with tab8:
            st.subheader("📈 Daily Timeframe SMA Crossover Terminal")
            st.write("આ સેક્શન ક્લોઝિંગ પ્રાઈઝ અને અગાઉના દિવસના ડેટાના આધારે કરંટ લાઈવ ક્રોસઓવર્સ ટ્રેક કરે છે. સચોટ પરિણામ માટે ડાબી બાજુ સાઇડબારમાંથી દિવસોની સંખ્યા (Days Filter) વધારીને ૧૦ થી ૩૦ દિવસ સેટ કરો.")
            
            # દરેક સ્ટોક માટે રોલિંગ SMA ની ગણતરી કરવી
            df['SMA_9'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=9).mean())
            df['SMA_21'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=21).mean())
            df['SMA_50'] = df.groupby(sym_col)[close_col].transform(lambda x: x.rolling(window=50).mean())
            
            # ગઈકાલના (Previous Day) ડેટા માટે શિફ્ટ વેલ્યુ મેળવવી
            df['PREV_CLOSE_LIVE'] = df.groupby(sym_col)[close_col].shift(1)
            df['PREV_SMA_9'] = df.groupby(sym_col)['SMA_9'].shift(1)
            df['PREV_SMA_21'] = df.groupby(sym_col)['SMA_21'].shift(1)
            df['PREV_SMA_50'] = df.groupby(sym_col)['SMA_50'].shift(1)
            
            # માત્ર સૌથી લેટેસ્ટ દિવસનો ડેટા ક્રોસઓવર જોવા માટે અલગ તારવવો
            latest_date_s = df['DATE_OBJ'].max()
            sma_latest_df = df[df['DATE_OBJ'] == latest_date_s].copy()
            
            # કોમન ડિસ્પ્લે ફંક્શન ટેબલ ફોર્મેટિંગ સુધારે છે
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

            # અંદરના પેટા-ભાગો માટે એકોર્ડિયન અથવા અલગ સેક્શન
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🔹 SMA 9 Filters", "🔹 SMA 21 Filters", "🔹 SMA 50 Filters"])
            
            with sub_tab1:
                col_b1, col_r1 = st.columns(2)
                with col_b1:
                    # SMA 9: નીચેથી ઉપર Bullish (ગઈકાલે પ્રાઈઝ SMA9 ની નીચે હતી, આજે ઉપર આવી ગઈ)
                    bullish_9 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_9']) & (sma_latest_df[close_col] > sma_latest_df['SMA_9'])]
                    display_sma_table(bullish_9, "🟢 SMA 9: નીચેથી ઉપર (Bullish Crossover)", True)
                with col_r1:
                    # SMA 9: ઉપરથી નીચે Bearish (ગઈકાલે પ્રાઈઝ SMA9 ની ઉપર હતી, આજે નીચે આવી ગઈ)
                    bearish_9 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_9']) & (sma_latest_df[close_col] < sma_latest_df['SMA_9'])]
                    display_sma_table(bearish_9, "🔴 SMA 9: ઉપરથી નીચે (Bearish Crossover)", False)
                    
            with sub_tab2:
                col_b2, col_r2 = st.columns(2)
                with col_b2:
                    # SMA 21: નીચેથી ઉપર Bullish
                    bullish_21 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_21']) & (sma_latest_df[close_col] > sma_latest_df['SMA_21'])]
                    display_sma_table(bullish_21, "🟢 SMA 21: નીચેથી ઉપર (Bullish Crossover)", True)
                with col_r2:
                    # SMA 21: ઉપરથી નીચે Bearish
                    bearish_21 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_21']) & (sma_latest_df[close_col] < sma_latest_df['SMA_21'])]
                    display_sma_table(bearish_21, "🔴 SMA 21: ઉપરથી નીચે (Bearish Crossover)", False)

            with sub_tab3:
                col_b3, col_r3 = st.columns(2)
                with col_b3:
                    # SMA 50: નીચેથી ઉપર Bullish
                    bullish_50 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] <= sma_latest_df['PREV_SMA_50']) & (sma_latest_df[close_col] > sma_latest_df['SMA_50'])]
                    display_sma_table(bullish_50, "🟢 SMA 50: નીચેથી ઉપર (Bullish Crossover)", True)
                with col_r3:
                    # SMA 50: ઉપરથી નીચે Bearish
                    bearish_50 = sma_latest_df[(sma_latest_df['PREV_CLOSE_LIVE'] >= sma_latest_df['PREV_SMA_50']) & (sma_latest_df[close_col] < sma_latest_df['SMA_50'])]
                    display_sma_table(bearish_50, "🔴 SMA 50: ઉપરથી નીચે (Bearish Crossover)", False)

        with tab5:
            st.success("🎯 **તમારું અલ્ટીમેટ સ્માર્ટ મની ઓટોમેશન ટર્મિનલ v3+ તૈયાર છે!**")
            st.info("💡 **પ્રોફેશનલ માર્કેટ એનાલિસિસ ટિપ:**")
            st.markdown("""
            * **SMA Crossover Scanner (નવું):** ટૂંકા ગાળાના ટ્રેન્ડ રિવર્સલ પકડવા માટે SMA 9 અને SMA 21 જુઓ. જો કોઈ શેર સિંગલ ડે માં જ શક્તિશાળી સંસ્થાકીય ડિલિવરી વોલ્યુમ સાથે **SMA 50 બ્રેકઆઉટ** આપે, તો મોટો ટ્રેન્ડ શરૂ થવાની પ્રબળ સંભાવના રહે છે.
            * **Consolidation Breakout:** જો કોઈ સ્ટોક ટેબ ૧ માં સાંકડી રેન્જમાંથી બહાર નીકળતો દેખાય, તો તેમાં મોટી મુવમેન્ટ આવવાની શક્યતા ખૂબ વધારે હોય છે.
            * **Price-Volume Action Matrix:** ટ્રેડિંગ કરતી વખતે હંમેશા **Pure Bullish ક્વાડ્રન્ટ** ના સ્ટોક્સ લોન્ગ પોઝિશન માટે અને **Aggressive Shorting ક્વાડ્રન્ટ** ના સ્ટોક્સ શોર્ટ સેલિંગ માટે વોચલિસ્ટમાં રાખવા.
            * **Swing Trading Scanner:** જ્યારે માર્કેટ પ્રોફિટ બુકિંગ કરતું હોય ત્યારે આ ટેબ વરદાન સાબિત થાય છે. અહીં એવા સ્ટોક્સ મળે છે જ્યાં રીટેલર્સ ગભરાઈને માલ વેચે છે અને મોટી સંસ્થાઓ નીચા ભાવે માલ એકઠો (Accumulate) કરે છે.
            """)
else:
    st.info("👋 શરૂ કરવા માટે ડાબી બાજુથી તારીખ અને દિવસો પસંદ કરીને '🚀 NSE માંથી મલ્ટી-ડે ડેટા મેળવો' બટન પર ક્લિક કરો અથવા મેન્યુઅલી ફાઇલો અપલોડ કરો.")