"""
Pre-loaded demo queries showcasing GraphRAG efficiency.
These queries are designed to show GraphRAG's token/cost advantages.
"""

DEMO_QUERIES = [
    {
        "query": "Explain how BJT current gain affects amplifier performance",
        "reference": (
            "BJT current gain (β) is the ratio of collector current to base current. "
            "Higher β means more current amplification, which directly affects amplifier gain. "
            "In voltage amplification, the transistor amplifies small input signals at the base "
            "into larger output signals at the collector. A higher current gain allows for higher "
            "voltage gain (Av = gmRC where gm is transconductance). This is essential for small-signal "
            "amplification in audio and RF circuits."
        ),
        "category": "BJT & Amplifiers",
        "expected_advantage": "GraphRAG focuses on BJT → Beta → Current Gain relationships, reducing retrieved context"
    },
    {
        "query": "What is the role of decoupling capacitors in electronic circuits?",
        "reference": (
            "Decoupling capacitors filter out AC noise from power supply lines, ensuring stable DC bias. "
            "They bypass high-frequency noise to ground while maintaining DC levels. "
            "In amplifiers, decoupling capacitors prevent interaction between stages by blocking DC "
            "while passing AC signals. They work at the power pin (Vcc) to maintain constant voltage supply. "
            "Typical values are 0.1μF for high-frequency bypass and 10-100μF for bulk decoupling."
        ),
        "category": "Circuit Components",
        "expected_advantage": "Graph retrieval finds decoupling capacitor relationships quickly"
    },
    {
        "query": "Describe the relationship between transistor biasing and amplifier stability",
        "reference": (
            "Proper biasing sets the Q-point (quiescent operating point) in the linear region. "
            "Stable biasing uses voltage divider networks to make Q-point less temperature-dependent. "
            "Temperature changes affect Vbe (base-emitter voltage) and β (current gain), "
            "causing Q-point drift. Proper biasing compensates for these effects through emitter resistors "
            "and collector feedback. Stability requires: independent Q-point from β variation, "
            "temperature-stable bias currents, and proper bypass capacitor placement."
        ),
        "category": "Biasing & Stability",
        "expected_advantage": "Graph knows transistor biasing ↔ stability relationship intuitively"
    },
]

# Reference answer for fallback (simple LLM-only baseline)
SIMPLE_LLM_BASELINE = (
    "A BJT (Bipolar Junction Transistor) is a three-terminal semiconductor device used for amplification. "
    "It has a base, collector, and emitter. Current flowing into the base controls a larger current "
    "flowing from collector to emitter. This is used in amplifier circuits."
)

# Sidebar configuration
SIDEBAR_CONFIG = {
    "top_k": {"min": 1, "max": 20, "default": 5, "help": "Number of top chunks to retrieve"},
    "hops": {"min": 1, "max": 3, "default": 1, "help": "Graph traversal depth (1=direct, 2=1-hop, 3=2-hops)"},
    "cost_per_1k_input": {"min": 0.0, "max": 0.01, "default": 0.0005, "help": "Input token cost per 1K tokens"},
    "cost_per_1k_output": {"min": 0.0, "max": 0.01, "default": 0.0015, "help": "Output token cost per 1K tokens"},
}

# Metric thresholds for highlighting
METRIC_THRESHOLDS = {
    "token_reduction_percent": 25,  # Flag if GraphRAG saves >25% tokens
    "latency_reduction_percent": 20,  # Flag if GraphRAG is >20% faster
    "cost_reduction_percent": 25,  # Flag if GraphRAG saves >25% cost
}

# Success criteria for judges
SUCCESS_CRITERIA = {
    "token_efficiency": "GraphRAG uses ≤75% tokens of Basic RAG",
    "quality_maintained": "GraphRAG BERTScore ≥ 0.85",
    "performance": "GraphRAG latency < 2.5 seconds",
    "cost_savings": "GraphRAG cost ≤ 75% of Basic RAG",
}
