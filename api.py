from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent
import time

app = FastAPI(title="AI Trading Research Assistant API")


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    tool_calls: list
    latency_seconds: float


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Trading Research Assistant API is running"}


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    start_time = time.time()

    answer, trace = run_agent(request.question)

    tool_calls_summary = [
        {"tool": t.get("tool"), "args": t.get("raw_args")}
        for t in trace if "tool" in t
    ]

    latency = time.time() - start_time

    return QuestionResponse(
        question=request.question,
        answer=answer,
        tool_calls=tool_calls_summary,
        latency_seconds=round(latency, 2)
    )