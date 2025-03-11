import streamlit as st

def render_question_input(process_query_func, generate_summary_func):
    """
    Render the question input component.
    
    Args:
        process_query_func: Function to process user queries
        generate_summary_func: Function to generate document summaries
    """
    # Create a container for the input area
    input_container = st.container(border=True)
    
    with input_container:
        # Question input
        col1, col2 = st.columns([5, 1])
        
        with col1:
            query = st.text_area(
                "Ask a question about the document:",
                key="query_input",
                height=100,
                placeholder="Type your question here..."
            )
        
        with col2:
            st.write("") # Add some space
            st.write("") # Add some space
            
            # Submit button
            if st.button("Send", use_container_width=True):
                if query.strip():
                    process_query_func(query.strip())
                    # Clear the input after submission
                    st.session_state.query_input = ""
                else:
                    st.warning("Please enter a question.")
            
            # Summary button
            if st.button("Summarize", use_container_width=True):
                generate_summary_func()