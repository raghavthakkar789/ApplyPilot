from applypilot.schemas.errors import ErrorDetail, ErrorResponse


def test_error_schema_is_stable() -> None:
    response = ErrorResponse(error=ErrorDetail(code="invalid_request", message="Request rejected."))
    assert response.model_dump() == {
        "error": {"code": "invalid_request", "message": "Request rejected.", "request_id": None}
    }
