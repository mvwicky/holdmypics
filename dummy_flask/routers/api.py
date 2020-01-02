from fastapi import APIRouter

router = APIRouter()


@router.get("/{size}/")
async def just_size(size: int):
    pass
