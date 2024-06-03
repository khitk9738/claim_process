from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ClaimBase(SQLModel):
    service_dttm: datetime = Field(default_factory=datetime.utcnow)
    submitted_proc: str = Field(regex=r"^D.*")
    group_id: str
    subscriber_id: str
    provider_npi: str = Field(regex=r"^[0-9]{10}$")
    provider_fees: float
    allowed_fees: float
    member_co_ins: float
    member_co_pay: float
    quadrant: Optional[str] = None
    net_fee: Optional[float] = 0.0

class Claim(ClaimBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)

class ClaimCreate(ClaimBase):
    pass

class ClaimTopProvider:
    def __init__(self, provider_npi, net_fee):
        self.provider_npi = provider_npi
        self.net_fee = net_fee

    # comparator for sorting
    def __lt__(self, other):
        return self.net_fee < other.net_fee