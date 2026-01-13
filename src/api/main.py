from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import *
from api.auth import create_access_token, verify_token, authenticate_user

app = FastAPI(title="Banking AI Agent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/login", response_model=TokenResponse)
async def login(auth: AuthRequest):
    if not authenticate_user(auth.username, auth.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": auth.username})
    return TokenResponse(access_token=access_token)


@app.post("/agent/query", response_model=AgentResponse)
async def query_agent(request: QueryRequest, username: str = Depends(verify_token)):
    """
    Query the banking agent with authentication
    """
    # Here you would integrate with your ADK agent
    # For now, return a mock response

    return AgentResponse(
        status="success",
        response=f"Processed query: {request.query}",
        data={"customer_id": request.customer_id},
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
