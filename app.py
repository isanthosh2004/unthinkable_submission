"""
Code Review Assistant - Main Streamlit Application
A web app for uploading code files, getting AI-powered reviews, and generating PDF reports.
"""

import streamlit as st
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from services.llm_client import CodeReviewLLM
from services.pdf_generator import PDFGenerator
from db.database import DatabaseManager

# Configure Streamlit page
st.set_page_config(
    page_title="Code Review Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services with caching"""
    try:
        llm_client = CodeReviewLLM()
        pdf_generator = PDFGenerator()
        db_manager = DatabaseManager()
        return llm_client, pdf_generator, db_manager
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        return None, None, None

def main():
    """Main application function"""
    st.title("🔍 Code Review Assistant")
    st.markdown("Upload your code files and get AI-powered reviews with downloadable PDF reports!")
    
    # Initialize services
    llm_client, pdf_generator, db_manager = init_services()
    
    if not all([llm_client, pdf_generator, db_manager]):
        st.error("❌ Failed to initialize required services. Please check your configuration.")
        return
    
    # Create tabs
    tab1, tab2 = st.tabs(["📤 Upload & Review", "📊 Reports History"])
    
    with tab1:
        upload_and_review_tab(llm_client, pdf_generator, db_manager)
    
    with tab2:
        reports_history_tab(db_manager, pdf_generator)

def upload_and_review_tab(llm_client, pdf_generator, db_manager):
    """Handle file upload and code review functionality"""
    st.header("Upload Code Files")
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Choose code files to review",
        accept_multiple_files=True,
        type=['py', 'js', 'ts', 'cpp', 'c', 'java', 'go', 'rs', 'php', 'rb', 'swift', 'kt'],
        help="Supported formats: Python, JavaScript, TypeScript, C++, C, Java, Go, Rust, PHP, Ruby, Swift, Kotlin"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Display uploaded files summary
        with st.expander("📋 Upload Summary", expanded=True):
            for i, file in enumerate(uploaded_files, 1):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{i}.** {file.name}")
                with col2:
                    st.write(f"Size: {file.size:,} bytes")
                with col3:
                    st.write(f"Type: {file.type}")
        
        # Review button
        if st.button("🚀 Start Code Review", type="primary", use_container_width=True):
            process_code_review(uploaded_files, llm_client, pdf_generator, db_manager)

def process_code_review(uploaded_files, llm_client, pdf_generator, db_manager):
    """Process uploaded files and generate code review"""
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Prepare file contents
        status_text.text("📝 Preparing file contents...")
        progress_bar.progress(20)
        
        file_contents = []
        for file in uploaded_files:
            content = file.read().decode('utf-8')
            file_contents.append({
                'name': file.name,
                'content': content,
                'size': file.size,
                'type': file.type
            })
        
        # Step 2: Send to LLM
        status_text.text("🤖 Analyzing code with AI...")
        progress_bar.progress(40)
        
        review_result = llm_client.review_code(file_contents)
        
        if not review_result['success']:
            st.error(f"❌ LLM Review failed: {review_result['error']}")
            return
        
        # Step 3: Generate PDF
        status_text.text("📄 Generating PDF report...")
        progress_bar.progress(70)
        
        pdf_path = pdf_generator.generate_report(
            file_contents, 
            review_result['review'], 
            review_result.get('metadata', {})
        )
        
        # Step 4: Save to database
        status_text.text("💾 Saving report to database...")
        progress_bar.progress(90)
        
        report_id = db_manager.save_report(
            files=[f['name'] for f in file_contents],
            pdf_path=pdf_path,
            review_content=review_result['review'],
            metadata=review_result.get('metadata', {})
        )
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Review completed successfully!")
        
        # Display results
        display_review_results(review_result['review'], pdf_path, report_id)
        
    except Exception as e:
        st.error(f"❌ An error occurred during code review: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")

def display_review_results(review_content, pdf_path, report_id):
    """Display the review results and download options"""
    st.success("🎉 Code review completed!")
    
    # Create columns for results and download
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Review Results")
        st.markdown(review_content)
    
    with col2:
        st.subheader("📥 Download Options")
        
        # PDF download button
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file.read(),
                    file_name=f"code_review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        # Re-run analysis button
        if st.button("🔄 Re-run Analysis", use_container_width=True):
            st.rerun()

def reports_history_tab(db_manager, pdf_generator):
    """Display reports history and management options"""
    st.header("📊 Reports History")
    
    # Get all reports
    reports = db_manager.get_all_reports()
    
    if not reports:
        st.info("📭 No reports found. Upload some code files to get started!")
        return
    
    # Search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search reports", placeholder="Search by filename or date...")
    
    with col2:
        sort_option = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Filename"])
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Filter reports
    filtered_reports = reports
    if search_term:
        filtered_reports = [
            r for r in reports 
            if search_term.lower() in r['files'].lower() or 
               search_term.lower() in r['created_at'].lower()
        ]
    
    # Sort reports
    if sort_option == "Date (Newest)":
        filtered_reports.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_option == "Date (Oldest)":
        filtered_reports.sort(key=lambda x: x['created_at'])
    elif sort_option == "Filename":
        filtered_reports.sort(key=lambda x: x['files'])
    
    # Display reports
    st.subheader(f"📋 Found {len(filtered_reports)} report(s)")
    
    for report in filtered_reports:
        with st.expander(f"📄 {report['files']} - {report['created_at']}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Files:** {report['files']}")
                st.write(f"**Created:** {report['created_at']}")
                st.write(f"**Report ID:** {report['id']}")
            
            with col2:
                # Download PDF button
                if os.path.exists(report['pdf_path']):
                    with open(report['pdf_path'], "rb") as pdf_file:
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_file.read(),
                            file_name=f"report_{report['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_{report['id']}"
                        )
                else:
                    st.warning("PDF not found")
            
            with col3:
                # Re-run analysis button
                if st.button("🔄 Re-run", key=f"rerun_{report['id']}"):
                    st.info("Re-run functionality coming soon!")
            
            # Show review preview
            if report['review_content']:
                st.markdown("**Review Preview:**")
                st.markdown(report['review_content'][:500] + "..." if len(report['review_content']) > 500 else report['review_content'])

if __name__ == "__main__":
    main()
