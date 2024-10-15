from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:5173"]
app = FastAPI(separate_input_output_schemas=False, root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(routers.documentation_router)
