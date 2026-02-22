import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ================= 1. 初始化 Session State (用于安全登录状态管理) =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 获取当前页面路由 (home, login, signup)
try:
    current_page = st.query_params.get("page", "home")
except:
    current_page = st.experimental_get_query_params().get("page", ["home"])[0]

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"  # 全局彻底关闭侧边栏
)

# ================= 3. 企业级专业 CSS (Qlik SaaS Style) =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp {
        background-color: #F8FAFC; 
        font-family: 'Inter', -apple-system, sans-serif;
        color: #334155;
    }

    /* 彻底隐藏顶部杂项与侧边栏 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}
    .block-container { padding-top: 5rem !important; }

    /* 🚀 顶部居中导航栏 (Tabs) - 巨型字体 & 加粗无图标版 */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background: #FFFFFF;
        border-radius: 16px;
        padding: 12px 24px;
        gap: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 64px;
        border-radius: 12px;
        background-color: transparent;
        color: #64748B;
        font-weight: 800 !important; /* 超粗体 */
        font-size: 32px !important; /* 字体加大两倍 */
        padding: 0 24px;
        transition: all 0.3s;
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
        padding: 32px;
        margin-bottom: 24px;
    }

    /* Qlik 风格 Hero Section (主页) */
    .hero-container {
        display: flex; align-items: center; justify-content: space-between;
        padding: 4rem 3rem; background-color: #FFFFFF; border-radius: 20px;
        border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        margin-bottom: 2rem; gap: 4rem;
    }
    .hero-left { flex: 1.2; }
    .hero-subtitle { font-size: 14px; font-weight: 800; color: #0F766E; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem; }
    .hero-title { font-size: 4.5rem; font-weight: 900; line-height: 1.1; color: #0F172A; margin-bottom: 1.5rem; letter-spacing: -2px; }
    .hero-title span { color: #0F766E; }
    .hero-desc { font-size: 1.25rem; color: #475569; line-height: 1.6; margin-bottom: 2rem; }

    .hero-right { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .bento-card { border-radius: 16px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.05); transition: transform 0.3s; }
    .bento-card:hover { transform: translateY(-5px); }
    .card-tall { grid-row: span 2; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; min-height: 360px; }
    .card-short-1 { background: #0F766E; color: white; min-height: 160px; }
    .card-short-2 { background: #F1F5F9; color: #0F172A; min-height: 160px; border: 1px solid #E2E8F0;}

    .chem-tag { background:#FFFFFF; padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700; box-shadow:0 2px 5px rgba(0,0,0,0.05); color:#0F172A;}

    /* 区块标题 */
    .section-header { border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 24px; margin-bottom: 20px; background: #FFFFFF; }
    .section-header h2 { font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; }
    .header-blue { border-left: 4px solid #3b82f6; }
    .header-teal { border-left: 4px solid #0F766E; }
    .header-amber { border-left: 4px solid #f59e0b; }

    /* Metadata Grid */
    .metadata-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
    .metadata-item { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; }
    .metadata-label { font-size: 12px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
    .metadata-value { font-size: 15px; font-weight: 600; color: #0F172A; word-wrap: break-word; }

    /* 全局按钮优化 */
    .stButton>button { background-color: #FFFFFF; border: 1px solid #CBD5E1; color: #0F172A; font-weight: 700; border-radius: 8px; transition: all 0.2s; height: 45px;}
    .stButton>button:hover { border-color: #0F766E; color: #0F766E; background-color: #F0FDF4; }

    /* 自定义悬浮顶部导航栏 (带自定义Logo) */
    .custom-top-navbar {
        position: fixed; top: 0; left: 0; right: 0; height: 70px;
        background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        border-bottom: 1px solid #E2E8F0; display: flex; align-items: center;
        justify-content: space-between; padding: 0 3rem; z-index: 999999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .custom-top-navbar .logo img { height: 40px; margin-top: 5px; } /* 调整 Logo 大小 */
    .custom-top-navbar .login-btn {
        background-color: #0F172A; color: #FFFFFF; padding: 8px 24px;
        border-radius: 30px; font-weight: 700; font-size: 15px;
        text-decoration: none; transition: all 0.3s;
    }
    .custom-top-navbar .login-btn:hover { background-color: #0F766E; transform: translateY(-2px); color: #FFFFFF;}
    .custom-top-navbar .logout-btn { background-color: #FFFFFF; color: #EF4444; border: 1px solid #EF4444; padding: 8px 24px; border-radius: 30px; font-weight: 700; text-decoration: none;}
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ================= 4. 动态渲染顶部悬浮栏 (Logo + Login 逻辑) =================
# ⚠️⚠️⚠️ 替换下面这个 src 的链接为你在 Github 上 Logo 图片的 Raw 链接！
LOGO_IMAGE_URL = "https://github.com/jeremiah0188/Battery_dataset/blob/main/logo.png"

if st.session_state.is_admin:
    nav_html = f"""
    <div class="custom-top-navbar">
        <div class="logo"><img src="{LOGO_IMAGE_URL}" alt="Logo" onerror="this.onerror=null; this.parentElement.innerHTML='<span style=\\'font-size:24px; font-weight:900; color:#0F172A;\\'>OpenBattery</span>';"></div>
        <a href="/?page=home" target="_self" class="logout-btn">Log Out</a>
    </div>
    """
else:
    btn_text = "Homepage" if current_page in ["login", "signup"] else "Log In"
    btn_link = "/?page=home" if current_page in ["login", "signup"] else "/?page=login"
    nav_html = f"""
    <div class="custom-top-navbar">
        <div class="logo"><img src="{LOGO_IMAGE_URL}" alt="Logo" onerror="this.onerror=null; this.parentElement.innerHTML='<span style=\\'font-size:24px; font-weight:900; color:#0F172A;\\'>OpenBattery</span>';"></div>
        <a href="{btn_link}" target="_self" class="login-btn">{btn_text}</a>
    </div>
    """
st.markdown(nav_html, unsafe_allow_html=True)

# 处理登出逻辑（如果带有 logout 参数或者需要清除状态）
# 这里通过直接点链接刷新页面重置状态，如果是部署端，可以通过检测 query params 来处理

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
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain', 'Category', 'Sub-category', 'Status'])


df = load_data()

# ================= 6. 核心路由与页面渲染 =================

# ----------------- 页面 A：登录页 (Login) -----------------
if current_page == "login" and not st.session_state.is_admin:
    _, col, _ = st.columns([1, 1.2, 1])  # 居中布局
    with col:
        st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-size: 32px; font-weight: 800; color: #0F172A; margin-bottom: 8px;'>Sign in to your account</h2>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='color: #64748B; font-size: 15px; margin-bottom: 24px; line-height: 1.6;'>Access the dataset platform to manage submissions, review metadata, and track approval status.</p>",
            unsafe_allow_html=True)

        email_input = st.text_input("Email address", placeholder="Enter your email")
        pwd_input = st.text_input("Password", type="password", placeholder="Enter your password")

        st.checkbox("Remember me")

        # 使用 Streamlit columns 排列按钮
        if st.button("Sign In", type="primary", use_container_width=True):
            if not email_input:
                st.error("Please enter your email address.")
            elif not pwd_input:
                st.error("Please enter your password.")
            elif pwd_input == st.secrets.get("admin_password", ""):
                # 登录成功
                st.session_state.is_admin = True
                st.success("Signed in successfully. Redirecting...")
                st.markdown('<meta http-equiv="refresh" content="1;url=/?page=home">', unsafe_allow_html=True)
            else:
                st.error("Invalid email or password. Login failed. Please try again.")

        st.markdown("<hr style='border-color: #E2E8F0; margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;'><a href='#' style='color: #0F766E; font-weight: 600; text-decoration: none;'>Forgot password?</a></div>",
            unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; margin-top: 12px; color: #64748B;'>Don’t have an account? <a href='/?page=signup' target='_self' style='color: #0F172A; font-weight: 700; text-decoration: none;'>Create an account</a></div>",
            unsafe_allow_html=True)

        st.markdown(
            '<div style="margin-top:24px; padding:16px; background:#F8FAFC; border-radius:8px;"><p style="font-size:13px; color:#64748B; margin:0;"><strong>For admins:</strong> Administrators can sign in to review submissions and manage dataset records.</p></div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 页面 B：注册页 (Sign Up) -----------------
elif current_page == "signup" and not st.session_state.is_admin:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-size: 32px; font-weight: 800; color: #0F172A; margin-bottom: 8px;'>Create an account</h2>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='color: #64748B; font-size: 15px; margin-bottom: 24px; line-height: 1.6;'>Create an account to submit datasets, manage your contributions, and receive review notifications.</p>",
            unsafe_allow_html=True)

        st.text_input("Full Name", placeholder="Enter your full name")
        st.text_input("Email address", placeholder="Enter your email")
        st.text_input("Password", type="password", placeholder="Create a password")
        st.text_input("Confirm password", type="password", placeholder="Confirm your password")

        if st.button("Create account", type="primary", use_container_width=True):
            st.info("Registration is temporarily closed. Please contact the administrator for account access.")

        st.markdown("<hr style='border-color: #E2E8F0; margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; color: #64748B;'>Already have an account? <a href='/?page=login' target='_self' style='color: #0F172A; font-weight: 700; text-decoration: none;'>Sign in</a></div>",
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 页面 C：主站 (Main App) -----------------
else:
    # 顶部居中导航构建 (去除了 Emoji，纯文字大号加粗)
    tab_names = ["Homepage", "Browse Datasets", "Contribute Data", "About", "Contact"]
    if st.session_state.is_admin:
        tab_names.append("Admin Dashboard")

    tabs = st.tabs(tab_names)

    # ================= TAB 1: Homepage =================
    with tabs[0]:
        public_count = len(df[df['Status'] == 'Approved'])
        # Chemistry Tags 更新
        chem_tags_html = "".join([f'<span class="chem-tag">{c}</span>' for c in
                                  ["NMC", "LFP", "NCA", "LCO", "LMO", "LTO", "Solid-state", "Li-metal", "Li-S",
                                   "Mixed"]])

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
                    <div style="font-size: 14px; font-weight:700; opacity: 0.8; text-transform:uppercase;">Platform Metrics</div>
                    <div>
                        <div style="font-size: 64px; font-weight: 900; margin-top: auto; line-height:1;">{public_count}+</div>
                        <div style="font-size: 18px; opacity: 0.9; font-weight:600; margin-top:8px;">Curated Datasets</div>
                    </div>
                </div>
                <div class="bento-card card-short-1">
                    <div style="font-size: 14px; font-weight:700; opacity: 0.9; text-transform:uppercase;">A Leader in Quality</div>
                    <div style="font-size: 28px; font-weight: 900; margin-top: auto;">Open Access</div>
                </div>
                <div class="bento-card card-short-2">
                    <div style="font-size: 14px; font-weight:800; color: #64748B; text-transform:uppercase;">Supported Chemistry</div>
                    <div style="display:flex; gap:8px; margin-top: auto; flex-wrap: wrap;">
                        {chem_tags_html}
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(hero_html, unsafe_allow_html=True)

    # ================= TAB 2: Browse Datasets (层级化过滤系统) =================
    with tabs[1]:
        st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)

        public_df = df[df['Status'] == 'Approved']
        filter_col, result_col = st.columns([1, 3])

        with filter_col:
            st.markdown('<div class="research-card">', unsafe_allow_html=True)
            st.markdown(
                "<h3 style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:16px;'>🔍 Filters</h3>",
                unsafe_allow_html=True)
            search_kw = st.text_input("Keyword Search", placeholder="e.g. Oxford, NMC...")

            # 🚀 层级化过滤器 (Cascading Filters)
            st.markdown("<hr style='border-color: #E2E8F0; margin: 16px 0;'>", unsafe_allow_html=True)
            sel_domain = st.selectbox("Domain", ["All", "Energy", "Healthcare", "Manufacturing", "Transportation"])

            sel_category = "All"
            sel_subcategory = "All"

            if sel_domain == "Energy":
                sel_category = st.selectbox("Category", ["All", "Battery", "Grid", "Solar", "Wind"])
                if sel_category == "Battery":
                    sel_subcategory = st.selectbox("Battery Data Type",
                                                   ["All", "Time-Series", "EIS", "Aging / Cycling", "Benchmark",
                                                    "Experimental", "Simulation"])

            st.markdown('</div>', unsafe_allow_html=True)

        with result_col:
            filtered_df = public_df.copy()
            # 执行层级过滤逻辑
            if search_kw:
                mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False)).any(axis=1)
                filtered_df = filtered_df[mask]

            if sel_domain != "All" and 'Domain' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Domain'] == sel_domain]
            if sel_category != "All" and 'Category' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Category'] == sel_category]
            if sel_subcategory != "All" and 'Sub-category' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Sub-category'] == sel_subcategory]

            st.markdown(f"**Result Counter:** {len(filtered_df)} datasets found.")

            if not filtered_df.empty:
                st.markdown('<div class="research-card" style="padding: 16px;">', unsafe_allow_html=True)
                # 动态显示列
                display_cols = [c for c in ['Dataset Name', 'Domain', 'Category', 'Sub-category', 'Author'] if
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

                    details_html = ""
                    details_html += f'<div class="research-card">'
                    details_html += f'<h2 style="font-size: 28px; font-weight:800; color: #0F172A; margin-bottom: 8px;">{selected_dataset}</h2>'
                    details_html += f'<p style="color: #64748B; font-size: 15px; margin-bottom: 24px; font-weight:500;">Source: {details.get("Source Organization", details.get("Author", "N/A"))}</p>'

                    link = details.get('Link', '')
                    if link.startswith('http'):
                        details_html += f'<div style="margin-bottom: 24px;"><a href="{link}" target="_blank" style="display:inline-block; background:#0F766E; color:#FFF; padding:10px 24px; text-decoration:none; border-radius:8px; font-weight:700; font-size:14px;">🔗 Download / Visit Source</a></div>'

                    details_html += '<div class="metadata-grid">'
                    for col_name in df.columns:
                        if col_name not in ['Link', 'Status', 'Dataset Name']:
                            val = details.get(col_name, 'N/A')
                            if str(val).strip() != '' and str(val).lower() != 'nan':
                                details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                    details_html += '</div></div>'

                    st.markdown(details_html, unsafe_allow_html=True)
            else:
                st.warning("No datasets match your filters. Try adjusting the Domain or Category.")

    # ================= TAB 3: Contribute Data =================
    with tabs[2]:
        st.markdown('<div class="section-header header-teal"><h2>Contribute a Dataset</h2></div>',
                    unsafe_allow_html=True)

        with st.form("upload_form", border=False):
            st.markdown('<div class="research-card">', unsafe_allow_html=True)
            st.write(
                "Help expand this curated dataset hub. Please provide standardized metadata to improve discoverability.")

            st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
            st.markdown("#### Section 1: Basic Information")
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Dataset Name *")
            new_desc = c2.text_input("Short Description *")

            c1b, c2b, c3b = st.columns(3)
            # 与搜索栏联动的层级录入
            new_domain = c1b.selectbox("Domain *", ["Energy", "Healthcare", "Manufacturing", "Transportation", "Other"])
            new_category = c2b.text_input("Category (e.g., Battery, Grid)")
            new_subcat = c3b.text_input("Sub-category (e.g., Time-Series, EIS)")

            new_link = st.text_input("Source URL * (External Download Link)")
            new_org = st.text_input("Source Organization / Publisher")

            st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
            st.markdown("#### Section 2: Technical Specifications")
            c3, c4, c5 = st.columns(3)
            new_chem = c3.selectbox("Battery Chemistry",
                                    ["Not Applicable", "NMC", "LFP", "NCA", "LCO", "LMO", "LTO", "Solid-state",
                                     "Li-metal", "Li-S", "Mixed", "Other"])
            new_cell = c4.text_input("Cell / Module Type")
            new_temp = c5.text_input("Temperature Range (°C)")

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
                        'Dataset Name': new_name, 'Domain': new_domain, 'Category': new_category,
                        'Sub-category': new_subcat,
                        'Short Description': new_desc, 'Link': new_link, 'Source Organization': new_org,
                        'Battery Chemistry': new_chem, 'Cell / Module Type': new_cell,
                        'Temperature Range': new_temp, 'Author': new_contributor, 'Contributor Email': new_email,
                        'Status': 'Pending'
                    })
                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                    st.success("Successfully submitted to the moderation queue!")
                    st.cache_data.clear()
            st.markdown('</div>', unsafe_allow_html=True)

    # ================= TAB 4 & 5: About & Contact =================
    with tabs[3]:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header header-blue"><h2>About This Platform</h2></div>',
                    unsafe_allow_html=True)
        st.write(
            "This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.")
        st.write("**Maintained by Jian Wu**, focusing on battery data analysis and SOH estimation.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('<div class="research-card" style="text-align: center; padding: 60px 20px;">',
                    unsafe_allow_html=True)
        st.markdown('<h2 style="color:#0F172A; font-weight:900; margin-bottom:16px;">Get in Touch</h2>',
                    unsafe_allow_html=True)
        st.write("For questions, dataset suggestions, collaboration, or corrections, please contact:")
        st.markdown("<h3 style='color:#0F766E; font-weight:800; margin-top:20px;'>jian.wu@utbm.fr</h3>",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ================= TAB 6: Admin Dashboard =================
    if st.session_state.is_admin:
        with tabs[5]:
            st.markdown('<div class="research-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>',
                        unsafe_allow_html=True)
            with st.form("admin_form", border=False):
                edited_df = st.data_editor(df, column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                           use_container_width=True, num_rows="dynamic")
                if st.form_submit_button("💾 Synchronize Cloud Data"):
                    conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                    st.success("Synchronized successfully!")
                    st.cache_data.clear()
            st.markdown('</div>', unsafe_allow_html=True)