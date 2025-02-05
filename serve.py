import os
import json
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok

app = FastAPI()

class Item(BaseModel):
    objectId: str
    title: str
    tags: list[str]

class ObjectIdRequest(BaseModel):
    objectId: str

# Load data from output.json
with open('output.json', 'r') as file:
    data = json.load(file)

# Create dictionaries
objectId_to_recommendations = {item['objectId']: item['recommendations'] for item in data}
objectId_to_tags = {item['objectId']: item['tags'] for item in data}
objectId_to_count = {item['objectId']: 0 for item in data}

# Create objectId to title map from JSON files in results directory
results_dir = 'results'
objectId_to_title = {}
for filename in os.listdir(results_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'r') as file:
            result_data = json.load(file)
            objectId = result_data.get("objectId", "")
            title = result_data.get("title", "")
            if objectId and title:
                objectId_to_title[objectId] = title

# Print dictionaries
# print("objectId_to_recommendations:", objectId_to_recommendations)
# print("objectId_to_tags:", objectId_to_tags)
# print("objectId_to_count:", objectId_to_count)
# print("objectId_to_title:", objectId_to_title)

@app.post("/firstObj")
async def first_obj():
    # Reset all counts to 0
    for key in objectId_to_count:
        objectId_to_count[key] = 0

    # Select a random objectId
    random_objectId = random.choice(list(objectId_to_recommendations.keys()))

    # Increase count for the selected objectId
    objectId_to_count[random_objectId] += 1

    # Create the response item
    item = Item(
        objectId=random_objectId,
        title=objectId_to_title.get(random_objectId, "Unknown Title"),
        tags=objectId_to_tags[random_objectId]
    )

    return item

@app.post("/nextObj")
async def next_obj(request: ObjectIdRequest):
    current_objectId = request.objectId
    if current_objectId not in objectId_to_recommendations:
        raise HTTPException(status_code=404, detail="ObjectId not found")

    recommendations = objectId_to_recommendations[current_objectId]

    # Ensure all recommended objectIds are in the count dictionary
    for rec in recommendations:
        if rec not in objectId_to_count:
            objectId_to_count[rec] = 0

    # Find the recommendation with the minimum count
    next_objectId = min(recommendations, key=lambda x: objectId_to_count[x])

    # Increase count for the selected objectId
    objectId_to_count[next_objectId] += 1

    # Create the response item
    next_item = Item(
        objectId=next_objectId,
        title=objectId_to_title.get(next_objectId, "Unknown Title"),
        tags=objectId_to_tags[next_objectId]
    )

    return next_item

if __name__ == "__main__":
    # Open a ngrok tunnel to the server
    public_url = ngrok.connect(8000)
    print(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:8000\"")

    # Start the server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)