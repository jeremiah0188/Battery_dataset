import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. 获取 URL 参数 (必须在 Config 之前抓取) =================
# 检查网址是否有 ?admin=Jian (注意 Jian 的首字母大写)
# 使用 .get 方式更稳定
admin_val = st.query_params.get("admin", "")
is_jian_entry = (admin_val == "Jian")

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    layout="wide",
    # 【核心修改】：如果是管理员入口，强制展开侧边栏；否则强制收起
    initial_sidebar_state="expanded" if is_jian_entry else "collapsed"
)

# ================= 3. 深度定制 CSS (追求极致洁净感) =================
# 1. 隐藏菜单、页脚、顶部装饰条
# 2. 如果不是 Jian 模式，物理隐藏整个侧边栏
hide_css = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #stDecoration {display:none;}
"""

if not is_jian_entry:
    # 普通用户模式：彻底隐藏侧边栏及其开关按钮
    hide_css += """
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    """
else:
    # 管理员（Jian）模式：我们需要看到侧边栏，所以要确保它不被 display:none
    # 同时稍微调整 header 确保侧边栏能正常推开页面
    hide_css += """
    [data-testid="stSidebar"] {display: flex !important;}
    [data-testid="collapsedControl"] {visibility: visible !important;}
    """

st.markdown(hide_css + "</style>", unsafe_allow_html=True)

# ================= 4. File & Data Setup =================
DATA_FILE = "dataset.xlsx"
UPLOAD_DIR = "uploaded_files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, header=0, skiprows=[1])
        except:
            df = pd.read_excel(DATA_FILE, header=0)
        df = df.astype(str)
        if 'Status' not in df.columns:
            df['Status'] = 'Approved'
        return df
    else:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Battery Type', 'Capacity (Ah)', 'Status'])


df = load_data()

# ================= 5. 管理员身份验证 (仅在暗门开启时) =================
is_admin = False
if is_jian_entry:
    st.sidebar.title("👨‍💻 Jian's Control Panel")
    # 提醒管理员当前处于特殊入口
    st.sidebar.info("Secret entry detected: Jian Mode")

    try:
        target_password = st.secrets["admin_password"]
    except:
        target_password = ""
        st.sidebar.warning("Admin password not set in Secrets!")

    admin_pw = st.sidebar.text_input("Enter Password", type="password")
    if admin_pw == target_password and target_password != "":
        is_admin = True
        st.sidebar.success("Admin unlocked!")
    elif admin_pw != "":
        st.sidebar.error("Wrong password!")

# ================= 6. Main Page UI =================
st.title("🔋 Open Battery Dataset Portal")
st.markdown("Browse, download, and share open-source battery datasets for research and engineering.")

# 根据身份决定显示的标签页
if is_admin:
    tabs = st.tabs(["📚 Browse Datasets", "☁️ Upload Dataset", "⚙️ Admin Dashboard"])
else:
    tabs = st.tabs(["📚 Browse Datasets", "☁️ Upload Dataset"])

# ================= TAB 1: Browse Datasets =================
with tabs[0]:
    st.header("Available Datasets")
    public_df = df[df['Status'] == 'Approved']
    search_query = st.text_input("🔍 Search datasets (e.g., author, battery type, keyword)")

    if search_query and not public_df.empty:
        mask = public_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = public_df[mask]
    else:
        filtered_df = public_df

    if not filtered_df.empty:
        key_columns = ['Dataset Name', 'Author', 'Battery Type', 'Capacity (Ah)', 'Operation Conditions']
        display_cols = [c for c in key_columns if c in filtered_df.columns]
        st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Dataset Details & Download")
        dataset_names = filtered_df['Dataset Name'].astype(str).unique().tolist()
        selected_dataset = st.selectbox("Select a dataset to view full details:", ["(Select)"] + dataset_names)

        if selected_dataset != "(Select)":
            details = filtered_df[filtered_df['Dataset Name'] == selected_dataset].iloc[0]
            with st.expander(f"📖 {selected_dataset} - Full Information", expanded=True):
                link = details.get('Link', '')
                if pd.notna(link) and str(link).startswith('http') and str(link).lower() != 'nan':
                    st.markdown(f"### [🔗 Click Here to Download / Go to Source]({link})")

                st.markdown("#### Detailed Metadata")
                col1, col2 = st.columns(2)
                all_columns = [c for c in df.columns if c not in ['Link', 'Status']]
                half_index = len(all_columns) // 2
                for i, col_name in enumerate(all_columns):
                    val = details.get(col_name, 'N/A')
                    if str(val).lower() == 'nan': val = 'N/A'
                    if i <= half_index:
                        col1.write(f"{col_name}: {val}")
                    else:
                        col2.write(f"{col_name}: {val}")
    else:
        st.warning("No matching datasets found.")

# ================= TAB 2: Upload Dataset =================
with tabs[1]:
    st.header("Contribute a Dataset")
    st.info("Note: Uploaded datasets will be reviewed before appearing in the public portal.")

    with st.form("upload_form"):
        new_name = st.text_input("Dataset Name *")
        new_author = st.text_input("Author / Institution")
        new_link = st.text_input("External Link (GitHub, Mendeley, etc.)")
        new_battery = st.selectbox("Battery Type", ["Cylindrical", "Pouch", "Prismatic", "Coin cell", "Other"])
        new_notes = st.text_area("Additional Notes")
        uploaded_file = st.file_uploader("Upload local file (Optional)", type=['csv', 'xlsx', 'zip'])
        submitted = st.form_submit_button("📤 Submit for Review")

        if submitted:
            if not new_name:
                st.error("Dataset Name is required!")
            else:
                file_path = ""
                if uploaded_file is not None:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    file_name = f"{timestamp}_{uploaded_file.name}"
                    save_path = os.path.join(UPLOAD_DIR, file_name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_path = save_path

                new_row = {col: "" for col in df.columns}
                new_row.update({
                    'Dataset Name': new_name, 'Author': new_author,
                    'Link': new_link if new_link else file_path,
                    'Battery Type': new_battery, 'Status': 'Pending'
                })
                new_df = pd.DataFrame([new_row])
                updated_df = pd.concat([df, new_df], ignore_index=True)
                updated_df.to_excel(DATA_FILE, index=False)
                st.success(f"Success! '{new_name}' is pending review.")
                st.cache_data.clear()

# ================= TAB 3: Admin Dashboard =================
if is_admin:
    with tabs[2]:
        st.header("⚙️ Admin Dashboard")
        with st.form("admin_form"):
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["Approved", "Pending", "Rejected"])
                },
                use_container_width=True, num_rows="dynamic"
            )
            if st.form_submit_button("💾 Save Changes to Database"):
                edited_df.to_excel(DATA_FILE, index=False)
                st.success("Database updated!")
                st.cache_data.clear()