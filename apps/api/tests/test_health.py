import asyncio

from httpx import ASGITransport, AsyncClient, Response

from applypilot.main import create_application


def request(path: str) -> Response:
    async def send() -> Response:
        transport = ASGITransport(app=create_application())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(send())


def test_live_endpoint() -> None:
    response = request("/api/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_is_safe() -> None:
    response = request("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    serialized = response.text.lower()
    assert "password" not in serialized
    assert "database_url" not in serialized
    assert "owner" not in serialized


def test_routes_use_api_boundary() -> None:
    assert request("/health/live").status_code == 404
    assert request("/api/health/live").status_code == 200
