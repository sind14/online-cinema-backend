from fastapi import FastAPI

app = FastAPI(title="Online Cinema")

@app.get("/")
async def root():
    return {"message": "Hello, Online Cinema!"}
