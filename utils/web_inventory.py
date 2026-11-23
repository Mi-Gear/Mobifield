import hashlib
hmac
import json
import time

from aiohttp import web
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.database import Inventory, PlayerModel, Session


def validate_init_data(init_data: str, bot_token: str) -> dict:
    if not init_data or len(init_data) > 8192:
        raise ValueError("Некорректные Telegram initData")
    from urllib.parse import parse_qsl
    values = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    received_hash = values.pop("hash", None)
    if not received_hash:
        raise ValueError("В initData отсутствует hash")
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Подпись Telegram initData недействительна")
    auth_date = int(values.get("auth_date", "0"))
    if auth_date > time.time() + 30 or time.time() - auth_date > 86400:
        raise ValueError("Telegram initData устарели")
    user = json.loads(values.get("user", "{}"))
    player_id = user.get("id")
    if not isinstance(player_id, int):
        raise ValueError("В initData отсутствует Telegram user ID")
    return {"user_id": player_id}


async def inventory_data(request: web.Request) -> web.Response:
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    try:
        identity = validate_init_data(init_data, request.app["bot_token"])
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        return web.json_response({"error": str(error)}, status=401)

    player_id = identity["user_id"]
    async with Session() as session:
        player = await session.get(PlayerModel, player_id)
        if player is None:
            return web.json_response({"error": "Персонаж не найден"}, status=404)
        result = await session.scalars(
            select(Inventory)
            .where(Inventory.pl_id == player_id)
            .options(selectinload(Inventory.base))
        )
        items = []
        for record in result.all():
            item = record.base
            items.append({
                "id": item.id,
                "name": item.name,
                "count": record.count,
                "type": item.type,
                "rarity": item.rarity,
                "cost": item.cost,
                "description": item.description,
                "image": item.image_pathname,
            })
        return web.json_response({"items": items, "gold": player.gold})


def create_app(bot_token: str) -> web.Application:
    app = web.Application()
    app["bot_token"] = bot_token
    app.router.add_get("/inventory/data", inventory_data)
    return app


async def start_inventory_web(bot_token: str) -> web.AppRunner:
    runner = web.AppRunner(create_app(bot_token))
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8765)
    await site.start()
    return runner
