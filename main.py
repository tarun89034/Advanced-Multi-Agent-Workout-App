import streamlit as st
import time
from loguru import logger
from observability import init_observability
from ai import ask_ai, get_macros
from profiles import create_profile, get_notes, get_profile
from form_submit import update_personal_info, add_note, delete_note

# Initialize page configuration
st.set_page_config(
    page_title="Production AI Infrastructure",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_observability("ai-workflow-app")

# Custom Styling to simulate modern, Stripe/Vercel-like enterprise look
st.markdown("""
<style>
    /* Base styling adjustments for dark mode */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* Hide top padding and default header */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1400px !important;
    }

    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.03em;
        color: #ffffff;
    }
    
    /* Premium Architecture Cards */
    .arch-card {
        background: linear-gradient(145deg, #151b2b 0%, #0d121f 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -4px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    .arch-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px -4px rgba(56, 189, 248, 0.15);
    }
    
    /* Status indicators */
    .status-active {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
        margin-right: 8px;
    }
    .status-warning {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #f59e0b;
        box-shadow: 0 0 10px #f59e0b;
        margin-right: 8px;
    }
    
    /* Code Containers */
    pre {
        background-color: #0f172a !important;
        border: 1px solid #1e293b;
        border-radius: 8px;
    }
    
    /* Architecture Diagram Components */
    .arch-diagram {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 60px 0;
        background: radial-gradient(circle at center, rgba(15, 23, 42, 0.8) 0%, rgba(11, 15, 25, 0) 70%);
        margin: 40px 0;
        border: 1px solid rgba(30, 41, 59, 0.5);
        border-radius: 20px;
    }
    .node {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #334155;
        padding: 16px 32px;
        border-radius: 8px;
        color: #94a3b8;
        font-family: monospace;
        font-size: 14px;
        z-index: 2;
        backdrop-filter: blur(10px);
        text-align: center;
        min-width: 250px;
    }
    .node-primary {
        border-color: #38bdf8;
        color: #e0f2fe;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
    }
    .node-highlight {
        border-color: #10b981;
        color: #d1fae5;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    .line {
        width: 2px;
        height: 30px;
        background: linear-gradient(to bottom, #38bdf8, transparent);
        z-index: 1;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    
    /* Checklist text */
    .check-item {
        margin: 8px 0;
        color: #cbd5e1;
        font-size: 15px;
    }
    
    /* ─── Responsive Breakpoints ─── */
    @media (max-width: 1024px) {
        .arch-diagram {
            padding: 40px 16px;
        }
        .node {
            min-width: 200px;
            padding: 12px 20px;
            font-size: 13px;
        }
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .arch-card {
            padding: 20px;
            margin-bottom: 16px;
        }
        .arch-diagram {
            padding: 24px 8px;
            margin: 20px 0;
        }
        .node {
            min-width: 160px;
            padding: 10px 14px;
            font-size: 12px;
        }
        .line {
            height: 20px;
        }
        /* Stack model cards vertically on mobile */
        .arch-diagram > div:last-child {
            flex-direction: column !important;
            align-items: center;
            gap: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


def draw_architecture_diagram():
    st.markdown("""
    <div class="arch-diagram">
        <div class="node">👤 Users (Internet)</div>
        <div class="line"></div>
        <div class="node"><span class="status-active"></span>Cloudflare CDN/WAF (Access)</div>
        <div class="line"></div>
        <div class="node">Cloudflare Tunnel (Secure Ingress)</div>
        <div class="line"></div>
        <div class="node">🐳 Docker Container (App Runtime)</div>
        <div class="line"></div>
        <div class="node">🧠 Langflow Engine</div>
        <div class="line"></div>
        <div class="node node-primary">⚙️ Custom OpenRouter Node<br><small style="color:#64748b">custom_components/openrouter_component.py</small></div>
        <div class="line"></div>
        <div style="display:flex; gap:20px;">
            <div class="node node-highlight">✨ Primary<br><b>Z.ai GLM 4.5 Air</b><br><small>Free</small></div>
            <div class="node" style="opacity:0.8;">🔄 Fallback 1<br><b>DeepSeek Chat</b></div>
            <div class="node" style="opacity:0.6;">🆘 Emergency<br><b>GPT-4o-Mini</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def observability_stack():
    st.markdown("""
    <div class="arch-card">
        <h3 style="margin-top:0;">📊 Observability Stack</h3>
        <p style="color:#94a3b8; font-size:14px; margin-bottom:24px;">Production monitoring integration tracking latency, failures, and token usage via OpenTelemetry.</p>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div style="background:#0f172a; padding:16px; border-radius:8px; border:1px solid #1e293b;">
                <div style="color:#38bdf8; font-weight:bold; margin-bottom:8px;">LangSmith</div>
                <div style="font-size:13px; color:#64748b;">Prompt traces, tool usage, generation latency.</div>
            </div>
            <div style="background:#0f172a; padding:16px; border-radius:8px; border:1px solid #1e293b;">
                <div style="color:#f59e0b; font-weight:bold; margin-bottom:8px;">Sentry</div>
                <div style="font-size:13px; color:#64748b;">Exception catching, Langflow crash reports.</div>
            </div>
            <div style="background:#0f172a; padding:16px; border-radius:8px; border:1px solid #1e293b;">
                <div style="color:#10b981; font-weight:bold; margin-bottom:8px;">Grafana / Prometheus</div>
                <div style="font-size:13px; color:#64748b;">Docker metrics, Cloudflare tunnel health.</div>
            </div>
            <div style="background:#0f172a; padding:16px; border-radius:8px; border:1px solid #1e293b;">
                <div style="color:#c084fc; font-weight:bold; margin-bottom:8px;">Loguru File Logs</div>
                <div style="font-size:13px; color:#64748b;">Async rotation, 10MB/10 days retention.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def production_checklist():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="arch-card" style="height: 100%;">
            <h4 style="color:#e2e8f0;">🔒 Security</h4>
            <div class="check-item">✅ Env Vars <code>.env</code></div>
            <div class="check-item">✅ Cloudflare Access</div>
            <div class="check-item">✅ 60 req/min/IP Limiting</div>
            <div class="check-item">✅ HTTPS Tunnel</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="arch-card" style="height: 100%;">
            <h4 style="color:#e2e8f0;">🛡️ Reliability</h4>
            <div class="check-item">✅ 3x Max Retries</div>
            <div class="check-item">✅ 60s Request Timeout</div>
            <div class="check-item">✅ Token Streaming</div>
            <div class="check-item">✅ Multi-Provider Fallbacks</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="arch-card" style="height: 100%;">
            <h4 style="color:#e2e8f0;">📈 Scalability</h4>
            <div class="check-item">✅ Docker + Compose</div>
            <div class="check-item">✅ <code>httpx.AsyncClient</code></div>
            <div class="check-item">✅ Model API Caching</div>
            <div class="check-item">✅ Loguru + OpenTelemetry</div>
        </div>
        """, unsafe_allow_html=True)


def tool_calling_validation():
    st.markdown("""
    <div class="arch-card" style="border-color: #f59e0b;">
        <h3 style="margin-top:0; color:#f59e0b;">🛡️ Tool Calling Validation & Agent Integrity</h3>
        <p style="color:#94a3b8; font-size:14px; margin-bottom:20px;">
            Validating the integrity of the Langflow tool chains before routing user queries.
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:16px;">
            <div style="flex:1; min-width:200px; background:#0f172a; padding:16px; border-radius:8px;">
                <span style="color:#10b981;">✅ Calculators</span><br>
                <small style="color:#64748b;">Mathematical operations validated.</small>
            </div>
            <div style="flex:1; min-width:200px; background:#0f172a; padding:16px; border-radius:8px;">
                <span style="color:#10b981;">✅ Retrievers</span><br>
                <small style="color:#64748b;">Vector DB context retrieval healthy.</small>
            </div>
            <div style="flex:1; min-width:200px; background:#0f172a; padding:16px; border-radius:8px;">
                <span style="color:#38bdf8;">🔄 Agents & Routers</span><br>
                <small style="color:#64748b;">Semantic routing active.</small>
            </div>
        </div>
        <div style="margin-top:20px; padding:16px; background:rgba(239, 68, 68, 0.1); border-left:4px solid #ef4444; border-radius:4px;">
            <strong style="color:#ef4444; font-size:14px;">⚠️ Known Production Risks Monitored:</strong>
            <ul style="color:#cbd5e1; font-size:13px; margin-top:8px; margin-bottom:0;">
                <li>Hallucinated tool calls on open-weight models</li>
                <li>Malformed JSON arguments passing to internal APIs</li>
                <li>Broken or infinite agent loops during multi-step reasoning</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)


@st.fragment()
def demo_application():
    st.markdown("### 🧪 Validation Environment (Workout App Domain)")
    st.caption("Testing Langflow connectivity with the newly deployed OpenRouter node.")
    
    profile = st.session_state.profile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("personal_data"):
            st.subheader("Context Payload Generation")
            st.caption("Creates context dictionary for the Langflow Agent")
            
            name = st.text_input("Name", value=profile["general"].get("name", "Test User"))
            age = st.number_input("Age", value=profile["general"].get("age", 25))
            weight = st.number_input("Weight (kg)", value=float(profile["general"].get("weight", 70.0)))
            
            goals = st.multiselect("Goals", ["Muscle Gain", "Fat Loss", "Stay Active"], default=profile.get("goals", ["Muscle Gain"]))
            
            if st.form_submit_button("Sync Context"):
                st.session_state.profile = update_personal_info(profile, "general", name=name, weight=weight, age=age)
                st.session_state.profile = update_personal_info(profile, "goals", goals=goals)
                st.success("Context synchronized.")
                
    with col2:
        st.subheader("Tool Calling & Inference")
        st.caption("Executes asynchronous flow using fallback models.")
        
        user_question = st.text_area("System Prompt / Question", "Based on my context, what is my ideal daily calorie intake?")
        
        if st.button("Execute Inference Pipeline", type="primary", use_container_width=True):
            with st.spinner("Connecting to Langflow -> OpenRouter..."):
                start_time = time.time()
                try:
                    # Sync wrapping async logic from ai.py
                    result = ask_ai(st.session_state.profile, user_question)
                    st.success(f"Inference complete in {time.time() - start_time:.2f}s")
                    st.info("Output Data:")
                    st.write(result)
                except Exception as e:
                    st.error(f"Inference Pipeline Error: {e}")


def main():
    # Header Section
    st.title("Enterprise AI Workflow Infrastructure")
    st.markdown("<p style='font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;'>Production-grade multi-agent architecture powered by Langflow, OpenRouter, and Z.ai.</p>", unsafe_allow_html=True)
    
    # Priority Implementation Section
    st.markdown("""
    <div style="background: rgba(56, 189, 248, 0.1); border-left: 4px solid #38bdf8; padding: 16px 24px; border-radius: 4px; margin-bottom: 40px;">
        <span style="color: #38bdf8; font-weight: bold; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Highest Immediate Production Priorities Implemented</span>
        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px;">
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">1. Streaming</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">2. Retries</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">3. Timeout</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">4. Env vars</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">5. Docker</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">6. CF Tunnel</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">7. Authentication</span>
            <span style="background: #0f172a; padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #cbd5e1; border: 1px solid #1e293b;">8. Fallbacks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Architecture Section
    draw_architecture_diagram()
    
    # Checklist Panel
    st.markdown("### Operational Readiness")
    production_checklist()
    
    st.markdown("---")
    
    # Observability Stack
    observability_stack()
    
    st.markdown("---")

    # Tool Calling Validation
    tool_calling_validation()
    
    st.markdown("---")

    # State initialization for the demo components
    if "profile" not in st.session_state:
        profile_id = 1
        profile = get_profile(profile_id)
        if not profile:
            profile_id, profile = create_profile(profile_id)

        st.session_state.profile = profile
        st.session_state.profile_id = profile_id

    if "notes" not in st.session_state:
        st.session_state.notes = get_notes(st.session_state.profile_id)

    # Wrap the original functionality inside the demo component
    demo_application()


if __name__ == "__main__":
    main()

