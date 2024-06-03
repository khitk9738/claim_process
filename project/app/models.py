from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# This Python class `ClaimBase` defines fields for a claim with service date and time, submitted
# procedure, group ID, subscriber ID, provider NPI, fees, co-insurance, co-pay, quadrant, and net fee.
# The `service_dttm` field is a datetime object with a default value of the current date and time.
# The `submitted_proc` field is a string that starts with the letter 'D'. The `provider_npi` field is a
# string with a regex pattern that matches a 10-digit number. The `net_fee` field is an optional float
# with a default value of 0.0. The `ClaimBase` class inherits from the `SQLModel` class.
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

# The `Claim` class represents a table with an `id` field that is an integer and serves as the primary
# key. The `Claim` class inherits from the `ClaimBase` class and sets the `table` parameter to `True`.
class Claim(ClaimBase, table=True):
    id: int = Field(default=None, nullable=False, primary_key=True)

class ClaimCreate(ClaimBase):
    pass

# The `ClaimTopProvider` class represents a claim with provider NPI and net fee, with a comparison
# method based on priority. The `__lt__` method is used to compare two instances of the class.
class ClaimTopProvider:
    def __init__(self, provider_npi, net_fee):
        self.provider_npi = provider_npi
        self.net_fee = net_fee

    def __lt__(self, other):
        return self.priority < other.priority    