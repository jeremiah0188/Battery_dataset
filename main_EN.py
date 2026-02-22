import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ================= 1. 获取 URL 参数 (最高优先级) =================
try:
    admin_val = st.query_params.get("admin", "")
except:
    admin_val = st.experimental_get_query_params().get("admin", [""])[0]

is_jian_entry = (admin_val == "Jian")

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded" if is_jian_entry else "collapsed"
)

# ================= 3. 深度定制 CSS (Linear x Apple Glassmorphism) =================
# 全局玻璃拟态与居中导航栏设计
glass_css = f"""
<style>
    /* 暖色渐变背景 */
    .stApp {{
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%), 
                    linear-gradient(to top, #a18cd1 0%, #fbc2eb 100%);
        background-blend-mode: soft-light;
        background-attachment: fixed;
    }}

    /* 隐藏顶部 GitHub、Share 和 Streamlit 菜单 */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #stDecoration {{display:none;}}

    /* 居中顶部导航栏 (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center; /* 核心：居中对齐 */
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 8px;
        gap: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        border-radius: 10px;
        background-color: transparent;
        color: #333;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #000;
    }}

    /* 玻璃卡片通用样式 */
    .glass-card {{
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15) !important;
    }}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

# 物理销毁普通用户的侧边栏
if not is_jian_entry:
    st.markdown(
        "<style>[data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}</style>",
        unsafe_allow_html=True)

# ================= 4. 🔗 Google Sheets 数据库配置 =================
# ⚠️⚠️⚠️ 必须修改：把下面这行换成你真实的 Google 表格网址！
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR): os.makedirs(UPLOAD_DIR)


@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL)
        df = df.dropna(how='all').astype(str).replace('nan', '')
        if 'Status' not in df.columns: df['Status'] = 'Approved'
        return df
    except:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain / Category', 'Status'])


df = load_data()

# ================= 5. 管理员身份验证 (仅限 Jian) =================
is_admin = False
if is_jian_entry:
    with st.sidebar:
        st.markdown("### 👨‍💻 Jian's Control Panel")
        target_password = st.secrets.get("admin_password", "")
        admin_pw = st.text_input("Enter Security Key", type="password")
        if admin_pw == target_password and target_password != "":
            is_admin = True
            st.success("Admin unlocked!")

# ================= 6. 顶部居中导航构建 =================
tab_names = ["🏠 Homepage", "📚 Browse Datasets", "☁️ Contribute Data", "ℹ️ About", "✉️ Contact"]
if is_admin:
    tab_names.append("⚙️ Admin Dashboard")

tabs = st.tabs(tab_names)

# ================= TAB 1: Homepage =================
with tabs[0]:
    st.markdown('<div class="glass-card" style="text-align: center; padding: 4rem 2rem;">', unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3rem; margin-bottom: 0;'>A Curated Hub for Public Research Datasets</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.2rem; color: #555; max-width: 800px; margin: 1rem auto;'>Explore, compare, and download public datasets with standardized metadata. Contribute new datasets to help the research community grow.</p>",
        unsafe_allow_html=True)

    # 模拟 CTA 按钮 (提示用户使用上方导航)
    st.info("👆 Use the navigation bar above to **Browse Datasets** or **Contribute Data**.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 核心统计与分类
    col1, col2, col3 = st.columns(3)
    public_count = len(df[df['Status'] == 'Approved'])
    with col1:
        st.markdown(
            f'<div class="glass-card" style="text-align:center;"><h3>{public_count}+</h3><p>Curated Datasets</p></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>🔋</h3><p>Battery & Time-Series</p></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>🌐</h3><p>Open Access</p></div>',
                    unsafe_allow_html=True)

# ================= TAB 2: Browse Datasets (分屏布局) =================
with tabs[1]:
    st.markdown("### Directory Header")
    st.write("Search and filter curated public datasets by domain, format, features, and research use cases.")

    public_df = df[df['Status'] == 'Approved']

    # 25% 过滤栏 | 75% 数据展示区
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        st.markdown('<div class="glass-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Filters")
        search_kw = st.text_input("Keyword Search")

        # 提取动态类别
        categories = ["All"] + list(
            public_df['Domain / Category'].unique()) if 'Domain / Category' in public_df.columns else ["All", "Battery",
                                                                                                       "Energy"]
        sel_cat = st.selectbox("Domain / Category", categories)

        sel_eis = st.checkbox("Contains EIS Data")
        sel_aging = st.checkbox("Contains Aging/Cycling")
        st.markdown('</div>', unsafe_allow_html=True)

    with result_col:
        # 执行过滤逻辑
        filtered_df = public_df.copy()
        if search_kw:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        if sel_cat != "All" and 'Domain / Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Domain / Category'] == sel_cat]

        st.markdown(f"**Result Counter:** {len(filtered_df)} datasets found.")

        if not filtered_df.empty:
            # 详情查看器 (Dataset Details)
            selected_dataset = st.selectbox("📖 View Dataset Details:",
                                            ["(Select to view)"] + filtered_df['Dataset Name'].tolist())

            if selected_dataset != "(Select to view)":
                details = filtered_df[filtered_df['Dataset Name'] == selected_dataset].iloc[0]
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(f"## {selected_dataset}")
                st.write(
                    f"**Source:** {details.get('Source Organization', details.get('Author', 'N/A'))} | **Last Updated:** System Tracked")

                link = details.get('Link', '')
                if link.startswith('http'):
                    st.link_button("🔗 Download / Visit Original Source", link)

                st.markdown("### Core Metadata")
                col_m1, col_m2 = st.columns(2)
                for i, c in enumerate(df.columns):
                    if c not in ['Link', 'Status', 'Dataset Name']:
                        val = details.get(c, 'N/A')
                        if str(val).strip() != '':
                            (col_m1 if i % 2 == 0 else col_m2).write(f"**{c}**: `{val}`")
                st.markdown('</div>', unsafe_allow_html=True)

            # 数据预览表
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            display_cols = [c for c in ['Dataset Name', 'Domain / Category', 'Author', 'Battery Chemistry'] if
                            c in filtered_df.columns]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ================= TAB 3: Contribute Data (全量表单) =================
with tabs[2]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("Contribute a Dataset")
    st.write(
        "Help expand this curated dataset hub by submitting a public dataset. Please provide standardized metadata to improve discoverability and reuse.")

    with st.form("upload_form", border=False):
        st.markdown("#### Section 1: Basic Information")
        c1, c2 = st.columns(2)
        new_name = c1.text_input("Dataset Name *")
        new_domain = c2.text_input("Domain / Category * (e.g., Battery, Energy)")
        new_desc = st.text_area("Short Description *")
        new_app = st.text_input("Application Area (e.g., SOH, RUL)")
        new_link = st.text_input("Source URL * (External Download Link)")
        new_org = st.text_input("Source Organization / Publisher")

        st.markdown("#### Section 2: Battery / Experiment Metadata (Optional)")
        c3, c4, c5 = st.columns(3)
        new_chem = c3.text_input("Battery Chemistry (e.g., LFP, NMC)")
        new_cell = c4.text_input("Cell / Module Type")
        new_temp = c5.text_input("Temperature Range (°C)")

        c6, c7 = st.columns(2)
        new_eis = c6.selectbox("Includes EIS Data?", ["No", "Yes"])
        new_aging = c7.selectbox("Includes Aging / Cycling Data?", ["No", "Yes"])

        st.markdown("#### Section 3: Contributor Information")
        c8, c9 = st.columns(2)
        new_contributor = c8.text_input("Contributor Name *")
        new_email = c9.text_input("Contact Email (Optional)")

        submitted = st.form_submit_button("📤 Submit to Moderation Queue")

        if submitted:
            if not new_name or not new_domain or not new_link or not new_contributor:
                st.error("Please fill in all required fields marked with *")
            else:
                new_row = {c: "" for c in df.columns}
                new_row.update({
                    'Dataset Name': new_name, 'Domain / Category': new_domain,
                    'Short Description': new_desc, 'Application Area': new_app,
                    'Link': new_link, 'Source Organization': new_org,
                    'Battery Chemistry': new_chem, 'Cell / Module Type': new_cell,
                    'Temperature Range': new_temp, 'Includes EIS Data': new_eis,
                    'Includes Aging / Cycling': new_aging, 'Author': new_contributor,
                    'Contributor Email': new_email, 'Status': 'Pending'
                })
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success(f"Success! Your dataset '{new_name}' has been placed in the moderation queue.")
                st.cache_data.clear()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 4: About =================
with tabs[3]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("About This Website")
    st.write(
        "This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.")

    st.header("Why This Platform Exists")
    st.write(
        "Many public datasets are difficult to compare due to inconsistent metadata, incomplete documentation, and scattered sources. This platform provides a structured and searchable interface to help users quickly evaluate dataset suitability.")

    st.header("About the Author")
    st.write(
        "This website is maintained by **Jian Wu**, a researcher working on battery data analysis, state-of-health (SOH) estimation, and dataset curation for data-driven modeling. The goal is to support reproducible research and easier access to high-quality public datasets.")

    st.header("Curation Principles")
    st.markdown(
        "- Metadata-first organization\n- Source transparency\n- Reproducibility support\n- Community contributions with moderation")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 5: Contact =================
with tabs[4]:
    st.markdown('<div class="glass-card" style="text-align: center; padding: 4rem;">', unsafe_allow_html=True)
    st.header("Contact & Support")
    st.write("For questions, dataset suggestions, collaboration, or corrections, please contact the maintainer.")
    st.markdown("### 📧 Email: [jian.wu@utbm.fr](mailto:jian.wu@utbm.fr)")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 6: Admin Dashboard (仅限 Jian) =================
if is_admin:
    with tabs[5]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.header("Moderation Queue & Admin Terminal")
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(
                df,
                column_config={"Status": st.column_config.SelectboxColumn("Status",
                                                                          options=["Approved", "Pending", "Rejected",
                                                                                   "Needs Revision"])},
                use_container_width=True, num_rows="dynamic"
            )
            if st.form_submit_button("💾 Synchronize Changes & Trigger Emails"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Cloud Synchronized successfully! 🚀")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)