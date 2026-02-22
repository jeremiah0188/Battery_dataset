import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ================= 1. 获取 URL 参数 =================
try:
    admin_val = st.query_params.get("admin", "")
except:
    admin_val = st.experimental_get_query_params().get("admin", [""])[0]

is_jian_entry = (admin_val == "Jian")

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    layout="wide",
    initial_sidebar_state="expanded" if is_jian_entry else "collapsed"
)

# ================= 3. 核心视觉设计：渐变背景与玻璃拟态 CSS =================
# 这里融合了你提供的图片风格：温暖渐变、背景模糊、极细边框
glass_css = f"""
<style>
    /* 全局背景：温暖的渐变色 */
    .stApp {{
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%), 
                    linear-gradient(to top, #a18cd1 0%, #fbc2eb 100%);
        background-blend-mode: soft-light;
        background-attachment: fixed;
    }}

    /* 隐藏 Streamlit 默认装饰 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{background-color: rgba(0,0,0,0);}}
    #stDecoration {{display:none;}}

    /* 侧边栏样式（管理员模式） */
    section[data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* 玻璃卡片通用类 */
    .glass-card {{
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }}

    /* 标签页导航样式（Linear 风格） */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 5px;
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        border-radius: 8px;
        background-color: transparent;
        transition: all 0.3s;
        color: #444;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}

    /* 标题排版：Linear/Apple 风格 */
    h1 {{
        font-family: 'Inter', -apple-system, sans-serif;
        font-weight: 800;
        color: #2D3436;
        letter-spacing: -1.5px;
    }}

    /* 玻璃按钮样式 */
    .stButton>button {{
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        color: #333 !important;
        transition: 0.3s all;
    }}
    .stButton>button:hover {{
        background: rgba(255, 255, 255, 0.6) !important;
        transform: translateY(-2px);
    }}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

if not is_jian_entry:
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none;}</style>",
                unsafe_allow_html=True)

# ================= 4. 🔗 Google Sheets 数据库配置 =================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL)
        df = df.dropna(how='all').astype(str).replace('nan', '')
        if 'Status' not in df.columns: df['Status'] = 'Approved'
        return df
    except:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Battery Type', 'Capacity (Ah)', 'Status'])


df = load_data()

# ================= 5. 管理员身份验证 =================
is_admin = False
if is_jian_entry:
    with st.sidebar:
        st.markdown("### 👨‍💻 Jian's Space")
        target_password = st.secrets.get("admin_password", "")
        admin_pw = st.text_input("Security Key", type="password")
        if admin_pw == target_password and target_password != "":
            is_admin = True
            st.success("Authorized")

# ================= 6. UI: Hero Section (基于预览图设计) =================
# 在主页面最上方展示 Hero 区域，只有首页（浏览页）才显示更明显的视觉引导
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col_hero, col_img = st.columns([1.5, 1])

with col_hero:
    st.title("The Open Battery Dataset")
    st.markdown("""
    A decentralized, glass-transparent repository for global battery research.  
    *Organize, review, and download high-fidelity data with precision.*
    """)
    # 动态统计数据
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.metric("Datasets", len(df[df['Status'] == 'Approved']))
    c2.metric("Pending", len(df[df['Status'] == 'Pending']))
    c3.metric("Type", "Open Source")
st.markdown('</div>', unsafe_allow_html=True)

# ================= 7. Tabs 内容 =================
if is_admin:
    tabs = st.tabs(["📚 Browse Library", "☁️ Contribute Data", "⚙️ Control Panel"])
else:
    tabs = st.tabs(["📚 Browse Library", "☁️ Contribute Data"])

# --- TAB 1: Browse Datasets ---
with tabs[0]:
    st.header("Library Index")
    public_df = df[df['Status'] == 'Approved']

    # 极简搜索栏
    search_query = st.text_input("🔍 Search by Author, Battery Type, or Keyword",
                                 placeholder="Try 'Cylindrical' or 'Pouch'...")

    if search_query:
        mask = public_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        display_df = public_df[mask]
    else:
        display_df = public_df

    # 玻璃化数据表格
    st.markdown('<div style="background: rgba(255,255,255,0.1); border-radius:15px; padding:10px;">',
                unsafe_allow_html=True)
    st.dataframe(display_df[['Dataset Name', 'Author', 'Battery Type', 'Capacity (Ah)']], use_container_width=True,
                 hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 详情选择器
    selected_name = st.selectbox("View full metadata for:", ["(Select Dataset)"] + display_df['Dataset Name'].tolist())
    if selected_name != "(Select Dataset)":
        details = display_df[display_df['Dataset Name'] == selected_name].iloc[0]
        st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"📖 {selected_name}")

        link = details.get('Link', '')
        if link.startswith('http'):
            st.link_button("🔗 Access Source / Download", link, use_container_width=True)

        st.markdown("#### Metadata Matrix")
        col_m1, col_m2 = st.columns(2)
        all_cols = [c for c in df.columns if c not in ['Link', 'Status']]
        for i, c in enumerate(all_cols):
            val = details.get(c, 'N/A')
            if i % 2 == 0:
                col_m1.write(f"**{c}**: `{val}`")
            else:
                col_m2.write(f"**{c}**: `{val}`")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: Upload Dataset ---
with tabs[1]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Contribute to the Matrix")
    st.write("Your contribution will be verified by the core admin team before going live.")

    with st.form("upload_form", border=False):
        f1, f2 = st.columns(2)
        new_name = f1.text_input("Dataset Title *")
        new_author = f2.text_input("Lead Author / Lab")
        new_link = st.text_input("External URL (Zenodo, GitHub, etc.)")
        new_battery = st.selectbox("Form Factor", ["Cylindrical", "Pouch", "Prismatic", "Coin cell", "Other"])
        new_notes = st.text_area("Research Summary")

        submitted = st.form_submit_button("📤 Submit Metadata")

        if submitted:
            if not new_name:
                st.error("Title is required")
            else:
                new_row = {c: "" for c in df.columns}
                new_row.update(
                    {'Dataset Name': new_name, 'Author': new_author, 'Link': new_link, 'Battery Type': new_battery,
                     'Status': 'Pending'})
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success("Successfully pushed to queue.")
                st.cache_data.clear()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: Admin Dashboard ---
if is_admin:
    with tabs[2]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.header("Control Terminal")
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                use_container_width=True, num_rows="dynamic"
            )
            if st.form_submit_button("💾 Synchronize Changes"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Cloud Synchronized")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)