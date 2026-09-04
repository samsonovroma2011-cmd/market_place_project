from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update


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
        result = await self.session.execute(add_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model)

    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)

    async def edit(self, data: BaseModel, is_patch=False, **filter_by):
        edit_stmt = update(self.model).values(**data.model_dump(exclude_unset=is_patch), **filter_by)
        await self.session.execute(edit_stmt)