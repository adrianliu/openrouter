from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

conversations: dict[str, list[dict]] = {}


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body["message"]
    session_id = "default"

    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    conversations[session_id].append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=conversations[session_id],
    )

    reply = response.choices[0].message.content
    conversations[session_id].append({"role": "assistant", "content": reply})

    return {"reply": reply}
