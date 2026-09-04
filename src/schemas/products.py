from pydantic import BaseModel, ConfigDict, Field


class ProductRequest(BaseModel):
    title: str = Field(description="Название (поиск по подстроке)")
    price: float = Field(ge=0, description="Цена")
    quantity: int = Field(ge=0, description="Минимальное количество")
    category: str = Field(description="Категория")
    description: str | None = Field(None, description="Описание")

    model_config = ConfigDict(from_attributes=True)

class ProductFilter(BaseModel):
    title: str | None = Field(None, description="Название")
    price_min: float | None = Field(None, ge=0, description="Минимальная Цена")
    price_max: int | None = Field(None, ge=0, description="Максимальная цена")
    category: str | None = Field(None, description="Категория")

    model_config = ConfigDict(from_attributes=True)

class ProductRequestPartial(BaseModel):
    title: str | None = Field(None, description="Название (поиск по подстроке)")
    price: float | None = Field(None, ge=0, description="Цена")
    quantity: int | None = Field(None, ge=0, description="Минимальное количество")
    category: str | None = Field(None, description="Категория")
    description: str | None = Field(None, description="Описание")

    model_config = ConfigDict(from_attributes=True)


class Product(ProductRequest):
    id: int
    estimation: float = Field(0, ge=0, le=5, description="Рейтинг")