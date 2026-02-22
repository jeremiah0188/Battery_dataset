import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 1. 初始化 Session State =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Homepage"
if "search_kw" not in st.session_state:
    st.session_state.search_kw = ""
if "global_search_input" not in st.session_state:
    st.session_state.global_search_input = ""

# --- 初始化模拟通知数据 ---
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "title": "✅ Your dataset submission has been approved",
         "msg": "The 'LFP Degradation Profiling' dataset is now live.", "time": "10 mins ago", "read": False,
         "type": "System"},
        {"id": 2, "title": "🆕 New dataset added in Battery / EIS",
         "msg": "Check out the new 'Oxford Fast Charging' dataset.", "time": "2 hours ago", "read": False,
         "type": "Dataset"},
        {"id": 3, "title": "⏳ Your submission is under review", "msg": "Your recent file upload is being validated.",
         "time": "1 day ago", "read": True, "type": "Review"},
        {"id": 4, "title": "⚠️ Source link validation failed", "msg": "The Github link provided seems broken.",
         "time": "3 days ago", "read": True, "type": "System"}
    ]

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

current_page = st.session_state.current_view

# ================= 3. 动态背景引擎 =================
bg_gradients = {
    "Homepage": "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 45%, #EEF2FF 100%)",
    "Browse Datasets": "linear-gradient(135deg, #F0FDF4 0%, #F8FAFC 50%, #ECFEFF 100%)",
    "Contribute Data": "linear-gradient(135deg, #FFFBEB 0%, #F8FAFC 50%, #FEF3C7 100%)",
    "About": "linear-gradient(135deg, #F5F3FF 0%, #F8FAFC 50%, #E0E7FF 100%)",
    "Contact": "linear-gradient(135deg, #FEF2F2 0%, #F8FAFC 50%, #FFEDD5 100%)",
    "Settings": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "Notifications": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "login": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "signup": "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "Admin Dashboard": "linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%)"
}
current_bg = bg_gradients.get(current_page, "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 100%)")

st.markdown(f"""
<style>
    .stApp {{
        background: {current_bg} !important;
        background-attachment: fixed !important;
        transition: background 0.8s ease-in-out !important;
    }}
</style>
""", unsafe_allow_html=True)

# ================= 4. 极致优化的专业 CSS (解决阴影框、重影与动画) =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp { font-family: 'Inter', -apple-system, sans-serif; color: #334155; }
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}

    .block-container {
        max-width: 96% !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }

    /* ================= 🎯 终极清除顶层外部白卡 ================= */
    /* 锁定页面最顶部的横向大容器，清除它的背景和边框 */
    [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="column"] div {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* iframe 层彻底透明化，确保只有内部设定的胶囊会显示颜色和阴影 */
    [data-testid="stHorizontalBlock"]:first-of-type iframe {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
    }

    /* 顶栏入场动画 */
    [data-testid="stHorizontalBlock"]:first-of-type {
        animation: headerSlideDown 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        align-items: center !important;
        margin-bottom: 24px !important;
    }
    @keyframes headerSlideDown {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* ================= 🔍 搜索框美化：白色圆角 + 右侧小圆圈 ================= */
    /* 清除输入框双层重影 */
    div[data-testid="stTextInput"] > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] {
        position: relative;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 50px !important;
        padding: 10px 48px 10px 20px !important; /* 给右侧圆圈留出空间 */
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        background-color: rgba(255, 255, 255, 0.96) !important;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04) !important;
        font-size: 13px !important;
        height: 44px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #4A6D5F !important;
        box-shadow: 0 8px 25px rgba(74, 109, 95, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* 利用伪元素插入右侧的圆形搜索图标 */
    div[data-testid="stTextInput"] > div::after {
        content: "🔍";
        position: absolute;
        right: 5px;
        top: 50%;
        transform: translateY(-50%);
        width: 34px;
        height: 34px;
        background-color: #F1F5F9;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: #475569;
        pointer-events: none; /* 让点击穿透，用户可直接回车 */
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }

    /* ================= ⚙️🔔 图标按钮无边框 + 悬浮动效 ================= */
    .icon-btn-container button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 22px !important;
        color: #475569 !important;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), background 0.2s !important;
        height: 44px !important;
        width: 44px !important;
        padding: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50% !important;
    }
    .icon-btn-container button:hover {
        transform: scale(1.1) translateY(-2px) !important;
        background: rgba(241, 245, 249, 0.8) !important;
        box-shadow: 0 4px 12px rgba(15,23,42,0.05) !important;
    }

    /* ================= 全局白卡样式与动画 ================= */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04) !important;
        padding: 24px !important;
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 15px 35px rgba(15, 23, 42, 0.06) !important;
        transform: translateY(-2px) !important;
    }

    /* 全局主按钮样式 */
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
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(112, 128, 144, 0.4) !important;
    }

    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    /* ================= 首页动效复原 ================= */
    .hero-container { display: flex; padding: 4rem; background: radial-gradient(circle at top left, #FFF 0%, rgba(255,255,255,0.4) 100%); border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.03); margin-bottom: 2rem; gap: 4rem; backdrop-filter: blur(10px); }
    .hero-left { flex: 1.2; }
    .hero-title { font-size: 4.8rem; font-weight: 900; line-height: 1.1; color: #0F172A; margin-bottom: 1.5rem; letter-spacing: -2px; transition: transform 0.4s; }
    .hero-title:hover { transform: scale(1.02); }
    .hero-title span { background: linear-gradient(135deg, #4A6D5F 0%, #115E59 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 1.25rem; color: #475569; line-height: 1.7; margin-bottom: 2rem; }

    .bento-card { border-radius: 20px; padding: 28px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid rgba(255,255,255,0.5); box-shadow: 0 10px 30px rgba(0,0,0,0.04); transition: transform 0.4s, box-shadow 0.4s; }
    .bento-card:hover { transform: translateY(-6px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

    .chem-tag { background: rgba(255,255,255,0.8); padding:8px 16px; border-radius:30px; font-size:13px; font-weight:800; color:#0F172A; border: 1px solid rgba(0,0,0,0.02); display: inline-block; margin: 4px; transition: all 0.3s; }
    .chem-tag:hover { background: #4A6D5F; color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(74,109,95,0.3); }

    .dataset-list-row { display: flex; padding: 18px 24px; font-size: 14px; border-bottom: 1px solid #F1F5F9; align-items: center; transition: all 0.2s ease; }
    .dataset-list-row:hover { background-color: #F8FAFC !important; transform: scale(1.005); border-radius: 8px; }

    .metadata-item { background: rgba(255, 255, 255, 0.5); border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; transition: all 0.3s; }
    .metadata-item:hover { background: #FFFFFF; transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0,0,0,0.04); }

    .section-header h2 { font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; transition: all 0.3s ease; }
    .section-header:hover h2 { color: #4A6D5F; transform: translateX(6px); }

    /* ================= Notifications 页面样式 ================= */
    .notif-card { background: rgba(255,255,255,0.9); border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(15,23,42,0.03); transition: all 0.3s; }
    .notif-card.unread { border-left: 6px solid #4A6D5F; background: #FFFFFF; box-shadow: 0 8px 20px rgba(74, 109, 95, 0.08); }
    .notif-card.read { opacity: 0.75; }
    .notif-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(15,23,42,0.06); }

    /* Footer */
    .custom-footer { width: 100%; padding: 40px 16px 20px 16px; margin-top: 40px; color: #64748B; font-size: 14px; border-top: 1px solid #E2E8F0; display: flex; flex-direction: column; gap: 16px; }
    .footer-links { display: flex; gap: 16px; font-weight: 600; }
    .footer-links a { color: #475569; text-decoration: none; transition: color 0.2s; }
    .footer-links a:hover { color: #4A6D5F; }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ================= 5. 全新极简顶栏：单行无缝布局 =================
# 宽度占比分配： Logo (1.3) | Nav (4.5) | Search (2.4) | Icons (0.8) | Auth (1.0)
LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"

with st.container():
    col_logo, col_nav, col_search, col_icons, col_auth = st.columns([1.3, 4.5, 2.4, 0.8, 1.0],
                                                                    vertical_alignment="center")

    # 1. Logo
    with col_logo:
        st.image(LOGO_IMAGE_URL, width=170)

    # 2. 胶囊导航栏（完美边界控制）
    with col_nav:
        if st.session_state.current_view not in ["login", "signup"]:
            menu_tabs = ["Homepage", "Browse Datasets", "Contribute Data", "About", "Contact"]
            base_icons = ['house', 'search', 'cloud-upload', 'info-circle', 'envelope']
            if st.session_state.is_admin:
                menu_tabs.append("Dashboard")
                menu_icons = base_icons + ['shield-lock']
            else:
                menu_icons = base_icons

            # 处理路由：避免循环更新Bug
            if st.session_state.current_view in menu_tabs:
                default_idx = menu_tabs.index(st.session_state.current_view)
            else:
                default_idx = 0

            # 内部容器完全包裹阴影，外部强制透明
            selected_page = option_menu(
                menu_title=None,
                options=menu_tabs,
                icons=menu_icons,
                default_index=default_idx,
                orientation="horizontal",
                styles={
                    "container": {
                        "padding": "6px 8px !important",
                        "background-color": "rgba(255, 255, 255, 0.95) !important",
                        "border": "1px solid rgba(226, 232, 240, 0.8) !important",
                        "border-radius": "999px !important",
                        "box-shadow": "0 8px 25px rgba(15, 23, 42, 0.05) !important",
                        "margin": "0 auto",
                        "width": "fit-content !important",
                        "display": "flex",
                        "justify-content": "center",
                    },
                    "icon": {"color": "#64748B", "font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px",
                        "font-weight": "700",
                        "color": "#475569",
                        "padding": "10px 14px",
                        "margin": "0 2px",
                        "border-radius": "50px",
                        "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                        "white-space": "nowrap"
                    },
                    "nav-link-selected": {
                        "background-color": "#4A6D5F",
                        "color": "#FFFFFF",
                        "font-weight": "800",
                        "box-shadow": "0 4px 10px rgba(74,109,95,0.3)"
                    },
                }
            )

            # 路由逻辑修复：只有点击菜单发生变化时才更新，并且在设定/通知页时不触发循环
            expected_selected = st.session_state.current_view if st.session_state.current_view in menu_tabs else \
            menu_tabs[default_idx]
            if selected_page != expected_selected:
                st.session_state.current_view = selected_page
                st.rerun()

    # 3. 搜索框 (内置搜索图标的精美样式)
    with col_search:
        def submit_global_search():
            if st.session_state.global_search_input:
                st.session_state.search_kw = st.session_state.global_search_input
                st.session_state.current_view = "Browse Datasets"


        st.text_input(
            "Search",
            key="global_search_input",
            label_visibility="collapsed",
            placeholder="Search...",
            on_change=submit_global_search
        )

    # 4. 图标功能区：Settings & Notifications
    with col_icons:
        i1, i2 = st.columns(2)
        with i1:
            st.markdown('<div class="icon-btn-container">', unsafe_allow_html=True)
            if st.button("⚙️", type="tertiary", use_container_width=True, help="Settings"):
                st.session_state.current_view = "Settings"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with i2:
            st.markdown('<div class="icon-btn-container">', unsafe_allow_html=True)
            # 根据要求移除红点提示，仅保留简洁图标
            if st.button("🔔", type="tertiary", use_container_width=True, help="Notifications"):
                st.session_state.current_view = "Notifications"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # 5. 登录状态
    with col_auth:
        if st.session_state.is_admin:
            if st.button("Log Out", use_container_width=True):
                st.session_state.is_admin = False
                st.session_state.current_view = "Homepage"
                st.rerun()
        else:
            if st.session_state.current_view not in ["login", "signup"]:
                if st.button("Sign In", use_container_width=True):
                    st.session_state.current_view = "login"
                    st.rerun()

# ================= 6. Google Sheets 数据库配置 =================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=10)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL)
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1).fillna('').astype(str)
        if 'Status' not in df.columns: df['Status'] = 'Approved'
        return df
    except Exception:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Domain', 'Category', 'Sub-category', 'Status'])


df = load_data()
public_df = df[df['Status'] == 'Approved'] if 'Status' in df.columns else df.copy()

# ================= 7. 核心路由与页面内容渲染 =================

# ----------------- 页面 A & B：Login / Signup -----------------
if current_page in ["login", "signup"] and not st.session_state.is_admin:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            title = "Welcome Back" if current_page == "login" else "Create Account"
            desc = "Sign in to access the contributor dashboard." if current_page == "login" else "Join the portal to track your submissions."

            st.markdown(f"<h2 style='font-size:34px; font-weight:900; color:#0F172A; text-align:center;'>{title}</h2>",
                        unsafe_allow_html=True)
            st.markdown(f"<p style='color:#64748B; font-size:15px; margin-bottom:32px; text-align:center;'>{desc}</p>",
                        unsafe_allow_html=True)

            if current_page == "signup": st.text_input("Full Name", placeholder="e.g. John Doe")
            st.text_input("Email address", placeholder="name@company.com")
            pwd_input = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)

            btn_label = "Sign In" if current_page == "login" else "Register Account"
            if st.button(btn_label, use_container_width=True):
                if current_page == "login":
                    if pwd_input == st.secrets.get("admin_password", ""):
                        st.session_state.is_admin = True
                        st.session_state.current_view = "Homepage"
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.info("Registration is temporarily closed. Please contact the administrator.")

            st.markdown("<hr style='border-color:#E2E8F0; margin: 32px 0 24px 0;'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                other_lbl = "Create an Account" if current_page == "login" else "Sign In instead"
                other_tgt = "signup" if current_page == "login" else "login"
                if st.button(other_lbl, use_container_width=True):
                    st.session_state.current_view = other_tgt
                    st.rerun()
            with c2:
                if st.button("Return Home", use_container_width=True):
                    st.session_state.current_view = "Homepage"
                    st.rerun()

# ----------------- 页面：Settings (全面推荐内容) -----------------
elif current_page == "Settings":
    st.markdown('<div class="section-header header-blue"><h2>⚙️ Global Settings</h2></div>', unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Account Settings", "Preferences", "Dataset Preferences", "Notification Prefs"])

    with t1:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; margin-bottom:16px;'>A. Account Settings</h4>",
                        unsafe_allow_html=True)
            st.text_input("Display Name", value="Admin User" if st.session_state.is_admin else "Guest User")
            st.text_input("Email", value="admin@battery-atlas.com" if st.session_state.is_admin else "")
            st.text_input("Password", value="********", type="password")
            st.text_input("Role", value="Administrator" if st.session_state.is_admin else "Contributor", disabled=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Save Profile Changes", type="primary")

    with t2:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; margin-bottom:16px;'>B. Preferences</h4>", unsafe_allow_html=True)
            st.selectbox("Default page", ["Homepage", "Browse Datasets", "Dashboard"])
            st.selectbox("Theme", ["Auto", "Light", "Dark"])
            st.slider("Items per page", 10, 100, 25)
            st.selectbox("Language", ["English", "中文"])

    with t3:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; margin-bottom:16px;'>C. Dataset Preferences</h4>",
                        unsafe_allow_html=True)
            st.selectbox("Preferred domain", ["Energy", "Battery", "Healthcare", "Manufacturing"])
            st.selectbox("Preferred chemistry", ["NMC", "LFP", "NCA", "LCO", "All"])
            st.selectbox("Default sort", ["Most Recent", "A-Z"])

    with t4:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0F172A; margin-bottom:16px;'>D. Notification Preferences</h4>",
                        unsafe_allow_html=True)
            st.toggle("Email notifications", value=True)
            st.toggle("Submission status updates", value=True)
            st.toggle("New dataset alerts", value=False)
            st.toggle("Weekly digest", value=True)

# ----------------- 页面：Notifications (Inbox样式) -----------------
elif current_page == "Notifications":
    st.markdown('<div class="section-header header-amber"><h2>🔔 Notifications Inbox</h2></div>',
                unsafe_allow_html=True)

    # 顶部操作按钮
    c1, c2, c3 = st.columns([4, 1.5, 1.5])
    with c1:
        notif_filter = st.selectbox("Filter", ["All", "Unread", "System", "Dataset", "Review"],
                                    label_visibility="collapsed")
    with c2:
        if st.button("Mark all as read", use_container_width=True):
            for n in st.session_state.notifications: n["read"] = True
            st.rerun()
    with c3:
        if st.button("Clear read", use_container_width=True):
            st.session_state.notifications = [n for n in st.session_state.notifications if not n["read"]]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 渲染列表
    filtered_notifs = st.session_state.notifications
    if notif_filter == "Unread":
        filtered_notifs = [n for n in filtered_notifs if not n["read"]]
    elif notif_filter != "All":
        filtered_notifs = [n for n in filtered_notifs if n["type"] == notif_filter]

    if not filtered_notifs:
        st.info("No notifications to display.")
    else:
        for n in filtered_notifs:
            read_cls = "read" if n["read"] else "unread"
            badge_color = "#3B82F6" if n["type"] == "System" else "#10B981" if n["type"] == "Dataset" else "#F59E0B"

            html = f"""
            <div class="notif-card {read_cls}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                    <div style="font-size:16px; font-weight:800; color:#0F172A;">{n['title']}</div>
                    <div style="font-size:12px; color:#64748B; font-weight:600;">{n['time']}</div>
                </div>
                <div style="font-size:14px; color:#475569; margin-bottom:12px;">{n['msg']}</div>
                <div><span style="background: {badge_color}20; color: {badge_color}; padding: 4px 10px; border-radius: 6px; font-size:11px; font-weight:800; text-transform:uppercase;">{n['type']}</span></div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

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
                                      placeholder="e.g. Oxford, NMC...")
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
        if sel_domain != "All" and 'Domain' in filtered_df.columns: filtered_df = filtered_df[
            filtered_df['Domain'] == sel_domain]
        if sel_category != "All" and 'Category' in filtered_df.columns: filtered_df = filtered_df[
            filtered_df['Category'] == sel_category]
        if sel_subcategory != "All" and 'Sub-category' in filtered_df.columns: filtered_df = filtered_df[
            filtered_df['Sub-category'] == sel_subcategory]

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.7); padding: 12px 16px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #0F172A;">
                <span style="background: #4A6D5F; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-right: 8px;">{len(filtered_df)}</span> Datasets Found
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_df.empty:
            html_parts = [
                '<div style="border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; background: #FFFFFF; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.02);">']
            html_parts.append(
                '<div style="display: flex; background-color: #F8FAFC; padding: 14px 24px; font-size: 13px; font-weight: 700; color: #475569; border-bottom: 1px solid #E2E8F0; text-transform: uppercase;"><div style="flex: 2.5;">Dataset Name</div><div style="flex: 1.5;">Author</div><div style="flex: 1;">Domain</div></div>')

            for _, row in filtered_df.iterrows():
                raw_author = str(row.get('Author', 'Unspecified')).strip()
                display_author = raw_author[:22] + "..." if len(raw_author) > 25 else raw_author
                ds_name = row.get('Dataset Name', 'Unnamed')
                domain = row.get('Domain', 'N/A')

                html_parts.append('<div class="dataset-list-row">')
                html_parts.append(
                    f'<div class="ds-name" style="flex: 2.5; font-weight: 700; color: #0F172A;">{ds_name}</div>')
                html_parts.append(f'<div style="flex: 1.5; color: #475569;">{display_author}</div>')
                html_parts.append(
                    f'<div style="flex: 1; color: #64748B;"><span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600;">{domain}</span></div>')
                html_parts.append('</div>')

            html_parts.append('</div>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)

            st.markdown('<div class="section-header header-teal"><h2>📖 Dataset Details</h2></div>',
                        unsafe_allow_html=True)
            valid_datasets = filtered_df[
                filtered_df['Dataset Name'] != ''] if 'Dataset Name' in filtered_df.columns else filtered_df
            selected_dataset = st.selectbox("Select a dataset to view details:",
                                            ["(Select to view)"] + valid_datasets['Dataset Name'].tolist(),
                                            label_visibility="collapsed")

            if selected_dataset != "(Select to view)":
                details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]
                details_html = f'<div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; padding: 24px;">'
                details_html += f'<h2 style="font-size: 28px; font-weight:900; color: #0F172A;">{selected_dataset}</h2>'

                link = str(details.get('Link', '')).strip()
                if link.startswith('http'):
                    details_html += f'<a href="{link}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:12px 22px; text-decoration:none; border-radius:50px; font-weight:700; margin: 16px 0;">🔗 Download Source</a>'

                details_html += '<div class="metadata-grid">'
                for col_name in df.columns:
                    if col_name not in ['Link', 'Status', 'Dataset Name']:
                        val = str(details.get(col_name, '')).strip()
                        if val: details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                details_html += '</div></div>'
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
            with st.form("upload_form", border=False):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Dataset Name *")
                new_desc = c2.text_input("Short Description *")
                c1b, c2b, c3b = st.columns(3)
                new_domain = c1b.selectbox("Domain *",
                                           ["Energy", "Healthcare", "Manufacturing", "Transportation", "Other"])
                new_category = c2b.text_input("Category")
                new_subcat = c3b.text_input("Sub-category")
                new_link = st.text_input("Source URL (Optional if local file provided)")
                uploaded_file = st.file_uploader("Or Upload Local File", type=['csv', 'xlsx', 'zip', 'json', 'txt'])
                new_contributor = st.text_input("Contributor Name *")

                if st.form_submit_button("Submit to Moderation Queue"):
                    if not new_name or not new_domain or not new_contributor or (not new_link and not uploaded_file):
                        st.error("⚠️ Please fill in all required fields marked with *")
                    else:
                        final_link = new_link if not uploaded_file else f"[Local File] {uploaded_file.name} | URL: {new_link}"
                        new_row = {'Dataset Name': new_name, 'Domain': new_domain, 'Category': new_category,
                                   'Sub-category': new_subcat, 'Short Description': new_desc, 'Link': final_link,
                                   'Author': new_contributor, 'Status': 'Pending'}
                        conn.update(spreadsheet=SPREADSHEET_URL,
                                    data=pd.concat([df, pd.DataFrame([new_row])], ignore_index=True))
                        st.success("🎉 Successfully submitted!")
                        st.cache_data.clear()

# ----------------- 页面 F：About -----------------
elif current_page == "About":
    st.markdown("""
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; padding: 32px;">
        <div class="section-header header-blue"><h2 style="margin: 0;">About This Platform</h2></div>
        <p style="margin-top:20px; font-size: 16px; line-height: 1.8; color: #475569;">A curated platform for organizing and sharing public datasets to improve research discoverability.</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- 页面 G：Contact -----------------
elif current_page == "Contact":
    st.markdown("""
    <div style="background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; text-align: center; padding: 70px 20px;">
        <h2 style="color:#0F172A; font-weight:900; margin-bottom:16px; font-size: 36px;">Get in Touch</h2>
        <a href="mailto:jian.wu@utbm.fr" style="display:inline-block; background:linear-gradient(135deg, #4A6D5F 0%, #3B5B4F 100%); color:#FFF; padding:14px 30px; text-decoration:none; border-radius:50px; font-weight:800; font-size:17px;">✉️ jian.wu@utbm.fr</a>
    </div>
    """, unsafe_allow_html=True)

# ----------------- 页面 H：Admin Dashboard -----------------
elif current_page == "Dashboard" and st.session_state.is_admin:
    st.markdown('<div class="section-header header-amber"><h2>🛡️ Admin Dashboard</h2></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(df, column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])},
                                       use_container_width=True)
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized successfully!")
                st.cache_data.clear()

# ================= 8. 全局 Footer =================
st.markdown("""
<div class="custom-footer">
    <div class="footer-links"><a href="#">Citation Policy</a> <span class="footer-separator">/</span> <a href="#">Terms & Privacy</a></div>
    <div class="footer-copyright">© 2026 Open Battery Dataset Portal. Maintained by Jian Wu.</div>
</div>
""", unsafe_allow_html=True)