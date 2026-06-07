from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db

app = FastAPI(title="DORA Contract Metadata Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "DORA Platform API", "docs": "/docs", "version": "0.1.0"}


from .routers import contracts, providers, services, clauses, dashboard, import_excel, export

app.include_router(providers.router,     prefix="/api/providers",  tags=["providers"])
app.include_router(contracts.router,     prefix="/api/contracts",  tags=["contracts"])
app.include_router(services.router,      prefix="/api/services",   tags=["services"])
app.include_router(clauses.router,       prefix="/api",            tags=["clauses"])
app.include_router(dashboard.router,     prefix="/api/dashboard",  tags=["dashboard"])
app.include_router(import_excel.router,  prefix="/api/import",     tags=["import"])
app.include_router(export.router,        prefix="/api/export",     tags=["export"])
