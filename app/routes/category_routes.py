from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.schemas import CategoryCreate, CategoryOut
from app.database import categories_collection
from app.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])


def serialize_category(cat: dict) -> dict:
    return {
        "id": str(cat["_id"]),
        "name": cat["name"],
        "description": cat.get("description", "")
    }


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user)):
    existing = await categories_collection.find_one({"name": {"$regex": f"^{category.name}$", "$options": "i"}})
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    doc = category.model_dump()
    result = await categories_collection.insert_one(doc)
    created = await categories_collection.find_one({"_id": result.inserted_id})
    return serialize_category(created)


@router.get("/", response_model=List[CategoryOut])
async def get_categories():
    categories = []
    async for cat in categories_collection.find():
        categories.append(serialize_category(cat))
    return categories


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category ID")
    result = await categories_collection.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
