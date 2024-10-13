from fastapi import FastAPI, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse# type: ignore
from fastapi.middleware.cors import CORSMiddleware# type: ignore
from .fetch_emails import init as fetch_emails
from .classify_emails import main as classify
from .semantic_search import semantic_search as search_emails
from openai import OpenAI
import json
from pinecone import Pinecone
from pydantic import BaseModel

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

with open("/app/app/config.json") as config:
  config = json.load(config)
client = OpenAI(api_key=config["openai"]["api_key"])
PINECONE_KEY = config["pinecone"]["api_key"]
PINECONE_ENV = config["pinecone"]["environment"]
pc = Pinecone(api_key=PINECONE_KEY)
PINECONE_INDEX = pc.Index(config["pinecone"]["index"])

origins = [
    "http://localhost:3000"
]

# Add CORS middleware to allow communication from React Native frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You may restrict this to your frontend's IP/domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler for unhandled exceptions
@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {str(exc)}"},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to MailPilot API"}

@app.get("/emails/")
def get_emails():
    try:
        emails = fetch_emails()
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@app.post("/classify/")
def classify_emails():
    try:
        results = classify(client)
        return {"classifications": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to classify emails: {str(e)}")

@app.post("/semantic-search")
async def semantic_search(request: SearchRequest):
    try:
        search_results = search_emails(request.query, client, PINECONE_INDEX)
        
        return {"result": search_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search emails: {str(e)}")
