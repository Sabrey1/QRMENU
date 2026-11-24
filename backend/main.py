from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from app.dependencies import Db
from app.config import settings
from app.api.v1.router import router as v1_router
from app.api.v1.routers import public
from app.services import public as public_service
from app.rate_limit import RateLimitMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="QR Menu API")
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://emenu.sabrey.xyz", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router, prefix="/v1")
    # Keep existing clients working while they migrate to the versioned URLs.
    app.include_router(v1_router, include_in_schema=False)
    serve_frontend = settings.serve_frontend
    frontend_dist = settings.frontend_dist_dir
    if serve_frontend:
        if not (frontend_dist / "index.html").is_file() or not (frontend_dist / "assets").is_dir():
            raise RuntimeError("Frontend build missing; build frontend before enabling SERVE_FRONTEND")
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="frontend-assets")

    @app.get("/healthz", include_in_schema=False)
    def health():
        return {"status": "ok"}

    @app.get("/")
    def home(request: Request, db: Db):
        if serve_frontend:
            return FileResponse(frontend_dist / "index.html")
        slug = public.slug_from_request(request)
        if slug:
            return public_service.get_menu(db, slug)
        return {"message": "QR Menu API is running"}

    return app


app = create_app()
