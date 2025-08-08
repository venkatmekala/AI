import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"

def ask_llm(user_input):
    """
    Send prompt to local Ollama LLM and get structured JSON back.
    """
    prompt = f"""
You are an API caller agent. 
User will give you a natural language request.
You must return ONLY a JSON object with two fields:
- "url": API endpoint to call
- "method": HTTP method ("GET" or "POST")
If method is POST, also include "body" field as a JSON object.

Example:
User: Get details for item 123
Response:
{{"url": "http://localhost:8000/items/123", "method": "GET"}}

User: Get product details for product 123
Response:
{{"url": "http://localhost:8000/items/123", "method": "GET"}}

User: Post shipment for order 456 with carrier DHL
Response:
{{"url": "http://localhost:8000/shipments", "method": "POST", "body": {{"order_id": 456, "carrier": "DHL"}}}}

Now process this request:
{user_input}
"""

    resp = requests.post(
        OLLAMA_API,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )
    data = resp.json()
    text_output = data.get("response", "").strip()

    try:
        return json.loads(text_output)
    except json.JSONDecodeError:
        print("⚠️ Could not parse LLM output as JSON. Raw output:")
        print(text_output)
        return None


def call_api(api_request):
    """
    Calls the API based on LLM's JSON output.
    """
    if not api_request:
        return None

    method = api_request.get("method", "GET").upper()
    url = api_request.get("url")
    body = api_request.get("body", {})

    try:
        if method == "GET":
            r = requests.get(url)
        elif method == "POST":
            r = requests.post(url, json=body)
        else:
            print(f"❌ Unsupported HTTP method: {method}")
            return None

        if r.status_code == 200:
            return r.json()
        else:
            print(f"❌ API call failed with status {r.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return None


if __name__ == "__main__":
    while True:
        user_input = input("\nAsk: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        api_request = ask_llm(user_input)
        if api_request:
            print("\n🤖 LLM decided to call API with:")
            print(json.dumps(api_request, indent=2))

            response = call_api(api_request)
            print("\n📦 API Response:")
            print(json.dumps(response, indent=2))
