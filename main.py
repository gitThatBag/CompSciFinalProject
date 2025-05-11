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
    question_id: int

@app.get("/", response_class=HTMLResponse)
async def get_game():
    # Simply get the first question
    response = supabase.table("questions").select("*").order("id").limit(1).execute()
    
    if not response.data:
        return HTMLResponse(content="No questions available.")
    
    current_question = response.data[0]

    # Read your HTML template
    with open("templates/game_template.html", "r") as file:
        template = file.read()

    # Replace the placeholders
    question_html = template.replace("{{option_a}}", current_question["option_a"])
    question_html = question_html.replace("{{option_b}}", current_question["option_b"])
    question_html = question_html.replace("{{question_id}}", str(current_question["id"]))

    return HTMLResponse(content=question_html)

@app.get("/question/{question_id}", response_class=HTMLResponse)
async def get_question_page(question_id: int):
    # Fetch the requested question
    response = supabase.table("questions").select("*").eq("id", question_id).execute()
    
    if not response.data:
        return HTMLResponse(content="Question not found.", status_code=404)
    
    current_question = response.data[0]
    
    # Read your HTML template
    with open("templates/game_template.html", "r") as file:
        template = file.read()

    # Replace the placeholders
    question_html = template.replace("%%option_a%%", current_question["option_a"])
    question_html = question_html.replace("%%option_b%%", current_question["option_b"])
    question_html = question_html.replace("%%question_id%%", str(current_question["id"]))

    return HTMLResponse(content=question_html)

@app.post("/submit")
async def submit_answer(choice: ChoiceModel):
    # Get the question to update
    response = supabase.table("questions").select("*").eq("id", choice.question_id).execute()
    
    if not response.data:
        return JSONResponse(content={"error": "Question not found"}, status_code=404)
    
    question = response.data[0]
    
    # Update the count
    if choice.choice == question["option_a"]:
        current_value = question.get("option_a_results", 0) or 0
        supabase.table("questions").update(
            {"option_a_results": current_value + 1}
        ).eq("id", question["id"]).execute()
    elif choice.choice == question["option_b"]:
        current_value = question.get("option_b_results", 0) or 0
        supabase.table("questions").update(
            {"option_b_results": current_value + 1}
        ).eq("id", question["id"]).execute()
    else:
        return JSONResponse(content={"error": "Invalid choice"}, status_code=400)
    
    # Get the next question ID
    next_response = supabase.table("questions").select("id").gt("id", choice.question_id).order("id").limit(1).execute()
    
    if not next_response.data:
        return JSONResponse(content={"next_id": None, "completed": True}, status_code=200)
    
    return JSONResponse(content={"next_id": next_response.data[0]["id"]}, status_code=200)

@app.get("/results", response_class=HTMLResponse)
async def get_results():
    response = supabase.table("questions").select("*").order("id").execute()
    questions = response.data

    html = """
    <html>
    <head>
        <title>Results</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 2rem; }
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