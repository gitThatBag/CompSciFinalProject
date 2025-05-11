
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from pydantic import BaseModel
from uuid import uuid4


app = FastAPI()

# Set up Supabase
url = "https://ebkgvudslketmjxvbdpq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVia2d2dWRzbGtldG1qeHZiZHBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2MjMwNzgsImV4cCI6MjA2MjE5OTA3OH0.Y1MdCLVK0hUCDo1QH8unSPHjji7Y595_irOckdSPgmk"
supabase: Client = create_client(url, key)

# Serve static files if needed
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Temporary in-memory session storage (you may use a database for persistent storage)
user_sessions = {}

class ChoiceModel(BaseModel):
    choice: str

@app.middleware("http")
async def add_session(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())  # Generate a new session if not found
        response = await call_next(request)
        response.set_cookie("session_id", session_id)
        return response
    request.state.session_id = session_id
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def get_game(request: Request):
    # Get the user's session ID
    session_id = request.state.session_id

    # Retrieve the current question index from the session (default to 0 if not found)
    current_index = user_sessions.get(session_id, 0)

    # Fetch the question list from Supabase
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    if current_index >= len(questions):
        return HTMLResponse(content="No more questions.", status_code=404)

    # Get the current question
    current_question = questions[current_index]

    # Render the HTML with the question
    with open("templates/main.html", "r") as file:
        template = file.read()

    question_html = template.replace("{{option_a}}", current_question["option_a"])
    question_html = question_html.replace("{{option_b}}", current_question["option_b"])

    return HTMLResponse(content=question_html)

@app.get("/next", response_class=JSONResponse)
async def get_next_question(request: Request):
    session_id = request.state.session_id
    current_index = user_sessions.get(session_id, 0)

    # Fetch all questions
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    if current_index < len(questions):
        # Serve the current question
        current_question = questions[current_index]
        return {"a": current_question["option_a"], "b": current_question["option_b"]}
    else:
        return {"a": "", "b": ""}

@app.post("/update-result")
async def update_result(choice: ChoiceModel, request: Request):
    session_id = request.state.session_id
    user_choice = choice.choice

    # Fetch all questions
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    for question in questions:
        if user_choice == question["option_a"]:
            current_value = question.get("option_a_results", 0)
            supabase.table("questions").update(
                {"option_a_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            break
        elif user_choice == question["option_b"]:
            current_value = question.get("option_b_results", 0)
            supabase.table("questions").update(
                {"option_b_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            break

    # Update session to move to the next question
    user_sessions[session_id] = user_sessions.get(session_id, 0) + 1

    return JSONResponse(content={"message": "Updated results"}, status_code=200)

@app.get("/results", response_class=HTMLResponse)
async def get_results():
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    html = """
    <html>
    <head>
        <title>Results</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 2rem; }
            h2 { color: #333; }
            .question {
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .bar {
                height: 30px;
                margin: 0.5rem 0;
                display: flex;
                border-radius: 5px;
                overflow: hidden;
                background: #ddd;
            }
            .a-bar { background: #3498db; color: white; text-align: right; padding-right: 10px; }
            .b-bar { background: #e74c3c; color: white; text-align: right; padding-right: 10px; }
        </style>
    </head>
    <body>
        <h1>Game Results</h1>
    """

    for q in questions:
        a = q["option_a"]
        b = q["option_b"]
        a_count = q.get("option_a_results", 0) or 0
        b_count = q.get("option_b_results", 0) or 0
        total = a_count + b_count

        a_percent = round((a_count / total) * 100) if total > 0 else 0
        b_percent = 100 - a_percent if total > 0 else 0

        html += f"""
        <div class="question">
            <h2>{a} <span style="color:#666;">vs</span> {b}</h2>
            <div class="bar">
                <div class="a-bar" style="width: {a_percent}%;">{a_percent}%</div>
            </div>
            <p>{a}: {a_count} votes</p>
            <div class="bar">
                <div class="b-bar" style="width: {b_percent}%;">{b_percent}%</div>
            </div>
            <p>{b}: {b_count} votes</p>
            <p><strong>Total votes:</strong> {total}</p>
        </div>
        """

    html += "</body></html>"
    return HTMLResponse(content=html)