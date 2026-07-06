from src.graph import graph_builder

from fastapi import FastAPI

app = FastAPI(
    title="Phoenix AI"
)

@app.get("/")
def root():
    return {"message": "Phoenix AI"}


@app.get("/build/{prompt}")
def build(prompt: str):
    graph = graph_builder()
    result = graph.invoke({"user_input": prompt})
    return {"result": result}