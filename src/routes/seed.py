from fastapi import APIRouter, Depends
from src.seed.users import seed_users, seed_basic_users
from src.seed.tags import seed_tags
from src.seed.photos import seed_photos
from src.seed.comments import seed_comments
from src.seed.ratings import seed_ratings
from src.seed.photo2tag import seed_photo_2_tag
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/basic_users")
async def seed_fake_basic_users(db: AsyncSession = Depends(get_db)):
    await seed_basic_users(db)
    return {
        "message": "You have 5 new fake users: admin, moderator, user, guest, banned"
    }


@router.post("/fake_users")
async def seed_fake_users(number_users: int = 3, db: AsyncSession = Depends(get_db)):
    await seed_users(number_users, db)
    return {"message": f"You have {number_users} new fake Users"}


@router.post("/fake_tags")
async def seed_fake_tags(number_tags: int = 10, db: AsyncSession = Depends(get_db)):
    await seed_tags(number_tags, db)
    return {"message": f"You have {number_tags} new fake Tags"}


@router.post("/fake_photos")
async def seed_fake_photos(number_photos: int = 10, db: AsyncSession = Depends(get_db)):
    await seed_photos(number_photos, db)
    return {"message": f"You have {number_photos} new fake Photos"}


@router.post("/fake_comments")
async def seed_fake_comments(
    number_comments: int = 100, db: AsyncSession = Depends(get_db)
):
    await seed_comments(number_comments, db)
    return {"message": f"You have {number_comments} new fake Comments"}


@router.post("/fake_ratings")
async def seed_fake_ratings(db: AsyncSession = Depends(get_db)):
    await seed_ratings(db)
    return {"message": f"You have new fake Ratings"}


@router.post("/fake_photo_2_tag")
async def seed_fake_photo_2_tag(db: AsyncSession = Depends(get_db)):
    await seed_photo_2_tag(db)
    return {"message": f"You have new fake Photos_2_Tags data"}


@router.post("/full_complect")
async def seed_fake_full_complect(db: AsyncSession = Depends(get_db)):
    await seed_basic_users(db)
    await seed_users(5, db)
    await seed_tags(10, db)
    await seed_photos(10, db)
    await seed_comments(50, db)
    await seed_ratings(db)
    await seed_photo_2_tag(db)
    return {"message": "You have complect fake data"}
