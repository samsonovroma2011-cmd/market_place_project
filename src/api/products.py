from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependency import PaginationDep
from src.database import async_session_maker
from src.models import ProductsOrm
from src.repositories.products import ProductRepository
from src.schemas.products import ProductRequest

router = APIRouter(prefix="/{category}/products")

@router.get("")
async def get_products(
        product_data: ProductRequest,
        pagination: PaginationDep,
):
    async with async_session_maker() as session:
        products = await ProductRepository(session=session).get_filter_product(
            limit=pagination.limit,
            offset=pagination.offset,
            filters=product_data
        )
        return products