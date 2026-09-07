from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)  # PHP, positive = expense, negative = income
    description = Column(String, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "merchant": self.merchant,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }
