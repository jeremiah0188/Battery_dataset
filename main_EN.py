import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. Page Configuration (必须放在最前面) =================
st.set_page_config(page_title="Open Battery Dataset Portal", layout="wide")

# --- 隐藏 Streamlit 默认装饰和 GitHub 图标 ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}       /* 隐藏右上角菜单 */
            footer {visibility: hidden;}          /* 隐藏页脚 */
            header {visibility: hidden;}          /* 隐藏顶部 GitHub 图标栏 */
            #stDecoration {display:none;}         /* 隐藏顶部彩虹装饰条 */
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ================= 2. File & Directory Setup =================
DATA_FILE = "dataset.xlsx"
UPLOAD_DIR = "uploaded_files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ================= 3. Load Data & Initialize Status =================
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            # 尝试跳过第二行（如果是元数据行）
            df = pd.read_excel(DATA_FILE, header=0, skiprows=[1])
        except:
            df = pd.read_excel(DATA_FILE, header=0)

        df = df.astype(str)

        # 核心逻辑：确保 Status 列存在
        if 'Status' not in df.columns:
            df['Status'] = 'Approved'
        return df
    else:
        return pd.DataFrame(columns=['Dataset Name', 'Author', 'Battery Type', 'Capacity (Ah)', 'Status'])

df = load_data()

# ================= 4. Sidebar Admin Login =================
st.sidebar.title("👨‍💻 Admin Access")
st.sidebar.write("For host to review datasets.")

# 从 Secrets 安全读取密码，如果未设置则默认为空字符串防止报错
try:
    target_password = st.secrets["admin_password"]
except:
    target_password = ""
    st.sidebar.warning("Admin password not set in Secrets!")

admin_pw = st.sidebar.text_input("Password", type="password")

# ================= 5. Main Page UI =================
st.title("🔋 Open Battery Dataset Portal")
st.markdown("Browse, download, and share open-source battery datasets for research and engineering.")

# 验证密码是否正确
is_admin = (admin_pw == target_password and target_password != "")

if is_admin:
    st.sidebar.success("Admin unlocked!")
    tabs = st.tabs(["📚 Browse Datasets", "☁️ Upload Dataset", "⚙️ Admin Dashboard"])
else:
    tabs = st.tabs(["📚 Browse Datasets", "☁️ Upload Dataset"])

# ================= TAB 1: Browse Datasets =================
with tabs[0]:
    st.header("Available Datasets")

    # 过滤：向公众展示 "Approved" 的数据
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

        valid_datasets = filtered_df[filtered_df['Dataset Name'].notna()]
        dataset_names = valid_datasets['Dataset Name'].astype(str).unique().tolist()

        selected_dataset = st.selectbox("Select a dataset to view full details:", ["(Select)"] + dataset_names)

        if selected_dataset != "(Select)":
            details = valid_datasets[valid_datasets['Dataset Name'] == selected_dataset].iloc[0]

            with st.expander(f"📖 {selected_dataset} - Full Information", expanded=True):
                link = details.get('Link', '')
                if pd.notna(link) and str(link).startswith('http') and str(link).lower() != 'nan':
                    st.markdown(f"### [🔗 Click Here to Download / Go to Source]({link})")
                else:
                    st.info("No external download link provided.")

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
    st.info("Note: Uploaded datasets will be reviewed by the admin before appearing in the public portal.")

    with st.form("upload_form"):
        new_name = st.text_input("Dataset Name *")
        new_author = st.text_input("Author / Institution")
        new_link = st.text_input("External Link (GitHub, Mendeley, Drive, etc.)")
        new_battery = st.selectbox("Battery Type",
                                   ["Cylindrical (18650/21700)", "Pouch", "Prismatic", "Coin cell", "Other"])
        new_notes = st.text_area("Additional Notes / Description")

        uploaded_file = st.file_uploader("Upload local file (Optional)",
                                         type=['csv', 'xlsx', 'zip', 'rar'])

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
                    'Dataset Name': new_name,
                    'Author': new_author,
                    'Link': new_link if new_link else file_path,
                    'Battery Type': new_battery,
                    'Additional Notes': new_notes,
                    'Status': 'Pending'
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
        st.write("Manage dataset submissions. Change status to 'Approved' to publish.")

        with st.form("admin_form"):
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Approved", "Pending", "Rejected"],
                        required=True,
                    )
                },
                use_container_width=True,
                num_rows="dynamic"
            )

            save_changes = st.form_submit_button("💾 Save Changes to Database")

            if save_changes:
                edited_df.to_excel(DATA_FILE, index=False)
                st.success("Database updated successfully!")
                st.cache_data.clear()