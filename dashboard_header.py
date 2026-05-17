import streamlit as st


def render_header() -> None:
    """Render professional ECEGraphAI dashboard header."""
    header_html = """
    <style>
        .ece-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        }
        .ece-title { 
            font-size: 3.5em;
            font-weight: 900;
            color: white;
            text-align: center;
            margin: 0 0 10px 0;
        }
        .ece-subtitle {
            font-size: 1.3em;
            color: #e0e7ff;
            text-align: center;
            margin: 10px 0 0 0;
        }
    </style>
    <div class="ece-header">
        <div class="ece-title">ECEGraphAI</div>
        <div class="ece-subtitle">A Token-Efficient GraphRAG Learning Assistant</div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)




def render_header_with_stats(
    token_reduction: float | None = None,
    cost_reduction: float | None = None,
    accuracy_maintained: bool | None = None,
) -> None:
    """Render header with dynamic metrics from pipeline runs."""
    header_html = """
    <style>
        .ece-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        }
        .ece-title { 
            font-size: 3.5em;
            font-weight: 900;
            color: white;
            text-align: center;
            margin: 0 0 10px 0;
        }
        .ece-subtitle {
            font-size: 1.3em;
            color: #e0e7ff;
            text-align: center;
            margin: 10px 0 0 0;
        }
    </style>
    <div class="ece-header">
        <div class="ece-title">ECEGraphAI</div>
        <div class="ece-subtitle">A Token-Efficient GraphRAG Learning Assistant</div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
