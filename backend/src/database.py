import asyncpg
from asyncpg import Connection


TABLES_NAMES = [
    "users",
    "tracks"
]


async def get_db_conn() -> Connection:
    username = 'postgres'
    password = '1234'
    host = 'localhost'
    name = 'music'

    db_conn = await asyncpg.connect(
        f"postgresql://{username}:{password}@{host}/{name}"
    )

    try:
        yield db_conn
    finally:
        await db_conn.close()


async def create_tables() -> None:
    db_conn = await get_db_conn()

    async with db_conn.transaction():
        await db_conn.execute(
            """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(64) NOT NULL,
                    password TEXT NOT NULL,
                    rates_number INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS tracks (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(128) NOT NULL,
                    rate DOUBLE PRECISION,
                    rates_number INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS users_rates (
                    user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
                    track_id INTEGER REFERENCES tracks (id) ON DELETE CASCADE,
                    rate DOUBLE PRECISION NOT NULL
                );
            """
        )


async def create_functions() -> None:
    db_conn = await get_db_conn()

    async with db_conn.transaction():
        await db_conn.execute(
            """
                CREATE OR REPLACE FUNCTION get_basic_track(track_id integer)
                -- Возвращает базовую информацию о треке --
                RETURNS TABLE (
                    tracks.id,
                    tracks.name
                ) AS $$
                BEGIN
                    SELECT tracks.id,
                           tracks.name
                    FROM tracks
                    WHERE tracks.id = track_id
                END; $$
                LANGUAGE sql;
                
                
                CREATE OR REPLACE FUNCTION get_basic_user(user_id integer)
                -- Возвращает базовую информацию о пользователе --
                RETURNS TABLE (
                    users.id,
                    users.name
                ) AS $$
                BEGIN
                    SELECT users.id,
                           users.name
                    FROM users
                    WHERE users.id = user_id
                END; $$
                LANGUAGE sql;


                CREATE OR REPLACE FUNCTION update_user_rate()
                -- Обновляет рейтинг трека с учетом новой оценки пользователя --
                RETURNS TRIGGER AS $$
                BEGIN
                    IF (TG_OP = 'INSERT') THEN

                        UPDATE tracks
                        SET rate =
                                CASE
                                    WHEN tracks.rate IS NULL THEN NEW.rate
                                    ELSE ((tracks.rate * tracks.rates_number) + NEW.rate)
                                         / (tracks.rates_number + 1)
                                END,
                            rates_number = tracks.rates_number + 1
                        WHERE tracks.id = NEW.track_id

                    ELSIF (TG_OP = 'UPDATE') THEN

                        UPDATE tracks
                        SET rate = 
                            ((tracks.rate * tracks.rates_number) - OLD.rate + NEW.rate)
                            / (tracks.rates_number + 1)
                        WHERE tracks.id = OLD.track_id

                    ELSIF (TG_OP = 'DELETE') THEN

                        UPDATE tracks
                        SET rate =
                                CASE tracks.rates_number
                                    WHEN 1 THEN NULL
                                    ELSE ((tracks.rate * tracks.rates_number) - OLD.rate)
                                        / (tracks.rates_number - 1)
                                END,
                            rates_number = tracks.rates_number - 1
                        WHERE tracks.id = OLD.track_id
                    
                    END IF;
                    RETURN NEW;
                END; $$
                LANGUAGE plpsql;
            """
        )


async def delete_tables() -> None:
    db_conn = await get_db_conn()

    tables = ','.join(TABLES_NAMES)

    async with db_conn.transaction():
        await db_conn.execute(
            f"""
                DROP IF EXISTS TABLE {tables} CASCADE;
                DROP SEQUENCE IF EXISTS {tables} CASCADE;
            """
        )
