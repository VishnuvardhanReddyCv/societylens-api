from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, expenses, issues, announcements, admin, tenants, contractors, payments

app = FastAPI(
    title="SocietyLens API",
    description="Multi-tenant apartment maintenance management platform for Indian apartment communities.",
    version="1.0.0",
)

origins = list({
    "http://localhost:3000",
    settings.FRONTEND_URL,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(issues.router)
app.include_router(announcements.router)
app.include_router(admin.router)
app.include_router(tenants.router)
app.include_router(contractors.router)
app.include_router(payments.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "service": "societylens-api"}
