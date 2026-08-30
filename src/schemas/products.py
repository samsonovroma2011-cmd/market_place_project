from pydantic import BaseModel, ConfigDict, Field


class ProductRequest(BaseModel):
    category: str | None = Field(None, description="Категория")
    title: str | None = Field(None, description="Название (поиск по подстроке)")
    price_min: float | None = Field(None, ge=0, description="Минимальная цена")
    price_max: float | None = Field(None, ge=0, description="Максимальная цена")
    estimation: float | None = Field(None, ge=0, le=5, description="Минимальный рейтинг")
    quantity: int | None = Field(None, ge=0, description="Минимальное количество")

    model_config = ConfigDict(from_attributes=True)

class Product(ProductRequest):
    id: int