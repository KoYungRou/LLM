import streamlit as st

# Define available models with their details
AVAILABLE_MODELS = {
    "GPT-4o": {
        "provider": "OpenAI",
        "description": "OpenAI's most powerful model",
        "doc_link": "https://platform.openai.com/docs/models"
    },
    "Gemini-Flash": {
        "provider": "Google",
        "description": "Google's fast and efficient model",
        "doc_link": "https://ai.google.dev/gemini-api/docs"
    },
    "DeepSeek": {
        "provider": "DeepSeek",
        "description": "DeepSeek LLM for advanced reasoning",
        "doc_link": "https://www.deepseek.com/api-documentation"
    },
    "Claude": {
        "provider": "Anthropic",
        "description": "Anthropic's helpul AI assistant",
        "doc_link": "https://docs.anthropic.com"
    },
    "Grok": {
        "provider": "xAI",
        "description": "xAI's chat model",
        "doc_link": "https://grok.x.ai/docs"
    }
}

def render_model_selector():
    """Render the model selector component in the sidebar."""
    st.subheader("Select Model")
    
    # Model selection
    selected_model = st.selectbox(
        "Choose an LLM model:",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
        key="model_selector"
    )
    
    # Update session state
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
    
    # Display model info
    model_info = AVAILABLE_MODELS[selected_model]
    st.caption(f"Provider: {model_info['provider']}")
    st.caption(model_info['description'])
    st.caption(f"[Documentation]({model_info['doc_link']})")