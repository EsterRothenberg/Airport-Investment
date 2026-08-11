import streamlit as st
import tempfile
from pathlib import Path

from agent.agent import AirportInvestmentAgent
from utils.voice import VoiceProcessor


st.set_page_config(
    page_title="Airport Investment Intelligence",
    page_icon="✈️",
    layout="wide",
)


st.title("Airport Investment Intelligence Agent")

st.caption(
    "AI-assisted screening of U.S. airport modernization "
    "and terminal expansion opportunities."
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "agent" not in st.session_state:
    st.session_state.agent = AirportInvestmentAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_processor" not in st.session_state:
    try:
        st.session_state.voice_processor = VoiceProcessor()
    except ValueError:
        st.session_state.voice_processor = None

if "enable_voice_output" not in st.session_state:
    st.session_state.enable_voice_output = False


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("Analysis Scope")

    st.write("**Analysis year:** 2025")
    st.write("**Growth baseline:** 2024")

    st.divider()

    st.write("**Data sources**")
    st.write("- U.S. DOT / BTS T-100")
    st.write("- BTS On-Time Performance")
    st.write("- OurAirports metadata")

    st.divider()

    st.write("**Expansion Opportunity Score**")
    st.write(
        "A deterministic screening score based on:"
    )

    st.write(
        """
        - Demand Growth
        - Capacity Pressure
        - Operational Pressure
        - Network Value
        - Market Scale
        """
    )

    st.caption(
        "The score is directional and does not estimate financial ROI."
    )

    st.divider()

    st.write("**🎤 Voice Features**")
    
    voice_enabled = st.session_state.voice_processor is not None
    
    if voice_enabled:
        st.session_state.enable_voice_output = st.checkbox(
            "🔊 Play agent responses aloud",
            value=st.session_state.enable_voice_output,
        )
        
        voice_choice = st.radio(
            "Voice:",
            ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            index=0,
        )
        st.session_state.voice_choice = voice_choice
    else:
        st.warning("⚠️ Voice features unavailable. Check OPENAI_API_KEY.")

    st.divider()

    if st.button("Start new conversation"):
        st.session_state.agent.reset()
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# Welcome message
# --------------------------------------------------

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            """
            Ask me about U.S. airport investment opportunities.

            Examples:

            - Which airports in California look strongest for terminal expansion?
            - Compare LAX and SNA.
            - What percentage of flights from Anchorage are long-haul?
            - Analyze SFO for expansion opportunity.
            """
        )


# --------------------------------------------------
# Existing conversation
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


# --------------------------------------------------
# User input - Text or Voice
# --------------------------------------------------

col1, col2 = st.columns([0.9, 0.1])

with col1:
    user_message = st.chat_input(
        "Ask about a U.S. airport or region..."
    )

with col2:
    voice_input_available = st.session_state.voice_processor is not None
    
    if voice_input_available:
        use_voice = st.checkbox("🎤", value=False, help="Record voice input")
    else:
        use_voice = False

if use_voice and voice_input_available:
    audio_data = st.audio_input("Record your question:")
    
    if audio_data is not None:
        try:
            with st.spinner("Transcribing audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_data.getbuffer())
                    tmp_path = tmp.name
                
                user_message = st.session_state.voice_processor.transcribe_audio(tmp_path)
                Path(tmp_path).unlink()
                
                st.success(f"Transcribed: {user_message}")
        except Exception as exc:
            st.error(f"Transcription error: {exc}")
            user_message = None

if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    # ----------------------------------------------
    # Agent response
    # ----------------------------------------------

    with st.chat_message("assistant"):
        with st.spinner(
            "Analyzing airport data..."
        ):
            try:
                response = (
                    st.session_state.agent.chat(
                        user_message
                    )
                )

                st.markdown(response)
                
                if st.session_state.enable_voice_output and st.session_state.voice_processor:
                    try:
                        with st.spinner("Generating voice response..."):
                            voice_choice = getattr(st.session_state, "voice_choice", "alloy")
                            audio_bytes = st.session_state.voice_processor.text_to_speech_bytes(
                                response,
                                voice=voice_choice,
                            )
                            st.audio(audio_bytes, format="audio/mp3")
                    except Exception as exc:
                        st.warning(f"Could not generate voice: {exc}")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

            except Exception as exc:
                error_message = (
                    "I couldn't complete the analysis. "
                    f"Details: {exc}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
