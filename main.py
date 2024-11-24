from fastapi import FastAPI, HTTPException
import json
import requests
from pydantic import BaseModel
import sqlite3

def init_db():
    conn = sqlite3.connect('llm_responses.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            context TEXT,
            question TEXT,
            answer TEXT,
            rating INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()




app = FastAPI()

""""
post: whenever you want to write something into your database
get: whenever you want to read from database
Delete: whenever you want to delete the information
put:- whenever you want to update the existing information


"""



class Information(BaseModel):
    name: str
    age: int
    email: str

class GetResponse(BaseModel):
    question: str
    context: str

class RatingRequest(BaseModel):
    response: str
    rating: int

@app.post("/save_information")
async def save_information(request_prams:Information):
    return {
        "name": request_prams.name,
        "age": request_prams.age,
        "email": request_prams.email
    }
@app.post("/get_ollama_response")
async def get_response(request_prams: GetResponse):
    question = request_prams.question
    full_context = f"context: {request_prams.context} \n\n Question: {request_prams.question}"
    url = "http://localhost:11434/api/generate"
    payload = json.dumps({
        "model": "llama3.2:1b",
        "prompt": full_context,
        "options": {
            "top_k": 1,
            "top_p": 0.1,
            "temperature": 0.1
        },
        "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        try:
            generated_response = response.json()
            final_response = generated_response.get("response")
            conn = sqlite3.connect('llm_responses.db')
            cursor = conn.cursor()
            cursor.execute("""
                        INSERT INTO responses (context, question, answer)
                        VALUES (?, ?, ?)
                    """, (request_prams.context, request_prams.question, final_response))
            conn.commit()
            conn.close()
            return {"response": final_response}
        except Exception as e:
            print(str(e))
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to generate response")
    
@app.post("/insert_rating")
async def get_response(request_prams: RatingRequest):
    try:
        conn = sqlite3.connect('llm_responses.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE responses
            SET rating = ?
            where answer= ?
        """,(request_prams.rating, request_prams.response)
                        )
        
        conn.commit()
        conn.close()
        return {"data": "rating stored successfully"}

    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)