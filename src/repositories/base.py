from pydantic import BaseModel
from sqlalchemy import select, insert


class BaseRepository:
    model: None
    schema: BaseModel

    def __init__(self, session):
        self.session = session

    async def get_all(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]


    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().one_or_none()]


    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        return await self.session.execute(add_stmt)