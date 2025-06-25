from pydantic import BaseModel


class ModifyProductNameForm(BaseModel):
    compayny_goods_cd: str
    name: str


