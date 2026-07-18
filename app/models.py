from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database import Base


class Pessoa(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(
        String(150),
        nullable=False,
        index=True
    )

    telefone = Column(
        String(20),
        nullable=False
    )

    principal = Column(
        String(150),
        nullable=False,
        index=True
    )

    confirmacao = Column(
        Boolean,
        nullable=True,
        default=None
    )