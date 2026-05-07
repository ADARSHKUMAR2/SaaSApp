from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os

app = FastAPI()

@app.get("/api")
def idea():
    # 1. Properly configured for GitHub Models
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ.get("GITHUB_TOKEN"),
    )
    
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]
    # 2. Using the correct, valid model
    stream = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=prompt, 
        stream=True
    )

    def event_stream():
        for chunk in stream:
            # SAFETY CHECK: Only proceed if 'choices' is not empty
            if len(chunk.choices) > 0:
                text = chunk.choices[0].delta.content
                
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        yield f"data: {line}\n"
                    yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")