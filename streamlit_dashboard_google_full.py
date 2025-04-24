
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Circle Condo Dashboard", layout="wide")

st.title("📊 รายงานความเสียหายจากเหตุแผ่นดินไหว")
st.markdown("ข้อมูลจากแบบสอบถาม Google Sheets + แผนซ่อมจากการประชุม")

# Load Google Sheet as CSV
sheet_id = "1Chr7GsJxl99sK9-9vW0ZM-t6xbphTLiUYn36v_HpHPI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
except Exception as e:
    st.error(f"โหลดข้อมูลจาก Google Sheets ไม่สำเร็จ: {e}")
    st.stop()

# Extract key columns
room_col = [col for col in df.columns if "Room No" in col][0]
damage_col = [col for col in df.columns if "ลักษณะของความเสียหาย" in col][0]
image_col = [col for col in df.columns if "รูปภาพ" in col or "Picture" in col][-1]

# Clean and expand data
df_filtered = df[[room_col, damage_col, image_col]].dropna(subset=[room_col, damage_col])
df_filtered['Damage Types'] = df_filtered[damage_col].str.split(',')
df_filtered = df_filtered.explode('Damage Types')
df_filtered['Damage Types'] = df_filtered['Damage Types'].str.strip()

# Summary
freq = df_filtered['Damage Types'].value_counts().reset_index()
freq.columns = ['ประเภทความเสียหาย', 'จำนวนที่พบ']

room_group = df_filtered.groupby(room_col)['Damage Types'].count().reset_index()
room_group.columns = ['หมายเลขห้อง', 'จำนวนความเสียหาย']
room_top = room_group.sort_values(by='จำนวนความเสียหาย', ascending=False).head(10)

# --- Tabs ---
tab1, tab2 = st.tabs(["📋 วิเคราะห์จากแบบสอบถาม", "📆 แผนดำเนินการ"])

with tab1:
    damage_types = sorted(df_filtered['Damage Types'].dropna().unique())
    selected = st.multiselect("เลือกประเภทความเสียหาย", damage_types, default=damage_types)

    df_view = df_filtered[df_filtered['Damage Types'].isin(selected)]

    st.markdown("### 🔎 สรุปประเภทความเสียหาย")
    fig = px.bar(freq[freq['ประเภทความเสียหาย'].isin(selected)],
                 x='จำนวนที่พบ', y='ประเภทความเสียหาย', orientation='h')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏠 ห้องที่พบความเสียหายมากที่สุด")
    st.dataframe(room_top, use_container_width=True)

    st.markdown("### 📸 ความเสียหายพร้อมภาพประกอบ")
    def make_link(url):
        if pd.notnull(url) and str(url).startswith("http"):
            return f'<a href="{url}" target="_blank">ดูภาพ</a>'
        return ''
    df_view['ดูภาพ'] = df_view[image_col].apply(make_link)
    st.write(df_view[[room_col, 'Damage Types', 'ดูภาพ']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.markdown("### 🗓️ แผนดำเนินการซ่อมแซมจากการประชุม")
    try:
        with open("meeting_plan_gantt_updated.html", "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600, scrolling=True)
    except FileNotFoundError:
        st.warning("ไม่พบไฟล์ Gantt Chart: กรุณาวาง 'meeting_plan_gantt_updated.html' ไว้ในโฟลเดอร์เดียวกัน")
