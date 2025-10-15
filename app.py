"""
Code Review Assistant - Main Streamlit Application
A web app for uploading code files, getting AI-powered reviews, and generating PDF reports.
"""

import streamlit as st
import os
from datetime import datetime
from typing import List, Dict, Any
import traceback
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# ===========================================================
# 🌐 Load Environment and API Configuration
# ===========================================================

# 1️⃣ Load from .env for local dev
load_dotenv()

# 2️⃣ Load from Streamlit Cloud Secrets (takes priority)
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
    os.environ["DATABASE_PATH"] = st.secrets.get("DATABASE_PATH", "db/code_reviews.db")
    os.environ["REPORTS_DIRECTORY"] = st.secrets.get("REPORTS_DIRECTORY", "reports")
    os.environ["DEFAULT_MODEL"] = st.secrets.get("DEFAULT_MODEL", "qwen/qwen-2.5-coder-32b-instruct:free")

# ✅ Debug indicator – shows if API key is loaded
st.caption(f"🔑 API Key Loaded: {bool(os.getenv('OPENROUTER_API_KEY'))}")

# ===========================================================
# 🧠 Import Custom Modules
# ===========================================================
from services.llm_client import CodeReviewLLM
from services.pdf_generator import PDFGenerator
from db.database import DatabaseManager

# ---------------------------------------------------------------------
# 🧠 Streamlit Page Configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Code Review Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# 🔐 Simple Authentication (Session-Based)
# ---------------------------------------------------------------------
USERS = {
    "admin": {"name": "Admin", "password": "admin123", "is_admin": True},
    "santhosh": {"name": "Santhosh Kumar", "password": "user123", "is_admin": False},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


def do_login():
    """Perform simple credential check"""
    input_user = st.session_state.get("login_username", "").strip()
    input_pass = st.session_state.get("login_password", "")
    user = USERS.get(input_user)
    if user and input_pass == user["password"]:
        st.session_state.logged_in = True
        st.session_state.username = input_user
        st.session_state.display_name = user["name"]
        st.session_state.is_admin = user.get("is_admin", False)
        st.success(f"✅ Logged in as {user['name']}")
    else:
        st.session_state.logged_in = False
        st.error("❌ Invalid username or password")


def do_logout():
    """Clear login session"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.display_name = ""
    st.session_state.is_admin = False
    st.experimental_rerun()


# Sidebar Login
if not st.session_state.logged_in:
    st.sidebar.title("🔐 Sign In")
    st.sidebar.text_input("Username", key="login_username")
    st.sidebar.text_input("Password", type="password", key="login_password")
    st.sidebar.button("Sign In", on_click=do_login)
    st.sidebar.markdown("---")
    st.sidebar.info("Demo: admin/admin123 or santhosh/user123")
    st.stop()
else:
    st.sidebar.write(f"👋 Welcome, **{st.session_state.display_name}**")
    if st.sidebar.button("Logout"):
        do_logout()

# Convenience vars
username = st.session_state.username
is_admin = st.session_state.is_admin

# ---------------------------------------------------------------------
# ⚙️ Initialize Services
# ---------------------------------------------------------------------
@st.cache_resource
def init_services():
    """Initialize all services"""
    try:
        llm_client = CodeReviewLLM()
        pdf_generator = PDFGenerator()
        db_manager = DatabaseManager()
        return llm_client, pdf_generator, db_manager
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {str(e)}")
        return None, None, None

# ---------------------------------------------------------------------
# 📊 Complexity Graph
# ---------------------------------------------------------------------
def plot_complexity_graph():
    """Sample time & space complexity visualization"""
    n = [10, 100, 1000, 10000]
    time = [1, 2, 3, 4]
    space = [1, 1.5, 2, 2.5]
    fig, ax = plt.subplots()
    ax.plot(n, time, label="Time Complexity (O(n))", marker="o")
    ax.plot(n, space, label="Space Complexity (O(log n))", marker="s")
    ax.legend()
    ax.set_xlabel("Input size (n)")
    ax.set_ylabel("Growth")
    ax.set_title("📈 Sample Complexity Graph")
    ax.grid(True)
    st.pyplot(fig)

# ---------------------------------------------------------------------
# 🚀 Main Application
# ---------------------------------------------------------------------
def main():
    st.title("🔍 Code Review Assistant")
    st.markdown("Upload your code files and get AI-powered reviews with downloadable PDF reports!")

    llm_client, pdf_generator, db_manager = init_services()
    if not all([llm_client, pdf_generator, db_manager]):
        st.error("❌ Could not initialize required services.")
        return

    # Role-based view
    if is_admin:
        st.sidebar.subheader("🧭 Admin Dashboard")
        admin_dashboard(db_manager)
    else:
        st.sidebar.subheader("👤 User Dashboard")
        user_dashboard(username, llm_client, pdf_generator, db_manager)

# ---------------------------------------------------------------------
# 👑 Admin Dashboard
# ---------------------------------------------------------------------
def admin_dashboard(db_manager):
    st.header("📊 All Reports (Admin View)")
    reports = db_manager.get_all_reports()
    if not reports:
        st.info("📭 No reports found yet.")
        return
    search_term = st.text_input("🔍 Search by username, file, or date")
    if search_term:
        reports = [r for r in reports if search_term.lower() in str(r).lower()]
    st.write(f"Showing {len(reports)} reports.")
    display_reports(reports)

# ---------------------------------------------------------------------
# 👤 User Dashboard
# ---------------------------------------------------------------------
def user_dashboard(username, llm_client, pdf_generator, db_manager):
    tab1, tab2 = st.tabs(["📤 Upload & Review", "📜 My Reports"])
    with tab1:
        upload_and_review_tab(username, llm_client, pdf_generator, db_manager)
    with tab2:
        reports_history_tab(username, db_manager, pdf_generator)

# ---------------------------------------------------------------------
# 🧩 Upload & Review Tab
# ---------------------------------------------------------------------
def upload_and_review_tab(username, llm_client, pdf_generator, db_manager):
    st.header("📤 Upload Code Files for Review")
    uploaded_files = st.file_uploader(
        "Choose code files to review",
        accept_multiple_files=True,
        type=['py', 'js', 'ts', 'cpp', 'c', 'java', 'go', 'rs', 'php', 'rb', 'swift', 'kt'],
        help="Supported: Python, JS, TS, C++, Java, Go, Rust, PHP, Ruby, Swift, Kotlin"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        with st.expander("📋 Uploaded Files Summary", expanded=True):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"**{i}. {file.name}** — {file.size:,} bytes")

        st.subheader("📊 Live Complexity Graph (Example)")
        plot_complexity_graph()

        if st.button("🚀 Start Code Review", type="primary", use_container_width=True):
            process_code_review(username, uploaded_files, llm_client, pdf_generator, db_manager)

# ---------------------------------------------------------------------
# 🤖 Code Review Processing
# ---------------------------------------------------------------------
def process_code_review(username, uploaded_files, llm_client, pdf_generator, db_manager):
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("📝 Reading files...")
        progress_bar.progress(20)
        file_contents = []
        for file in uploaded_files:
            content = file.read().decode("utf-8")
            file_contents.append({
                "name": file.name,
                "content": content,
                "size": file.size,
                "type": file.type
            })

        status_text.text("🤖 Generating AI-powered review...")
        progress_bar.progress(50)
        review_result = llm_client.review_code(file_contents)
        if not review_result["success"]:
            st.error(f"❌ LLM Review failed: {review_result['error']}")
            return

        status_text.text("📄 Generating PDF report...")
        progress_bar.progress(80)
        pdf_path = pdf_generator.generate_report(
            file_contents,
            review_result["review"],
            review_result.get("metadata", {})
        )

        status_text.text("💾 Saving report...")
        report_id = db_manager.save_report(
            username=username,
            files=[f["name"] for f in file_contents],
            pdf_path=pdf_path,
            review_content=review_result["review"],
            metadata=review_result.get("metadata", {})
        )

        progress_bar.progress(100)
        status_text.text("✅ Review completed successfully!")
        display_review_results(review_result["review"], pdf_path, report_id)

    except Exception as e:
        st.error(f"❌ Error during code review: {str(e)}")
        st.error(traceback.format_exc())

# ---------------------------------------------------------------------
# 🧾 Display Review Results
# ---------------------------------------------------------------------
def display_review_results(review_content, pdf_path, report_id):
    st.success("🎉 Code review completed!")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📋 AI Review Summary")
        st.markdown(review_content)
    with col2:
        st.subheader("📥 Download Report")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file.read(),
                    file_name=f"code_review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        if st.button("🔄 Re-run Analysis", use_container_width=True):
            st.rerun()

# ---------------------------------------------------------------------
# 📜 Reports History Tab
# ---------------------------------------------------------------------
def reports_history_tab(username, db_manager, pdf_generator):
    st.header("📜 My Past Reviews")
    reports = db_manager.get_reports_for_user(username)
    if not reports:
        st.info("📭 No reports found. Try uploading your first code review!")
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search reports")
    with col2:
        sort_option = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Filename"])

    filtered_reports = reports
    if search_term:
        filtered_reports = [r for r in reports if search_term.lower() in r["files"].lower()]

    if sort_option == "Date (Newest)":
        filtered_reports.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_option == "Date (Oldest)":
        filtered_reports.sort(key=lambda x: x["created_at"])
    elif sort_option == "Filename":
        filtered_reports.sort(key=lambda x: x["files"])

    display_reports(filtered_reports)

# ---------------------------------------------------------------------
# 🧱 Helper Function — Display Reports
# ---------------------------------------------------------------------
def display_reports(reports):
    st.subheader(f"📋 Found {len(reports)} report(s)")
    for report in reports:
        with st.expander(f"📄 {report['files']} — {report['created_at']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 **User:** {report.get('username', 'N/A')}")
                st.write(f"📁 **Files:** {report['files']}")
                st.write(f"🕒 **Created:** {report['created_at']}")
                st.write(f"🆔 **Report ID:** {report['id']}")
            with col2:
                if os.path.exists(report["pdf_path"]):
                    with open(report["pdf_path"], "rb") as pdf_file:
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_file.read(),
                            file_name=f"report_{report['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_{report['id']}"
                        )
                else:
                    st.warning("⚠️ PDF not found")

            if report.get("review_content"):
                st.markdown("**Preview:**")
                preview = report["review_content"][:500] + "..." if len(report["review_content"]) > 500 else report["review_content"]
                st.markdown(preview)

# ---------------------------------------------------------------------
# 🏁 Entry Point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
