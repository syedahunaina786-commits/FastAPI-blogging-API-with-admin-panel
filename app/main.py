from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes import auth_routes, blog_routes, category_routes, admin_routes
from app.database import blogs_collection, categories_collection

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Blogging API with Admin Panel",
    description="RESTful Blogging API with Categories, Search, JWT Auth, and Jinja2 Admin Dashboard",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(auth_routes.router)
app.include_router(category_routes.router)
app.include_router(blog_routes.router)
app.include_router(admin_routes.router)


@app.get("/", response_class=HTMLResponse, tags=["Public Blog"])
async def public_home(request: Request, q: str = "", category: str = "", tag: str = ""):
    query = {"published": True}
    if q:
        query["title"] = {"$regex": q, "$options": "i"}
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
    if tag:
        query["tags"] = {"$regex": f"^{tag}$", "$options": "i"}

    blogs = []
    async for b in blogs_collection.find(query).sort("created_at", -1):
        b["id"] = str(b["_id"])
        blogs.append(b)

    categories = []
    async for c in categories_collection.find():
        categories.append(c["name"])
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "blogs": blogs,
            "categories": categories,
            "q": q,
            "selected_category": category,
            "selected_tag": tag
        }
    )
