from fastapi import FastAPI

app = FastAPI()

items_db = {
    "123": {"item_id": "123", "name": "Sample Item", "quantity": 100}
}

@app.get("/items/{item_id}")
def get_item(item_id: str):
    item = items_db.get(item_id)
    if item:
        return {"status": "success", "data": item}
    return {"status": "error", "message": "Item not found"}
