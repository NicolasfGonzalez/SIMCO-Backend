from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Creamos la instancia exacta que busca Uvicorn
app = FastAPI(
    title="FastAPI Base App",
    version="1.0.0"
)

# Configuración básica de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Healthy", "message": "Plantilla Base Funcionando"}