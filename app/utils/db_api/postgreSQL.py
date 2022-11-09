from typing import Union
import asyncpg
from asyncpg import Pool, Connection
from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        registration_time VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        user_name VARCHAR(255) NULL,
        chat_id BIGINT NOT NULL UNIQUE,
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, registration_time, full_name, user_name, telegram_id, chat_id, training_num):
        sql = """INSERT INTO users(registration_time, full_name, user_name, 
        telegram_id, chat_id, training_num) VALUES($1, $2, $3, $4, $5, $6) returning *"""
        return await self.execute(sql, registration_time, full_name, user_name, telegram_id, chat_id, training_num,
                                  fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    # Обновление данных в бд

    async def update_user_height(self, height, telegram_id):
        sql = "UPDATE Users SET height=$1 WHERE telegram_id=$2"
        return await self.execute(sql, height, telegram_id, execute=True)

    async def update_user_age(self, age, telegram_id):
        sql = "UPDATE Users SET age=$1 WHERE telegram_id=$2"
        return await self.execute(sql, age, telegram_id, execute=True)

    # Удаление всех пользователей
    async def delete_all_users(self):
        await self.execute("DELETE FROM Users WHERE True")

    async def delete_user(self, telegram_id):
        await self.execute(f"DELETE FROM Users WHERE telegram_id={telegram_id}", execute=True)

    # Удаление таблицы
    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
