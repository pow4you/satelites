from controller import Controller

from fastapi import FastAPI



app = FastAPI()

@app.get("/")
def root():
    return {"hell-0" : "wrld"}