"""
Alternative theme for ECEGraphAI dashboard header.
Provides dark theme and other style variations.
"""

import streamlit as st


def render_header_dark_theme():
    """
    Professional dashboard header with dark/cyberpunk theme.
    Alternative to the gradient purple theme.
    """
    st.markdown("""
    <style>
    /* Dark theme header container */
    .header-container-dark {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(15, 52, 96, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(52, 211, 153, 0.2);
    }

    /* Neon title */
    .main-title-neon {
        font-size: 3.5em;
        font-weight: 900;
        text-align: center;
        margin: 0;
        padding: 20px 0 10px 0;
        letter-spacing: 2px;
        color: #00ff88;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff8833;
        font-family: 'Courier New', monospace;
    }

    /* Cyan subtitle */
    .subtitle-neon {
        font-size: 1.2em;
        color: #00d9ff;
        text-align: center;
        margin: 10px 0 20px 0;
        font-weight: 600;
        letter-spacing: 1px;
        text-shadow: 0 0 5px #00d9ff77;
    }

    /* Description */
    .description-dark {
        font-size: 1em;
        color: #e0e0e0;
        text-align: center;
        margin: 20px 0;
        line-height: 1.6;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Icons row - dark theme */
    .icons-row-dark {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 30px 0;
        flex-wrap: wrap;
    }

    .icon-item-dark {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        padding: 15px 20px;
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .icon-item-dark:hover {
        background: rgba(0, 255, 136, 0.1);
        border-color: rgba(0, 255, 136, 0.5);
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.2);
    }

    .icon-emoji-dark {
        font-size: 2.5em;
        line-height: 1;
        filter: drop-shadow(0 0 5px #00ff8844);
    }

    .icon-label-dark {
        font-size: 0.95em;
        color: #00ff88;
        font-weight: 600;
    }

    /* Metrics banner - dark */
    .metrics-banner-dark {
        background: rgba(15, 52, 96, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        padding: 25px;
        margin: 25px 0 0 0;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }

    .metric-item-dark {
        text-align: center;
        padding: 15px;
        background: rgba(0, 255, 136, 0.05);
        border-radius: 10px;
        border-left: 3px solid #00ff88;
        transition: all 0.3s ease;
    }

    .metric-item-dark:hover {
        background: rgba(0, 255, 136, 0.1);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.15);
    }

    .metric-value-dark {
        font-size: 1.8em;
        font-weight: 900;
        color: #00ff88;
        margin: 10px 0 5px 0;
        text-shadow: 0 0 10px #00ff8844;
    }

    .metric-label-dark {
        font-size: 0.85em;
        color: #a0a0a0;
        font-weight: 600;
        margin: 0;
    }

    .metric-icon-dark {
        font-size: 1.5em;
        margin-bottom: 10px;
    }

    /* Divider */
    .header-divider-dark {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.3), transparent);
        margin: 25px 0 0 0;
    }

    @media (max-width: 768px) {
        .main-title-neon {
            font-size: 2.5em;
        }
        .subtitle-neon {
            font-size: 1.1em;
        }
        .icons-row-dark {
            gap: 20px;
        }
        .metrics-banner-dark {
            grid-template-columns: 1fr;
        }
    }
    </style>

    <div class="header-container-dark">
        <div class="main-title-neon">&gt; ECEGraphAI</div>
        <div class="subtitle-neon">Token-Efficient GraphRAG Learning Assistant</div>

        <div class="description-dark">
            Comparing <strong>LLM-Only</strong>, <strong>Basic RAG</strong>, and <strong>GraphRAG</strong> pipelines
            for faster, cheaper, and more accurate AI retrieval.
        </div>

        <div class="icons-row-dark">
            <div class="icon-item-dark">
                <div class="icon-emoji-dark">🧠</div>
                <div class="icon-label-dark">LLM-Only</div>
            </div>
            <div class="icon-item-dark">
                <div class="icon-emoji-dark">📚</div>
                <div class="icon-label-dark">Basic RAG</div>
            </div>
            <div class="icon-item-dark">
                <div class="icon-emoji-dark">🕸️</div>
                <div class="icon-label-dark">GraphRAG</div>
            </div>
        </div>

        <div class="metrics-banner-dark">
            <div class="metric-item-dark">
                <div class="metric-icon-dark">⬇️</div>
                <div class="metric-value-dark">47%</div>
                <div class="metric-label-dark">Token Reduction</div>
            </div>
            <div class="metric-item-dark">
                <div class="metric-icon-dark">💰</div>
                <div class="metric-value-dark">52%</div>
                <div class="metric-label-dark">Cost Reduction</div>
            </div>
            <div class="metric-item-dark">
                <div class="metric-icon-dark">⬆️</div>
                <div class="metric-value-dark">✓ Yes</div>
                <div class="metric-label-dark">Quality Maintained</div>
            </div>
        </div>
        <div class="header-divider-dark"></div>
    </div>
    """, unsafe_allow_html=True)


def render_header_minimal():
    """
    Minimal, clean header design with subtle styling.
    Best for professional/academic contexts.
    """
    st.markdown("""
    <style>
    .header-minimal {
        padding: 30px 20px;
        margin-bottom: 30px;
        border-bottom: 2px solid #e5e7eb;
    }

    .title-minimal {
        font-size: 3em;
        font-weight: 900;
        text-align: center;
        color: #1f2937;
        margin: 0;
        padding: 0;
    }

    .subtitle-minimal {
        font-size: 1.2em;
        text-align: center;
        color: #6b7280;
        margin: 15px 0;
        font-weight: 500;
    }

    .description-minimal {
        font-size: 0.95em;
        text-align: center;
        color: #4b5563;
        margin: 20px 0;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    .metrics-row-minimal {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-top: 25px;
    }

    .metric-minimal {
        text-align: center;
        padding: 15px;
        background: #f9fafb;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .metric-value-minimal {
        font-size: 1.6em;
        font-weight: 900;
        color: #2563eb;
        margin: 10px 0 5px 0;
    }

    .metric-label-minimal {
        font-size: 0.8em;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    @media (max-width: 768px) {
        .title-minimal {
            font-size: 2em;
        }
        .subtitle-minimal {
            font-size: 1em;
        }
        .metrics-row-minimal {
            grid-template-columns: 1fr;
        }
    }
    </style>

    <div class="header-minimal">
        <div class="title-minimal">ECEGraphAI</div>
        <div class="subtitle-minimal">A Token-Efficient GraphRAG Learning Assistant</div>
        <div class="description-minimal">
            Comparing LLM-Only, Basic RAG, and GraphRAG pipelines for faster, cheaper, and more accurate AI retrieval.
        </div>

        <div class="metrics-row-minimal">
            <div class="metric-minimal">
                <div class="metric-value-minimal">47%</div>
                <div class="metric-label-minimal">Token Reduction</div>
            </div>
            <div class="metric-minimal">
                <div class="metric-value-minimal">52%</div>
                <div class="metric-label-minimal">Cost Reduction</div>
            </div>
            <div class="metric-minimal">
                <div class="metric-value-minimal">✓ Maintained</div>
                <div class="metric-label-minimal">Quality</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="ECEGraphAI - Theme Showcase", layout="wide")

    st.write("## Available Themes")

    with st.tabs(["Purple Gradient", "Dark Neon", "Minimal"]):
        with st.container():
            from dashboard_header import render_header
            st.subheader("Default: Purple Gradient Theme")
            render_header()

        with st.container():
            st.subheader("Dark Neon Theme")
            render_header_dark_theme()

        with st.container():
            st.subheader("Minimal Theme")
            render_header_minimal()
