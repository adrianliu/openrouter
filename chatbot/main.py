from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

conversations: dict[str, list[dict]] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Chatbot</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #1a1a2e; color: #eee; display: flex; justify-content: center; align-items: center; height: 100vh; }
    #chat-container { width: 600px; max-height: 90vh; display: flex; flex-direction: column; background: #16213e; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
    #messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
    .msg { padding: 10px 14px; border-radius: 10px; max-width: 80%; line-height: 1.5; white-space: pre-wrap; }
    .user { background: #0f3460; align-self: flex-end; }
    .assistant { background: #533483; align-self: flex-start; }
    #input-area { display: flex; padding: 12px; gap: 8px; border-top: 1px solid #333; }
    #input-area input { flex: 1; padding: 10px; border-radius: 8px; border: none; background: #0f3460; color: #eee; font-size: 14px; outline: none; }
    #input-area button { padding: 10px 20px; border-radius: 8px; border: none; background: #e94560; color: #fff; cursor: pointer; font-size: 14px; }
    #input-area button:hover { background: #c73e54; }
  </style>
</head>
<body>
  <div id="chat-container">
    <div id="messages"></div>
    <div id="input-area">
      <input id="input" type="text" placeholder="Type a message..." autofocus />
      <button onclick="send()">Send</button>
    </div>
  </div>
  <script>
    const messages = document.getElementById('messages');
    const input = document.getElementById('input');
    input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

    async function send() {
      const text = input.value.trim();
      if (!text) return;
      addMsg('user', text);
      input.value = '';
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      addMsg('assistant', data.reply);
    }

    function addMsg(role, content) {
      const div = document.createElement('div');
      div.className = 'msg ' + role;
      div.textContent = content;
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }
  </script>
</body>
</html>
"""


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
