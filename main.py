import os
import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig, function_tool
import asyncio
import requests

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the agent with the provided configuration
external_client = AsyncOpenAI(
    api_key= api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Create an instance of the OpenAIChatCompletionsModel with the external client
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", 
    openai_client=external_client
)

# Create a RunConfig instance with the model and external client
config = RunConfig(
    model=model,
    tracing_disabled=True
    )

# Get the instance ID and token from environment variables
instance_id = os.getenv("INSTANCE_ID")
token = os.getenv("API_TOKEN")

@function_tool
def send_whatsapp_message(number: str, message: str) -> str:
    try:
        url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
        payload = {
            "token": token,
            "to": number,
            "body": message
        }
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            return "✅ Recipe sent successfully via WhatsApp!"
        else:
            return f"❌ Failed to send WhatsApp message: {res.text}"
    except Exception as e:
        return f"❌ Exception: {e}"
    
@function_tool
def generate_recipe(dish_name: str) -> str:
    """
    Chef Baba uses his magic to generate a delicious recipe for the given dish name
    """
    return (
        f"Generate a simple and delicious recipe for the dish: {dish_name}. "
        f"The recipe should include a list of ingredients and step-by-step instructions. "
        f"Make it clear, fun, and beginner-friendly with emoji if needed."
    )

# 🍽️ Chef Agent
agent = Agent(
    name="chef-agent",
    instructions=(
        """
        You are Chef Baba — a cheerful, wise, and slightly dramatic culinary expert who shares mouth-watering recipes with flair and fun! 🍲🎭
        Your job:
        1. Use the 'generate_recipe' tool to create a recipe that includes:
            • A short intro or comment from you as Chef Baba
            • A clear list of ingredients
            • Step-by-step cooking instructions
            • An uplifting closing line like: "Now go, beta! Make Chef Baba proud! 👨‍🍳🔥"

        2. Once the recipe is ready, use the 'send_whatsapp_message' tool to send it to the given WhatsApp number.

        Tone:
        - Fun, encouraging, and a little over-the-top like a dramatic chef on a cooking show 🎬
        - Clear, human-sounding, and well-structured 🍽️

        Rules:
        - Never ask follow-up questions.
        - Do not respond to anything unrelated to food or recipes.
        - If asked your name, reply: "I am Chef Baba, the master of spices and smiles!" 😄
        """
    ),
    tools=[generate_recipe, send_whatsapp_message],
)

# 🖥️ Streamlit UI
st.set_page_config(page_title="Chef Baba", page_icon="👨‍🍳", layout="centered")
st.markdown(
    """
    <div style="text-align:center">
        <h1 style="color:#E91E63;">👨‍🍳 Welcome to Chef Baba's Kitchen!</h1>
        <p style="font-size:18px;color:#FFCDD2;">
        <i>"A pinch of drama, a spoon of wisdom, and a whole lot of flavor!"</i><br>
        Let Chef Baba cook up your favorite dish & send it to your WhatsApp, hot and ready! 🔥
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("recipe_form"):
    st.markdown(
        "<h4 style='color:#E91E63;'>📜 Your Wish, Baba's Dish!</h4>",
        unsafe_allow_html=True,
    )

    dish_name = st.text_input(
        "🍛 What dish do you crave, beta?", placeholder="e.g. Chicken Biryani"
    )

    watsapp_number = st.text_input(
        "📱 Where should the magic go?", placeholder="e.g. +92XXXXXXXXXX"
    )

    submitted = st.form_submit_button("🍽️ Summon Chef Baba")

if submitted:
    if not dish_name.strip() or not watsapp_number.strip():
        st.error(
            "📛 Oh dear! Both fields are required — without a dish name and WhatsApp number, Chef Baba cannot cook up the magic! ✨"
        )
    elif not (
        watsapp_number.startswith("+92")
        and len(watsapp_number) == 13
        and watsapp_number[1:].isdigit()
    ):
        st.error(
            "📵 The number must start with +92 and be exactly 13 digits long — like +92XXXXXXXXXX."
        )
    else:
        input_text = (
            f"Generate a delicious recipe for: {dish_name}. "
            f"Then send it to this WhatsApp number: {watsapp_number}."
        )

        def run_runner_sync_in_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return Runner.run_sync(agent, input=input_text, run_config=config)

        with st.spinner("🧙‍♂️ Chef Baba is summoning the flavors of the universe..."):
            result = run_runner_sync_in_loop()

        st.markdown(
            f"""
            <div style="background-color:#FCE4EC;padding:20px;border-radius:10px;border:5px solid #E91E63">
                <p style="color:#E91E63">
                🧙‍♂️ Ah-ha! The sacred recipe of <b>{dish_name}</b> has flown through the mystical winds of WhatsApp and landed safely at <b>{watsapp_number}</b>! 📱✨<br>
                Go now, and let the flames of your stove honor the legacy of Chef Baba! 👨‍🍳🔥
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.markdown(
    """
    <p style='color:#E91E63; font-size:18px; text-align:center;'>
        🍽️ Handcrafted with flair by <span style='font-size:20px;'> ✨ <b>Chef Baba</b> ✨</span><br>
        Stirring drama into every dish, and love into every bite. ❤️👨‍🍳
    </p>
    """,
    unsafe_allow_html=True,
)
