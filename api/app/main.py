from fastapi import FastAPI
from app import schemas
from app.dependencies.database import engine
from app import routers


app = FastAPI()
app.include_router(routers.auth.router)
app.include_router(routers.todo.router)



# Add CORS middleware when using a frontend



schemas.Base.metadata.create_all(bind=engine)


@app.get('/')
async def root():
    return {"message" : "Hello Wobot! Go to localhost:8000/docs"}