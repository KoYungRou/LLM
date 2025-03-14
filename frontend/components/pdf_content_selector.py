import streamlit as st
import requests

def render_pdf_selector(api_base_url: str):
    """Display PDF selection dropdown and show parsed content."""
    st.subheader("📚 Select Parsed PDF Content")

    try:
        # Call backend to list available PDFs
        response = requests.get(f"{api_base_url}/list_pdfs")
        if response.status_code != 200:
            st.error("Failed to fetch PDF list from backend.")
            return None, None

        pdf_list = response.json().get("pdfs", [])
        if not pdf_list:
            st.info("No parsed PDF files found.")
            return None, None

        # Show a dropdown (selectbox) for user to choose
        selected_pdf = st.selectbox("Choose a PDF:", pdf_list, key="pdf_selector")

        if st.button("📂 Load PDF Content"):
            content_response = requests.get(
                f"{api_base_url}/select_pdfcontent",
                params={"pdf_name": selected_pdf}
            )

            if content_response.status_code == 200:
                content = content_response.json().get("content", "")
                st.markdown(f"### 📄 {selected_pdf}.md content:")
                st.text_area("Parsed Content", content, height=300)
                return selected_pdf, content
            else:
                st.error("Failed to load PDF content.")

    except Exception as e:
        st.error(f"Error while fetching PDF content: {str(e)}")

    return None, None
