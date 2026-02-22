import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ================= 1. 初始化 Session State 与 页面路由 =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Homepage"
if "last_menu_selection" not in st.session_state:
    st.session_state.last_menu_selection = "Homepage"
if "search_kw" not in st.session_state:
    st.session_state.search_kw = ""
if "nav_click" not in st.session_state:
    st.session_state.nav_click = ""

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
    "Admin Dashboard": "linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%)",
    "Settings": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "Notifications": "linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%)"
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

# ================= 4. 专业 CSS =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp { font-family: 'Inter', -apple-system, sans-serif; color: #334155; }
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}

    .block-container {
        max-width: 95% !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04) !important;
        padding: 24px !important;
        margin-bottom: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 15px 35px rgba(15, 23, 42, 0.06) !important;
    }

    /* ================= 顶部导航区域 ================= */
    .nav-shell { width: 100%; display: block; }

    div[data-testid="stVerticalBlock"]:has(.nav-shell),
    div[data-testid="stVerticalBlock"]:has(.nav-shell) > div,
    div[data-testid="stVerticalBlock"]:has(.nav-shell) [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlock"]:has(.nav-shell) [data-testid="stHorizontalBlock"],
    div[data-testid="stVerticalBlock"]:has(.nav-shell) [data-testid="column"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stVerticalBlock"]:has(.nav-shell) {
        margin-bottom: 1.5rem !important;
        animation: headerSlideDown 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }

    @keyframes headerSlideDown {
        0% { opacity: 0; transform: translateY(-40px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* 导航按钮容器 */
    .nav-menu-row {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: nowrap;
        overflow-x: auto;
        white-space: nowrap;
        padding-top: 4px;
    }
    .nav-menu-row::-webkit-scrollbar { height: 0; }

    /* 顶部导航按钮（纯文字，无胶囊） */
    .nav-text-btn .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        color: #64748B !important;
        font-weight: 700 !important;
        font-size: 18px !important;   /* ✅ 导航字体大小在这里调 */
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 4px 8px 4px !important;
        margin: 0 !important;
        letter-spacing: 0 !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.25s ease !important;
        justify-content: center !important;
    }
    .nav-text-btn .stButton > button:hover {
        color: #4A6D5F !important;
        background: transparent !important;
        transform: translateY(-1px) !important;
        box-shadow: none !important;
    }

    /* 当前激活项（给不同 key 单独套 class） */
    .nav-active .stButton > button {
        color: #4A6D5F !important;
        font-weight: 800 !important;
        border-bottom-color: #4A6D5F !important;
    }

    /* 顶部搜索栏 */
    .nav-search .stTextInput input {
        border-radius: 14px !important;
        background-color: #F1F5F9 !important;
        border: 1px solid transparent !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        transition: all 0.3s ease;
    }
    .nav-search .stTextInput input:focus {
        background-color: #FFFFFF !important;
        border-color: #4A6D5F !important;
        box-shadow: 0 0 0 3px rgba(74, 109, 95, 0.12) !important;
    }

    /* 顶部图标按钮 */
    .icon-btn-wrap .stButton > button {
        width: 54px !important;
        height: 54px !important;
        min-width: 54px !important;
        min-height: 54px !important;
        padding: 0 !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.75) !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        font-size: 20px !important;
        color: #64748B !important;
        transition: all 0.25s ease !important;
    }
    .icon-btn-wrap .stButton > button:hover {
        color: #4A6D5F !important;
        border-color: #BFC7D2 !important;
        background: rgba(255,255,255,0.95) !important;
        transform: translateY(-1px) !important;
    }

    /* 顶部登录按钮 */
    .nav-auth .stButton>button {
        background-color: #708090 !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        height: 44px !important;
        padding: 0 24px !important;
        box-shadow: 0 4px 10px rgba(112, 128, 144, 0.3) !important;
    }
    .nav-auth .stButton>button:hover {
        background-color: #5c6a77 !important;
        box-shadow: 0 6px 16px rgba(112, 128, 144, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* 其他全局保持不变 */
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

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div { border-radius: 12px !important; }
    [data-baseweb="tab"] { padding-top: 8px !important; padding-bottom: 8px !important; }
    [data-baseweb="tab"] p { font-weight: 800 !important; font-size: 16px !important; color: #64748B; transition: color 0.3s; }
    [data-baseweb="tab"][aria-selected="true"] p { color: #0F172A !important; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #4A6D5F !important; height: 3px !important; border-radius: 3px 3px 0 0; }

    .section-header h2 { font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; transition: all 0.3s ease; }
    .section-header:hover h2 { color: #4A6D5F; transform: translateX(6px); }

    .hero-title { font-size: 4.8rem; font-weight: 900; line-height: 1.1; color: #0F172A; margin-bottom: 1.5rem; letter-spacing: -2px; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
    .hero-title:hover { transform: scale(1.02); }

    .dataset-list-row { display: flex; padding: 18px 24px; font-size: 14px; border-bottom: 1px solid #F1F5F9; align-items: center; transition: all 0.2s ease; background-color: transparent; }
    .dataset-list-row .ds-name { transition: color 0.2s ease; }
    .dataset-list-row:hover { background-color: #F8FAFC !important; }
    .dataset-list-row:hover .ds-name { color: #4A6D5F !important; }

    .hero-container {
        display: flex; align-items: center; justify-content: space-between; padding: 4.5rem 4rem; background: radial-gradient(circle at top left, #FFFFFF 0%, rgba(255,255,255,0.4) 100%);
        border-radius: 24px; border: 1px solid #FFFFFF; box-shadow: 0 10px 40px rgba(0,0,0,0.03); margin-bottom: 2rem; gap: 4rem; backdrop-filter: blur(10px);
    }
    .hero-left { flex: 1.2; }
    .hero-subtitle { font-size: 14px; font-weight: 800; color: #4A6D5F; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; }
    .hero-title span { background: linear-gradient(135deg, #4A6D5F 0%, #115E59 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 1.25rem; color: #475569; line-height: 1.7; margin-bottom: 2rem; }

    .hero-right { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .bento-card { border-radius: 20px; padding: 28px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.04); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255,255,255,0.5); }
    .bento-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

    .chem-tag { background: rgba(255,255,255,0.8); padding:8px 16px; border-radius:30px; font-size:13px; font-weight:800; box-shadow:0 2px 8px rgba(0,0,0,0.04); color:#0F172A; border: 1px solid rgba(0,0,0,0.02); display: inline-block; margin: 4px; }

    .section-header { border: 1px solid #FFFFFF; border-radius: 16px; padding: 16px 24px; margin-bottom: 20px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); transition: all 0.3s; }
    .header-blue { border-left: 5px solid #3B82F6; }
    .header-teal { border-left: 5px solid #4A6D5F; }
    .header-amber { border-left: 5px solid #F59E0B; }

    .metadata-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    .metadata-item {
        background: rgba(255, 255, 255, 0.5);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        transition: background 0.3s;
    }
    .metadata-item:hover { background: #FFFFFF; }
    .metadata-label {
        font-size: 12px;
        font-weight: 800;
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

    .custom-footer { width: 100%; padding: 40px 16px 20px 16px; margin-top: 40px; color: #64748B; font-size: 14px; border-top: 1px solid #E2E8F0; display: flex; flex-direction: column; gap: 16px; }
    .footer-links { display: flex; align-items: center; flex-wrap: wrap; gap: 16px; font-weight: 600; }
    .footer-links a { color: #475569; text-decoration: none; transition: color 0.2s; }
    .footer-links a:hover { color: #4A6D5F; }
    .footer-separator { color: #CBD5E1; font-weight: 400; }
    .footer-copyright { color: #94A3B8; font-size: 13px; }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)


# ================= 5. 顶部导航栏 =================
LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"

with st.container():
    st.markdown('<div class="nav-shell">', unsafe_allow_html=True)

    # 这里调布局宽度（菜单、搜索、图标、登录按钮占比）
    col_logo, col_menu, col_search, col_icons, col_auth = st.columns(
        [1.45, 6.9, 2.35, 1.1, 1.2],
        vertical_alignment="center"
    )

    with col_logo:
        st.image(LOGO_IMAGE_URL, width=200)  # ✅ logo 大小在这里调（比如 170 / 185 / 200）

    with col_menu:
        if st.session_state.current_view not in ["login", "signup"]:
            menu_tabs = ["Homepage", "Browse Datasets", "Contribute Data", "About", "Contact"]
            if st.session_state.is_admin:
                menu_tabs.append("Admin Dashboard")

            active_tab = (
                st.session_state.current_view
                if st.session_state.current_view in menu_tabs
                else st.session_state.last_menu_selection
            )

            st.markdown('<div class="nav-menu-row">', unsafe_allow_html=True)

            # 为了让文字按钮精确对齐，按文字长度给不同列宽
            if st.session_state.is_admin:
                nav_cols = st.columns([1.35, 2.05, 2.15, 1.0, 1.0, 1.8])
            else:
                nav_cols = st.columns([1.35, 2.05, 2.15, 1.0, 1.0])

            def render_nav_button(col, label, page_name, key_name):
                wrapper_cls = "nav-text-btn nav-active" if active_tab == page_name else "nav-text-btn"
                with col:
                    st.markdown(f'<div class="{wrapper_cls}">', unsafe_allow_html=True)
                    if st.button(label, key=key_name):
                        st.session_state.current_view = page_name
                        st.session_state.last_menu_selection = page_name
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            render_nav_button(nav_cols[0], "Homepage", "Homepage", "nav_home_btn")
            render_nav_button(nav_cols[1], "Browse Datasets", "Browse Datasets", "nav_browse_btn")
            render_nav_button(nav_cols[2], "Contribute Data", "Contribute Data", "nav_contribute_btn")
            render_nav_button(nav_cols[3], "About", "About", "nav_about_btn")
            render_nav_button(nav_cols[4], "Contact", "Contact", "nav_contact_btn")

            if st.session_state.is_admin:
                render_nav_button(nav_cols[5], "Admin Dashboard", "Admin Dashboard", "nav_admin_btn")

            st.markdown('</div>', unsafe_allow_html=True)

    with col_search:
        if st.session_state.current_view not in ["login", "signup"]:
            st.markdown('<div class="nav-search">', unsafe_allow_html=True)
            st.text_input(
                "Global Search",
                placeholder="Search datasets...",
                label_visibility="collapsed",
                key="global_nav_search"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    with col_icons:
        if st.session_state.current_view not in ["login", "signup"]:
            c_icon1, c_icon2 = st.columns(2)

            with c_icon1:
                st.markdown('<div class="icon-btn-wrap">', unsafe_allow_html=True)
                if st.button("⚙", help="Settings", key="nav_settings_btn"):
                    st.session_state.current_view = "Settings"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with c_icon2:
                st.markdown('<div class="icon-btn-wrap">', unsafe_allow_html=True)
                if st.button("🔔", help="Notifications", key="nav_notifications_btn"):
                    st.session_state.current_view = "Notifications"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with col_auth:
        st.markdown('<div class="nav-auth">', unsafe_allow_html=True)
        if st.session_state.is_admin:
            if st.button("Log Out", key="nav_logout_btn"):
                st.session_state.is_admin = False
                st.session_state.current_view = "Homepage"
                st.session_state.last_menu_selection = "Homepage"
                st.rerun()
        else:
            if st.session_state.current_view not in ["login", "signup"]:
                if st.button("Sign In", key="nav_signin_btn"):
                    st.session_state.current_view = "login"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= 6. Google Sheets 数据库配置 =================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL)
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1).fillna('').astype(str)
        if 'Status' not in df.columns:
            df['Status'] = 'Approved'
        return df
    except Exception:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain', 'Category', 'Sub-category', 'Status'])


df = load_data()
public_df = df[df['Status'] == 'Approved'] if 'Status' in df.columns else df.copy()

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
                    st.session_state.last_menu_selection = "Homepage"
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
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False, regex=False)).any(
                axis=1)
            filtered_df = filtered_df[mask]

        if sel_domain != "All" and 'Domain' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Domain'] == sel_domain]
        if sel_category != "All" and 'Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Category'] == sel_category]
        if sel_subcategory != "All" and 'Sub-category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Sub-category'] == sel_subcategory]

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; gap:8px; flex-wrap:wrap; background: rgba(255,255,255,0.7); padding: 12px 16px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #0F172A;">
                <span style="background: #4A6D5F; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-right: 8px;">{len(filtered_df)}</span> Datasets Found
            </div>
            <div style="font-size: 13px; color: #64748B; font-weight: 500;">
                Sort by: <span style="color: #0F172A; font-weight: 700;">Most Recent</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_df.empty:
            html_parts = []
            html_parts.append(
                '<div style="border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; background: #FFFFFF; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.02);">')
            html_parts.append(
                '<div class="dataset-list-header" style="display: flex; background-color: #F8FAFC; padding: 14px 24px; font-size: 13px; font-weight: 700; color: #475569; border-bottom: 1px solid #E2E8F0; text-transform: uppercase; letter-spacing: 0.5px;">')
            html_parts.append(
                '<div style="flex: 2.5;">Dataset Name</div><div style="flex: 1.5;">Author</div><div style="flex: 1;">Domain</div><div style="flex: 0.8; text-align: right;">Action</div></div>')

            for _, row in filtered_df.iterrows():
                raw_author = str(row.get('Author', 'Unspecified')).strip()
                if raw_author in ['Unspecified', 'N/A', '', 'nan']:
                    display_author = '<span style="color:#94A3B8; font-style:italic;">Unspecified</span>'
                else:
                    if ',' in raw_author:
                        display_author = f"{raw_author.split(',')[0].strip()} <span style='color:#94A3B8; font-weight:500;'>et al.</span>"
                    elif ' and ' in raw_author:
                        display_author = f"{raw_author.split(' and ')[0].strip()} <span style='color:#94A3B8; font-weight:500;'>et al.</span>"
                    elif len(raw_author) > 25:
                        display_author = raw_author[:22] + "..."
                    else:
                        display_author = raw_author

                ds_name = row.get('Dataset Name', 'Unnamed')
                domain = row.get('Domain', 'N/A')

                html_parts.append('<div class="dataset-list-row">')
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
            st.markdown("".join(html_parts), unsafe_allow_html=True)

            st.markdown(
                '<div class="section-header header-teal" style="margin-top: 10px;"><h2>📖 Dataset Details</h2></div>',
                unsafe_allow_html=True)
            valid_datasets = filtered_df[
                filtered_df['Dataset Name'] != ''] if 'Dataset Name' in filtered_df.columns else filtered_df
            selected_dataset = st.selectbox("Select a dataset to view full details:",
                                            ["(Select to view)"] + valid_datasets['Dataset Name'].tolist(),
                                            label_visibility="collapsed")

            if selected_dataset != "(Select to view)":
                details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]
                details_html = (
                    '<div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); padding: 24px; margin-bottom: 24px;">'
                    f'<h2 style="font-size: 28px; font-weight:900; color: #0F172A; margin-bottom: 8px; line-height:1.2;">{selected_dataset}</h2>'
                    f'<p style="color: #64748B; font-size: 15px; margin-bottom: 20px; font-weight:500;">Source: {details.get("Source Organization", details.get("Author", "N/A"))}</p>'
                )

                link = str(details.get('Link', '')).strip()
                if link.startswith('http'):
                    details_html += (
                        f'<div style="margin-bottom: 20px;">'
                        f'<a href="{link}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:12px 22px; text-decoration:none; border-radius:50px; font-weight:700; font-size:14px; box-shadow: 0 4px 10px rgba(74,109,95,0.2);">'
                        f'🔗 Download / Visit Source</a></div>'
                    )

                details_html += '<div class="metadata-grid">'
                for col_name in df.columns:
                    if str(col_name).strip() and "Unnamed" not in str(col_name) and col_name not in ['Link', 'Status',
                                                                                                     'Dataset Name']:
                        val = str(details.get(col_name, '')).strip()
                        if val and val.lower() not in ['nan', 'none', 'n/a', 'na', 'null', '']:
                            details_html += (
                                f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>')
                details_html += '</div>'

                details_html += (
                    f'<div style="margin-top:24px; padding:14px; background:rgba(255,255,255,0.6); border-left:4px solid #4A6D5F; border-radius:8px;">'
                    f'<h4 style="margin:0 0 8px 0; font-size:14px; color:#0F172A;">📚 How to Cite</h4>'
                    f'<p style="margin:0; font-size:13px; color:#475569;">Data accessed from the Open Battery Dataset Portal (2026). Original source: {details.get("Source Organization", "N/A")}. Dataset: {selected_dataset}.</p>'
                    f'</div></div>'
                )
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

                # 新增的本地文件上传选项
                st.markdown(
                    "<h5 style='font-size:15px; margin-top:10px; color:#334155;'>Upload Local Files (Optional)</h5>",
                    unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Attach a dataset file (CSV, Excel, JSON, ZIP, H5)",
                                                 type=["csv", "xlsx", "json", "zip", "h5"])

                c8, c9 = st.columns(2)
                new_contributor = c8.text_input("Contributor Name *")
                new_email = c9.text_input("Contact Email (Optional)")

                if st.form_submit_button("Submit to Moderation Queue"):
                    if not new_name or not new_domain or (not new_link and not uploaded_file) or not new_contributor:
                        st.error("Please fill in all required fields marked with * and provide either a URL or a file.")
                    else:
                        new_row = {c: "" for c in df.columns}

                        file_status = f"Local File: {uploaded_file.name}" if uploaded_file else new_link

                        new_row.update({
                            'Dataset Name': new_name, 'Domain': new_domain, 'Category': new_category,
                            'Sub-category': new_subcat,
                            'Short Description': new_desc, 'Link': file_status, 'Source Organization': new_org,
                            'Author': new_contributor, 'Contributor Email': new_email, 'Status': 'Pending'
                        })
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

# ----------------- 页面 F：About -----------------
elif current_page == "About":
    about_html = """
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); padding: 32px; margin-bottom: 24px;">
        <div class="section-header header-blue"><h2 style="margin: 0;">About This Platform</h2></div>
        <p style="margin-top:20px; font-size: 16px; line-height: 1.8; color: #475569;">This website is a curated platform for organizing and sharing public datasets. It is designed to improve dataset discoverability, metadata standardization, and reuse in research and engineering workflows.</p>
        <p style="font-size: 16px; line-height: 1.8; color: #475569;">Maintained by <strong style="color:#0F172A;">Jian Wu</strong>, focusing on battery data analysis and SOH estimation.</p>
    </div>
    """
    st.markdown(about_html, unsafe_allow_html=True)

# ----------------- 页面 G：Contact -----------------
elif current_page == "Contact":
    contact_html = """
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04); text-align: center; padding: 70px 20px;">
        <h2 style="color:#0F172A; font-weight:900; margin-bottom:16px; font-size: 36px;">Get in Touch</h2>
        <p style='font-size: 17px; color: #475569; margin-bottom: 26px;'>For questions, dataset suggestions, collaboration, or corrections, please contact:</p>
        <a href="mailto:jian.wu@utbm.fr" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:14px 30px; text-decoration:none; border-radius:50px; font-weight:800; font-size:17px; box-shadow: 0 6px 20px rgba(74,109,95,0.25);">✉️ jian.wu@utbm.fr</a>
    </div>
    """
    st.markdown(contact_html, unsafe_allow_html=True)

# ----------------- 页面 H：Admin Dashboard -----------------
elif current_page == "Admin Dashboard" and st.session_state.is_admin:
    st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                use_container_width=True,
                num_rows="dynamic"
            )
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized successfully!")
                st.cache_data.clear()

# ----------------- 页面 I：Settings (新增) -----------------
elif current_page == "Settings":
    st.markdown('<div class="section-header header-teal"><h2>⚙️ Settings</h2></div>', unsafe_allow_html=True)

    tab_account, tab_prefs, tab_data_prefs, tab_notifs = st.tabs([
        "Account Settings", "Preferences", "Dataset Preferences", "Notification Preferences"
    ])

    with tab_account:
        with st.container(border=True):
            st.markdown("### Account Information")
            role_text = "Administrator" if st.session_state.is_admin else "Contributor (Guest)"
            st.text_input("Display Name", value="Admin User" if st.session_state.is_admin else "Guest User")
            st.text_input("Email", value="admin@example.com" if st.session_state.is_admin else "")
            st.text_input("Password", type="password", value="********" if st.session_state.is_admin else "")
            st.text_input("Role", value=role_text, disabled=True)
            if st.button("Save Account Changes"):
                st.success("Account settings updated successfully!")

    with tab_prefs:
        with st.container(border=True):
            st.markdown("### General Settings")
            st.selectbox("Default page", ["Homepage", "Browse Datasets", "Contribute Data"])
            st.radio("Theme", ["Light", "Auto"], horizontal=True)
            st.slider("Items per page", min_value=10, max_value=100, value=20, step=10)
            st.selectbox("Language", ["English", "中文"])
            if st.button("Save Preferences"):
                st.success("Preferences saved successfully!")

    with tab_data_prefs:
        with st.container(border=True):
            st.markdown("### Dataset Customization")
            st.selectbox("Preferred domain", ["All", "Energy", "Battery", "Healthcare", "Manufacturing"])
            st.selectbox("Preferred chemistry", ["All", "NMC", "LFP", "NCA", "LCO", "Solid-state"])
            st.selectbox("Default sort", ["Most Recent", "A-Z", "Most Popular"])
            if st.button("Save Dataset Preferences"):
                st.success("Dataset preferences updated!")

    with tab_notifs:
        with st.container(border=True):
            st.markdown("### Email & Alert Preferences")
            st.toggle("Email notifications", value=True)
            st.toggle("Submission status updates", value=True)
            st.toggle("New dataset alerts", value=False)
            st.toggle("Weekly digest", value=True)
            if st.button("Save Notifications"):
                st.success("Notification preferences applied!")

# ----------------- 页面 J：Notifications (新增) -----------------
elif current_page == "Notifications":
    st.markdown('<div class="section-header header-blue"><h2>🔔 Notifications</h2></div>', unsafe_allow_html=True)

    # 顶部操作按钮
    col_btn, col_filter, _ = st.columns([3, 2, 5])
    with col_btn:
        b1, b2 = st.columns(2)
        with b1:
            st.button("Mark all as read", use_container_width=True)
        with b2:
            st.button("Clear read", use_container_width=True)
    with col_filter:
        st.selectbox("Filter", ["All", "Unread", "System", "Dataset", "Review"], label_visibility="collapsed")

    st.markdown("<hr style='border-color: #E2E8F0; margin: 16px 0 24px 0;'>", unsafe_allow_html=True)

    # Inbox 样式数据列表
    notifications = [
        {"title": "Your dataset submission has been approved",
         "msg": "Your dataset 'NMC Aging Profiling' is now live and accessible in the directory.",
         "time": "2 hours ago", "status": "Unread", "type": "Dataset", "icon": "✅"},
        {"title": "Your submission is under review",
         "msg": "Admin is currently reviewing 'LFP Cycling Data'. You will be notified once complete.",
         "time": "1 day ago", "status": "Read", "type": "Review", "icon": "⏳"},
        {"title": "New dataset added in Battery / EIS",
         "msg": "Check out the newly added 'Oxford Battery Degradation' dataset published by the community.",
         "time": "2 days ago", "status": "Read", "type": "System", "icon": "🆕"},
        {"title": "Source link validation failed",
         "msg": "The URL provided for 'Solid-state Tests' is unreachable. Please update the metadata.",
         "time": "1 week ago", "status": "Read", "type": "System", "icon": "⚠️"},
    ]

    # 渲染 Inbox
    for n in notifications:
        bg_color = "#F8FAFC" if n["status"] == "Read" else "#FFFFFF"
        border_color = "#E2E8F0" if n["status"] == "Read" else "#93C5FD"
        box_shadow = "none" if n["status"] == "Read" else "0 4px 15px rgba(59, 130, 246, 0.05)"

        notif_html = f"""
        <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 18px 24px; margin-bottom: 12px; display: flex; align-items: flex-start; gap: 20px; transition: transform 0.2s; box-shadow: {box_shadow};">
            <div style="font-size: 26px; padding-top: 2px;">{n['icon']}</div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 800; color: #0F172A; font-size: 16px;">{n['title']}</span>
                    <span style="font-size: 13px; color: #94A3B8; font-weight: 600;">{n['time']}</span>
                </div>
                <div style="color: #475569; font-size: 15px; margin-bottom: 12px; line-height: 1.5;">{n['msg']}</div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: #F1F5F9; color: #64748B; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">{n['type']}</span>
                    {f'<span style="background: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">{n["status"]}</span>' if n["status"] == "Unread" else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(notif_html, unsafe_allow_html=True)

# ================= 8. 全局 Footer =================
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