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
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded" if is_jian_entry else "collapsed"
)

# ================= 3. 深度定制 CSS (Professional Research UI) =================
clean_research_css = f"""
<style>
    /* 引入 Inter 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* 全局背景与字体设定 */
    .stApp {{
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
        color: #475569; /* 默认正文灰色 */
    }}

    /* 隐藏基础 UI */
    #MainMenu {{visibility: hidden;}}
    header {{background-color: transparent;}}
    footer {{visibility: hidden;}}
    #stDecoration {{display:none;}}

    /* 顶部导航栏 (Tabs) 极简白风格 */
    .stTabs [data-baseweb="tab-list"] {{
        justify-content: center;
        background: #FFFFFF;
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        border-radius: 8px;
        background-color: transparent;
        color: #64748B;
        font-weight: 600;
        transition: all 0.2s;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        box-shadow: none;
    }}

    /* --- 核心组件 1：纯白卡片 (Research Card) --- */
    .research-card {{
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
        padding: 24px;
        margin-bottom: 24px;
    }}

    /* --- 核心组件 2：H1 页面主标题容器 --- */
    .page-header {{
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 55%, #f6f0ff 100%);
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 32px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    }}
    .page-header h1 {{
        font-size: 48px;
        font-weight: 800;
        line-height: 1.1;
        color: #0F172A;
        margin-bottom: 12px;
        letter-spacing: -1px;
    }}
    .page-header p {{
        font-size: 18px;
        color: #475569;
        max-width: 800px;
        line-height: 1.6;
    }}

    /* --- 核心组件 3：H2 区块标题容器 (带颜色细线和极浅渐变) --- */
    .section-header {{
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }}
    .section-header h2 {{
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        margin: 0;
        padding: 0;
    }}
    .header-blue {{ background: linear-gradient(90deg, #ffffff, #eef6ff); border-left: 4px solid #3b82f6; }}
    .header-cyan {{ background: linear-gradient(90deg, #ffffff, #eefcf8); border-left: 4px solid #0ea5e9; }}
    .header-green {{ background: linear-gradient(90deg, #ffffff, #f3fbf5); border-left: 4px solid #10b981; }}
    .header-purple {{ background: linear-gradient(90deg, #ffffff, #f7f3ff); border-left: 4px solid #8b5cf6; }}
    .header-amber {{ background: linear-gradient(90deg, #ffffff, #fff8ee); border-left: 4px solid #f59e0b; }}

    /* --- 核心组件 4：Metadata Grid (信息网格，替代杂乱文本) --- */
    .metadata-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        margin-top: 16px;
    }}
    .metadata-item {{
        background: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.02);
    }}
    .metadata-label {{
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .metadata-value {{
        font-size: 15px;
        font-weight: 500;
        color: #0F172A;
    }}

    /* 按钮优化 */
    .stButton>button {{
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        color: #0F172A;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
    }}
    .stButton>button:hover {{
        border-color: #0F766E;
        color: #0F766E;
        background-color: #F0FDF4;
    }}
</style>
"""
st.markdown(clean_research_css, unsafe_allow_html=True)

if not is_jian_entry:
    st.markdown(
        "<style>[data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}</style>",
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
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain / Category', 'Status'])


df = load_data()

# ================= 5. 管理员身份验证 =================
is_admin = False
if is_jian_entry:
    with st.sidebar:
        st.markdown("### 👨‍💻 Jian's Admin Panel")
        target_password = st.secrets.get("admin_password", "")
        admin_pw = st.text_input("Admin Password", type="password")
        if admin_pw == target_password and target_password != "":
            is_admin = True
            st.success("Access Granted")

# ================= 6. 顶部居中导航构建 =================
tab_names = ["🏠 Homepage", "📚 Browse Datasets", "☁️ Contribute Data", "ℹ️ About", "✉️ Contact"]
if is_admin:
    tab_names.append("⚙️ Admin Dashboard")

tabs = st.tabs(tab_names)

# ================= TAB 1: Homepage =================
with tabs[0]:
    # H1 页面主标题区域
    st.markdown("""
    <div class="page-header">
        <h1>A Curated Hub for Public Research Datasets</h1>
        <p>Explore, compare, and download public datasets with standardized metadata. Contribute new datasets to help the research community grow with high-fidelity, peer-reviewed data.</p>
    </div>
    """, unsafe_allow_html=True)

    # Trust Metrics (信任统计卡片 - 纯白风格)
    col1, col2, col3 = st.columns(3)
    public_count = len(df[df['Status'] == 'Approved'])
    with col1:
        st.markdown(
            f'<div class="research-card" style="text-align:center;"><h2 style="font-size:36px; color:#0F172A; margin:0;">{public_count}+</h2><p style="color:#64748B; margin:0; font-weight:600;">Curated Datasets</p></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            '<div class="research-card" style="text-align:center;"><h2 style="font-size:36px; color:#0F172A; margin:0;">🔋</h2><p style="color:#64748B; margin:0; font-weight:600;">Battery & Time-Series</p></div>',
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            '<div class="research-card" style="text-align:center;"><h2 style="font-size:36px; color:#0F172A; margin:0;">🌐</h2><p style="color:#64748B; margin:0; font-weight:600;">Open Access</p></div>',
            unsafe_allow_html=True)

# ================= TAB 2: Browse Datasets =================
with tabs[1]:
    st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)

    public_df = df[df['Status'] == 'Approved']
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0F172A; font-size:18px; margin-bottom:16px;'>🔍 Filters</h3>",
                    unsafe_allow_html=True)
        search_kw = st.text_input("Keyword Search")

        categories = ["All"] + list(
            public_df['Domain / Category'].unique()) if 'Domain / Category' in public_df.columns else ["All", "Battery",
                                                                                                       "Energy"]
        sel_cat = st.selectbox("Domain / Category", categories)
        st.markdown('</div>', unsafe_allow_html=True)

    with result_col:
        filtered_df = public_df.copy()
        if search_kw:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        if sel_cat != "All" and 'Domain / Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Domain / Category'] == sel_cat]

        if not filtered_df.empty:
            st.markdown('<div class="research-card" style="padding: 16px 24px;">', unsafe_allow_html=True)
            display_cols = [c for c in ['Dataset Name', 'Domain / Category', 'Author', 'Battery Chemistry'] if
                            c in filtered_df.columns]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Dataset Details 区块 ---
            st.markdown(
                '<div class="section-header header-purple" style="margin-top: 32px;"><h2>📖 Dataset Details</h2></div>',
                unsafe_allow_html=True)
            valid_datasets = filtered_df[filtered_df['Dataset Name'] != '']
            selected_dataset = st.selectbox("Select a dataset to view full details:",
                                            ["(Select to view)"] + valid_datasets['Dataset Name'].tolist(),
                                            label_visibility="collapsed")

            if selected_dataset != "(Select to view)":
                details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]

                # Metadata Grid 渲染
                grid_html = '<div class="research-card"><div class="metadata-grid">'
                for c in df.columns:
                    if c not in ['Link', 'Status', 'Dataset Name']:
                        val = details.get(c, 'N/A')
                        if str(val).strip() != '':
                            grid_html += f'''
                            <div class="metadata-item">
                                <div class="metadata-label">{c}</div>
                                <div class="metadata-value">{val}</div>
                            </div>
                            '''
                grid_html += '</div>'

                # 下载按钮单独放一行
                link = details.get('Link', '')
                if link.startswith('http'):
                    grid_html += f'<div style="margin-top: 24px;"><a href="{link}" target="_blank" style="background:#0F172A; color:#FFF; padding:10px 20px; text-decoration:none; border-radius:8px; font-weight:600; font-size:14px;">🔗 Download / Visit Source</a></div>'
                grid_html += '</div>'

                st.markdown(grid_html, unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ================= TAB 3: Contribute Data =================
with tabs[2]:
    st.markdown("""
    <div class="page-header">
        <h1>Contribute a Dataset</h1>
        <p>Help expand this curated dataset hub. Please provide standardized metadata to improve discoverability and reuse.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("upload_form", border=False):
        st.markdown('<div class="research-card">', unsafe_allow_html=True)

        st.markdown('<div class="section-header header-blue"><h2>Basic Information</h2></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        new_name = c1.text_input("Dataset Name *")
        new_domain = c2.text_input("Domain / Category *")
        new_desc = st.text_area("Short Description *")
        new_link = st.text_input("Source URL * (External Download Link)")

        st.markdown('<div class="section-header header-cyan"><h2>Technical Specifications</h2></div>',
                    unsafe_allow_html=True)
        c3, c4, c5 = st.columns(3)
        new_chem = c3.text_input("Battery Chemistry")
        new_cell = c4.text_input("Cell / Module Type")
        new_temp = c5.text_input("Temperature Range (°C)")

        st.markdown('<div class="section-header header-green"><h2>Contributor Info</h2></div>', unsafe_allow_html=True)
        c8, c9 = st.columns(2)
        new_contributor = c8.text_input("Contributor Name *")
        new_email = c9.text_input("Contact Email")

        submitted = st.form_submit_button("📤 Submit to Moderation Queue")

        if submitted:
            if not new_name or not new_domain or not new_link or not new_contributor:
                st.error("Please fill in all required fields marked with *")
            else:
                new_row = {c: "" for c in df.columns}
                new_row.update({
                    'Dataset Name': new_name, 'Domain / Category': new_domain,
                    'Short Description': new_desc, 'Link': new_link,
                    'Battery Chemistry': new_chem, 'Cell / Module Type': new_cell,
                    'Temperature Range': new_temp, 'Author': new_contributor,
                    'Contributor Email': new_email, 'Status': 'Pending'
                })
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success("Successfully submitted!")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 4 & 5: About & Contact =================
with tabs[3]:
    st.markdown('<div class="research-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header header-amber"><h2>About This Platform</h2></div>', unsafe_allow_html=True)
    st.write(
        "This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="research-card" style="text-align:center; padding: 60px 20px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#0F172A; margin-bottom:16px;">Get in Touch</h2>', unsafe_allow_html=True)
    st.write("For questions, dataset suggestions, collaboration, or corrections, please contact:")
    st.markdown("<h3 style='color:#0F766E;'>jian.wu@utbm.fr</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 6: Admin Dashboard =================
if is_admin:
    with tabs[5]:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header header-purple"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(df, column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                       use_container_width=True, num_rows="dynamic")
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized!")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)