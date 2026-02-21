import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. 获取 URL 参数 (抓取优先级最高) =================
# 获取 ?admin=Jian
# 尝试兼容新旧版本抓取方式
try:
    admin_val = st.query_params.get("admin", "")
except:
    admin_val = st.experimental_get_query_params().get("admin", [""])[0]

is_jian_entry = (admin_val == "Jian")

# ================= 2. Page Configuration =================
st.set_page_config(
    page_title="Open Battery Dataset Portal",
    layout="wide",
    # 如果是 Jian 模式，强制侧边栏展开；否则强制关闭
    initial_sidebar_state="expanded" if is_jian_entry else "collapsed"
)

# ================= 3. 深度定制 CSS (根据身份切换) =================
if not is_jian_entry:
    # 【普通用户模式】：极致洁净，完全抹除侧边栏痕迹
    hide_css = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #stDecoration {display:none;}
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        </style>
    """
else:
    # 【管理员 Jian 模式】：保留侧边栏功能，但隐藏右上角多余菜单
    hide_css = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);} /* 让顶部透明但不消失 */
        #stDecoration {display:none;}
        /* 强制确保侧边栏在 admin 模式下可见 */
        [data-testid="stSidebar"] {display: flex !important; visibility: visible !important;}
        </style>
    """

st.markdown(hide_css, unsafe_allow_html=True)

# ================= 4. 诊断提示 (仅在暗门开启时显示在主屏幕) =================
if is_jian_entry:
    st.toast("🔑 Admin Link Detected!")
    st.info("💡 **Jian Mode Active**: The admin sidebar should be visible on the left. If not, please try to refresh (Ctrl+F5).")

# ================= 5. File & Data Setup =================
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

# ================= 6. 管理员身份验证 =================
is_admin = False
if is_jian_entry:
    with st.sidebar:
        st.title("👨‍💻 Jian's Control Panel")
        try:
            target_password = st.secrets["admin_password"]
        except:
            target_password = ""
            st.warning("Password not set in Secrets!")

        admin_pw = st.text_input("Enter Admin Password", type="password")
        if admin_pw == target_password and target_password != "":
            is_admin = True
            st.success("Admin unlocked!")
        elif admin_pw != "":
            st.error("Incorrect password.")

# ================= 7. Main Page UI =================
st.title("🔋 Open Battery Dataset Portal")
st.markdown("Browse, download, and share open-source battery datasets for research and engineering.")

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