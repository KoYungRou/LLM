import streamlit as st

# Define model pricing per 1K tokens (in USD)
MODEL_PRICING = {
    "GPT-4o": {"input": 0.0000025, "output": 0.000001},
    "Gemini-Flash": {"input": 0.0035, "output": 0.0035},
    "DeepSeek": {"input": 0.0009, "output": 0.0009},
    "Claude": {"input": 0.008, "output": 0.024},
    "Grok": {"input": 0.005, "output": 0.015}
}

def render_cost_display():
    """Render the token usage and cost display component."""
    st.subheader("Token Usage & Cost")
    
    # Display token usage
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Input Tokens", 
            f"{st.session_state.token_usage['total_input_tokens']:,}"
        )
    with col2:
        st.metric(
            "Output Tokens", 
            f"{st.session_state.token_usage['total_output_tokens']:,}"
        )
    
    # Display cost
    st.metric(
        "Total Cost", 
        f"${st.session_state.token_usage['total_cost']:.4f}"
    )
    
    # Display current model pricing
    if st.session_state.selected_model in MODEL_PRICING:
        pricing = MODEL_PRICING[st.session_state.selected_model]
        st.caption(f"Current model pricing (per 1K tokens):")
        st.caption(f"Input: ${pricing['input']:.4f} | Output: ${pricing['output']:.4f}")
    
    # Reset button
    if st.button("Reset Usage Stats"):
        st.session_state.token_usage = {
            "total_input_tokens": 0, 
            "total_output_tokens": 0, 
            "total_cost": 0
        }
        st.rerun()