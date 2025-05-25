import os
import streamlit as st
import base64
from PIL import Image
from io import BytesIO

from lida import Manager, TextGenerationConfig, llm
import openai
import streamlit_authenticator as stauth


if not st.experimental_user.is_logged_in:
    if st.button("Log in"):
        st.login()
else:
    if st.button("Log out"):
        st.logout()
    st.write(f"Hello, {st.experimental_user.name}!")

# Configure OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("API key is not configured. Please set the OPENAI_API_KEY environment variable.")

# Convert base64 string to image
def base64_to_image(base64_string):
    byte_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(byte_data))

# Streamlit App setup
st.set_page_config(
    page_title="Automatic Insights and Visualization App",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.header("Automatic Insights and Visualization 🤖")

csv_path = "sales_data.csv"
if not os.path.exists(csv_path):
    st.error("The specified file 'sales_data.csv' does not exist. Please upload a valid CSV file.")
else:
    lida = Manager(text_gen=llm("openai"))
    textgen_config = TextGenerationConfig(n=1, temperature=0.2, model="gpt-4o-mini", use_cache=True)

    try:
        summary = lida.summarize(csv_path, summary_method="default", textgen_config=textgen_config)
    except Exception as e:
        st.error(f"Data summarization failed: {e}")
        summary = None

    if summary:
        text_input = st.text_input("Enter some text 👇")
        if text_input:
            user_query = text_input
            try:
                charts = lida.visualize(summary=summary, goal=user_query, textgen_config=textgen_config)
                if charts:
                    tabs = st.tabs([f"Goal {i+1}" for i in range(len(charts))])
                    for i, tab in enumerate(tabs):
                        with tab:
                            st.header(f"Goal {i+1}")
                            st.write(user_query)
                            st.image(base64_to_image(charts[i].raster))
                else:
                    st.warning("No charts were generated for the input query.")
            except Exception as e:
                st.error(f"Visualization generation failed: {e}")
