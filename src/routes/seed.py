from fastapi import APIRouter, Depends
from src.seed.users import seed_users
from src.seed.rates import seed_rates
from src.seed.vehicles import seed_vehicles
from src.seed.sessions import seed_sessions
# from src.seed.comments import seed_comments
# from src.seed.ratings import seed_ratings
# from src.seed.photo2tag import seed_photo_2_tag
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/users")
async def seed_new_users(db: AsyncSession = Depends(get_db)):
    await seed_users(db)
    return {"message": "You have new fake Users - 10 pieces"}


@router.post("/rates")
async def seed_new_rates(base: int = 10, db: AsyncSession = Depends(get_db)):
    await seed_rates(base, db)
    return {
        "message": "You have rates: ['hourly', 'daily', 'monthly', 'custom']"
    }

@router.post("/vehicles")
async def seed_new_vehicles(db: AsyncSession = Depends(get_db)):
    await seed_vehicles(db)
    return {
        "message": "You have new vehicles"
    }


@router.post("/sessions")
async def seed_num_sessions(num_sessions: int = 100, db: AsyncSession = Depends(get_db)):
    await seed_sessions(num_sessions, db)
    return {"message": f"You have {num_sessions} new fake Sessions"}


# @router.post("/fake_photos")
# async def seed_fake_photos(number_photos: int = 10, db: AsyncSession = Depends(get_db)):
#     await seed_photos(number_photos, db)
#     return {"message": f"You have {number_photos} new fake Photos"}


# @router.post("/fake_comments")
# async def seed_fake_comments(
#     number_comments: int = 100, db: AsyncSession = Depends(get_db)
# ):
#     await seed_comments(number_comments, db)
#     return {"message": f"You have {number_comments} new fake Comments"}


# @router.post("/fake_ratings")
# async def seed_fake_ratings(db: AsyncSession = Depends(get_db)):
#     await seed_ratings(db)
#     return {"message": f"You have new fake Ratings"}


# @router.post("/fake_photo_2_tag")
# async def seed_fake_photo_2_tag(db: AsyncSession = Depends(get_db)):
#     await seed_photo_2_tag(db)
#     return {"message": f"You have new fake Photos_2_Tags data"}


@router.post("/full_complect")
async def seed_full_complect(db: AsyncSession = Depends(get_db)):
    await seed_users(db)
    await seed_rates(10, db)
    await seed_vehicles(db)
#     await seed_tags(10, db)
#     await seed_photos(10, db)
#     await seed_comments(50, db)
#     await seed_ratings(db)
#     await seed_photo_2_tag(db)
    return {"message": "You have complect fake data"}
