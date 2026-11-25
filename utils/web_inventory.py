import hashlib
import hmac
import json
import time
from pathlib import Path
from urllib.parse import parse_qsl

from aiohttp import web
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.database import (
    Inventory,
    ItemBase,
    PlayerEquipment,
    PlayerModel,
    Session,
)


WEB_HOST = "127.0.0.1"
WEB_PORT = 8765
PROJECT_ROOT = Path(__file__).resolve().parent.parent

EQUIPMENT_SLOTS = {
    "rod": "equipment_rod",
    "gloves": "equipment_gloves",
    "axe": "equipment_axe",
    "pickaxe": "equipment_pickaxe",
    "weapon": "equipment_weapon",
    "ring1": "equipment_ring",
    "ring2": "equipment_ring",
    "ring3": "equipment_ring",
    "ring4": "equipment_ring",
    "ring5": "equipment_ring",
}


def validate_init_data(init_data: str, bot_token: str) -> dict:
    if not init_data or len(init_data) > 8192:
        raise ValueError("Некорректные Telegram initData")

    values = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    received_hash = values.pop("hash", None)
    if not received_hash:
        raise ValueError("В initData отсутствует hash")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(values.items())
    )
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Подпись Telegram initData недействительна")

    try:
        auth_date = int(values.get("auth_date", "0"))
        user = json.loads(values.get("user", "{}"))
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError("Некорректные данные Telegram") from error

    if auth_date <= 0 or auth_date > time.time() + 30 or time.time() - auth_date > 86400:
        raise ValueError("Telegram initData устарели")

    player_id = user.get("id") if isinstance(user, dict) else None
    if not isinstance(player_id, int):
        raise ValueError("В initData отсутствует Telegram user ID")

    return {"user_id": player_id}


def get_image_path(image_id: str) -> Path | None:
    if image_id == "__placeholder__":
        path = (PROJECT_ROOT / "images" / "placeholder.png").resolve()
        return path if path.is_file() else None

    if not image_id or len(image_id) > 100 or any(
        char not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for char in image_id
    ):
        return None

    # Resolve the item directory from the database in the async handler.
    return None


async def inventory_data(request: web.Request):
    image_id = request.query.get("image")
    if image_id:
        if image_id == "__placeholder__":
            image_path = get_image_path(image_id)
        else:
            async with Session() as session:
                item = await session.get(ItemBase, image_id)
                image_path = None
                if item is not None and item.image_pathname:
                    candidate = (
                        PROJECT_ROOT / item.image_pathname / f"{item.id}.png"
                    ).resolve()
                    if candidate.is_relative_to(PROJECT_ROOT) and candidate.is_file():
                        image_path = candidate

        if image_path is None or not image_path.is_file():
            image_path = get_image_path("__placeholder__")
        if image_path is None:
            raise web.HTTPNotFound(text="Изображение не найдено")
        return web.FileResponse(
            image_path,
            headers={"Cache-Control": "public, max-age=2592000"},
        )

    try:
        identity = validate_init_data(
            request.headers.get("X-Telegram-Init-Data", ""),
            request.app["bot_token"],
        )
    except (ValueError, TypeError) as error:
        return web.json_response({"error": str(error)}, status=401)

    player_id = identity["user_id"]
    async with Session() as session:
        player = await session.get(PlayerModel, player_id)
        if player is None:
            return web.json_response({"error": "Персонаж не найден"}, status=404)

        if request.method == "POST":
            try:
                payload = await request.json()
            except (json.JSONDecodeError, ValueError):
                return web.json_response({"error": "Некорректный запрос"}, status=400)

            action = str(payload.get("action", ""))
            slot = str(payload.get("slot", ""))
            if slot not in EQUIPMENT_SLOTS:
                return web.json_response({"error": "Неизвестный слот экипировки"}, status=400)

            if action == "equip":
                item_id = str(payload.get("item_id", ""))
                owned = await session.scalar(
                    select(Inventory)
                    .where(
                        Inventory.pl_id == player_id,
                        Inventory.id == item_id,
                        Inventory.count > 0,
                    )
                    .options(selectinload(Inventory.base))
                )
                if owned is None or owned.base is None or owned.base.type != EQUIPMENT_SLOTS[slot]:
                    return web.json_response(
                        {"error": "Этот предмет нельзя надеть в выбранный слот"},
                        status=400,
                    )

                already_equipped = await session.scalar(
                    select(PlayerEquipment).where(
                        PlayerEquipment.player_id == player_id,
                        PlayerEquipment.item_id == item_id,
                        PlayerEquipment.slot != slot,
                    )
                )
                if already_equipped is not None:
                    return web.json_response({"error": "Этот предмет уже надет"}, status=409)

                equipped = await session.get(PlayerEquipment, (player_id, slot))
                if equipped is None:
                    session.add(PlayerEquipment(
                        player_id=player_id, slot=slot, item_id=item_id
                    ))
                else:
                    equipped.item_id = item_id
            elif action == "unequip":
                equipped = await session.get(PlayerEquipment, (player_id, slot))
                if equipped is not None:
                    await session.delete(equipped)
            else:
                return web.json_response({"error": "Неизвестное действие"}, status=400)

            await session.commit()
            return web.json_response({"success": True})

        result = await session.scalars(
            select(Inventory)
            .where(Inventory.pl_id == player_id)
            .options(selectinload(Inventory.base))
        )

        items = []
        for record in result.all():
            item = record.base
            if item is None:
                continue
            items.append({
                "id": item.id,
                "name": item.name,
                "count": record.count,
                "location": item.location,
                "type": item.type,
                "rarity": item.rarity,
                "cost": item.cost,
                "description": item.description,
                "image": f"/inventory/data?image={item.id}",
            })

        equipment_result = await session.scalars(
            select(PlayerEquipment)
            .where(PlayerEquipment.player_id == player_id)
        )
        equipment = {}
        for equipped in equipment_result.all():
            item = await session.get(ItemBase, equipped.item_id)
            if item is None:
                continue
            equipment[equipped.slot] = {
                "id": item.id,
                "name": item.name,
                "rarity": item.rarity,
                "description": item.description,
                "cost": item.cost,
                "image": f"/inventory/data?image={item.id}",
            }

        return web.json_response({
            "items": items,
            "equipment": equipment,
            "gold": player.gold,
        })


def create_app(bot_token: str) -> web.Application:
    app = web.Application()
    app["bot_token"] = bot_token
    app.router.add_route("*", "/inventory/data", inventory_data)
    return app


async def start_inventory_web(bot_token: str) -> web.AppRunner:
    runner = web.AppRunner(create_app(bot_token))
    await runner.setup()
    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    try:
        await site.start()
    except Exception:
        await runner.cleanup()
        raise
    return runner
