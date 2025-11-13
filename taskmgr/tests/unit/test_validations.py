import pytest
from pydantic import ValidationError as PydanticValidationError
from app.models.schemas import TaskIn

def test_priority_range_validation():
    with pytest.raises(PydanticValidationError):
        TaskIn(title="x", project_id=1, priority=10)
