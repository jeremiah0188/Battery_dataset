import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 1. 初始化 Session State 与 页面路由 =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Homepage"
if "search_kw" not in st.session_state:
    st.session_state.search_kw = ""

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

current_page = st.session_state.current_view

# ================= 3. 动态背景引擎 (每个页面专属渐变色) =================
bg_gradients = {
    "Homepage": "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 45%, #EEF2FF 100%)",
    "Browse Datasets": "linear-gradient(135deg, #F0FDF4 0%, #F8FAFC 50%, #ECFEFF 100%)",
    "Contribute Data": "linear-gradient(135deg, #FFFBEB 0%, #F8FAFC 50%, #FEF3C7 100%)",
    "About": "linear-gradient(135deg, #F5F3FF 0%, #F8FAFC 50%, #E0E7FF 100%)",
    "Contact": "linear-gradient(135deg, #FEF2F2 0%, #F8FAFC 50%, #FFEDD5 100%)",
    "login": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "signup": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "Admin Dashboard": "linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%)"
}
current_bg = bg_gradients.get(current_page, "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 100%)")

dynamic_css = f"""
<style>
    .stApp {{
        background: {current_bg} !important;
        background-attachment: fixed !important; 
        transition: background 0.8s ease-in-out !important; 
    }}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)

# ================= 4. 企业级专业 CSS (包含全新微动画) =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp { font-family: 'Inter', -apple-system, sans-serif; color: #334155; }
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}

    .block-container { 
        max-width: 95% !important; 
        padding-top: 1.5rem !important; 
        padding-bottom: 2rem !important; 
    }

    /* ================= 🚀 核心修复：彻底扒掉外层导航的多层白卡 ================= */
    /* 1. 外层容器透明化 */
    div[data-testid="stVerticalBlock"]:has(.header-wrapper) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        animation: headerSlideDown 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        z-index: 999;
    }

    /* 2. 暴力清除内部所有子容器(包括Columns)的背景，解决"好几层"的问题 */
    div[data-testid="stVerticalBlock"]:has(.header-wrapper) * {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    @keyframes headerSlideDown {
        0% { opacity: 0; transform: translateY(-40px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    /* ========================================================================= */

    /* 全局内容白卡样式 (这里避开了 header-wrapper，只作用于内容区) */
    [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.header-wrapper)) {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04) !important;
        padding: 24px !important;
        margin-bottom: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.header-wrapper)):hover { 
        box-shadow: 0 15px 35px rgba(15, 23, 42, 0.06) !important; 
    }

    /* 全局按钮 Slate Gray (#708090) */
    .stButton>button { 
        background-color: #708090 !important; 
        border: none !important; 
        color: #FFFFFF !important; 
        font-weight: 700 !important; 
        border-radius: 50px !important; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; 
        height: 44px !important;
        padding: 0 24px !important; 
        letter-spacing: 0.5px;
        box-shadow: 0 4px 10px rgba(112, 128, 144, 0.3) !important;
    }
    .stButton>button:hover { 
        background-color: #5c6a77 !important; 
        box-shadow: 0 6px 16px rgba(112, 128, 144, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* Tabs 强制加粗 */
    [data-baseweb="tab"] { padding-top: 8px !important; padding-bottom: 8px !important; }
    [data-baseweb="tab"] p { font-weight: 800 !important; font-size: 16px !important; color: #64748B; transition: color 0.3s; }
    [data-baseweb="tab"][aria-selected="true"] p { color: #0F172A !important; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #4A6D5F !important; height: 3px !important; border-radius: 3px 3px 0 0; }

    /* 文字层级悬浮微动画 */
    .section-header h2 { 
        font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; 
        transition: all 0.3s ease; 
    }
    .section-header:hover h2 {
        color: #4A6D5F; 
        transform: translateX(6px); 
    }

    .hero-title { 
        font-size: 4.8rem; font-weight: 900; line-height: 1.1; color: #0F172A; 
        margin-bottom: 1.5rem; letter-spacing: -2px; 
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    .hero-title:hover {
        transform: scale(1.02); 
    }

    /* 无边框列表行 Hover 样式 */
    .dataset-list-row {
        display: flex; padding: 18px 24px; font-size: 14px; border-bottom: 1px solid #F1F5F9;
        align-items: center; transition: all 0.2s ease; background-color: transparent;
    }
    .dataset-list-row .ds-name {
        transition: color 0.2s ease;
    }
    .dataset-list-row:hover { 
        background-color: #F8FAFC !important; 
    }
    .dataset-list-row:hover .ds-name {
        color: #4A6D5F !important; 
    }

    .hero-container {
        display: flex; align-items: center; justify-content: space-between;
        padding: 4.5rem 4rem; 
        background: radial-gradient(circle at top left, #FFFFFF 0%, rgba(255,255,255,0.4) 100%);
        border-radius: 24px; border: 1px solid #FFFFFF; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.03);
        margin-bottom: 2rem; gap: 4rem; backdrop-filter: blur(10px);
    }
    .hero-left { flex: 1.2; }
    .hero-subtitle { font-size: 14px; font-weight: 800; color: #4A6D5F; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; }
    .hero-title span { background: linear-gradient(135deg, #4A6D5F 0%, #115E59 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 1.25rem; color: #475569; line-height: 1.7; margin-bottom: 2rem; }

    .hero-right { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .bento-card { border-radius: 20px; padding: 28px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.04); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255,255,255,0.5);}
    .bento-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

    .chem-tag { background: rgba(255,255,255,0.8); padding:8px 16px; border-radius:30px; font-size:13px; font-weight:800; box-shadow:0 2px 8px rgba(0,0,0,0.04); color:#0F172A; border: 1px solid rgba(0,0,0,0.02); display: inline-block; margin: 4px;}

    .section-header { border: 1px solid #FFFFFF; border-radius: 16px; padding: 16px 24px; margin-bottom: 20px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); transition: all 0.3s;}
    .header-blue { border-left: 5px solid #3B82F6; }
    .header-teal { border-left: 5px solid #4A6D5F; }
    .header-amber { border-left: 5px solid #F59E0B; }

    .metadata-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
    .metadata-item { background: rgba(255, 255, 255, 0.5); border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; transition: background 0.3s; }
    .metadata-item:hover { background: #FFFFFF; }
    .metadata-label { font-size: 12px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
    .metadata-value { font-size: 15px; font-weight: 600; color: #0F172A; word-wrap: break-word; }

    .custom-footer { width: 100%; padding: 40px 16px 20px 16px; margin-top: 40px; color: #64748B; font-size: 14px; border-top: 1px solid #E2E8F0; display: flex; flex-direction: column; gap: 16px; }
    .footer-links { display: flex; align-items: center; flex-wrap: wrap; gap: 16px; font-weight: 600; }
    .footer-links a { color: #475569; text-decoration: none; transition: color 0.2s; }
    .footer-links a:hover { color: #4A6D5F; }
    .footer-separator { color: #CBD5E1; font-weight: 400; }
    .footer-copyright { color: #94A3B8; font-size: 13px; }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ================= 5. 顶部导航栏 (🚀 外层彻底透明，内层胶囊实体化) =================
LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"

# 外层包裹：这里的 header-wrapper 能让上面的 CSS 生效，强制去掉了这里所有的边框和背景
with st.container():
    st.markdown('<div class="header-wrapper" style="display:none;"></div>', unsafe_allow_html=True)

    col_logo, col_menu, col_auth = st.columns([1.5, 8.5, 1.2], vertical_alignment="center")

    with col_logo:
        st.image(LOGO_IMAGE_URL, width=190)

    with col_menu:
        if st.session_state.current_view not in ["login", "signup"]:
            menu_tabs = ["Homepage", "Browse Datasets", "Contribute Data", "About", "Contact"]
            if st.session_state.is_admin:
                menu_tabs.append("Admin Dashboard")

            try:
                default_idx = menu_tabs.index(st.session_state.current_view)
            except ValueError:
                default_idx = 0

            # 🚀 移除了 !important 和复杂的 rgba，让 React 组件能正常解析并渲染独立白底和动画
            selected_page = option_menu(
                menu_title=None,
                options=menu_tabs,
                icons=['house', 'search', 'cloud-upload', 'info-circle', 'envelope', 'shield-lock'],
                default_index=default_idx,
                orientation="horizontal",
                styles={
                    "container": {
                        "padding": "10px",
                        "background-color": "#ffffff",
                        "border": "1px solid #E2E8F0",
                        "border-radius": "100px",
                        "box-shadow": "0 6px 20px rgba(0,0,0,0.06)",
                        "width": "100%",
                        "display": "flex",
                        "justify-content": "center"
                    },
                    "icon": {
                        "color": "#64748B",
                        "font-size": "16px"
                    },
                    "nav-link": {
                        "font-size": "15px",
                        "font-weight": "700",
                        "color": "#475569",
                        "padding": "10px 20px",
                        "margin": "0 4px",
                        "border-radius": "50px",
                        "transition": "background-color 0.3s ease, color 0.3s ease",
                        "--hover-color": "#F1F5F9"  # ✨ 现在这里生效了，鼠标放上会有浅灰底色！
                    },
                    "nav-link-selected": {
                        "background-color": "#4A6D5F",
                        "color": "#ffffff",
                        "font-weight": "800",
                        "border-radius": "50px"
                    },
                }
            )
            if selected_page != st.session_state.current_view:
                st.session_state.current_view = selected_page
                st.rerun()

    with col_auth:
        if st.session_state.is_admin:
            if st.button("Log Out"):
                st.session_state.is_admin = False
                st.session_state.current_view = "Homepage"
                st.rerun()
        else:
            if st.session_state.current_view not in ["login", "signup"]:
                if st.button("Sign In"):
                    st.session_state.current_view = "login"
                    st.rerun()

# ================= 6. 🔗 Google Sheets 数据库配置 =================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL)
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        df = df.fillna('')
        df = df.astype(str)
        if 'Status' not in df.columns: df['Status'] = 'Approved'
        return df
    except:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain', 'Category', 'Sub-category', 'Status'])


df = load_data()
public_df = df[df['Status'] == 'Approved']

# ================= 7. 核心路由与页面内容渲染 =================

# ----------------- 页面 A：登录页 (Login) -----------------
if current_page == "login" and not st.session_state.is_admin:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(
                "<h2 style='font-size: 34px; font-weight: 900; color: #0F172A; margin-bottom: 8px; text-align: center;'>Welcome Back</h2>",
                unsafe_allow_html=True)
            st.markdown(
                "<p style='color: #64748B; font-size: 15px; margin-bottom: 32px; line-height: 1.6; text-align: center;'>Sign in to access the contributor dashboard.</p>",
                unsafe_allow_html=True)
            email_input = st.text_input("Email address", placeholder="name@company.com")
            pwd_input = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In", use_container_width=True):
                if pwd_input == st.secrets.get("admin_password", ""):
                    st.session_state.is_admin = True
                    st.session_state.current_view = "Homepage"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

            st.markdown("<hr style='border-color: #E2E8F0; margin: 32px 0 24px 0;'>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Create an Account", use_container_width=True):
                    st.session_state.current_view = "signup"
                    st.rerun()
            with c2:
                if st.button("Return Home", use_container_width=True):
                    st.session_state.current_view = "Homepage"
                    st.rerun()

# ----------------- 页面 B：注册页 (Sign Up) -----------------
elif current_page == "signup" and not st.session_state.is_admin:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown(
                "<h2 style='font-size: 34px; font-weight: 900; color: #0F172A; margin-bottom: 8px; text-align: center;'>Create Account</h2>",
                unsafe_allow_html=True)
            st.markdown(
                "<p style='color: #64748B; font-size: 15px; margin-bottom: 32px; line-height: 1.6; text-align: center;'>Join the Open Battery Dataset Portal to contribute and track your submissions.</p>",
                unsafe_allow_html=True)

            st.text_input("Full Name", placeholder="e.g. John Doe")
            st.text_input("Email address", placeholder="name@company.com")
            st.text_input("Password", type="password", placeholder="Create a strong password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Register Account", use_container_width=True):
                st.info("Registration is temporarily closed. Please contact the administrator.")

            st.markdown("<hr style='border-color: #E2E8F0; margin: 32px 0 24px 0;'>", unsafe_allow_html=True)

            c3, c4 = st.columns(2)
            with c3:
                if st.button("Already have an account? Sign In", use_container_width=True):
                    st.session_state.current_view = "login"
                    st.rerun()
            with c4:
                if st.button("Return to Homepage", use_container_width=True):
                    st.session_state.current_view = "Homepage"
                    st.rerun()

# ----------------- 页面 C：Homepage -----------------
elif current_page == "Homepage":
    chem_tags_html = "".join(
        [f'<span class="chem-tag">{c}</span>' for c in ["NMC", "LFP", "NCA", "LCO", "LMO", "Solid-state"]])
    hero_html = (
        '<div class="hero-container">'
        '<div class="hero-left">'
        '<div class="hero-subtitle">Open Source Data & Analytics</div>'
        '<div class="hero-title">Battery Data <br><span>Differently</span></div>'
        '<div class="hero-desc">We deliver high-fidelity, peer-reviewed battery datasets and robust metadata integration tailored to meet the evolving needs of global energy research.</div>'
        '</div>'
        '<div class="hero-right">'
        '<div class="bento-card" style="grid-row:span 2; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); min-height:320px;">'
        '<div style="font-size: 14px; font-weight:800; color: #1E3A8A; text-transform:uppercase; opacity: 0.8;">Platform Metrics</div>'
        '<div>'
        f'<div style="font-size: 72px; font-weight: 900; color: #172554; margin-top: auto; line-height:1;">{len(public_df)}+</div>'
        '<div style="font-size: 18px; color: #1E40AF; font-weight:700; margin-top:12px;">Curated Datasets</div>'
        '</div></div>'
        '<div class="bento-card" style="background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); min-height: 160px;">'
        '<div style="font-size: 14px; font-weight:800; color: #14532D; text-transform:uppercase; opacity: 0.9;">A Leader in Quality</div>'
        '<div style="font-size: 28px; font-weight: 900; color: #064E3B; margin-top: auto;">Open Access</div>'
        '</div>'
        '<div class="bento-card" style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); min-height: 160px; border: 1px solid #FDE68A;">'
        '<div style="font-size: 14px; font-weight:800; color: #92400E; text-transform:uppercase;">Supported Chemistry</div>'
        f'<div style="margin-top: auto;">{chem_tags_html}</div>'
        '</div></div></div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.markdown('<div class="section-header header-teal"><h2>🌟 Latest Additions</h2></div>',
                    unsafe_allow_html=True)
        latest_datasets = public_df.tail(3)
        if not latest_datasets.empty:
            for _, row in latest_datasets.iterrows():
                with st.container(border=True):
                    st.markdown(f"{row.get('Dataset Name', 'Unnamed')}")
                    st.caption(
                        f"Domain: {row.get('Domain', 'N/A')} | Chem: {row.get('Battery Chemistry', 'N/A')} | Added by: {row.get('Author', 'Unknown')}")
        else:
            st.info("No datasets available yet.")

    with c_right:
        st.markdown('<div class="section-header header-amber"><h2>🔥 Popular Tags</h2></div>', unsafe_allow_html=True)
        with st.container(border=True):
            tags = ["EIS", "SOH", "RUL", "Time-Series", "Aging", "Simulation"]
            tags_html = "".join(
                [f'<span class="chem-tag" style="background:#F1F5F9; border-color:#CBD5E1;">{t}</span>' for t in tags])
            st.markdown(f"<div>{tags_html}</div><br>", unsafe_allow_html=True)
            st.info("💡 Tip: Use these keywords in the search bar.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header header-blue"><h2>💬 Quick FAQ</h2></div>', unsafe_allow_html=True)
    with st.expander("Do I need an account to download data?"):
        st.write(
            "No. All curated datasets on our platform are open-access and do not require an account to browse or download source files.")
    with st.expander("How long does the moderation review take?"):
        st.write(
            "Our admin team typically reviews submitted datasets within 48-72 hours to ensure metadata quality and source validity.")

# ----------------- 页面 D：Browse Datasets -----------------
elif current_page == "Browse Datasets":
    st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        with st.container(border=True):
            st.markdown(
                "<h3 style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:16px;'>🔍 Filters</h3>",
                unsafe_allow_html=True)
            search_kw = st.text_input("Keyword Search", value=st.session_state.search_kw,
                                      placeholder="e.g. Oxford, NMC, EIS...")
            st.session_state.search_kw = search_kw

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

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.7); padding: 12px 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px;">
            <div style="font-size: 15px; font-weight: 700; color: #0F172A;">
                <span style="background: #4A6D5F; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-right: 8px;">{len(filtered_df)}</span> Datasets Found
            </div>
            <div style="font-size: 13px; color: #64748B; font-weight: 500;">
                Sort by: <span style="color: #0F172A; font-weight: 700; cursor: pointer;">Most Recent</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_df.empty:
            html_parts = []
            html_parts.append(
                '<div style="border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; background: #FFFFFF; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.02);">')
            html_parts.append(
                '<div style="display: flex; background-color: #F8FAFC; padding: 14px 24px; font-size: 13px; font-weight: 700; color: #475569; border-bottom: 1px solid #E2E8F0; text-transform: uppercase; letter-spacing: 0.5px;">')
            html_parts.append(
                '<div style="flex: 2.5;">Dataset Name</div><div style="flex: 1.5;">Author</div><div style="flex: 1;">Domain</div><div style="flex: 0.8; text-align: right;">Action</div></div>')

            for _, row in filtered_df.iterrows():
                raw_author = str(row.get('Author', 'Unspecified')).strip()
                if raw_author in ['Unspecified', 'N/A', '', 'nan']:
                    display_author = '<span style="color:#94A3B8; font-style:italic;">Unspecified</span>'
                else:
                    if ',' in raw_author:
                        first_author = raw_author.split(',')[0].strip()
                        display_author = f"{first_author} <span style='color:#94A3B8; font-weight:500;'>et al.</span>"
                    elif ' and ' in raw_author:
                        first_author = raw_author.split(' and ')[0].strip()
                        display_author = f"{first_author} <span style='color:#94A3B8; font-weight:500;'>et al.</span>"
                    elif len(raw_author) > 25:
                        display_author = raw_author[:22] + "..."
                    else:
                        display_author = raw_author

                ds_name = row.get('Dataset Name', 'Unnamed')
                domain = row.get('Domain', 'N/A')

                html_parts.append('<div class="dataset-list-row">')
                # 🚀 将标题赋予 ds-name class，响应 CSS 悬浮变色
                html_parts.append(
                    f'<div class="ds-name" style="flex: 2.5; font-weight: 700; color: #0F172A; padding-right: 16px;">{ds_name}</div>')
                html_parts.append(
                    f'<div style="flex: 1.5; color: #475569; padding-right: 16px;" title="{raw_author}">{display_author}</div>')
                html_parts.append(
                    f'<div style="flex: 1; color: #64748B;"><span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600;">{domain}</span></div>')
                html_parts.append(
                    '<div style="flex: 0.8; text-align: right;"><span style="background: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; padding: 6px 14px; border-radius: 50px; font-size: 12px; font-weight: 700; cursor: default;">View ↓</span></div>')
                html_parts.append('</div>')

            html_parts.append('</div>')
            final_list_html = "".join(html_parts)
            st.markdown(final_list_html, unsafe_allow_html=True)

            st.markdown(
                '<div class="section-header header-teal" style="margin-top: 32px;"><h2>📖 Dataset Details</h2></div>',
                unsafe_allow_html=True)
            valid_datasets = filtered_df[filtered_df['Dataset Name'] != '']
            selected_dataset = st.selectbox("Select a dataset to view full details:",
                                            ["(Select to view)"] + valid_datasets['Dataset Name'].tolist(),
                                            label_visibility="collapsed")

            if selected_dataset != "(Select to view)":
                details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]

                details_html = (
                    '<div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); padding: 32px; margin-bottom: 24px;">'
                    f'<h2 style="font-size: 28px; font-weight:900; color: #0F172A; margin-bottom: 8px;">{selected_dataset}</h2>'
                    f'<p style="color: #64748B; font-size: 15px; margin-bottom: 24px; font-weight:500;">Source: {details.get("Source Organization", details.get("Author", "N/A"))}</p>'
                )

                link = details.get('Link', '')
                if link.startswith('http'):
                    details_html += f'<div style="margin-bottom: 24px;"><a href="{link}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:12px 28px; text-decoration:none; border-radius:50px; font-weight:700; font-size:14px; box-shadow: 0 4px 10px rgba(74,109,95,0.2); transition: transform 0.2s;">🔗 Download / Visit Source</a></div>'

                details_html += '<div class="metadata-grid">'
                for col_name in df.columns:
                    if str(col_name).strip() and "Unnamed" not in str(col_name) and col_name not in ['Link', 'Status',
                                                                                                     'Dataset Name']:
                        val = str(details.get(col_name, '')).strip()
                        if val and val.lower() not in ['nan', 'none', 'n/a', 'na', 'null', '']:
                            details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                details_html += '</div>'

                details_html += f'<div style="margin-top:32px; padding:16px; background:rgba(255,255,255,0.6); border-left:4px solid #4A6D5F; border-radius:8px;"><h4 style="margin:0 0 8px 0; font-size:14px; color:#0F172A;">📚 How to Cite</h4><p style="margin:0; font-size:13px; color:#475569;">Data accessed from the Open Battery Dataset Portal (2026). Original source: {details.get("Source Organization", "N/A")}. Dataset: {selected_dataset}.</p></div>'
                details_html += '</div>'

                st.markdown(details_html, unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ----------------- 页面 E：Contribute Data -----------------
elif current_page == "Contribute Data":
    st.markdown('<div class="section-header header-teal"><h2>Community Contributions</h2></div>',
                unsafe_allow_html=True)

    tab_submit, tab_request, tab_guide = st.tabs(["Submit a Dataset", "Request a Dataset", "Submission Guidelines"])

    with tab_submit:
        with st.container(border=True):
            st.write(
                "Help expand this curated dataset hub. Please provide standardized metadata to improve discoverability.")
            with st.form("upload_form", border=False):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Dataset Name *")
                new_desc = c2.text_input("Short Description *")

                c1b, c2b, c3b = st.columns(3)
                new_domain = c1b.selectbox("Domain *",
                                           ["Energy", "Healthcare", "Manufacturing", "Transportation", "Other"])
                new_category = c2b.text_input("Category (e.g., Battery, Grid)")
                new_subcat = c3b.text_input("Sub-category (e.g., Time-Series, EIS)")

                new_link = st.text_input("Source URL * (External Download Link)")
                new_org = st.text_input("Source Organization / Publisher")

                c8, c9 = st.columns(2)
                new_contributor = c8.text_input("Contributor Name *")
                new_email = c9.text_input("Contact Email (Optional)")

                if st.form_submit_button("Submit to Moderation Queue"):
                    if not new_name or not new_domain or not new_link or not new_contributor:
                        st.error("Please fill in all required fields marked with *")
                    else:
                        new_row = {c: "" for c in df.columns}
                        new_row.update({'Dataset Name': new_name, 'Domain': new_domain, 'Category': new_category,
                                        'Sub-category': new_subcat, 'Short Description': new_desc, 'Link': new_link,
                                        'Source Organization': new_org, 'Author': new_contributor,
                                        'Contributor Email': new_email, 'Status': 'Pending'})
                        updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                        st.success("Successfully submitted to the moderation queue!")
                        st.cache_data.clear()

    with tab_request:
        with st.container(border=True):
            st.markdown("### Can't find what you're looking for?")
            st.write(
                "Submit a request. If our community or admins find relevant open-source data, we'll add it to the platform.")
            with st.form("request_form", border=False):
                st.text_input("Requested Topic / Dataset Name *", placeholder="e.g. Real-world EV charging profiles")
                st.text_area("Additional Details",
                             placeholder="Specify any required parameters, chemistry, or format...")
                st.text_input("Your Email (to notify you if found)")
                if st.form_submit_button("Submit Request"):
                    st.success("Request submitted successfully! We will keep an eye out for this data.")

    with tab_guide:
        with st.container(border=True):
            st.markdown("### 📖 Curation Policy & Metadata Standards")
            st.write("""
            * Public Domain Only: Ensure the dataset you are submitting is publicly available or you hold the rights to share it.
            * URL Validity: Provide direct links to repositories (GitHub, Mendeley, Zenodo) rather than generic homepages.
            * Accuracy: Fill out the Chemistry and Data Type fields accurately to help researchers filter effectively.
            """)

# ----------------- 页面 F & G：About & Contact -----------------
elif current_page == "About":
    about_html = """
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); padding: 40px; margin-bottom: 24px;">
        <div class="section-header header-blue"><h2 style="margin: 0;">About This Platform</h2></div>
        <p style="margin-top:20px; font-size: 16px; line-height: 1.8; color: #475569;">This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.</p>
        <p style="font-size: 16px; line-height: 1.8; color: #475569;">Maintained by <strong style="color:#0F172A;">Jian Wu</strong>, focusing on battery data analysis and SOH estimation.</p>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)

elif current_page == "Contact":
    contact_html = """
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); text-align: center; padding: 100px 20px;">
        <h2 style="color:#0F172A; font-weight:900; margin-bottom:16px; font-size: 42px;">Get in Touch</h2>
        <p style='font-size: 18px; color: #475569; margin-bottom: 32px;'>For questions, dataset suggestions, collaboration, or corrections, please contact:</p>
        <a href="mailto:jian.wu@utbm.fr" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:16px 40px; text-decoration:none; border-radius:50px; font-weight:800; font-size:18px; box-shadow: 0 6px 20px rgba(74,109,95,0.25); transition: transform 0.2s;">✉️ jian.wu@utbm.fr</a>
    </div>
    """
    st.markdown(contact_html, unsafe_allow_html=True)

# ----------------- 页面 H：Admin Dashboard -----------------
elif current_page == "Admin Dashboard" and st.session_state.is_admin:
    st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(df, column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                       use_container_width=True, num_rows="dynamic")
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized successfully!")
                st.cache_data.clear()

# ======== 8. 全局自定义 Footer ========
st.markdown("""
<div class="custom-footer">
    <div class="footer-links">
        <a href="#">Citation Policy</a> <span class="footer-separator">/</span>
        <a href="#">Changelog</a> <span class="footer-separator">/</span>
        <a href="#">Terms & Privacy</a>
    </div>
    <div class="footer-copyright">
        © 2026 Open Battery Dataset Portal. Maintained by Jian Wu.
    </div>
</div>
""", unsafe_allow_html=True)