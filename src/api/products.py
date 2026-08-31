from fastapi import APIRouter

from src.api.dependency import PaginationDep
from src.database import async_session_maker
from src.repositories.products import ProductRepository
from src.schemas.products import ProductRequest

router = APIRouter(prefix="/products")

@router.get("")
async def get_products(
        product_data: ProductRequest,
        pagination: PaginationDep,
):
    async with async_session_maker() as session:
        products = await ProductRepository(session).get_filter_product(
            limit=pagination.limit,
            offset=pagination.offset,
            filters=product_data
        )
        return {"status_code": 200, "data": products}

@router.get("/{product_id}")
async def get_product_by_id(product_id: int):
    async with async_session_maker() as session:
        product = await ProductRepository(session).get_one_or_none(id=product_id)
        return {"status_code": 200, "data": product}


@router.post("")
async def create_product(product_data: ProductRequest):
    async with async_session_maker() as session:
        products = await ProductRepository(session).add(data=product_data)
        return {"status_code": 200, "data": products}
