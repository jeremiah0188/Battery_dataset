import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu

# ================= 1. Session State =================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Homepage"
if "search_kw" not in st.session_state:
    st.session_state.search_kw = ""

# ================= 2. Page Config =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

current_page = st.session_state.current_view

# ================= 3. 动态背景 =================
bg_gradients = {
    "Homepage":        "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 45%, #EEF2FF 100%)",
    "Browse Datasets": "linear-gradient(135deg, #F0FDF4 0%, #F8FAFC 50%, #ECFEFF 100%)",
    "Contribute Data": "linear-gradient(135deg, #FFFBEB 0%, #F8FAFC 50%, #FEF3C7 100%)",
    "About":           "linear-gradient(135deg, #F5F3FF 0%, #F8FAFC 50%, #E0E7FF 100%)",
    "Contact":         "linear-gradient(135deg, #FEF2F2 0%, #F8FAFC 50%, #FFEDD5 100%)",
    "login":           "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "signup":          "linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
    "Admin Dashboard": "linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%)",
}
current_bg = bg_gradients.get(current_page, "linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 100%)")

# ================= 4. 全局 CSS =================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {{ font-family:'Inter',-apple-system,sans-serif; color:#334155;
          background:{current_bg} !important; background-attachment:fixed !important;
          transition:background .8s ease-in-out !important; }}
[data-testid="stHeader"]{{display:none!important;}}
#MainMenu{{visibility:hidden;}} footer{{visibility:hidden;}} #stDecoration{{display:none;}}
[data-testid='stSidebar'],[data-testid='collapsedControl']{{display:none!important;}}
.block-container{{max-width:95%!important;padding-top:1rem!important;padding-bottom:2rem!important;}}

/* ── 全局白卡 ── */
[data-testid="stVerticalBlockBorderWrapper"]{{
    background:rgba(255,255,255,.85)!important;
    backdrop-filter:blur(12px)!important;
    border:1px solid rgba(255,255,255,.6)!important;
    border-radius:20px!important;
    box-shadow:0 10px 30px rgba(15,23,42,.04)!important;
    padding:24px!important; margin-bottom:24px;
    transition:transform .3s ease,box-shadow .3s ease;
}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{
    box-shadow:0 15px 35px rgba(15,23,42,.06)!important;
}}

/* ══════════════════════════════════════════════════════════
   导航修复核心：
   • 手机导航 = 纯 HTML (st.markdown)，不产生 Streamlit 容器
     CSS 在桌面端 display:none
   • 桌面导航 = 唯一一个 with st.container() 里的 option_menu
     CSS 在手机端 display:none，同时清除白卡背景

   因为手机 HTML 通过 st.markdown 注入，它会被包裹在
   Streamlit 自动生成的一个"markdown 块"里，
   而不会生成 stVerticalBlock 容器，所以 nth-child 计数不会被打乱。
   ══════════════════════════════════════════════════════════ */

/* 桌面端：隐藏手机 HTML 导航 */
.mobile-nav-wrap {{ display: none !important; }}

/* 手机端：显示手机 HTML 导航，隐藏桌面 Streamlit 导航 */
@media (max-width: 768px) {{
    .mobile-nav-wrap {{ display: block !important; }}

    /* 隐藏桌面 Streamlit 导航容器
       它是 .block-container 里第一个直接 stVerticalBlock 子容器 */
    div[data-testid="stMainBlockContainer"]
      > div > div[data-testid="stVerticalBlock"]
      > div[data-testid="stVerticalBlock"]:nth-child(2) {{
        display: none !important;
    }}

    .block-container{{max-width:100%!important;padding:.55rem!important;}}
}}

/* 去除桌面导航容器的白卡样式 */
div[data-testid="stMainBlockContainer"]
  > div > div[data-testid="stVerticalBlock"]
  > div[data-testid="stVerticalBlock"]:nth-child(2) {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-bottom: 14px !important;
    animation: headerSlide .8s cubic-bezier(.25,1,.5,1) forwards;
}}
div[data-testid="stMainBlockContainer"]
  > div > div[data-testid="stVerticalBlock"]
  > div[data-testid="stVerticalBlock"]:nth-child(2)
  [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stMainBlockContainer"]
  > div > div[data-testid="stVerticalBlock"]
  > div[data-testid="stVerticalBlock"]:nth-child(2)
  [data-testid="stHorizontalBlock"],
div[data-testid="stMainBlockContainer"]
  > div > div[data-testid="stVerticalBlock"]
  > div[data-testid="stVerticalBlock"]:nth-child(2)
  div[data-testid="column"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    padding: 0 !important;
    margin-bottom: 0 !important;
}}

@keyframes headerSlide{{
    0%{{opacity:0;transform:translateY(-24px);}}
    100%{{opacity:1;transform:translateY(0);}}
}}

/* ── 手机 HTML 导航样式 ── */
.mobile-nav-wrap {{
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(226,232,240,.85);
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(15,23,42,.05);
    padding: 10px 14px;
    margin-bottom: 14px;
}}
.mob-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
/* checkbox trick */
#mob-toggle {{ display: none; }}
.mob-hamburger {{
    cursor: pointer;
    background: #708090;
    color: #fff;
    border: none;
    border-radius: 50px;
    padding: 9px 20px;
    font-size: 18px;
    font-weight: 700;
    user-select: none;
    display: inline-block;
    box-shadow: 0 4px 10px rgba(112,128,144,.28);
}}
.mob-menu {{
    display: none;
    flex-direction: column;
    gap: 6px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #E2E8F0;
}}
#mob-toggle:checked ~ .mob-menu {{ display: flex !important; }}
.mob-link {{
    display: block;
    padding: 10px 14px;
    border-radius: 12px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #334155;
    font-weight: 700;
    font-size: 14px;
    text-decoration: none;
    cursor: default;
}}
.mob-link.active {{
    background: #4A6D5F !important;
    color: #fff !important;
    border-color: #4A6D5F !important;
}}

/* ── 全局按钮 ── */
.stButton>button{{
    background-color:#708090!important;border:none!important;color:#fff!important;
    font-weight:700!important;border-radius:50px!important;transition:all .25s ease!important;
    height:44px!important;padding:0 20px!important;letter-spacing:.3px;
    box-shadow:0 4px 10px rgba(112,128,144,.28)!important;
}}
.stButton>button:hover{{
    background-color:#5c6a77!important;
    box-shadow:0 6px 16px rgba(112,128,144,.45)!important;
    transform:translateY(-1px)!important;
}}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{{border-radius:12px!important;}}
[data-baseweb="tab"] p{{font-weight:800!important;font-size:15px!important;}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{{background-color:#4A6D5F!important;height:3px!important;}}

.section-header{{border:1px solid #fff;border-radius:16px;padding:16px 24px;margin-bottom:20px;
    background:rgba(255,255,255,.72);backdrop-filter:blur(10px);}}
.section-header h2{{margin:0;font-size:24px;font-weight:800;color:#0F172A;}}
.header-blue{{border-left:5px solid #3B82F6;}}
.header-teal{{border-left:5px solid #4A6D5F;}}
.header-amber{{border-left:5px solid #F59E0B;}}

.hero-container{{display:flex;align-items:center;justify-content:space-between;
    padding:4rem 3.5rem;background:radial-gradient(circle at top left,#fff 0%,rgba(255,255,255,.42) 100%);
    border-radius:24px;border:1px solid #fff;box-shadow:0 10px 40px rgba(0,0,0,.03);
    margin-bottom:2rem;gap:3rem;backdrop-filter:blur(10px);}}
.hero-left{{flex:1.2;}}
.hero-subtitle{{font-size:13px;font-weight:800;color:#4A6D5F;text-transform:uppercase;
    letter-spacing:2px;margin-bottom:.8rem;}}
.hero-title{{font-size:4.4rem;font-weight:900;line-height:1.05;color:#0F172A;
    margin-bottom:1rem;letter-spacing:-2px;}}
.hero-title span{{background:linear-gradient(135deg,#4A6D5F 0%,#115E59 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.hero-desc{{font-size:1.15rem;color:#475569;line-height:1.65;margin-bottom:1.2rem;}}
.hero-right{{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:1rem;}}
.bento-card{{border-radius:18px;padding:24px;display:flex;flex-direction:column;
    justify-content:space-between;box-shadow:0 10px 25px rgba(0,0,0,.04);
    border:1px solid rgba(255,255,255,.6);}}
.chem-tag{{background:rgba(255,255,255,.85);padding:7px 14px;border-radius:999px;
    font-size:12px;font-weight:800;color:#0F172A;border:1px solid rgba(0,0,0,.03);
    display:inline-block;margin:3px;}}

.dataset-list-row{{display:flex;padding:16px 20px;font-size:14px;
    border-bottom:1px solid #F1F5F9;align-items:center;transition:all .2s ease;}}
.dataset-list-row:hover{{background:#F8FAFC!important;}}
.dataset-list-row .ds-name{{font-weight:700;color:#0F172A;}}

.metadata-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));
    gap:14px;margin-top:16px;}}
.metadata-item{{background:rgba(255,255,255,.55);border:1px solid #E2E8F0;
    border-radius:12px;padding:14px;}}
.metadata-label{{font-size:11px;font-weight:800;color:#64748B;text-transform:uppercase;
    letter-spacing:.4px;margin-bottom:5px;}}
.metadata-value{{font-size:14px;font-weight:600;color:#0F172A;word-break:break-word;}}

.custom-footer{{width:100%;padding:34px 16px 16px;margin-top:32px;color:#64748B;
    font-size:14px;border-top:1px solid #E2E8F0;display:flex;flex-direction:column;gap:10px;}}
.footer-links{{display:flex;align-items:center;flex-wrap:wrap;gap:12px;font-weight:600;}}
.footer-links a{{color:#475569;text-decoration:none;}}
.footer-separator{{color:#CBD5E1;}}
.footer-copyright{{color:#94A3B8;font-size:12px;}}

@media(max-width:1024px){{
    .hero-container{{flex-direction:column!important;gap:1.2rem!important;padding:2rem 1.4rem!important;}}
    .hero-title{{font-size:2.8rem!important;}}
}}
@media(max-width:768px){{
    [data-testid="stVerticalBlockBorderWrapper"]{{padding:14px!important;margin-bottom:14px!important;border-radius:16px!important;}}
    .hero-container{{padding:1.2rem .9rem!important;border-radius:16px!important;}}
    .hero-title{{font-size:2rem!important;letter-spacing:-1px!important;}}
    .hero-desc{{font-size:.92rem!important;}}
    .hero-right{{grid-template-columns:1fr!important;}}
    .section-header{{padding:10px 12px!important;border-radius:12px!important;}}
    .section-header h2{{font-size:16px!important;}}
    .metadata-grid{{grid-template-columns:1fr!important;}}
    [data-baseweb="tab"] p{{font-size:13px!important;}}
    [data-testid="stTabs"] [data-baseweb="tab-list"]{{overflow-x:auto!important;white-space:nowrap!important;}}
    .stButton>button{{height:40px!important;font-size:14px!important;padding:0 14px!important;}}
}}
</style>
""", unsafe_allow_html=True)

# ================= 5. 导航栏 =================
# 架构：
#   ① st.markdown 注入纯 HTML 手机导航（CSS 桌面端 display:none）
#      → 被 Streamlit 包成一个 markdown element，不是独立 stVerticalBlock 容器
#   ② with st.container() 渲染桌面导航（CSS 手机端 display:none）
#      → 是 stVerticalBlock 的第 N 个子容器，nth-child 可精准靶向

LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"

menu_tabs  = ["Homepage", "Browse Datasets", "Contribute Data", "About", "Contact"]
base_icons = ['house', 'search', 'cloud-upload', 'info-circle', 'envelope']
if st.session_state.is_admin:
    menu_tabs.append("Admin Dashboard")
    menu_icons = base_icons + ['shield-lock']
else:
    menu_icons = base_icons

icon_map = {
    "Homepage":"🏠","Browse Datasets":"🔎","Contribute Data":"☁️",
    "About":"ℹ️","Contact":"✉️","Admin Dashboard":"🛡️"
}

# ── ① 手机 HTML 导航 ──
if current_page not in ["login", "signup"]:
    mob_links_html = ""
    for page in menu_tabs:
        active_cls = "active" if current_page == page else ""
        mob_links_html += f'<span class="mob-link {active_cls}">{icon_map.get(page,"•")} {page}</span>\n'

    auth_html = ""
    if st.session_state.is_admin:
        auth_html = '<span class="mob-hamburger" style="background:#EF4444;margin-right:8px;font-size:14px;">⎋ Logout</span>'

    st.markdown(f"""
    <div class="mobile-nav-wrap">
        <div class="mob-top">
            <img src="{LOGO_IMAGE_URL}" height="38" style="vertical-align:middle;"/>
            <div style="display:flex;align-items:center;gap:8px;">
                {auth_html}
                <label for="mob-toggle" class="mob-hamburger">☰</label>
            </div>
        </div>
        <input type="checkbox" id="mob-toggle"/>
        <div class="mob-menu">
            {mob_links_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── ② 桌面 Streamlit 导航（唯一的 st.container()，CSS 手机端隐藏）──
with st.container():
    col_logo, col_menu, col_auth = st.columns([1.55, 7.6, 1.2], vertical_alignment="center")

    with col_logo:
        st.image(LOGO_IMAGE_URL, width=190)

    with col_menu:
        if current_page not in ["login", "signup"]:
            try:
                default_idx = menu_tabs.index(current_page)
            except ValueError:
                default_idx = 0

            selected_page = option_menu(
                menu_title=None,
                options=menu_tabs,
                icons=menu_icons,
                default_index=default_idx,
                orientation="horizontal",
                styles={
                    "container": {
                        "padding": "6px 10px !important",
                        "background-color": "rgba(255,255,255,0.96) !important",
                        "border": "1px solid rgba(226,232,240,0.85) !important",
                        "border-radius": "100px !important",
                        "box-shadow": "0 8px 25px rgba(15,23,42,0.05) !important",
                        "margin": "0",
                        "width": "fit-content",
                        "min-width": "760px",
                        "max-width": "100%",
                    },
                    "icon": {"color": "#64748B", "font-size": "16px"},
                    "nav-link": {
                        "font-size": "14px","font-weight": "700","color": "#475569",
                        "padding": "10px 16px","margin": "0 4px","border-radius": "999px",
                        "white-space": "nowrap","transition": "all 0.25s ease",
                    },
                    "nav-link-selected": {
                        "background-color": "#4A6D5F","color": "#FFFFFF",
                        "font-weight": "800","border-radius": "999px",
                        "box-shadow": "0 4px 12px rgba(74,109,95,0.25)",
                    },
                },
            )
            if selected_page != st.session_state.current_view:
                st.session_state.current_view = selected_page
                st.rerun()

    with col_auth:
        if st.session_state.is_admin:
            if st.button("Log Out", key="desktop_logout"):
                st.session_state.is_admin = False
                st.session_state.current_view = "Homepage"
                st.rerun()
        else:
            if current_page not in ["login", "signup"]:
                if st.button("Sign In", key="desktop_signin"):
                    st.session_state.current_view = "login"
                    st.rerun()

# ================= 6. Google Sheets =================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1GY3dQ4yBtt2gbd-2Xxf1a_3UpwXKqACJcPX5qlMthzc/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(ttl=10)
def load_data():
    try:
        _df = conn.read(spreadsheet=SPREADSHEET_URL)
        _df = _df.dropna(how="all", axis=0).dropna(how="all", axis=1)
        _df = _df.fillna("").astype(str)
        if "Status" not in _df.columns:
            _df["Status"] = "Approved"
        return _df
    except Exception:
        return pd.DataFrame(columns=["Dataset Name","Author","Domain","Category","Sub-category","Status"])


df = load_data()
public_df = df[df["Status"] == "Approved"] if "Status" in df.columns else df.copy()


def safe_author_display(raw_author):
    raw_author = str(raw_author).strip()
    if raw_author in ["Unspecified","N/A","","nan"]:
        return raw_author, '<span style="color:#94A3B8;font-style:italic;">Unspecified</span>'
    if "," in raw_author:
        return raw_author, f"{raw_author.split(',')[0].strip()} <span style='color:#94A3B8;font-weight:500;'>et al.</span>"
    if " and " in raw_author:
        return raw_author, f"{raw_author.split(' and ')[0].strip()} <span style='color:#94A3B8;font-weight:500;'>et al.</span>"
    if len(raw_author) > 25:
        return raw_author, raw_author[:22] + "..."
    return raw_author, raw_author


# ================= 7. 页面内容 =================

# ---- Login ----
if current_page == "login" and not st.session_state.is_admin:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown("<h2 style='font-size:32px;font-weight:900;color:#0F172A;text-align:center;'>Welcome Back</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748B;font-size:14px;text-align:center;margin-bottom:24px;'>Sign in to access the contributor dashboard.</p>", unsafe_allow_html=True)
            st.text_input("Email address", placeholder="name@company.com")
            pwd_input = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True):
                if pwd_input == st.secrets.get("admin_password", ""):
                    st.session_state.is_admin = True
                    st.session_state.current_view = "Homepage"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            st.markdown("<hr style='border-color:#E2E8F0;margin:24px 0 18px;'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Create an Account", use_container_width=True, key="go_signup"):
                    st.session_state.current_view = "signup"; st.rerun()
            with c2:
                if st.button("Return Home", use_container_width=True, key="return_home_login"):
                    st.session_state.current_view = "Homepage"; st.rerun()

# ---- Sign Up ----
elif current_page == "signup" and not st.session_state.is_admin:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            st.markdown("<h2 style='font-size:32px;font-weight:900;color:#0F172A;text-align:center;'>Create Account</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748B;font-size:14px;text-align:center;margin-bottom:24px;'>Join the Open Battery Dataset Portal.</p>", unsafe_allow_html=True)
            st.text_input("Full Name", placeholder="e.g. John Doe")
            st.text_input("Email address", placeholder="name@company.com", key="signup_email")
            st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register Account", use_container_width=True):
                st.info("Registration is temporarily closed. Please contact the administrator.")
            st.markdown("<hr style='border-color:#E2E8F0;margin:24px 0 18px;'>", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                if st.button("Already have an account?", use_container_width=True, key="back_login"):
                    st.session_state.current_view = "login"; st.rerun()
            with c4:
                if st.button("Return to Homepage", use_container_width=True, key="back_home_signup"):
                    st.session_state.current_view = "Homepage"; st.rerun()

# ---- Homepage ----
elif current_page == "Homepage":
    chem_tags = "".join([f'<span class="chem-tag">{c}</span>' for c in ["NMC","LFP","NCA","LCO","LMO","Solid-state"]])
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-left">
            <div class="hero-subtitle">Open Source Data & Analytics</div>
            <div class="hero-title">Battery Data <br><span>Differently</span></div>
            <div class="hero-desc">High-fidelity, peer-reviewed battery datasets and robust metadata integration tailored to global energy research.</div>
        </div>
        <div class="hero-right">
            <div class="bento-card" style="grid-row:span 2;background:linear-gradient(135deg,#EFF6FF 0%,#DBEAFE 100%);min-height:280px;">
                <div style="font-size:12px;font-weight:800;color:#1E3A8A;text-transform:uppercase;">Platform Metrics</div>
                <div>
                    <div style="font-size:64px;font-weight:900;color:#172554;line-height:1;">{len(public_df)}+</div>
                    <div style="font-size:16px;color:#1E40AF;font-weight:700;margin-top:10px;">Curated Datasets</div>
                </div>
            </div>
            <div class="bento-card" style="background:linear-gradient(135deg,#F0FDF4 0%,#DCFCE7 100%);min-height:130px;">
                <div style="font-size:12px;font-weight:800;color:#14532D;text-transform:uppercase;">A Leader in Quality</div>
                <div style="font-size:24px;font-weight:900;color:#064E3B;">Open Access</div>
            </div>
            <div class="bento-card" style="background:linear-gradient(135deg,#FFFBEB 0%,#FEF3C7 100%);min-height:130px;">
                <div style="font-size:12px;font-weight:800;color:#92400E;text-transform:uppercase;">Supported Chemistry</div>
                <div>{chem_tags}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.markdown('<div class="section-header header-teal"><h2>🌟 Latest Additions</h2></div>', unsafe_allow_html=True)
        latest = public_df.tail(3)
        if not latest.empty:
            for _, row in latest.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row.get('Dataset Name','Unnamed')}**")
                    st.caption(f"Domain: {row.get('Domain','N/A')} | Chem: {row.get('Battery Chemistry','N/A')} | By: {row.get('Author','Unknown')}")
        else:
            st.info("No datasets available yet.")
    with c_right:
        st.markdown('<div class="section-header header-amber"><h2>🔥 Popular Tags</h2></div>', unsafe_allow_html=True)
        with st.container(border=True):
            tags_html = "".join([f'<span class="chem-tag" style="background:#F1F5F9;border-color:#CBD5E1;">{t}</span>' for t in ["EIS","SOH","RUL","Time-Series","Aging","Simulation"]])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.info("💡 Use these keywords in the search bar.")

    st.markdown('<div class="section-header header-blue"><h2>💬 Quick FAQ</h2></div>', unsafe_allow_html=True)
    with st.expander("Do I need an account to download data?"):
        st.write("No. All curated datasets are open-access and do not require an account.")
    with st.expander("How long does moderation review take?"):
        st.write("Our admin team typically reviews within 48–72 hours.")

# ---- Browse Datasets ----
elif current_page == "Browse Datasets":
    st.markdown('<div class="section-header header-blue"><h2>Dataset Directory</h2></div>', unsafe_allow_html=True)
    filter_col, result_col = st.columns([1, 3])

    with filter_col:
        with st.container(border=True):
            st.markdown("<h3 style='font-size:17px;font-weight:800;color:#0F172A;margin-bottom:12px;'>🔍 Filters</h3>", unsafe_allow_html=True)
            search_kw = st.text_input("Keyword Search", value=st.session_state.search_kw, placeholder="e.g. Oxford, NMC, EIS...")
            st.session_state.search_kw = search_kw
            st.markdown("<hr style='border-color:#E2E8F0;margin:12px 0;'>", unsafe_allow_html=True)
            sel_domain = st.selectbox("Domain", ["All","Energy","Healthcare","Manufacturing","Transportation"])
            sel_category = sel_subcategory = "All"
            if sel_domain == "Energy":
                sel_category = st.selectbox("Category", ["All","Battery","Grid","Solar","Wind"])
                if sel_category == "Battery":
                    sel_subcategory = st.selectbox("Battery Data Type", ["All","Time-Series","EIS","Aging / Cycling","Benchmark","Experimental","Simulation"])

    with result_col:
        filtered = public_df.copy()
        if search_kw:
            mask = filtered.astype(str).apply(lambda x: x.str.contains(search_kw, case=False, regex=False)).any(axis=1)
            filtered = filtered[mask]
        if sel_domain != "All" and "Domain" in filtered.columns:
            filtered = filtered[filtered["Domain"] == sel_domain]
        if sel_category != "All" and "Category" in filtered.columns:
            filtered = filtered[filtered["Category"] == sel_category]
        if sel_subcategory != "All" and "Sub-category" in filtered.columns:
            filtered = filtered[filtered["Sub-category"] == sel_subcategory]

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.7);padding:10px 14px;border-radius:12px;border:1px solid #E2E8F0;margin-bottom:14px;">
            <div style="font-size:14px;font-weight:700;color:#0F172A;">
                <span style="background:#4A6D5F;color:white;padding:4px 10px;border-radius:999px;font-size:12px;margin-right:6px;">{len(filtered)}</span> Datasets Found
            </div>
            <div style="font-size:12px;color:#64748B;font-weight:600;">Sort by: <span style="color:#0F172A;">Most Recent</span></div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered.empty:
            rows_html = ""
            for _, row in filtered.iterrows():
                raw_author, disp_author = safe_author_display(row.get("Author","Unspecified"))
                ds_name = row.get("Dataset Name","Unnamed")
                domain  = row.get("Domain","N/A")
                rows_html += f"""
                <div class="dataset-list-row">
                    <div class="ds-name" style="flex:2.5;padding-right:12px;">{ds_name}</div>
                    <div style="flex:1.5;color:#475569;padding-right:12px;" title="{raw_author}">{disp_author}</div>
                    <div style="flex:1;"><span style="background:#F1F5F9;border:1px solid #E2E8F0;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:600;">{domain}</span></div>
                    <div style="flex:0.8;text-align:right;"><span style="background:#F0FDF4;color:#166534;border:1px solid #DCFCE7;padding:5px 10px;border-radius:999px;font-size:11px;font-weight:700;">View ↓</span></div>
                </div>"""
            st.markdown(f"""
            <div style="border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;background:#fff;margin-bottom:18px;box-shadow:0 4px 20px rgba(0,0,0,.02);">
                <div style="display:flex;background:#F8FAFC;padding:12px 18px;font-size:12px;font-weight:700;color:#475569;border-bottom:1px solid #E2E8F0;text-transform:uppercase;letter-spacing:.4px;">
                    <div style="flex:2.5;">Dataset Name</div><div style="flex:1.5;">Author</div>
                    <div style="flex:1;">Domain</div><div style="flex:0.8;text-align:right;">Action</div>
                </div>{rows_html}
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header header-teal"><h2>📖 Dataset Details</h2></div>', unsafe_allow_html=True)
            valid = filtered[filtered["Dataset Name"] != ""] if "Dataset Name" in filtered.columns else filtered
            selected = st.selectbox("Select dataset:", ["(Select to view)"] + valid["Dataset Name"].tolist(), label_visibility="collapsed")

            if selected != "(Select to view)":
                details = valid[valid["Dataset Name"] == selected].iloc[0]
                link = str(details.get("Link","")).strip()
                link_html = f'<div style="margin-bottom:16px;"><a href="{link}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#4A6D5F 0%,#3B5B4F 100%);color:#fff;padding:10px 18px;text-decoration:none;border-radius:999px;font-weight:700;font-size:13px;">🔗 Download / Visit Source</a></div>' if link.startswith("http") else ""
                meta_html = ""
                for col_name in df.columns:
                    if str(col_name).strip() and "Unnamed" not in str(col_name) and col_name not in ["Link","Status","Dataset Name"]:
                        val = str(details.get(col_name,"")).strip()
                        if val and val.lower() not in ["nan","none","n/a","na","null",""]:
                            meta_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                st.markdown(f"""
                <div style="background:rgba(255,255,255,.88);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.65);border-radius:18px;box-shadow:0 10px 26px rgba(15,23,42,.04);padding:20px;margin-bottom:18px;">
                    <h2 style="font-size:24px;font-weight:900;color:#0F172A;margin-bottom:6px;">{selected}</h2>
                    <p style="color:#64748B;font-size:14px;margin-bottom:16px;">Source: {details.get("Source Organization", details.get("Author","N/A"))}</p>
                    {link_html}
                    <div class="metadata-grid">{meta_html}</div>
                    <div style="margin-top:18px;padding:12px;background:rgba(255,255,255,.6);border-left:4px solid #4A6D5F;border-radius:8px;">
                        <h4 style="margin:0 0 6px;font-size:13px;color:#0F172A;">📚 How to Cite</h4>
                        <p style="margin:0;font-size:12px;color:#475569;">Data accessed from the Open Battery Dataset Portal (2026). Dataset: {selected}.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ---- Contribute Data ----
elif current_page == "Contribute Data":
    st.markdown('<div class="section-header header-teal"><h2>Community Contributions</h2></div>', unsafe_allow_html=True)
    tab_submit, tab_request, tab_guide = st.tabs(["Submit a Dataset","Request a Dataset","Submission Guidelines"])

    with tab_submit:
        with st.container(border=True):
            st.write("Help expand this curated dataset hub.")
            with st.form("upload_form", border=False):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Dataset Name *")
                new_desc = c2.text_input("Short Description *")
                c1b, c2b, c3b = st.columns(3)
                new_domain    = c1b.selectbox("Domain *", ["Energy","Healthcare","Manufacturing","Transportation","Other"])
                new_category  = c2b.text_input("Category")
                new_subcat    = c3b.text_input("Sub-category")
                new_link      = st.text_input("Source URL *")
                new_org       = st.text_input("Source Organization / Publisher")
                c8, c9 = st.columns(2)
                new_contributor = c8.text_input("Contributor Name *")
                new_email       = c9.text_input("Contact Email (Optional)")
                if st.form_submit_button("Submit to Moderation Queue"):
                    if not new_name or not new_domain or not new_link or not new_contributor:
                        st.error("Please fill in all required fields marked with *")
                    else:
                        new_row = {c: "" for c in df.columns}
                        new_row.update({"Dataset Name":new_name,"Domain":new_domain,"Category":new_category,
                                        "Sub-category":new_subcat,"Short Description":new_desc,"Link":new_link,
                                        "Source Organization":new_org,"Author":new_contributor,
                                        "Contributor Email":new_email,"Status":"Pending"})
                        conn.update(spreadsheet=SPREADSHEET_URL, data=pd.concat([df, pd.DataFrame([new_row])], ignore_index=True))
                        st.success("Submitted to moderation queue!")
                        st.cache_data.clear()

    with tab_request:
        with st.container(border=True):
            st.markdown("### Can't find what you're looking for?")
            with st.form("request_form", border=False):
                st.text_input("Requested Topic *", placeholder="e.g. Real-world EV charging profiles")
                st.text_area("Additional Details")
                st.text_input("Your Email (optional)")
                if st.form_submit_button("Submit Request"):
                    st.success("Request submitted!")

    with tab_guide:
        with st.container(border=True):
            st.markdown("### 📖 Curation Policy")
            st.write("* Public Domain Only\n* URL Validity: prefer GitHub / Zenodo / Mendeley\n* Fill metadata accurately for discoverability.")

# ---- About ----
elif current_page == "About":
    st.markdown("""
    <div style="background:rgba(255,255,255,.88);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.65);border-radius:18px;box-shadow:0 10px 26px rgba(15,23,42,.04);padding:24px;">
        <div class="section-header header-blue"><h2 style="margin:0;">About This Platform</h2></div>
        <p style="margin-top:14px;font-size:15px;line-height:1.7;color:#475569;">A curated platform for organizing and sharing public battery datasets.</p>
        <p style="font-size:15px;line-height:1.7;color:#475569;">Maintained by <strong style="color:#0F172A;">Jian Wu</strong>, focusing on battery data analysis and SOH estimation.</p>
    </div>""", unsafe_allow_html=True)

# ---- Contact ----
elif current_page == "Contact":
    st.markdown("""
    <div style="background:rgba(255,255,255,.88);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.65);border-radius:18px;box-shadow:0 10px 26px rgba(15,23,42,.04);text-align:center;padding:56px 16px;">
        <h2 style="color:#0F172A;font-weight:900;margin-bottom:12px;font-size:30px;">Get in Touch</h2>
        <p style="font-size:15px;color:#475569;margin-bottom:20px;">For questions, dataset suggestions, collaboration, or corrections:</p>
        <a href="mailto:jian.wu@utbm.fr" style="display:inline-block;background:linear-gradient(135deg,#4A6D5F 0%,#3B5B4F 100%);color:#fff;padding:12px 20px;text-decoration:none;border-radius:999px;font-weight:800;font-size:15px;">✉️ jian.wu@utbm.fr</a>
    </div>""", unsafe_allow_html=True)

# ---- Admin ----
elif current_page == "Admin Dashboard" and st.session_state.is_admin:
    st.markdown('<div class="section-header header-amber"><h2>Moderation Queue</h2></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("admin_form", border=False):
            edited_df = st.data_editor(
                df,
                column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Approved","Pending","Rejected"])},
                use_container_width=True, num_rows="dynamic"
            )
            if st.form_submit_button("💾 Synchronize Cloud Data"):
                conn.update(spreadsheet=SPREADSHEET_URL, data=edited_df)
                st.success("Synchronized!")
                st.cache_data.clear()

# ================= 8. Footer =================
st.markdown("""
<div class="custom-footer">
    <div class="footer-links">
        <a href="#">Citation Policy</a><span class="footer-separator">/</span>
        <a href="#">Changelog</a><span class="footer-separator">/</span>
        <a href="#">Terms & Privacy</a>
    </div>
    <div class="footer-copyright">© 2026 Open Battery Dataset Portal. Maintained by Jian Wu.</div>
</div>
""", unsafe_allow_html=True)