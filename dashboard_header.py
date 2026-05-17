import streamlit as st


def render_header():
    """
    Professional dashboard header for ECEGraphAI with modern AI theme styling.
    Production-ready component with hackathon-style design.
    """
    st.markdown("""
    <style>
    /* Main header container */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }

    /* Title styling */
    .main-title {
        font-size: 3.5em;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin: 0;
        padding: 20px 0 10px 0;
        letter-spacing: -1px;
        background: linear-gradient(120deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Subtitle styling */
    .subtitle {
        font-size: 1.3em;
        color: #e0e7ff;
        text-align: center;
        margin: 10px 0 20px 0;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Description styling */
    .description {
        font-size: 1em;
        color: #f0f0f5;
        text-align: center;
        margin: 20px 0;
        line-height: 1.6;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Icons row */
    .icons-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 30px 0;
        flex-wrap: wrap;
    }

    .icon-item {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    .icon-emoji {
        font-size: 2.5em;
        line-height: 1;
    }

    .icon-label {
        font-size: 0.95em;
        color: #e0e7ff;
        font-weight: 600;
    }

    /* Metrics banner */
    .metrics-banner {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 25px;
        margin: 25px 0 0 0;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }

    .metric-item {
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border-left: 3px solid #8dd3f0;
        transition: all 0.3s ease;
    }

    .metric-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 1.8em;
        font-weight: 900;
        color: #8dd3f0;
        margin: 10px 0 5px 0;
    }

    .metric-label {
        font-size: 0.85em;
        color: #e0e7ff;
        font-weight: 600;
        margin: 0;
    }

    .metric-icon {
        font-size: 1.5em;
        margin-bottom: 10px;
    }

    /* Separator */
    .header-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 25px 0 0 0;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5em;
        }
        .subtitle {
            font-size: 1.1em;
        }
        .icons-row {
            gap: 20px;
        }
        .metrics-banner {
            grid-template-columns: 1fr;
        }
    }
    </style>

    <div class="header-container">
        <div class="main-title">ECEGraphAI</div>
        <div class="subtitle">A Token-Efficient GraphRAG Learning Assistant</div>

        <div class="description">
            Comparing <strong>LLM-Only</strong>, <strong>Basic RAG</strong>, and <strong>GraphRAG</strong> pipelines
            for faster, cheaper, and more accurate AI retrieval.
        </div>

        <div class="icons-row">
            <div class="icon-item">
                <div class="icon-emoji">🧠</div>
                <div class="icon-label">LLM-Only</div>
            </div>
            <div class="icon-item">
                <div class="icon-emoji">📚</div>
                <div class="icon-label">Basic RAG</div>
            </div>
            <div class="icon-item">
                <div class="icon-emoji">🕸️</div>
                <div class="icon-label">GraphRAG</div>
            </div>
        </div>

        <div class="metrics-banner">
            <div class="metric-item">
                <div class="metric-icon">⬇️</div>
                <div class="metric-value">47%</div>
                <div class="metric-label">Token Reduction</div>
            </div>
            <div class="metric-item">
                <div class="metric-icon">💰</div>
                <div class="metric-value">Lower Cost</div>
                <div class="metric-label">Cost Efficient</div>
            </div>
            <div class="metric-item">
                <div class="metric-icon">⬆️</div>
                <div class="metric-value">Better Accuracy</div>
                <div class="metric-label">Quality Maintained</div>
            </div>
        </div>
        <div class="header-divider"></div>
    </div>
    """, unsafe_allow_html=True)


def render_header_with_stats(token_reduction: float = None, cost_reduction: float = None, accuracy_maintained: bool = None):
    """
    Professional dashboard header with dynamic stats.
    Use this version when you have real metrics from pipeline runs.

    Args:
        token_reduction: Percentage token reduction (0-100)
        cost_reduction: Percentage cost reduction (0-100)
        accuracy_maintained: Boolean indicating if quality is maintained
    """
    st.markdown("""
    <style>
    /* Main header container */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }

    /* Title styling */
    .main-title {
        font-size: 3.5em;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin: 0;
        padding: 20px 0 10px 0;
        letter-spacing: -1px;
        background: linear-gradient(120deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Subtitle styling */
    .subtitle {
        font-size: 1.3em;
        color: #e0e7ff;
        text-align: center;
        margin: 10px 0 20px 0;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Description styling */
    .description {
        font-size: 1em;
        color: #f0f0f5;
        text-align: center;
        margin: 20px 0;
        line-height: 1.6;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Icons row */
    .icons-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 30px 0;
        flex-wrap: wrap;
    }

    .icon-item {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }

    .icon-emoji {
        font-size: 2.5em;
        line-height: 1;
    }

    .icon-label {
        font-size: 0.95em;
        color: #e0e7ff;
        font-weight: 600;
    }

    /* Metrics banner */
    .metrics-banner {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 25px;
        margin: 25px 0 0 0;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }

    .metric-item {
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border-left: 3px solid #8dd3f0;
        transition: all 0.3s ease;
    }

    .metric-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 1.8em;
        font-weight: 900;
        color: #8dd3f0;
        margin: 10px 0 5px 0;
    }

    .metric-label {
        font-size: 0.85em;
        color: #e0e7ff;
        font-weight: 600;
        margin: 0;
    }

    .metric-icon {
        font-size: 1.5em;
        margin-bottom: 10px;
    }

    /* Separator */
    .header-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 25px 0 0 0;
    }

    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5em;
        }
        .subtitle {
            font-size: 1.1em;
        }
        .icons-row {
            gap: 20px;
        }
        .metrics-banner {
            grid-template-columns: 1fr;
        }
    }
    </style>

    <div class="header-container">
        <div class="main-title">ECEGraphAI</div>
        <div class="subtitle">A Token-Efficient GraphRAG Learning Assistant</div>

        <div class="description">
            Comparing <strong>LLM-Only</strong>, <strong>Basic RAG</strong>, and <strong>GraphRAG</strong> pipelines
            for faster, cheaper, and more accurate AI retrieval.
        </div>

        <div class="icons-row">
            <div class="icon-item">
                <div class="icon-emoji">🧠</div>
                <div class="icon-label">LLM-Only</div>
            </div>
            <div class="icon-item">
                <div class="icon-emoji">📚</div>
                <div class="icon-label">Basic RAG</div>
            </div>
            <div class="icon-item">
                <div class="icon-emoji">🕸️</div>
                <div class="icon-label">GraphRAG</div>
            </div>
        </div>

        <div class="metrics-banner">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-icon">⬇️</div>
            <div class="metric-value">{token_reduction:.0f}%</div>
            <div class="metric-label">Token Reduction</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-icon">💰</div>
            <div class="metric-value">{cost_reduction:.0f}%</div>
            <div class="metric-label">Cost Reduction</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        status = "✓ Yes" if accuracy_maintained else "⚠️ Check"
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-icon">⬆️</div>
            <div class="metric-value">{status}</div>
            <div class="metric-label">Quality Maintained</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
        <div class="header-divider"></div>
    </div>
    """, unsafe_allow_html=True)
