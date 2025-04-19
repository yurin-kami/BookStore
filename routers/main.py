from fastapi import FastAPI
import book_router,user_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(book_router.router)
app.include_router(user_router.router)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app="main:app",host="0.0.0.0",port=8082,reload=True)