import streamlit as st
import requests
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

def render_file_upload():
    """Render the file upload and PDF selection components."""
    st.subheader("PDF Document")
    
 
    tab1, tab2 = st.tabs(["Upload New", "Select Existing"])
    
    with tab1:
        
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf", key="pdf_uploader")
        
    
        if uploaded_file is not None and (
            "pdf_name" not in st.session_state 
            or st.session_state.pdf_name != uploaded_file.name 
            or st.session_state.pdf_content is None
        ):
            with st.spinner("Processing PDF..."):
                try:
                   
                    pdf_bytes = uploaded_file.getvalue()

                    
                    files = {
                        "file": (uploaded_file.name, pdf_bytes, "application/pdf"),
                    }

                    
                    response = requests.post(f"{API_URL}/upload_pdf", files=files)
                    response.raise_for_status()

      
                    result = response.json()
                    
                    
                    st.session_state.pdf_content = result.get("content")
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.selected_text = None

                    st.success(f"PDF uploaded and processed: {uploaded_file.name}")

                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
    
    with tab2:
  
        try:
            response = requests.get(f"{API_URL}/list_pdfs")
            response.raise_for_status()
            available_pdfs = response.json().get("pdfs", [])
            
            if available_pdfs:
                selected_pdf = st.selectbox(
                    "Select a previously processed PDF",
                    options=available_pdfs,
                    key="pdf_selector"
                )
                
                if st.button("Load Selected PDF"):
                    with st.spinner("Loading PDF content..."):
                        resp = requests.get(
                            f"{API_URL}/select_pdfcontent", 
                            params={"pdf_name": selected_pdf}
                        )
                        resp.raise_for_status()
                        result = resp.json()
                        
                        st.session_state.pdf_content = result.get("content")
                        st.session_state.pdf_name = selected_pdf
                        st.session_state.selected_text = None
                        
                        st.success(f"PDF loaded: {selected_pdf}")
            else:
                st.info("No previously processed PDFs available.")
        except Exception as e:
            st.error(f"Error loading PDF list: {str(e)}")
    

    if "pdf_name" in st.session_state and st.session_state.pdf_name:
        st.caption(f"Current PDF: {st.session_state.pdf_name}")
        
        if st.session_state.pdf_content:
            st.subheader("PDF Content")
         
            pdf_container = st.container()
            with pdf_container:
            
                st.markdown(st.session_state.pdf_content)
           
            st.caption("To ask a question about specific text, select it below:")
            text_selection = st.text_area(
                "Selected text (leave empty to query entire document):",
                value=st.session_state.selected_text if st.session_state.selected_text else "",
                height=100,
                key="text_selection"
            )
            
        
            if text_selection.strip():
                st.session_state.selected_text = text_selection
            else:
                st.session_state.selected_text = None
