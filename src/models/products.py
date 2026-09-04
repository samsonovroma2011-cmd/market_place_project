from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ProductsOrm(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    price: Mapped[float]
    estimation: Mapped[float] = 0
    quantity: Mapped[int]
    category: Mapped[str]
    description: Mapped[str | None] = mapped_column(None)