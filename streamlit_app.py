import streamlit as st

# Custom CSS
st.markdown("""
    <style>
        body {
            background-color: #F4F7FA;
        }
        .main {
            background-color: #FFFFFF;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        }
        h1 {
            color: #6C63FF;
            font-size: 2.5rem;
        }
        h3 {
            color: #1F2937;
        }
        .stTextInput>div>div>input {
            background-color: #ffffff;
            color: #1F2937;
        }
        .stButton>button {
            background-color: #6C63FF;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 0.5rem;
        }
        .stButton>button:hover {
            background-color: #574fd6;
        }
    </style>
""", unsafe_allow_html=True)

# Set page config
st.set_page_config(
    page_title="Auri – Your AI Content Copilot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main UI
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.markdown("<h1>👋 Hey there, I’m Auri</h1>", unsafe_allow_html=True)
st.markdown("<h3>What do you want to achieve today?</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Give me new content ideas"):
        st.session_state['prompt'] = "Generate 5 content ideas for my niche"
with col2:
    custom_prompt = st.text_input("Or type your own request", "")

if "prompt" in st.session_state or custom_prompt:
    user_prompt = st.session_state.get('prompt', custom_prompt)
    st.markdown(f"💡 **Auri’s thinking about:** _{user_prompt}_")

    # Simulated output for now
    st.markdown("""
    <ul>
        <li>🎬 A simple 15s reel showing 'before vs after' transformation</li>
        <li>📈 A hook: 'Most people ignore this tip…'</li>
        <li>🤯 A myth-busting clip: 'You thought this was healthy?'</li>
        <li>🔁 A stitch: 'Respond to this trending sound with your twist'</li>
        <li>🧪 Try-on challenge or 3-part storytelling hook</li>
    </ul>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
