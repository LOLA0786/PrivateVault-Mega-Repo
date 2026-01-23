from fastapi import FastAPI
from galani.api.v3.enterprise import router

app = FastAPI(title="Galani Protocol v3")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
