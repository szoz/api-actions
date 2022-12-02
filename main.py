from fastapi import FastAPI
from uvicorn import run

app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Only endpoint with simple JSON response."""
    return {"status": "OK"}

if __name__ == "__main__":
    run("main:app", host='0.0.0.0', port=5000, log_level="info")
