from fastapi import APIRouter, Depends
from src.seed.users import seed_users
from src.seed.rates import seed_rates
from src.seed.vehicles import seed_vehicles
from src.seed.sessions import seed_sessions
from src.seed.settings import seed_settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/full_complect")
async def seed_full_complect(db: AsyncSession = Depends(get_db)):
    await seed_users(db)
    await seed_rates(10, db)
    await seed_vehicles(db)
    await seed_sessions(20, 3, db)
    return {"message": "You have complect fake data"}


@router.post("/settings")
async def seed_new_settings(db: AsyncSession = Depends(get_db)):
    await seed_settings(db)
    return {"message": "You have settings"}


@router.post("/users")
async def seed_new_users(db: AsyncSession = Depends(get_db)):
    await seed_users(db)
    return {"message": "You have new fake Users - 10 pieces"}


@router.post("/rates")
async def seed_new_rates(base: int = 10, db: AsyncSession = Depends(get_db)):
    await seed_rates(base, db)
    return {"message": "You have rates: ['hourly', 'daily', 'monthly', 'custom']"}


@router.post("/vehicles")
async def seed_new_vehicles(db: AsyncSession = Depends(get_db)):
    await seed_vehicles(db)
    return {"message": "You have new vehicles"}


@router.post("/sessions")
async def seed_num_sessions(
    num_sessions: int = 20, left_in: int = 3, db: AsyncSession = Depends(get_db)
):
    await seed_sessions(num_sessions, left_in, db)
    return {"message": f"You have {num_sessions} new fake Sessions"}
