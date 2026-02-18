from pydantic import BaseModel, ConfigDict


def to_snake(value: str) -> str:
    # Convert camelCase → snake_case
    out = ""
    for c in value:
        if c.isupper():
            out += "_" + c.lower()
        else:
            out += c
    snake_cased = out.lstrip("_")
    # print(f"to_camel value = {value} camel_cased = {snake_cased}")
    return snake_cased


class BaseInData(BaseModel):
    model_config = ConfigDict(
        # alias_generator=to_snake,
        populate_by_name=True,
        from_attributes=True,
    )


class BaseRecordData(BaseModel): 
    model_config = {"from_attributes": True}
