from fastapi import FastAPI
from interfaces.http.router.documentation import docPythonrouter
from interfaces.http.router.docker import dockerRouter

app = FastAPI(title="API Documentation", description="API para documentar codigo usando IA")
app.include_router(docPythonrouter)
app.include_router(dockerRouter)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )