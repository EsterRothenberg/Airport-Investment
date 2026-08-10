import streamlit as st

from agent.agent import AirportInvestmentAgent


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
# User input
# --------------------------------------------------

user_message = st.chat_input(
    "Ask about a U.S. airport or region..."
)

if user_message:
    # Store + display user message
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
