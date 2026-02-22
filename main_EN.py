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

# ================= 3. 企业级专业 CSS (Qlik SaaS Style & Clean Research) =================
professional_css = """
<style>
    /* 引入现代化字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 全局背景与字体 */
    .stApp {
        background-color: #F8FAFC; /* 冷灰白，极简专业 */
        font-family: 'Inter', -apple-system, sans-serif;
        color: #334155;
    }

    /* 顶部居中导航栏 (Tabs) - 🚀 字体加大两倍优化版 */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background: #FFFFFF;
        border-radius: 16px;
        padding: 12px 20px;
        gap: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; /* 加高以适应大字体 */
        border-radius: 10px;
        background-color: transparent;
        color: #64748B;
        font-weight: 700;
        font-size: 28px !important; /* 🚀 强制字体加大 */
        padding: 0 20px;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        box-shadow: none;
    }

    /* 纯白内容卡片 (Research Card) */
    .research-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.03);
        padding: 24px;
        margin-bottom: 24px;
    }

    /* Qlik 风格 Hero Section (主页) */
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 3rem 2rem;
        background-color: #FFFFFF;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        margin-bottom: 2rem;
        gap: 4rem;
    }
    .hero-left { flex: 1; max-width: 50%; }
    .hero-subtitle {
        font-size: 14px; font-weight: 700; color: #0F766E; 
        text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 4rem; font-weight: 800; line-height: 1.1; 
        color: #0F172A; margin-bottom: 1.5rem; letter-spacing: -1.5px;
    }
    .hero-title span { color: #0F766E; }
    .hero-desc {
        font-size: 1.125rem; color: #475569; line-height: 1.6; margin-bottom: 2rem;
    }

    /* 右侧 Bento Box 网格区 */
    .hero-right {
        flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
    }
    .bento-card {
        border-radius: 16px; padding: 24px; color: white; display: flex; 
        flex-direction: column; justify-content: space-between; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); transition: transform 0.3s;
    }
    .bento-card:hover { transform: translateY(-5px); }
    .card-tall { grid-row: span 2; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); min-height: 320px; }
    .card-short-1 { background: #0F766E; min-height: 150px; }
    .card-short-2 { background: #F1F5F9; color: #0F172A; min-height: 150px; border: 1px solid #E2E8F0;}

    /* 区块标题带色条 (Section Headers) */
    .section-header {
        border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 24px; 
        margin-bottom: 20px; background: #FFFFFF;
    }
    .section-header h2 { font-size: 22px; font-weight: 700; color: #0F172A; margin: 0; }
    .header-blue { border-left: 4px solid #3b82f6; }
    .header-teal { border-left: 4px solid #0F766E; }
    .header-amber { border-left: 4px solid #f59e0b; }

    /* Metadata Grid (全量元数据网格) */
    .metadata-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    .metadata-item {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
    }
    .metadata-label {
        font-size: 12px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metadata-value {
        font-size: 15px;
        font-weight: 600;
        color: #0F172A;
        word-wrap: break-word;
    }

    /* 按钮优化 */
    .stButton>button {
        background-color: #FFFFFF; border: 1px solid #CBD5E1; 
        color: #0F172A; font-weight: 600; border-radius: 8px; transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #0F766E; color: #0F766E; background-color: #F0FDF4;
    }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ================= 4. 针对普通用户的“沉浸式”隔离与自定义顶部 Logo 栏 =================
if not is_jian_entry:
    regular_user_header = """
    <style>
        /* 🚀 彻底隐藏默认的 Streamlit 顶部包含 Github/Share 的 Header */
        [data-testid="stHeader"] { display: none !important; }

        /* 彻底隐藏侧边栏 */
        [data-testid='stSidebar'], [data-testid='collapsedControl'] { display: none !important; }

        /* 给页面顶部留出导航栏的空间 */
        .block-container { padding-top: 5rem !important; }

        /* 🚀 自定义悬浮顶部导航栏 (Logo + Login) */
        .custom-top-navbar {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 64px;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            z-index: 999999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .custom-top-navbar .logo {
            font-size: 22px;
            font-weight: 800;
            color: #0F172A;
        }
        .custom-top-navbar .login-btn {
            background-color: #0F766E;
            color: #FFFFFF;
            padding: 6px 20px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.3s;
        }
        .custom-top-navbar .login-btn:hover {
            background-color: #0D645E;
            transform: translateY(-2px);
        }
    </style>
    <div class="custom-top-navbar">
        <div class="logo">🔋 OpenBattery</div>
        <a href="?admin=Jian" target="_self" class="login-btn">LOGIN</a>
    </div>
    """
    st.markdown(regular_user_header, unsafe_allow_html=True)
else:
    # Admin 模式下，仅隐藏不必要的底部水印，保留原生控制权
    st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# ================= 5. 🔗 Google Sheets 数据库配置 =================
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

# ================= 6. 管理员身份验证 =================
is_admin = False
if is_jian_entry:
    with st.sidebar:
        st.markdown("### 👨‍💻 Jian's Admin Panel")
        target_password = st.secrets.get("admin_password", "")
        admin_pw = st.text_input("Security Key", type="password")
        if admin_pw == target_password and target_password != "":
            is_admin = True
            st.success("Admin unlocked!")

# ================= 7. 顶部居中导航构建 =================
tab_names = ["🏠 Homepage", "📚 Browse Datasets", "☁️ Contribute Data", "ℹ️ About", "✉️ Contact"]
if is_admin:
    tab_names.append("⚙️ Admin Dashboard")

tabs = st.tabs(tab_names)

# ================= TAB 1: Homepage =================
with tabs[0]:
    public_count = len(df[df['Status'] == 'Approved'])
    hero_html = f"""
    <div class="hero-container">
        <div class="hero-left">
            <div class="hero-subtitle">Open Source Data & Analytics</div>
            <div class="hero-title">Battery Data <br><span>Differently</span></div>
            <div class="hero-desc">
                We deliver high-fidelity, peer-reviewed battery datasets and robust metadata integration tailored to meet the evolving needs of global energy research.
            </div>
        </div>
        <div class="hero-right">
            <div class="bento-card card-tall">
                <div style="font-size: 14px; font-weight:600; opacity: 0.8;">Platform Metrics</div>
                <div>
                    <div style="font-size: 56px; font-weight: 800; margin-top: auto;">{public_count}+</div>
                    <div style="font-size: 16px; opacity: 0.9;">Curated Datasets</div>
                </div>
            </div>
            <div class="bento-card card-short-1">
                <div style="font-size: 14px; font-weight:600; opacity: 0.9;">A Leader in Quality</div>
                <div style="font-size: 24px; font-weight: 800; margin-top: auto;">Open Access</div>
            </div>
            <div class="bento-card card-short-2">
                <div style="font-size: 14px; font-weight:700; color: #64748B;">Supported Chemistry</div>
                <div style="display:flex; gap:10px; margin-top: auto; flex-wrap: wrap;">
                    <span style="background:#FFFFFF; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700; box-shadow:0 2px 5px rgba(0,0,0,0.05);">NMC</span>
                    <span style="background:#FFFFFF; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700; box-shadow:0 2px 5px rgba(0,0,0,0.05);">LFP</span>
                    <span style="background:#FFFFFF; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700; box-shadow:0 2px 5px rgba(0,0,0,0.05);">NCA</span>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

# ================= TAB 2: Browse Datasets (分屏布局) =================
with tabs[1]:
    st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)

    public_df = df[df['Status'] == 'Approved']
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:16px; color:#0F172A; margin-bottom:16px;'>🔍 Filters</h3>",
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

        st.markdown(f"**Result Counter:** {len(filtered_df)} datasets found.")

        if not filtered_df.empty:
            st.markdown('<div class="research-card" style="padding: 16px;">', unsafe_allow_html=True)
            display_cols = [c for c in ['Dataset Name', 'Domain / Category', 'Author', 'Battery Chemistry'] if
                            c in filtered_df.columns]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                '<div class="section-header header-teal" style="margin-top: 24px;"><h2>📖 Dataset Details</h2></div>',
                unsafe_allow_html=True)

            valid_datasets = filtered_df[filtered_df['Dataset Name'] != '']
            selected_dataset = st.selectbox("Select a dataset to view full details:",
                                            ["(Select to view)"] + valid_datasets['Dataset Name'].tolist(),
                                            label_visibility="collapsed")

            if selected_dataset != "(Select to view)":
                details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]

                # 🚀 核心修复：纯单行拼接字符串，彻底杜绝 Markdown 缩进解析 Bug
                details_html = ""
                details_html += f'<div class="research-card">'
                details_html += f'<h2 style="font-size: 28px; color: #0F172A; margin-bottom: 8px;">{selected_dataset}</h2>'
                details_html += f'<p style="color: #64748B; font-size: 15px; margin-bottom: 24px;">Source: {details.get("Source Organization", details.get("Author", "N/A"))}</p>'

                link = details.get('Link', '')
                if link.startswith('http'):
                    details_html += f'<div style="margin-bottom: 24px;"><a href="{link}" target="_blank" style="display:inline-block; background:#0F766E; color:#FFF; padding:10px 24px; text-decoration:none; border-radius:8px; font-weight:600; font-size:14px;">🔗 Download / Visit Source</a></div>'

                details_html += '<div class="metadata-grid">'

                for col_name in df.columns:
                    if col_name not in ['Link', 'Status', 'Dataset Name']:
                        val = details.get(col_name, 'N/A')
                        if str(val).strip() != '' and str(val).lower() != 'nan':
                            # 无空格拼接，绝不触发代码块模式
                            details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'

                details_html += '</div></div>'

                # 输出修复后的无缩进 HTML
                st.markdown(details_html, unsafe_allow_html=True)

        else:
            st.warning("No datasets match your filters.")

# ================= TAB 3: Contribute Data =================
with tabs[2]:
    st.markdown('<div class="section-header header-teal"><h2>Contribute a Dataset</h2></div>', unsafe_allow_html=True)

    with st.form("upload_form", border=False):
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.write(
            "Help expand this curated dataset hub. Please provide standardized metadata to improve discoverability.")

        st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("#### Section 1: Basic Information")
        c1, c2 = st.columns(2)
        new_name = c1.text_input("Dataset Name *")
        new_domain = c2.text_input("Domain / Category *")
        new_desc = st.text_area("Short Description *")
        new_link = st.text_input("Source URL * (External Download Link)")
        new_org = st.text_input("Source Organization / Publisher")

        st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("#### Section 2: Technical Specifications")
        c3, c4, c5 = st.columns(3)
        new_chem = c3.text_input("Battery Chemistry")
        new_cell = c4.text_input("Cell / Module Type")
        new_temp = c5.text_input("Temperature Range (°C)")

        c6, c7 = st.columns(2)
        new_eis = c6.selectbox("Includes EIS Data?", ["No", "Yes"])
        new_aging = c7.selectbox("Includes Aging / Cycling Data?", ["No", "Yes"])

        st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("#### Section 3: Contributor Info")
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
                    'Short Description': new_desc, 'Link': new_link, 'Source Organization': new_org,
                    'Battery Chemistry': new_chem, 'Cell / Module Type': new_cell,
                    'Temperature Range': new_temp, 'Includes EIS Data': new_eis, 'Includes Aging / Cycling': new_aging,
                    'Author': new_contributor, 'Contributor Email': new_email, 'Status': 'Pending'
                })
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success("Successfully submitted to the moderation queue!")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 4 & 5: About & Contact =================
with tabs[3]:
    st.markdown('<div class="research-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header header-blue"><h2>About This Platform</h2></div>', unsafe_allow_html=True)
    st.write(
        "This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.")
    st.write("**Maintained by Jian Wu**, focusing on battery data analysis and SOH estimation.")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="research-card" style="text-align: center; padding: 60px 20px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#0F172A; margin-bottom:16px;">Get in Touch</h2>', unsafe_allow_html=True)
    st.write("For questions, dataset suggestions, collaboration, or corrections, please contact:")
    st.markdown("<h3 style='color:#0F766E;'>jian.wu@utbm.fr</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 6: Admin Dashboard =================
if is_admin:
    with tabs[5]:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(df, column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                       use_container_width=True, num_rows="dynamic")
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized!")
                st.cache_data.clear()
        st.markdown('</div>', unsafe_allow_html=True)