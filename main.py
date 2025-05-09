
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client

app = FastAPI()

# Set up Supabase
url = "https://ebkgvudslketmjxvbdpq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVia2d2dWRzbGtldG1qeHZiZHBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY2MjMwNzgsImV4cCI6MjA2MjE5OTA3OH0.Y1MdCLVK0hUCDo1QH8unSPHjji7Y595_irOckdSPgmk"
supabase: Client = create_client(url, key)

# Serve static files if needed
#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_game():
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    if not questions:
        return HTMLResponse(content="No questions found.", status_code=404)

    first = questions[0]
    with open("templates/main.html", "r") as file:
        template = file.read()

    question_html = template.replace("{{option_a}}", first["option_a"])
    question_html = question_html.replace("{{option_b}}", first["option_b"])

    return HTMLResponse(content=question_html)

@app.get("/next", response_class=JSONResponse)
async def get_next_question(index: int = 1):
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    if index < len(questions):
        q = questions[index]
        return {"a": q["option_a"], "b": q["option_b"]}
    return {"a": "", "b": ""}


"""
@app.post("/update-result")
async def update_result(choice: dict):
    user_choice = choice.get("choice")

    # Get all questions
    response = supabase.table("questions").select("*").execute()
    questions = response.data

    for question in questions:
        if user_choice == question["option_a"]:
            current_value = question.get("option_a_results", 0)
            supabase.table("questions").update(
                {"option_a_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            return JSONResponse(content={"message": "Updated option_a_results"}, status_code=200)

        elif user_choice == question["option_b"]:
            current_value = question.get("option_b_results", 0)
            supabase.table("questions").update(
                {"option_b_results": current_value + 1}
            ).eq("id", question["id"]).execute()
            return JSONResponse(content={"message": "Updated option_b_results"}, status_code=200)

    return JSONResponse(content={"message": "Choice not found."}, status_code=404)
"""