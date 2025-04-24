
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Circle Condo Dashboard", layout="wide")

st.title("📊 รายงานความเสียหายจากเหตุแผ่นดินไหว")
st.markdown("ข้อมูลจากแบบสอบถาม Google Sheets + แผนซ่อมจากการประชุม")

sheet_id = "1Chr7GsJxl99sK9-9vW0ZM-t6xbphTLiUYn36v_HpHPI"
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

st.markdown("## 🔗 สถานะการเชื่อมต่อ Google Sheet")
try:
    df = pd.read_csv(sheet_url, nrows=1)
    st.success("✅ เชื่อมต่อ Google Sheet สำเร็จ")
except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
    st.stop()

df = pd.read_csv(sheet_url)
room_col = [col for col in df.columns if "Room No" in col][0]
damage_col = [col for col in df.columns if "ลักษณะของความเสียหาย" in col][0]
image_col = [col for col in df.columns if "รูปภาพ" in col or "Picture" in col][-1]

df_filtered = df[[room_col, damage_col, image_col]].dropna(subset=[room_col, damage_col])
df_filtered['Damage Types'] = df_filtered[damage_col].str.split(',')
df_filtered = df_filtered.explode('Damage Types')
df_filtered['Damage Types'] = df_filtered['Damage Types'].str.strip()

freq = df_filtered['Damage Types'].value_counts().reset_index()
freq.columns = ['ประเภทความเสียหาย', 'จำนวนที่พบ']

room_group = df_filtered.groupby(room_col)['Damage Types'].count().reset_index()
room_group.columns = ['หมายเลขห้อง', 'จำนวนความเสียหาย']
room_top = room_group.sort_values(by='จำนวนความเสียหาย', ascending=False).head(10)

tab1, tab2, tab3 = st.tabs([
    "📋 วิเคราะห์จากแบบสอบถาม", 
    "📆 แผนดำเนินการ", 
    "📘 คู่มือการใช้งาน"
])

with tab1:
    st.markdown("### 🔍 ค้นหาเลขห้อง")
    search_query = st.text_input("🔎 ใส่หมายเลขห้องที่ต้องการค้นหา (บางส่วนหรือทั้งหมด)")
    if search_query:
        df_filtered_display = df_filtered[df_filtered[room_col].astype(str).str.contains(search_query)]
    else:
        df_filtered_display = df_filtered.copy()

    damage_types = sorted(df_filtered_display['Damage Types'].dropna().unique())
    selected = st.multiselect("เลือกประเภทความเสียหาย", damage_types, default=damage_types)

    df_view = df_filtered_display[df_filtered_display['Damage Types'].isin(selected)]

    st.markdown("### 🔎 สรุปประเภทความเสียหาย")
    fig = px.bar(df_view['Damage Types'].value_counts().reset_index().rename(columns={'index': 'ประเภทความเสียหาย', 'Damage Types': 'จำนวนที่พบ'}),
                 x='จำนวนที่พบ', y='ประเภทความเสียหาย', orientation='h')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏠 ห้องที่พบความเสียหายมากที่สุด")
    top_rooms = df_view.groupby(room_col)['Damage Types'].count().reset_index().sort_values(by='Damage Types', ascending=False).head(10)
    top_rooms.columns = ['หมายเลขห้อง', 'จำนวนความเสียหาย']
    st.dataframe(top_rooms, use_container_width=True)

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

with tab3:
    st.markdown("## 🧾 คู่มือการ Deploy แดชบอร์ด Circle Condo")
    st.markdown("""
### 🔧 สิ่งที่ต้องเตรียม

1. ไฟล์หลัก:
   - `streamlit_dashboard_google_full.py`
   - `meeting_plan_gantt_updated.html`
   - `requirements.txt`
2. Google Sheet ที่เปิดสิทธิ์เป็น Viewer

---

### 🚀 วิธี Deploy บน Streamlit Cloud

1. ไปที่ [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. กด “Deploy an app”
3. เลือก GitHub repo ที่มีไฟล์ด้านบน
4. ตั้งค่า Main file: `streamlit_dashboard_google_full.py`
5. กด Deploy ✅ ได้ลิงก์ เช่น:
   `https://circle-dashboard.streamlit.app`

---

### 💡 ตัวอย่าง requirements.txt
```
streamlit
pandas
plotly
```

---

### 📦 การใช้งานแบบ Offline
```bash
streamlit run streamlit_dashboard_google_full.py
```
*ต้องวาง `meeting_plan_gantt_updated.html` ในโฟลเดอร์เดียวกัน*

---

### 📌 ข้อแนะนำเพิ่มเติม

- เก็บไฟล์ไว้ใน Google Drive หรือ USB สำรอง
- แชร์ลิงก์ผ่าน QR Code หรือ LINE OA
- ใช้คู่มือนี้ Deploy ใหม่ได้ทันที
""")

