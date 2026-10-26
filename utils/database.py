import logging
from pathlib import Path
from typing import Any

from sqlalchemy import Integer, String, Table, MetaData, select, inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite+aiosqlite:///utils/db.sqlite"
Path("utils").mkdir(parents=True, exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lvl: Mapped[int] = mapped_column("level", Integer, default=1, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class LocationRequirement(Base):
    __tablename__ = "location_req"

    location: Mapped[str] = mapped_column(String, primary_key=True)
    fishing: Mapped[int] = mapped_column(Integer)
    choping: Mapped[int] = mapped_column(Integer)
    searching: Mapped[int] = mapped_column(Integer)
    hunting: Mapped[int] = mapped_column(Integer)
    mining: Mapped[int] = mapped_column(Integer)

class PlayerStatsModel(Base):
    __tablename__ = "player_stats"

    player_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    strength: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    endurance: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    luck: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)


class FSMModel(Base):
    __tablename__ = "fsm_states"

    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[str] = mapped_column(String, default="{}", nullable=False)


class TrashModel(Base):
    __tablename__ = "trash"

    id: Mapped[int] = mapped_column("ID", Integer, primary_key=True)
    msg_id: Mapped[int] = mapped_column("msg_id", Integer, primary_key=True)


_inventory_metadata = MetaData()
_inventory_table: Table | None = None


async def init_db() -> None:
    """Создаёт недостающие ORM-таблицы и подключает существующую таблицу inventory."""
    global _inventory_table

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

        table_names = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )
        if "inventory" in table_names:
            await connection.run_sync(
                _inventory_metadata.reflect,
                only=["inventory"],
            )

    _inventory_table = _inventory_metadata.tables.get("inventory")
    if _inventory_table is not None:
        logger.info("SQLAlchemy: таблица inventory подключена")
    else:
        logger.warning("Таблица inventory пока отсутствует; операции с инвентарём недоступны")
    logger.info("SQLAlchemy database initialized")


async def get_player(player_id: int):
    from utils.player import player as Player

    async with Session() as session:
        record = await session.get(PlayerModel, player_id)
        if record is None:
            return None
        result = Player()
        result.id = record.id
        result.name = record.name
        result.lvl = record.lvl
        result.exp = record.exp
        result.gold = record.gold
        return result

async def get_loc_requir(location: str):
    async with Session() as session:
        record = await session.get(LocationRequirement,location)
        result = {}
        result['fishing'] = record.fishing
        result['choping'] = record.choping
        result['searching'] = record.searching
        result['hunting'] = record.hunting
        result['mining'] = record.mining
        return result



async def add_player(player: Any) -> None:
    async with Session() as session:
        record = await session.get(PlayerModel, player.id)
        if record is None:
            session.add(
                PlayerModel(
                    id=player.id,
                    name=player.name,
                    lvl=getattr(player, "lvl", 1),
                    exp=getattr(player, "exp", 0),
                    gold=getattr(player, "gold", 0),
                )
            )
            await session.commit()
            logger.info("Registered player id=%s", player.id)
        else:
            logger.debug("Player already exists id=%s", player.id)


async def initialize_player_stats(player_id: int, points: int = 10) -> None:
    """Создаёт базовые характеристики игрока, если их ещё нет."""
    async with Session() as session:
        stats = await session.get(PlayerStatsModel, player_id)
        if stats is None:
            session.add(PlayerStatsModel(player_id=player_id, points=points))
            await session.commit()


async def get_player_stats(player_id: int) -> dict[str, int]:
    """Возвращает характеристики и оставшиеся очки игрока."""
    async with Session() as session:
        stats = await session.get(PlayerStatsModel, player_id)
        if stats is None:
            stats = PlayerStatsModel(player_id=player_id, points=10)
            session.add(stats)
            await session.commit()
            await session.refresh(stats)
        return {
            "strength": stats.strength,
            "agility": stats.agility,
            "endurance": stats.endurance,
            "luck": stats.luck,
            "points": stats.points,
        }


async def allocate_stat_point(player_id: int, stat_name: str) -> dict[str, int]:
    """Добавляет одно очко к характеристике, если очки ещё остались."""
    allowed_stats = {"strength", "agility", "endurance", "luck"}
    if stat_name not in allowed_stats:
        raise ValueError(f"Неизвестная характеристика: {stat_name}")

    async with Session() as session:
        stats = await session.get(PlayerStatsModel, player_id)
        if stats is None:
            stats = PlayerStatsModel(player_id=player_id, points=10)
            session.add(stats)
            await session.flush()

        if stats.points > 0:
            setattr(stats, stat_name, getattr(stats, stat_name) + 1)
            stats.points -= 1
            await session.commit()
            logger.info(
                "Saved player stats: player_id=%s stat=%s points_left=%s",
                player_id, stat_name, stats.points,
            )
        else:
            await session.rollback()
            logger.warning("No stat points left: player_id=%s", player_id)

        return {
            "strength": stats.strength,
            "agility": stats.agility,
            "endurance": stats.endurance,
            "luck": stats.luck,
            "points": stats.points,
        }


async def delete_messages(player_id: int, bot) -> None:
    async with Session() as session:
        records = (await session.scalars(
            select(TrashModel).where(TrashModel.id == player_id)
        )).all()
        for record in records:
            try:
                await bot.delete_message(chat_id=record.id, message_id=record.msg_id)
            except Exception:
                logger.exception(
                    "Could not delete tracked message chat_id=%s message_id=%s",
                    record.id,
                    record.msg_id,
                )
            await session.delete(record)
        await session.commit()


async def add_to_trash(player_id: int, msg_id: int) -> None:
    async with Session() as session:
        session.add(TrashModel(id=player_id, msg_id=msg_id))
        await session.commit()


async def get_inventory(player_id: int) -> list[tuple]:
    if _inventory_table is None:
        logger.warning("Cannot load inventory: table inventory does not exist")
        return []

    player_column = next(
        (column for column in _inventory_table.columns
         if column.name.lower() == "pl_id"),
        None,
    )
    if player_column is None:
        raise RuntimeError("В таблице inventory не найден столбец PL_ID")

    async with engine.connect() as connection:
        result = await connection.execute(
            select(_inventory_table).where(player_column == player_id)
        )
        return [tuple(row) for row in result.fetchall()]


async def close_db() -> None:
    await engine.dispose()
    logger.info("SQLAlchemy engine closed")
