from fastapi import FastAPI
from stock_research import main_foo

app = FastAPI()

@app.get("/api/getinvestinfo", tags=["investinfo"])
async def get_invest_info():
    """
    Returns a dummy JSON response if the token is valid.
    """
    rec = main_foo()
    
    return rec

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

# to run: uvicorn app:app --reload
