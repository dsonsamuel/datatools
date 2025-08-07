import streamlit as st
from agents import Agent, Runner
from pathlib import Path
from langchain.llms.openai import OpenAI
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from streamlit_navigation_bar import st_navbar
import sqlite3
import base64
from PIL import Image
from io import BytesIO
from lida import Manager, TextGenerationConfig, llm


st.set_page_config(page_title="New Generation Digital Banking", page_icon="🦜")
st.title("New Generation Digital Banking")

#pages = ["Home", "Library", "Tutorials", "Development", "Download"]
#styles = {
 #   "nav": {
  #      "background-color": "rgb(123, 209, 146)",
  #  },
  #  "div": {
  #      "max-width": "32rem",
  #  },
  #  "span": {
  #      "border-radius": "0.5rem",
  #      "color": "rgb(49, 51, 63)",
  #      "margin": "0 0.125rem",
  #      "padding": "0.4375rem 0.625rem",
  #  },
  #  "active": {
  #      "background-color": "rgba(255, 255, 255, 0.25)",
  #  },
  #  "hover": {
   #     "background-color": "rgba(255, 255, 255, 0.35)",
   # },
#}

#page = st_navbar(pages, styles=styles)
#st.write(page)

INJECTION_WARNING = """
                    SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.
                    Read more [here](https://python.langchain.com/docs/security).
                    """
LOCALDB = "USE_LOCALDB"

# User inputs


# Check user inputs
# if not db_uri:
db_uri='mysql://admin_360data:(NNeRMx^&#LW@72.167.69.35/360data'   
   # st.info("Please enter database URI to connect to your database.")
   # st.stop()

#if not openai_api_key:
   # st.info("Please add your OpenAI API key to continue.")
   # st.stop()

# Setup agent
llm = OpenAI(openai_api_key=openai_api_key, temperature=0, streaming=True)


@st.cache_resource(ttl="2h")
def configure_db(db_uri):
    if db_uri == LOCALDB:
        # Make the DB connection read-only to reduce risk of injection attacks
        # See: https://python.langchain.com/docs/security
        db_filepath = (Path(__file__).parent / "Chinook.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    return SQLDatabase.from_uri(database_uri=db_uri)


db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

#if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
 #   st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

#for msg in st.session_state.messages:
#    st.chat_message(msg["role"]).write(msg["content"])

def base64_to_image(base64_string):
            byte_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(byte_data))

user_query = st.text_input("Ask me anything!")

if user_query:
    #st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = agent.invoke(user_query, callbacks=[st_cb])
     #   st.session_state.messages.append({"role": "assistant", "content": response})
      #  response =  Runner.run(agent,user_query)
        st.write(response["output"])
       
        from lida import Manager, llm
        lida = Manager(text_gen=llm("openai"))  # or "palm", "cohere", etc.

        #lida = Manager(text_gen=llm)
        textgen_config = TextGenerationConfig(n=1, temperature=0.2, model="gpt-4o-mini", use_cache=True)


        try:
            summary = lida.summarize('sales_data.csv', summary_method="default", textgen_config=textgen_config)
        except Exception as e:
            st.error(f"Data summarization failed: {e}")
            summary = None
        
        if summary:
            charts = lida.visualize(summary=summary, goal=user_query, textgen_config=textgen_config)
            for chart in charts:
                #image = base64_to_image(chart.raster)
                st.image(base64_to_image(chart.raster))


