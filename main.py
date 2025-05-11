import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from pydantic import BaseModel

app = FastAPI()

# Set up Supabase
url = "https://ebkgvudslketmjxvbdpq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVia2d2dWRzbGtldG1qeHZiZHBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2MjMwNzgsImV4cCI6MjA2MjE5OTA3OH0.Y1MdCLVK0hUCDo1QH8unSPHjji7Y595_irOckdSPgmk"
supabase: Client = create_client(url, key)

class ChoiceModel(BaseModel):
    choice: str

@app.get("/", response_class=HTMLResponse)
async def get_game():
    # Fetch the first question from Supabase
    response = supabase.table("questions").select("*").execute()
    questions = response.data
    
    if not questions:
        return HTMLResponse(content="No questions available.", status_code=404)
    
    # Get the first question
    current_question = questions[0]
    
    # Read the HTML template
    with open("templates/main.html", "r") as file:
        template = file.read()
    
    # Replace placeholders with actual question options
    question_html = template.replace("{{option_a}}", current_question["option_a"])
    question_html = question_html.replace("{{option_b}}", current_question["option_b"])
    
    return HTMLResponse(content=question_html)

@app.get("/next", response_class=JSONResponse)
async def get_next_question(request: Request):
    # Get the current index from the query param (default to 0)
    current_index = int(request.query_params.get("index", 0))
    next_index = current_index + 1
    
    # Fetch all questions
    response = supabase.table("questions").select("*").execute()
    questions = response.data
    
    if next_index < len(questions):
        # Serve the next question
        next_question = questions[next_index]
        return {"a": next_question["option_a"], "b": next_question["option_b"], "index": next_index}
    else:
        return {"a": "", "b": "", "index": next_index}

@app.post("/update-result")
async def update_result(choice: ChoiceModel):
    user_choice = choice.choice
    
    # Find the question that matches the user's choice
    response = supabase.table("questions").select("*").execute()
    questions = response.data
    
    for question in questions:
        if user_choice == question["option_a"]:
            current_value = question.get("option_a_results", 0) or 0
            supabase.table("questions").update(
                {"option_a_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            break
        elif user_choice == question["option_b"]:
            current_value = question.get("option_b_results", 0) or 0
            supabase.table("questions").update(
                {"option_b_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            break
    
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