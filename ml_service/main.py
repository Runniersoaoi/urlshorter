from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="URL Safety ML Service")

class URLRequest(BaseModel):
    url: str

# Simple heuristic model for demonstration
# In a real scenario, we would load a trained model using joblib
def is_suspicious(url: str) -> bool:
    suspicious_patterns = [
        r"bit\.ly", # Example of potentially abused shorteners (though we are one)
        r"free-gift",
        r"login.*update",
        r"verify.*account",
        r"paypal.*support",
        r"apple.*id",
        r"google.*docs"
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
            
    if len(url) > 100: # Excessively long URLs
        return True
        
    return False

@app.post("/predict")
async def predict(request: URLRequest):
    suspicious = is_suspicious(request.url)
    return {"safe": not suspicious, "score": 0.0 if suspicious else 1.0}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
