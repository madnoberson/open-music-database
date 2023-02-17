import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_get_basic_user(client: AsyncClient, johndoe_basic: dict):
    """
        Сценарий: Неавторизованный пользователь запрашивает
        базовую информацию о пользователе johndoe
    """

    response = await client.get(
        url='/users/1/basic/'
    )

    johndoe_basic_out = {
        "user": johndoe_basic,
        "is_owner": False
    }

    assert response.status_code == 200
    assert response.json() == johndoe_basic_out


@pytest.mark.anyio
async def test_get_basic_user_authorized(
    client: AsyncClient,
    johndoe_token: str,
    johndoe_basic: dict
):
    """
        Сценарий: Авторизованный пользователь johndoe запрашивает
        базовую информацию о себе 
    """

    headers = {
        "Authorization": johndoe_token
    }

    response = await client.get(
        url='/users/1/basic/',
        headers=headers
    )

    johndoe_basic_out = {
        "user": johndoe_basic,
        "is_owner": True
    }

    assert response.status_code == 200
    assert response.json() == johndoe_basic_out
