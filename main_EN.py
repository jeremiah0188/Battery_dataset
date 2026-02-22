import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ================= 1. 初始化 Session State 与 页面路由 =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 获取当前页面路由 (默认是 home)
try:
    current_page = st.query_params.get("page", "home")
except:
    current_page = st.experimental_get_query_params().get("page", ["home"])[0]

is_jian_entry = (st.query_params.get("admin", "") == "Jian" or current_page == "login")

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 3. 企业级专业 CSS (纯白无边框版) =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp {
        background-color: #F8FAFC; 
        font-family: 'Inter', -apple-system, sans-serif;
        color: #334155;
    }

    /* 彻底隐藏 Streamlit 默认顶部、底部和侧边栏 */
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}

    /* 为自定义导航栏留出空间 */
    .block-container { padding-top: 6rem !important; }

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

    .chem-tag { background: rgba(255,255,255,0.7); padding:6px 14px; border-radius:20px; font-size:13px; font-weight:800; box-shadow:0 2px 5px rgba(0,0,0,0.03); color:#0F172A; border: 1px solid rgba(0,0,0,0.05);}

    /* 区块标题 */
    .section-header { border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 24px; margin-bottom: 20px; background: #FFFFFF; }
    .section-header h2 { font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; }
    .header-blue { border-left: 4px solid #3b82f6; }
    .header-teal { border-left: 4px solid #0F766E; }
    .header-amber { border-left: 4px solid #f59e0b; }

    /* Metadata Grid 优化，杜绝空方块 */
    .metadata-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
    .metadata-item { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; }
    .metadata-label { font-size: 12px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
    .metadata-value { font-size: 15px; font-weight: 600; color: #0F172A; word-wrap: break-word; }

    /* 全局按钮优化 */
    .stButton>button { background-color: #FFFFFF; border: 1px solid #CBD5E1; color: #0F172A; font-weight: 700; border-radius: 8px; transition: all 0.2s; height: 45px;}
    .stButton>button:hover { border-color: #0F766E; color: #0F766E; background-color: #F0FDF4; }

    /* 🚀 全新悬浮顶部导航栏 (Logo + 居左菜单 + Login) */
    .custom-top-navbar {
        position: fixed; top: 0; left: 0; right: 0; height: 70px;
        background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        border-bottom: 1px solid #E2E8F0; display: flex; align-items: center;
        justify-content: space-between; padding: 0 3rem; z-index: 999999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .nav-left-section {
        display: flex; align-items: center; gap: 2.5rem;
    }
    .custom-top-navbar .logo img { height: 40px; }

    /* 核心导航菜单样式 */
    .nav-menu {
        display: flex; gap: 1.8rem;
    }
    .nav-menu a {
        color: #475569; font-size: 15px; font-weight: 700; 
        text-decoration: none; transition: color 0.2s;
    }
    .nav-menu a:hover { color: #0F172A; }
    .nav-menu a.active { color: #0F766E; border-bottom: 2px solid #0F766E; padding-bottom: 4px; }

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

# ================= 4. 动态渲染全新顶部菜单栏 =================
# ⚠️替换这里的 Logo 链接
LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"


def get_active_cls(page_name):
    return "active" if current_page == page_name else ""


# 生成菜单 HTML
menu_html = f"""
    <div class="nav-menu">
        <a href="/?page=home" class="{get_active_cls('home')}">Homepage</a>
        <a href="/?page=browse" class="{get_active_cls('browse')}">Browse Datasets</a>
        <a href="/?page=contribute" class="{get_active_cls('contribute')}">Contribute Data</a>
        <a href="/?page=about" class="{get_active_cls('about')}">About</a>
        <a href="/?page=contact" class="{get_active_cls('contact')}">Contact</a>
"""
if st.session_state.is_admin:
    menu_html += f'<a href="/?page=admin" class="{get_active_cls("admin")}" style="color:#F59E0B;">Admin Dashboard</a>'
menu_html += "</div>"

# 生成完整 Navbar HTML
if st.session_state.is_admin:
    nav_html = f"""
    <div class="custom-top-navbar">
        <div class="nav-left-section">
            <div class="logo"><img src="{LOGO_IMAGE_URL}" onerror="this.onerror=null; this.parentElement.innerHTML='<span style=\\'font-size:24px; font-weight:900; color:#0F172A;\\'>OpenBattery</span>';"></div>
            {menu_html}
        </div>
        <a href="/?page=home" target="_self" class="logout-btn">Log Out</a>
    </div>
    """
else:
    nav_html = f"""
    <div class="custom-top-navbar">
        <div class="nav-left-section">
            <div class="logo"><img src="{LOGO_IMAGE_URL}" onerror="this.onerror=null; this.parentElement.innerHTML='<span style=\\'font-size:24px; font-weight:900; color:#0F172A;\\'>OpenBattery</span>';"></div>
            {menu_html}
        </div>
        <a href="/?page=login" target="_self" class="login-btn">Log In</a>
    </div>
    """
st.markdown(nav_html, unsafe_allow_html=True)

# ================= 5. 🔗 Google Sheets 数据库配置 =================
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
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain', 'Category', 'Sub-category', 'Status'])


df = load_data()

# ================= 6. 核心路由与页面内容渲染 =================

# ----------------- 页面 A：登录页 (Login) -----------------
if current_page == "login" and not st.session_state.is_admin:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-size: 32px; font-weight: 800; color: #0F172A; margin-bottom: 8px;'>Sign in to your account</h2>",
            unsafe_allow_html=True)
        st.markdown(
            "<p style='color: #64748B; font-size: 15px; margin-bottom: 24px; line-height: 1.6;'>Access the dataset platform to manage submissions, review metadata, and track approval status.</p>",
            unsafe_allow_html=True)

        email_input = st.text_input("Email address", placeholder="Enter your email")
        pwd_input = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Sign In", type="primary", use_container_width=True):
            if not email_input:
                st.error("Please enter your email address.")
            elif not pwd_input:
                st.error("Please enter your password.")
            elif pwd_input == st.secrets.get("admin_password", ""):
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
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 页面 B：注册页 (Sign Up) -----------------
elif current_page == "signup" and not st.session_state.is_admin:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
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

        if st.button("Create account", type="primary", use_container_width=True):
            st.info("Registration is temporarily closed. Please contact the administrator.")
        st.markdown("<hr style='border-color: #E2E8F0; margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; color: #64748B;'>Already have an account? <a href='/?page=login' target='_self' style='color: #0F172A; font-weight: 700; text-decoration: none;'>Sign in</a></div>",
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 页面 C：Homepage -----------------
elif current_page == "home":
    public_count = len(df[df['Status'] == 'Approved'])
    chem_tags_html = "".join([f'<span class="chem-tag">{c}</span>' for c in
                              ["NMC", "LFP", "NCA", "LCO", "LMO", "LTO", "Solid-state", "Li-metal", "Li-S", "Mixed"]])

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
            <div class="bento-card" style="grid-row:span 2; background: linear-gradient(135deg, #F0F9FF 0%, #E0E7FF 100%); min-height:320px;">
                <div style="font-size: 14px; font-weight:800; color: #312E81; text-transform:uppercase; opacity: 0.8;">Platform Metrics</div>
                <div>
                    <div style="font-size: 64px; font-weight: 900; color: #1E1B4B; margin-top: auto; line-height:1;">{public_count}+</div>
                    <div style="font-size: 18px; color: #3730A3; font-weight:700; margin-top:8px;">Curated Datasets</div>
                </div>
            </div>
            <div class="bento-card" style="background: linear-gradient(135deg, #ECFEFF 0%, #CCFBF1 100%); min-height: 160px;">
                <div style="font-size: 14px; font-weight:800; color: #115E59; text-transform:uppercase; opacity: 0.9;">A Leader in Quality</div>
                <div style="font-size: 28px; font-weight: 900; color: #042F2E; margin-top: auto;">Open Access</div>
            </div>
            <div class="bento-card" style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); min-height: 160px; border: 1px solid #FDE68A;">
                <div style="font-size: 14px; font-weight:800; color: #92400E; text-transform:uppercase;">Supported Chemistry</div>
                <div style="display:flex; gap:8px; margin-top: auto; flex-wrap: wrap;">
                    {chem_tags_html}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

# ----------------- 页面 D：Browse Datasets -----------------
elif current_page == "browse":
    st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)

    public_df = df[df['Status'] == 'Approved']
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        st.markdown('<div class="research-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:16px;'>🔍 Filters</h3>",
                    unsafe_allow_html=True)
        search_kw = st.text_input("Keyword Search", placeholder="e.g. Oxford, NMC...")

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
                        # 🚀 严格校验：剔除 nan, None, N/A 和空字符串，彻底消灭空方框！
                        if pd.notna(val) and str(val).strip() != '' and str(val).strip().lower() not in ['nan', 'none',
                                                                                                         'n/a', 'na']:
                            details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                details_html += '</div></div>'

                st.markdown(details_html, unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ----------------- 页面 E：Contribute Data -----------------
elif current_page == "contribute":
    st.markdown('<div class="section-header header-teal"><h2>Contribute a Dataset</h2></div>', unsafe_allow_html=True)

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
        new_domain = c1b.selectbox("Domain *", ["Energy", "Healthcare", "Manufacturing", "Transportation", "Other"])
        new_category = c2b.text_input("Category (e.g., Battery, Grid)")
        new_subcat = c3b.text_input("Sub-category (e.g., Time-Series, EIS)")

        new_link = st.text_input("Source URL * (External Download Link)")
        new_org = st.text_input("Source Organization / Publisher")

        st.markdown("<hr style='margin: 24px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("#### Section 2: Technical Specifications")
        c3, c4, c5 = st.columns(3)
        new_chem = c3.selectbox("Battery Chemistry",
                                ["Not Applicable", "NMC", "LFP", "NCA", "LCO", "LMO", "LTO", "Solid-state", "Li-metal",
                                 "Li-S", "Mixed", "Other"])
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
                    'Dataset Name': new_name, 'Domain': new_domain, 'Category': new_category,
                    'Sub-category': new_subcat,
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

# ----------------- 页面 F & G：About & Contact -----------------
elif current_page == "about":
    st.markdown('<div class="research-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header header-blue"><h2>About This Platform</h2></div>', unsafe_allow_html=True)
    st.write(
        "This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.")
    st.write("Maintained by Jian Wu, focusing on battery data analysis and SOH estimation.")
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "contact":
    st.markdown('<div class="research-card" style="text-align: center; padding: 80px 20px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#0F172A; font-weight:900; margin-bottom:16px;">Get in Touch</h2>',
                unsafe_allow_html=True)

    # 🚀 精准满足需求：邮箱不放大，内嵌在文字后方加粗
    st.markdown(
        "<p style='font-size: 16px; color: #475569;'>For questions, dataset suggestions, collaboration, or corrections, please contact: <strong>jian.wu@utbm.fr</strong></p>",
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 页面 H：Admin Dashboard -----------------
elif current_page == "admin" and st.session_state.is_admin:
    st.markdown('<div class="research-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
    with st.form("admin_form", border=False):
        edited_df = st.data_editor(df, column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                   use_container_width=True, num_rows="dynamic")
        if st.form_submit_button("💾 Synchronize Cloud Data"):
            conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
            st.success("Synchronized successfully!")
            st.cache_data.clear()
    st.markdown('</div>', unsafe_allow_html=True)

# 兜底：如果输入了错误的 page 参数，自动跳回 home
else:
    st.markdown('<meta http-equiv="refresh" content="0;url=/?page=home">', unsafe_allow_html=True)