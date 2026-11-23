import secrets
import time

from aiohttp import web
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.database import Inventory, PlayerModel, Session


WEB_URL = "https://mobifield.duckdns.org:68"
TOKEN_TTL = 600
SESSION_TTL = 43200

_login_tokens: dict[str, tuple[int, float]] = {}
_sessions: dict[str, tuple[int, float]] = {}


def create_login_token(player_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _login_tokens[token] = (player_id, time.time() + TOKEN_TTL)
    return token


async def login(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except (ValueError, TypeError):
        return web.json_response({"error": "Некорректный запрос"}, status=400)

    token = payload.get("token") if isinstance(payload, dict) else None
    if not isinstance(token, str):
        return web.json_response({"error": "Не передан ключ входа"}, status=400)

    entry = _login_tokens.pop(token, None)
    if entry is None or entry[1] < time.time():
        return web.json_response({"error": "Ссылка устарела или уже использована"}, status=401)

    player_id = entry[0]
    async with Session() as session:
        player = await session.get(PlayerModel, player_id)
        if player is None:
            return web.json_response({"error": "Персонаж не найден"}, status=404)

    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = (player_id, time.time() + SESSION_TTL)
    response = web.json_response({"ok": True})
    response.set_cookie("mf_session", session_id, max_age=SESSION_TTL, httponly=True, secure=True, samesite="Strict", path="/")
    return response


async def inventory_data(request: web.Request) -> web.Response:
    session_id = request.cookies.get("mf_session")
    entry = _sessions.get(session_id) if session_id else None
    if entry is None or entry[1] < time.time():
        if session_id:
            _sessions.pop(session_id, None)
        return web.json_response({"error": "Требуется вход через Telegram-бота"}, status=401)

    player_id = entry[0]
    async with Session() as session:
        player = await session.get(PlayerModel, player_id)
        if player is None:
            return web.json_response({"error": "Персонаж не найден"}, status=404)
        result = await session.scalars(select(Inventory).where(Inventory.pl_id == player_id).options(selectinload(Inventory.base)))
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


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/inventory/login", login)
    app.router.add_get("/inventory/data", inventory_data)
    return app


async def start_inventory_web() -> web.AppRunner:
    runner = web.AppRunner(create_app())
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8765)
    await site.start()
    return runner
