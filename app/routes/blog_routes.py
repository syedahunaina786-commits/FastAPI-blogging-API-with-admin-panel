from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.schemas import BlogCreate, BlogUpdate, BlogOut
from app.database import blogs_collection
from app.auth import get_current_user

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])


def serialize_blog(blog: dict) -> dict:
    return {
        "id": str(blog["_id"]),
        "title": blog["title"],
        "content": blog["content"],
        "category": blog["category"],
        "tags": blog.get("tags", []),
        "author": blog.get("author", "Admin"),
        "published": blog.get("published", True),
        "created_at": blog["created_at"],
        "updated_at": blog["updated_at"]
    }


@router.post("/", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
async def create_blog(blog: BlogCreate, current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    doc = blog.model_dump()
    doc["author"] = current_user.get("username", "Admin")
    doc["created_at"] = now
    doc["updated_at"] = now

    result = await blogs_collection.insert_one(doc)
    created = await blogs_collection.find_one({"_id": result.inserted_id})
    return serialize_blog(created)


@router.get("/", response_model=List[BlogOut])
async def get_all_blogs(
    title: Optional[str] = Query(None, description="Search by blog title"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if tag:
        query["tags"] = {"$regex": f"^{tag}$", "$options": "i"}
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}

    blogs = []
    async for blog in blogs_collection.find(query).sort("created_at", -1):
        blogs.append(serialize_blog(blog))
    return blogs


@router.get("/{blog_id}", response_model=BlogOut)
async def get_single_blog(blog_id: str):
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")
    blog = await blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return serialize_blog(blog)


@router.put("/{blog_id}", response_model=BlogOut)
async def update_blog(blog_id: str, updates: BlogUpdate, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    update_data["updated_at"] = datetime.now(timezone.utc)
    result = await blogs_collection.update_one({"_id": ObjectId(blog_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Blog post not found")

    updated_blog = await blogs_collection.find_one({"_id": ObjectId(blog_id)})
    return serialize_blog(updated_blog)


@router.delete("/{blog_id}", status_code=status.HTTP_200_OK)
async def delete_blog(blog_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")
    result = await blogs_collection.delete_one({"_id": ObjectId(blog_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return {"message": "Blog deleted successfully"}
