from fastapi import HTTPException, Depends
from asyncpg import Connection

from ..schemas.users import (
    BasicUser,
    BasicUserOut,
    User,
    UserOut,
    UserRateIn,
    UserRateOut
)
from ..schemas.auth import TokenUser

from ..database import get_db_conn
from .auth import get_current_user


class UsersService:
    def __init__(
        self,
        db_connection: Connection = Depends(get_db_conn),
        current_user: TokenUser = Depends(get_current_user)
    ) -> None:
        self.db_conn = db_connection
        self.current_user = current_user
    
    async def get_basic_user(
        self,
        user_id: int
    ) -> BasicUserOut:
        user_record = await self.db_conn.fetchrow(
            f"SELECT * FROM get_basic_user({user_id})"
        )

        if not user_record:
            raise HTTPException(404)
        
        user_dict = dict(user_record)

        is_owner = False
        if self.current_user.id:
            if self.current_user.id == user_id:
                is_owner = True

        user = BasicUser.parse_obj(user_dict)

        return BasicUserOut(
            user=user,
            is_owner=is_owner
        )

    async def get_user(
        self,
        user_id: int
    ):
        user_record = await self.db_conn.fetchrow(
            f"""
                SELECT *
                FROM users
                WHERE users.id == {user_id}
            """
        )

        if not user_record:
            raise HTTPException(404)
        
        user_dict = dict(user_record)

        is_owner = False
        if self.current_user:
            if self.current_user.id == user_id:
                is_owner = True
        
        user = User.parse_obj(user_dict)

        return UserOut(
            user=user,
            is_owner=is_owner
        )
    
    async def create_rate(
        self,
        create_rate: UserRateIn
    ) -> UserRateOut:
        if not self.current_user:
            raise HTTPException(401)
        
        track_rate_record = await self.db_conn.fetchrow(
           f"""
                INSERT INTO users_rates
                (user_id, track_id, rate)
                VALUES
                (
                    {self.current_user.id},
                    {create_rate.track_id},
                    {create_rate.rate}
                )
                RETURNING rate AS user_rate,
                (
                    SELECT tracks.rate AS track_rate,
                           tracks.rates_number AS track_rates_number    
                    FROM tracks
                    WHERE tracks.id = {create_rate.track_id}
                )
           """ 
        )



    
    
