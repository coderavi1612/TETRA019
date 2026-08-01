from typing import Type, Dict, Any
from pydantic import BaseModel, ValidationError

class JSONSchemaValidator:
    @staticmethod
    def validate_schema(data: Dict[str, Any], schema_model: Type[BaseModel]) -> BaseModel:
        """
        Validates the parsed dictionary data against the Pydantic schema model.
        """
        try:
            return schema_model.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {str(e)}")
