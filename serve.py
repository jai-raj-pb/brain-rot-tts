from fastapi import FastAPI, Request
from pydantic import BaseModel
from pyngrok import ngrok

app = FastAPI()

class Item(BaseModel):
    objectId: str

@app.post("/get-response")
async def get_response(item: Item):
    # For demonstration, we just append "_response" to the objectId
    responseObjectId = f"{item.objectId}_response"
    return {"responseObjectId": responseObjectId}

if __name__ == "__main__":
    # Open a ngrok tunnel to the server
    public_url = ngrok.connect(8000)
    print(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:8000\"")

    # Start the server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)