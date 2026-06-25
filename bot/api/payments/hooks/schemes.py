from pydantic import BaseModel


class FormDataAaio(BaseModel):
    status: str
    merchant_id: str
    invoice_id: str
    order_id: str
    amount: str
    currency: str
    profit: float
    commission: float
    commission_client: float 
    commission_type: float
    sign: str
    method: str 
    desc: str 
    email: str
    us_key: str
