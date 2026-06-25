from pydantic import BaseModel
from typing import Literal


class UpdateStatus(BaseModel):
    order_id: str
    status: Literal['Pending', 'Paid', 'Cancelled', 'Expired', 'Error']
