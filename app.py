import streamlit as st
import pandas as pd
import json
import sqlite3
from whatsapp_parser import parse_whatsapp_chat
from gemini_integration import get_gemini_response
from database import init_database, save_summary_to_db, get_all_summaries

# Initialize database
init_database()

# Set page configuration
st.set_page_config(
    page_title="WhatsApp Chat Summarizer",
    page_icon="💬",
    layout="wide"
)

# Title and description
st.title("🛠️ WhatsApp Chat Summarizer for Police Officers")
st.markdown("Upload WhatsApp chat exports (.txt files) to generate structured summaries, task lists, and flagged keywords using AI.")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Upload & Analyze", "View History"])

if page == "Upload & Analyze":
    # Sidebar for file upload
    st.sidebar.header("Upload Chat File")
    uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file", type="txt")

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_chat.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Parse the chat
        try:
            df = parse_whatsapp_chat("temp_chat.txt")
            
            # Display chat preview
            st.header("📋 Chat Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("🔍 Generate Summary", type="primary"):
                with st.spinner("Processing chat with AI..."):
                    # Convert dataframe to string for Gemini
                    chat_history = df.to_string()
                    
                    # Get Gemini response
                    response = get_gemini_response(chat_history)
                    
                    # Parse the response
                    sections = response.split('\n\n')
                    
                    # Extract sections
                    summary_start = response.find("Summary of Topics:") + len("Summary of Topics:")
                    summary_end = response.find("Actionable Tasks:")
                    summary = response[summary_start:summary_end].strip()
                    
                    tasks_start = response.find("Actionable Tasks:") + len("Actionable Tasks:")
                    tasks_end = response.find("Flagged Keywords:")
                    tasks = response[tasks_start:tasks_end].strip()
                    
                    keywords_start = response.find("Flagged Keywords:") + len("Flagged Keywords:")
                    keywords_end = response.find("Raw Gemini Output:")
                    if keywords_end == -1:
                        keywords = response[keywords_start:].strip()
                    else:
                        keywords = response[keywords_start:keywords_end].strip()
                    
                    # Parse tasks into structured data
                    task_lines = [line.strip() for line in tasks.split('\n') if line.strip().startswith('-')]
                    task_data = []
                    
                    for task_line in task_lines:
                        # Parse task line
                        task_line = task_line[1:].strip()  # Remove the '-' prefix
                        if "Task:" in task_line and "Responsible:" in task_line:
                            parts = task_line.split(", ")
                            task_desc = parts[0].replace("Task:", "").strip()
                            responsible = parts[1].replace("Responsible:", "").strip()
                            deadline = parts[2].replace("Deadline:", "").strip() if len(parts) > 2 else "N/A"
                            task_data.append({"Task": task_desc, "Responsible": responsible, "Deadline": deadline})
                    
                    # Save to database
                    record_id = save_summary_to_db(
                        uploaded_file.name,
                        summary,
                        task_data,
                        keywords,
                        response
                    )
                    
                    st.success(f"✅ Summary saved to database with ID: {record_id}")
                    
                    # Display results in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.header("📝 Summary of Topics")
                        st.write(summary)
                        
                        st.header("🔍 Flagged Keywords")
                        st.write(keywords)
                    
                    with col2:
                        st.header("✅ Actionable Tasks")
                        
                        if task_data:
                            task_df = pd.DataFrame(task_data)
                            edited_df = st.data_editor(task_df, use_container_width=True)
                        else:
                            st.write("No actionable tasks found.")
                    
                    # Raw output section
                    with st.expander("🔧 Raw Output"):
                        st.text(response)
                    
                    # Download options
                    st.header("💾 Download Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # JSON download
                        result_data = {
                            "summary": summary,
                            "tasks": task_data,
                            "keywords": keywords,
                            "raw_output": response
                        }
                        json_str = json.dumps(result_data, indent=2)
                        st.download_button(
                            label="Download as JSON",
                            data=json_str,
                            file_name="chat_summary.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # CSV download for tasks
                        if task_data:
                            csv = pd.DataFrame(task_data).to_csv(index=False)
                            st.download_button(
                                label="Download Tasks as CSV",
                                data=csv,
                                file_name="tasks.csv",
                                mime="text/csv"
                            )
        
        except Exception as e:
            st.error(f"Error processing chat file: {str(e)}")

    else:
        st.info("👆 Please upload a WhatsApp chat file (.txt) to get started.")
        
        # Instructions
        st.header("📖 How to Use")
        st.markdown("""
        1. **Export WhatsApp Chat**: Open WhatsApp, go to the chat you want to analyze, tap the three dots menu, select "More" → "Export chat" → "Without media"
        2. **Upload File**: Use the sidebar to upload the exported .txt file
        3. **Review Preview**: Check the parsed chat data in the preview table
        4. **Generate Summary**: Click the "Generate Summary" button to process with AI
        5. **Review Results**: Examine the summary, tasks, and keywords
        6. **Download**: Save results as JSON or CSV files
        """)

elif page == "View History":
    st.header("📚 Chat Summary History")
    
    # Get all summaries from database
    summaries = get_all_summaries()
    
    if summaries:
        # Create a summary table
        summary_table = []
        for summary in summaries:
            summary_table.append({
                "ID": summary['id'],
                "Filename": summary['filename'],
                "Upload Date": summary['upload_timestamp'],
                "Summary Preview": summary['summary'][:100] + "..." if len(summary['summary']) > 100 else summary['summary']
            })
        
        df_history = pd.DataFrame(summary_table)
        st.dataframe(df_history, use_container_width=True)
        
        # Select a summary to view details
        selected_id = st.selectbox("Select a summary to view details:", [s['id'] for s in summaries])
        
        if selected_id:
            selected_summary = next(s for s in summaries if s['id'] == selected_id)
            
            st.header(f"📋 Details for Summary ID: {selected_id}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Summary")
                st.write(selected_summary['summary'])
                
                st.subheader("🔍 Keywords")
                st.write(selected_summary['keywords'])
            
            with col2:
                st.subheader("✅ Tasks")
                if selected_summary['tasks']:
                    task_df = pd.DataFrame(selected_summary['tasks'])
                    st.dataframe(task_df, use_container_width=True)
                else:
                    st.write("No tasks found.")
            
            # Download options for historical data
            st.header("💾 Download Historical Data")
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON download
                result_data = {
                    "summary": selected_summary['summary'],
                    "tasks": selected_summary['tasks'],
                    "keywords": selected_summary['keywords'],
                    "raw_output": selected_summary['raw_output']
                }
                json_str = json.dumps(result_data, indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=json_str,
                    file_name=f"chat_summary_{selected_id}.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV download for tasks
                if selected_summary['tasks']:
                    csv = pd.DataFrame(selected_summary['tasks']).to_csv(index=False)
                    st.download_button(
                        label="Download Tasks as CSV",
                        data=csv,
                        file_name=f"tasks_{selected_id}.csv",
                        mime="text/csv"
                    )
    else:
        st.info("No chat summaries found in the database. Upload and analyze a chat first!")

