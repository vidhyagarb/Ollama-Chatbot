from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
    url = "http://localhost:11434/api/generate"
    payload = json.dumps({
        "model": "llama3.2:latest",
        "prompt": question,
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
        generated_response = response.json()
        final_response = generated_response.get("response")
        return {"response": final_response}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to generate response")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)