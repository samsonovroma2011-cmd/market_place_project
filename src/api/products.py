from fastapi import APIRouter

from src.api.dependency import PaginationDep, DBDep
from src.schemas.products import ProductFilter, ProductRequest, ProductRequestPartial

router = APIRouter(prefix="/products", tags=["Товары"])

@router.get("")
async def get_products(
        product_data: ProductFilter,
        pagination: PaginationDep,
        db: DBDep
):

    products = await db.products.get_filter_product(
        limit=pagination.limit,
        offset=pagination.offset,
        filters=product_data
    )
    return {"status_code": 200, "data": products}

@router.get("/{product_id}")
async def get_product_by_id(product_id: int, db: DBDep):
    product = await db.products.get_one_or_none(id=product_id)
    return {"status_code": 200, "data": product}


@router.post("")
async def create_product(product_data: ProductRequest, db: DBDep):
    products = await db.products.add(data=product_data)
    await db.commit()

    return {"status_code": 200, "data": products}


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: DBDep):
    await db.products.delete(id=product_id)
    await db.commit()

    return {"status_code": 200}

@router.put("/{product_id}")
async def edit_product(product_id: int, product_data: ProductRequest, db: DBDep):
    await db.products.edit(data=product_data, id=product_id)
    await db.commit()

    return {"status_code": 200}

@router.patch("/{product_id}")
async def edit_partly_product(product_id: int, product_data: ProductRequestPartial, db: DBDep):
    await db.products.edit(data=product_data, is_patch=True, id=product_id)
    await db.commit()

    return {"status_code": 200}