import pytest
from httpx import AsyncClient
from asyncpg import Connection, UndefinedTableError

from ..app import app
from ..services.auth import AuthService
from ..database import (
    create_functions,
    create_tables,
    delete_tables
)

@pytest.fixture(scope='function')
async def client() -> AsyncClient:
    async with AsyncClient(
        app=app, base_url='http://test'
    ) as client:
        yield client


@pytest.fixture(scope='function', autouse=True)
async def refresh_db() -> None:
    try:
        await delete_tables()
    except UndefinedTableError:
        pass
    
    await create_functions()
    await create_tables()


@pytest.fixture(scope='function')
async def johndoe_token(request, client: AsyncClient) -> str:
    """
        Возвращает access token для пользователя johndoe
    """

    user_data = {
        "name": "johndoe",
        "password": "secretpassword"
    }

    response = await client.post(
        url='/sign_up/',
        json=user_data
    )

    return response.json()['access_token']


@pytest.fixture(scope='function')
async def janedoe_token(request, client: AsyncClient) -> str:
    """
        Возвращает access token для пользователя janedoe
    """

    user_data = {
        "name": "janedoe",
        "password": "secretpassword"
    }

    response = await client.post(
        url='/sign_up/',
        json=user_data
    )

    return response.json()['access_token']


@pytest.fixture(scope='function')
def johndoe_basic() -> dict:
    """ Возвращает базовую информацию о пользователе johndoe """

    return {
        "id": 1,
        "name": "johndoe"
    }


@pytest.fixture(scope='function')
def janedoe_basic() -> dict:
    """ Возвращает базовую информацию о пользователе janedoe """

    return {
        "id": 2,
        "name": "janedoe"
    }


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


