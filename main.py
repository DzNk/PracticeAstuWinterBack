from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import routers

origins = ["http://localhost:5173"]
app = FastAPI(
    separate_input_output_schemas=False,
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.user_router)
app.include_router(routers.products_router)

