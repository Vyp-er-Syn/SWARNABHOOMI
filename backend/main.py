from fastapi import FastAPI

app = FastAPI(
    title="SWARNABHOOMI API",
    description="Rice Production Intelligence & Demand Coordination Platform"
)

@app.get("/")
def health_check():
    return {
        "status": "SWARNABHOOMI Backend is online",
        "roles_supported": ["Farmer", "Agrarian", "Buyer", "Government"]
    }