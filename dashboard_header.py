import streamlit as st


_HEADER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@500;700;800&display=swap');

:root {
    --ai-bg-1: #071a24;
    --ai-bg-2: #0f2b3d;
    --ai-glass: rgba(255, 255, 255, 0.08);
    --ai-border: rgba(132, 209, 255, 0.30);
    --ai-accent: #62d7ff;
    --ai-accent-2: #5af6bf;
    --ai-text: #eef8ff;
    --ai-subtext: #c7deeb;
}

.ece-header {
    position: relative;
    overflow: hidden;
    margin-bottom: 1.75rem;
    padding: 2.1rem 1.25rem;
    border-radius: 22px;
    border: 1px solid var(--ai-border);
    background:
        radial-gradient(circle at 8% 15%, rgba(90, 246, 191, 0.28), transparent 36%),
        radial-gradient(circle at 92% 10%, rgba(98, 215, 255, 0.28), transparent 34%),
        linear-gradient(140deg, var(--ai-bg-1) 0%, var(--ai-bg-2) 45%, #14374f 100%);
    box-shadow: 0 20px 50px rgba(4, 14, 20, 0.35);
    animation: ece-fade-in 650ms ease-out both;
}

.ece-header::before,
.ece-header::after {
    content: "";
    position: absolute;
    pointer-events: none;
}

.ece-header::before {
    inset: auto -16% -64% auto;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(90, 246, 191, 0.20), transparent 68%);
}

.ece-header::after {
    inset: -22% auto auto -12%;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(98, 215, 255, 0.18), transparent 70%);
}

.ece-shell {
    position: relative;
    z-index: 1;
    max-width: 1020px;
    margin: 0 auto;
    text-align: center;
}

.ece-title {
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.3rem, 7vw, 4.1rem);
    letter-spacing: -0.03em;
    line-height: 1.02;
    font-weight: 700;
    color: var(--ai-text);
    text-shadow: 0 2px 24px rgba(98, 215, 255, 0.18);
}

.ece-subtitle {
    margin: 0.7rem 0 0;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.28rem);
    font-weight: 700;
    color: var(--ai-subtext);
}

.ece-description {
    margin: 1.1rem auto 0;
    max-width: 830px;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(0.93rem, 1.6vw, 1.04rem);
    line-height: 1.62;
    color: #dff0fa;
}

.ece-icons {
    margin-top: 1.5rem;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.8rem;
}

.ece-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.46rem;
    border-radius: 999px;
    padding: 0.5rem 0.9rem;
    border: 1px solid rgba(194, 238, 255, 0.38);
    background: rgba(8, 22, 30, 0.52);
    color: #edfbff;
    font-family: 'Manrope', sans-serif;
    font-size: 0.93rem;
    font-weight: 700;
}

.ece-chip-emoji {
    font-size: 1.05rem;
    line-height: 1;
}

.ece-metrics {
    margin-top: 1.4rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.7rem;
}

.ece-metric {
    border-radius: 12px;
    border: 1px solid rgba(172, 231, 255, 0.30);
    background: var(--ai-glass);
    backdrop-filter: blur(7px);
    padding: 0.76rem 0.68rem;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(0.84rem, 1.5vw, 1.02rem);
    font-weight: 800;
    letter-spacing: 0.01em;
    color: #f6fdff;
}

.ece-metric-down {
    color: #b7e9ff;
}

.ece-metric-up {
    color: #9ef8d1;
}

@keyframes ece-fade-in {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
}

@media (max-width: 860px) {
    .ece-metrics {
        grid-template-columns: 1fr;
    }
}
</style>
"""


def _render_header_markup(metrics_banner_html: str) -> None:
    st.markdown(
        f"""
        {_HEADER_CSS}
        <section class="ece-header">
            <div class="ece-shell">
                <h1 class="ece-title">ECEGraphAI</h1>
                <p class="ece-subtitle">A Token-Efficient GraphRAG Learning Assistant</p>
                <p class="ece-description">
                    Comparing LLM-Only, Basic RAG, and GraphRAG pipelines for faster, cheaper, and more accurate AI retrieval.
                </p>

                <div class="ece-icons">
                    <span class="ece-chip"><span class="ece-chip-emoji">🧠</span> LLM</span>
                    <span class="ece-chip"><span class="ece-chip-emoji">📚</span> RAG</span>
                    <span class="ece-chip"><span class="ece-chip-emoji">🕸️</span> GraphRAG</span>
                </div>

                <div class="ece-metrics">
                    {metrics_banner_html}
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the professional static dashboard header."""
    _render_header_markup(
        """
        <div class="ece-metric ece-metric-down">↓ 47% Token Reduction</div>
        <div class="ece-metric ece-metric-down">↓ Lower Cost</div>
        <div class="ece-metric ece-metric-up">↑ Better Accuracy</div>
        """
    )


def render_header_with_stats(
    token_reduction: float | None = None,
    cost_reduction: float | None = None,
    accuracy_maintained: bool | None = None,
) -> None:
    """Render the same header while allowing run-specific metric text."""
    token_text = f"↓ {token_reduction:.0f}% Token Reduction" if token_reduction is not None else "↓ 47% Token Reduction"

    if cost_reduction is not None:
        cost_text = f"↓ {cost_reduction:.0f}% Lower Cost"
    else:
        cost_text = "↓ Lower Cost"

    if accuracy_maintained is True:
        accuracy_text = "↑ Better Accuracy"
    elif accuracy_maintained is False:
        accuracy_text = "→ Accuracy in Check"
    else:
        accuracy_text = "↑ Better Accuracy"

    _render_header_markup(
        f"""
        <div class="ece-metric ece-metric-down">{token_text}</div>
        <div class="ece-metric ece-metric-down">{cost_text}</div>
        <div class="ece-metric ece-metric-up">{accuracy_text}</div>
        """
    )
