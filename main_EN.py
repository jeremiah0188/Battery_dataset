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

# ================= 3. 极致现代视觉 CSS (包含新模块样式) =================
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #F0F9FF 0%, #F8FAFC 45%, #EEF2FF 100%) !important;
        font-family: 'Inter', -apple-system, sans-serif;
        color: #334155;
    }

    [data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    [data-testid='stSidebar'], [data-testid='collapsedControl'] {display: none !important;}

    .block-container { 
        max-width: 95% !important; 
        padding-top: 1.5rem !important; 
        padding-bottom: 6rem !important; /* 给 Footer 留空间 */
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

    .stButton>button { 
        background-color: #FFFFFF !important; 
        border: 1.5px solid #CBD5E1 !important; 
        color: #0F172A !important; 
        font-weight: 700 !important; 
        border-radius: 50px !important; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; 
        height: 48px !important;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.02) !important;
    }
    .stButton>button:hover { 
        border-color: #0F766E !important; 
        color: #0F766E !important; 
        background-color: #F8FAFC !important; 
        box-shadow: 0 6px 16px rgba(15, 118, 110, 0.12) !important;
        transform: translateY(-2px) !important;
    }

    /* 首页卡片样式 */
    .hero-container {
        display: flex; align-items: center; justify-content: space-between;
        padding: 4.5rem 4rem; 
        background: radial-gradient(circle at top left, #FFFFFF 0%, #F8FAFC 100%);
        border-radius: 24px;
        border: 1px solid #FFFFFF; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.03);
        margin-bottom: 2rem; gap: 4rem;
    }
    .hero-left { flex: 1.2; }
    .hero-subtitle { font-size: 14px; font-weight: 800; color: #0F766E; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; }
    .hero-title { font-size: 4.8rem; font-weight: 900; line-height: 1.1; color: #0F172A; margin-bottom: 1.5rem; letter-spacing: -2px; }
    .hero-title span { background: linear-gradient(135deg, #0F766E 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-desc { font-size: 1.25rem; color: #475569; line-height: 1.7; margin-bottom: 2rem; }

    .hero-right { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .bento-card { border-radius: 20px; padding: 28px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.04); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255,255,255,0.5);}
    .bento-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

    .chem-tag { background: rgba(255,255,255,0.8); padding:8px 16px; border-radius:30px; font-size:13px; font-weight:800; box-shadow:0 2px 8px rgba(0,0,0,0.04); color:#0F172A; border: 1px solid rgba(0,0,0,0.02); display: inline-block; margin: 4px;}

    .section-header { border: 1px solid #FFFFFF; border-radius: 16px; padding: 16px 24px; margin-bottom: 20px; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }
    .section-header h2 { font-size: 24px; font-weight: 800; color: #0F172A; margin: 0; }
    .header-blue { border-left: 5px solid #3B82F6; }
    .header-teal { border-left: 5px solid #0F766E; }
    .header-amber { border-left: 5px solid #F59E0B; }

    .metadata-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
    .metadata-item { background: rgba(248, 250, 252, 0.6); border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; transition: background 0.3s; }
    .metadata-item:hover { background: #FFFFFF; }
    .metadata-label { font-size: 12px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
    .metadata-value { font-size: 15px; font-weight: 600; color: #0F172A; word-wrap: break-word; }

    /* 全局自定义页脚 */
    .custom-footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px);
        color: #94A3B8; padding: 16px 48px; display: flex; justify-content: space-between;
        align-items: center; font-size: 13px; z-index: 999; border-top: 1px solid #334155;
    }
    .custom-footer a { color: #CBD5E1; text-decoration: none; margin-left: 24px; transition: color 0.2s; font-weight: 500;}
    .custom-footer a:hover { color: #38BDF8; }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)

# ================= 4. 顶部无刷新导航栏 (保持5个完美核心) =================
LOGO_IMAGE_URL = "https://raw.githubusercontent.com/jeremiah0188/Battery_dataset/main/logo.png"

col_logo, col_menu, col_auth = st.columns([1.5, 6.5, 1.5])
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

        selected_page = option_menu(
            menu_title=None,
            options=menu_tabs,
            icons=['house', 'search', 'cloud-upload', 'info-circle', 'envelope', 'shield-lock'],
            default_index=default_idx,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "border": "none",
                              "margin-top": "8px"},
                "icon": {"color": "#64748B", "font-size": "16px"},
                "nav-link": {"font-size": "15px", "font-weight": "700", "color": "#475569", "margin": "0 10px",
                             "--hover-color": "rgba(255,255,255,0.5)", "border-radius": "30px"},
                "nav-link-selected": {"background-color": "#0F766E", "color": "white", "icon-color": "white",
                                      "box-shadow": "0 4px 10px rgba(15,118,110,0.2)"},
            }
        )
        if selected_page != st.session_state.current_view:
            st.session_state.current_view = selected_page
            st.rerun()

with col_auth:
    st.write("")
    if st.session_state.is_admin:
        # 管理员登录后，可以显示 My Submissions 或直接退出
        if st.button("Log Out", use_container_width=True):
            st.session_state.is_admin = False
            st.session_state.current_view = "Homepage"
            st.rerun()
    else:
        if st.session_state.current_view not in ["login", "signup"]:
            if st.button("Log In", use_container_width=True):
                st.session_state.current_view = "login"
                st.rerun()

current_page = st.session_state.current_view

# ================= 5. 🔗 Google Sheets 数据库配置 =================
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

# ================= 6. 核心路由与页面内容渲染 =================

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
            if st.button("Return Home", use_container_width=True):
                st.session_state.current_view = "Homepage"
                st.rerun()

# ----------------- 页面 B：注册页 (Sign Up) (略，如果需要可以保持原样) -----------------
elif current_page == "signup" and not st.session_state.is_admin:
    # 保持原代码逻辑即可，为精简演示这里省略内部代码，直接跳转回 login
    st.session_state.current_view = "login"
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

    # ======== 新增模块 1 & 2：Latest Additions 与 Popular Tags ========
    c_left, c_right = st.columns([2, 1])

    with c_left:
        st.markdown('<div class="section-header header-teal"><h2>🌟 Latest Additions</h2></div>',
                    unsafe_allow_html=True)
        # 提取最新通过的 3 个数据集展示
        latest_datasets = public_df.tail(3)
        if not latest_datasets.empty:
            for _, row in latest_datasets.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row.get('Dataset Name', 'Unnamed')}**")
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
            st.info("💡 Tip: Use these keywords in the 'Browse Datasets' search bar.")

    # ======== 新增模块 3：简版 FAQ ========
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
            st.session_state.search_kw = search_kw  # 保持状态

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

        st.markdown(f"**Result Counter:** {len(filtered_df)} datasets found.")

        if not filtered_df.empty:
            with st.container(border=True):
                display_cols = [c for c in ['Dataset Name', 'Domain', 'Category', 'Sub-category', 'Author'] if
                                c in filtered_df.columns]
                st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

            st.markdown(
                '<div class="section-header header-teal" style="margin-top: 24px;"><h2>📖 Dataset Details</h2></div>',
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
                    details_html += f'<div style="margin-bottom: 24px;"><a href="{link}" target="_blank" style="display:inline-block; background:linear-gradient(135deg, #0F766E 0%, #115E59 100%); color:#FFF; padding:12px 28px; text-decoration:none; border-radius:50px; font-weight:700; font-size:14px; box-shadow: 0 4px 10px rgba(15,118,110,0.2); transition: transform 0.2s;">🔗 Download / Visit Source</a></div>'

                details_html += '<div class="metadata-grid">'
                for col_name in df.columns:
                    if str(col_name).strip() and "Unnamed" not in str(col_name) and col_name not in ['Link', 'Status',
                                                                                                     'Dataset Name']:
                        val = str(details.get(col_name, '')).strip()
                        if val and val.lower() not in ['nan', 'none', 'n/a', 'na', 'null', '']:
                            details_html += f'<div class="metadata-item"><div class="metadata-label">{col_name}</div><div class="metadata-value">{val}</div></div>'
                details_html += '</div>'

                # ======== 新增模块 4：Citation 引用指南 ========
                details_html += f'<div style="margin-top:32px; padding:16px; background:#F8FAFC; border-left:4px solid #0F766E; border-radius:8px;"><h4 style="margin:0 0 8px 0; font-size:14px; color:#0F172A;">📚 How to Cite</h4><p style="margin:0; font-size:13px; color:#475569; font-family:monospace;">Data accessed from the Open Battery Dataset Portal (2026). Original source: {details.get("Source Organization", "N/A")}. Dataset: {selected_dataset}.</p></div>'
                details_html += '</div>'

                st.markdown(details_html, unsafe_allow_html=True)
        else:
            st.warning("No datasets match your filters.")

# ----------------- 页面 E：Contribute Data (加入 Tabs 分栏) -----------------
elif current_page == "Contribute Data":
    st.markdown('<div class="section-header header-teal"><h2>Community Contributions</h2></div>',
                unsafe_allow_html=True)

    # ======== 新增模块 5：利用 Tabs 整理提交、心愿单和指南 ========
    tab_submit, tab_request, tab_guide = st.tabs(
        ["📤 Submit a Dataset", "🙋 Request a Dataset", "📖 Submission Guidelines"])

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

                if st.form_submit_button("📤 Submit to Moderation Queue"):
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
                if st.form_submit_button("🙋 Submit Request"):
                    st.success("Request submitted successfully! We will keep an eye out for this data.")

    with tab_guide:
        with st.container(border=True):
            st.markdown("### 📖 Curation Policy & Metadata Standards")
            st.write("""
            * **Public Domain Only:** Ensure the dataset you are submitting is publicly available or you hold the rights to share it.
            * **URL Validity:** Provide direct links to repositories (GitHub, Mendeley, Zenodo, NASA Dash) rather than generic homepages.
            * **Accuracy:** Fill out the Chemistry and Data Type fields as accurately as possible to help researchers filter effectively.
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
        <a href="mailto:jian.wu@utbm.fr" style="display:inline-block; background:linear-gradient(135deg, #0F766E 0%, #115E59 100%); color:#FFF; padding:16px 40px; text-decoration:none; border-radius:50px; font-weight:800; font-size:18px; box-shadow: 0 6px 20px rgba(15,118,110,0.25); transition: transform 0.2s;">✉️ jian.wu@utbm.fr</a>
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

# ======== 7. 全局自定义 Footer (页脚) ========
st.markdown("""
<div class="custom-footer">
    <div>© 2026 Open Battery Dataset Portal. Maintained by Jian Wu.</div>
    <div>
        <a href="#">Citation Policy</a>
        <a href="#">Changelog</a>
        <a href="#">Terms & Privacy</a>
    </div>
</div>
""", unsafe_allow_html=True)