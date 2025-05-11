import os
import random
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

# Session storage now tracks answered questions and maintains order
user_sessions = {}  # Format: {session_id: {"question_order": [], "current_index": 0, "answered": []}}

class ChoiceModel(BaseModel):
    choice: str

@app.middleware("http")
async def add_session(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        # Initialize new session with randomized question order
        response = supabase.table("questions").select("id").execute()
        question_ids = [q["id"] for q in response.data]
        random.shuffle(question_ids)
        user_sessions[session_id] = {
            "question_order": question_ids,
            "current_index": 0,
            "answered": []
        }
        request.state.session_id = session_id
        response = await call_next(request)
        response.set_cookie("session_id", session_id)
        return response
    elif session_id not in user_sessions:
        # Initialize if session exists but not in our storage
        response = supabase.table("questions").select("id").execute()
        question_ids = [q["id"] for q in response.data]
        random.shuffle(question_ids)
        user_sessions[session_id] = {
            "question_order": question_ids,
            "current_index": 0,
            "answered": []
        }
    request.state.session_id = session_id
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def get_game(request: Request):
    session_id = request.state.session_id
    session_data = user_sessions.get(session_id)
    
    if not session_data:
        return HTMLResponse(content="Session expired. Please refresh.", status_code=400)

    # Get the current question ID from the ordered list
    if session_data["current_index"] >= len(session_data["question_order"]):
        return HTMLResponse(content="You've completed all questions!", status_code=200)

    current_question_id = session_data["question_order"][session_data["current_index"]]
    
    # Fetch the specific question from Supabase
    response = supabase.table("questions").select("*").eq("id", current_question_id).execute()
    if not response.data:
        return HTMLResponse(content="Question not found.", status_code=404)
    
    current_question = response.data[0]

    # Render the HTML
    with open("templates/main.html", "r") as file:
        template = file.read()

    question_html = template.replace("{{option_a}}", current_question["option_a"])
    question_html = question_html.replace("{{option_b}}", current_question["option_b"])

    return HTMLResponse(content=question_html)

@app.get("/next", response_class=JSONResponse)
async def get_next_question(request: Request):
    session_id = request.state.session_id
    session_data = user_sessions.get(session_id)
    
    if not session_data:
        return JSONResponse(content={"error": "Invalid session"}, status_code=400)

    # Check if we've completed all questions
    if session_data["current_index"] >= len(session_data["question_order"]):
        return {"completed": True, "message": "All questions completed"}

    current_question_id = session_data["question_order"][session_data["current_index"]]
    
    # Fetch the question
    response = supabase.table("questions").select("*").eq("id", current_question_id).execute()
    if not response.data:
        return JSONResponse(content={"error": "Question not found"}, status_code=404)
    
    current_question = response.data[0]
    
    return {
        "a": current_question["option_a"],
        "b": current_question["option_b"],
        "question_id": current_question_id,
        "progress": f"{session_data['current_index'] + 1}/{len(session_data['question_order'])}"
    }

@app.post("/update-result")
async def update_result(choice: ChoiceModel, request: Request):
    session_id = request.state.session_id
    user_choice = choice.choice
    
    if session_id not in user_sessions:
        return JSONResponse(content={"error": "Invalid session"}, status_code=400)
    
    session_data = user_sessions[session_id]
    current_index = session_data["current_index"]
    
    if current_index >= len(session_data["question_order"]):
        return JSONResponse(content={"error": "All questions completed"}, status_code=400)
    
    current_question_id = session_data["question_order"][current_index]
    
    # Fetch the question to validate choices
    response = supabase.table("questions").select("*").eq("id", current_question_id).execute()
    if not response.data:
        return JSONResponse(content={"error": "Question not found"}, status_code=404)
    
    question = response.data[0]
    
    # Update the count
    if user_choice == question["option_a"]:
        current_value = question.get("option_a_results", 0)
        supabase.table("questions").update(
            {"option_a_results": current_value + 1}
        ).eq("id", question["id"]).execute()
    elif user_choice == question["option_b"]:
        current_value = question.get("option_b_results", 0)
        supabase.table("questions").update(
            {"option_b_results": current_value + 1}
        ).eq("id", question["id"]).execute()
    else:
        return JSONResponse(content={"error": "Invalid choice"}, status_code=400)
    
    # Mark question as answered and move to next
    if current_question_id not in session_data["answered"]:
        session_data["answered"].append(current_question_id)
    session_data["current_index"] += 1
    
    return JSONResponse(content={
        "message": "Updated results",
        "progress": f"{session_data['current_index']}/{len(session_data['question_order'])}"
    }, status_code=200)

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
            h1 { color: #333; text-align: center; }
            .question {
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }
            .bar-container {
                display: flex;
                height: 30px;
                margin: 1rem 0;
                border-radius: 5px;
                overflow: hidden;
                background: #eee;
            }
            .a-bar { 
                background: #3498db; 
                color: white; 
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 10px;
                font-weight: bold;
            }
            .b-bar { 
                background: #e74c3c; 
                color: white; 
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 10px;
                font-weight: bold;
            }
            .total { text-align: center; color: #666; margin-top: 1rem; }
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
            <div class="bar-container">
                <div class="a-bar" style="width: {a_percent}%;">{a_percent}%</div>
            </div>
            <p>{a}: {a_count} votes</p>
            <div class="bar-container">
                <div class="b-bar" style="width: {b_percent}%;">{b_percent}%</div>
            </div>
            <p>{b}: {b_count} votes</p>
            <p class="total"><strong>Total votes:</strong> {total}</p>
        </div>
        """

    html += "</body></html>"
    return HTMLResponse(content=html)