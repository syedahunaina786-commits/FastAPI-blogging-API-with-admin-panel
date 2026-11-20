from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import users_collection, blogs_collection, categories_collection
from app.auth import hash_password, verify_password, create_access_token, decode_token

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


async def get_admin_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        return None
    return await users_collection.find_one({"email": payload["sub"]})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@router.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await users_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password"},
            status_code=400
        )

    token = create_access_token({"sub": user["email"], "username": user["username"]})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response


@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    existing = await users_collection.find_one({"email": email})
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Email already registered. Please sign in."},
            status_code=400
        )

    await users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hash_password(password),
        "is_admin": True
    })
    token = create_access_token({"sub": email, "username": username})
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, q: str = "", category: str = ""):
    user = await get_admin_user(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    query = {}
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}}
        ]
    if category:
        query["category"] = category

    blogs = []
    async for b in blogs_collection.find(query).sort("created_at", -1):
        b["id"] = str(b["_id"])
        blogs.append(b)

    categories = []
    async for c in categories_collection.find():
        c["id"] = str(c["_id"])
        categories.append(c)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "blogs": blogs,
            "categories": categories,
            "search_q": q,
            "selected_category": category
        }
    )


@router.post("/blogs/create")
async def admin_create_blog(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),
    content: str = Form(...)
):
    user = await get_admin_user(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    now = datetime.now(timezone.utc)
    await blogs_collection.insert_one({
        "title": title,
        "content": content,
        "category": category,
        "tags": tag_list,
        "author": user.get("username", "Admin"),
        "published": True,
        "created_at": now,
        "updated_at": now
    })
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/blogs/edit/{blog_id}")
async def admin_edit_blog(
    request: Request,
    blog_id: str,
    title: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),
    content: str = Form(...)
):
    user = await get_admin_user(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    if ObjectId.is_valid(blog_id):
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        await blogs_collection.update_one(
            {"_id": ObjectId(blog_id)},
            {"$set": {
                "title": title,
                "category": category,
                "tags": tag_list,
                "content": content,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/blogs/delete/{blog_id}")
async def admin_delete_blog(request: Request, blog_id: str):
    user = await get_admin_user(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    if ObjectId.is_valid(blog_id):
        await blogs_collection.delete_one({"_id": ObjectId(blog_id)})
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/categories/create")
async def admin_create_category(request: Request, name: str = Form(...), description: str = Form("")):
    user = await get_admin_user(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)

    existing = await categories_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if not existing and name.strip():
        await categories_collection.insert_one({"name": name.strip(), "description": description.strip()})
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
