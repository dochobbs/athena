import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from athena.client.athena_client import AthenaClient


def _mock_response(data, status_code=200):
  """Create a mock httpx.Response."""
  resp = MagicMock()
  resp.status_code = status_code
  resp.json.return_value = data
  resp.raise_for_status = MagicMock()
  return resp


@pytest.mark.asyncio
async def test_get_conditions():
  client = AthenaClient(base_url="http://localhost:9105")
  mock_get = AsyncMock(return_value=_mock_response([
    {"id": "asthma", "display_name": "Asthma", "specialties": ["peds", "im"]},
  ]))
  with patch.object(client._client, "get", mock_get):
    results = await client.get_conditions(specialty="pediatrics")
    assert len(results) == 1
    assert results[0]["id"] == "asthma"
    mock_get.assert_called_once_with(
      "/api/conditions",
      params={"specialty": "pediatrics"},
    )


@pytest.mark.asyncio
async def test_get_framework():
  client = AthenaClient(base_url="http://localhost:9105")
  mock_get = AsyncMock(return_value=_mock_response({"id": "asthma", "topic": "Asthma"}))
  with patch.object(client._client, "get", mock_get):
    result = await client.get_framework("asthma")
    assert result["topic"] == "Asthma"


@pytest.mark.asyncio
async def test_health_check():
  client = AthenaClient(base_url="http://localhost:9105")
  mock_get = AsyncMock(return_value=_mock_response({"status": "healthy"}))
  with patch.object(client._client, "get", mock_get):
    result = await client.health_check()
    assert result is True


@pytest.mark.asyncio
async def test_health_check_down():
  client = AthenaClient(base_url="http://localhost:9105")
  with patch.object(client._client, "get", AsyncMock(side_effect=httpx.ConnectError("refused"))):
    result = await client.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_fallback_on_error():
  client = AthenaClient(base_url="http://localhost:9105")
  with patch.object(client._client, "get", AsyncMock(side_effect=httpx.ConnectError("refused"))):
    results = await client.get_conditions(specialty="pediatrics")
    assert results == []
