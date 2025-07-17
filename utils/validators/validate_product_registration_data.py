from typing import Any, List
from models.product.product_registration_data import ProductRegistrationRawData

def get_model_keys() -> List[str]:
    """
    Dynamically extract all column names from ProductRegistrationRawData ORM model.
    """
    return list(ProductRegistrationRawData.__table__.columns.keys())

def validate_product_registration_data(data: Any) -> bool:
    """
    Validate that the input data is a dict and contains all required keys from the model.
    Args:
        data: The product registration data to validate.
    Returns:
        True if valid, False otherwise.
    """
    required_keys = get_model_keys()
    if not isinstance(data, dict):
        return False
    for key in required_keys:
        if key not in data:
            return False
    return True

def get_missing_keys(data: Any) -> List[str]:
    """
    Return a list of missing keys from the data based on the model.
    """
    required_keys = get_model_keys()
    if not isinstance(data, dict):
        return required_keys
    return [key for key in required_keys if key not in data] 