from sqlalchemy import select

from src.models import ProductsOrm
from src.repositories.base import BaseRepository
from src.schemas.products import Product, ProductRequest


class ProductRepository(BaseRepository):
    model = ProductsOrm
    schema = Product

    def _apply_filters(self, query, filters: ProductRequest):
        if filters.category is not None:
            query = query.where(ProductsOrm.category == filters.category)
        if filters.title is not None:
            query = query.where(ProductsOrm.title.ilike(f"%{filters.title}%"))
        if filters.price_min is not None:
            query = query.where(ProductsOrm.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(ProductsOrm.price <= filters.price_max)

        return query

    async def get_filter_product(
            self,
            limit: int,
            offset: int,
            filters: ProductRequest
    ):
        query = select(self.model)
        query = self._apply_filters(query=query, filters=filters)
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return [self.schema.model_validate(el) for el in result.scalars.all()]
