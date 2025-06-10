"""
Serialization utilities for Pydantic models.
"""
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def serialize(obj: BaseModel) -> str:
    """
    Serialize a Pydantic model to JSON string.
    
    Args:
        obj: Pydantic model instance
        
    Returns:
        JSON string representation
    """
    return obj.json()

def deserialize(data: str, model: Type[T]) -> T:
    """
    Deserialize JSON string to a Pydantic model.
    
    Args:
        data: JSON string
        model: Pydantic model class
        
    Returns:
        Instance of the specified Pydantic model
    """
    return model.parse_raw(data) 