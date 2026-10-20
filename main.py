import random
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Optional, Any

# =====================================================================
# Цветной вывод и эффект печати
# =====================================================================

_print = print


def setup_color() -> bool:
    """Включает поддержку ANSI, если это возможно."""
    if os.environ.get("NO_COLOR"):
        return False

    if os.name == "nt":
        os.system("")

    try:
        return sys.stdout.isatty()
    except Exception:
        return False


COLOR_ENABLED = setup_color()

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
    "lightred": "\033[91m",
    "lightgreen": "\033[92m",
    "lightyellow": "\033[93m",
    "lightblue": "\033[94m",
    "lightmagenta": "\033[95m",
    "lightcyan": "\033[96m",
}

RARITY_COLORS = {
    "обычный": "white",
    "необычный": "lightgreen",
    "редкий": "lightblue",
    "эпический": "lightmagenta",
    "легендарный": "lightyellow",
}


def colorize(text: str, color: Optional[str] = None, bold: bool = False) -> str:
    if not COLOR_ENABLED or not text:
        return text

    code = COLORS.get(color, "") if color else ""
    if bold:
        code = COLORS["bold"] + code

    if not code:
        return text

    return f"{code}{text}{COLORS['reset']}"


def infer_color(text: str) -> Optional[str]:
    if "\033[" in text:
        return None

    t = text.lower()

    if any(x in t for x in (
        "ошибка", "недостаточно", "неверный", "нельзя", "не удалось",
        "вы пали", "поражение", "повреждено", "слишком", "напа", "предатель"
    )):
        return "red"

    if any(x in t for x in (
        "победа", "получено", "награда", "квест завершён", "покупка совершена",
        "предмет продан", "улучшен", "сохранена", "загружена", "успешно",
        "достижение"
    )):
        return "green"

    if any(x in t for x in (
        "урон", "атакует", "промахивается", "крит", "бой", "защита",
        "уклоняетесь", "враг", "яд", "ожог", "проклятие"
    )):
        return "yellow"

    if any(x in t for x in (
        "карта", "локация", "главное меню", "действия", "выберите", "назад"
    )):
        return "cyan"

    if any(x in t for x in (
        "квест", "задание", "получено задание", "новый квест", "фрагмент сюжета"
    )):
        return "magenta"

    if any(x in t for x in ("золото", "цена", "стоимость", "репутация")):
        return "yellow"

    return None


def print(*values, sep: str = " ", end: str = "\n", color: Optional[str] = None, bold: bool = False, **kwargs) -> None:
    text = sep.join(str(v) for v in values)

    if "\033[" in text:
        _print(text, end=end, **kwargs)
        return

    if color is None:
        color = infer_color(text)

    _print(colorize(text, color, bold), end=end, **kwargs)


TYPEWRITER_SPEED = 0.006
TYPEWRITER_ENABLED = False
try:
    TYPEWRITER_ENABLED = sys.stdout.isatty() and not os.environ.get("NO_TYPEWRITER")
except Exception:
    TYPEWRITER_ENABLED = False


def typewriter(text: str, color: Optional[str] = None, speed: float = TYPEWRITER_SPEED, newline: bool = True) -> None:
    if not TYPEWRITER_ENABLED or speed <= 0:
        print(text, color=color)
        return

    prefix = COLORS.get(color, "") if COLOR_ENABLED and color else ""
    reset = COLORS["reset"] if COLOR_ENABLED and prefix else ""

    try:
        if prefix:
            sys.stdout.write(prefix)

        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            if ch in " \n":
                time.sleep(speed * 0.3)
            else:
                time.sleep(speed)

        if reset:
            sys.stdout.write(reset)

        if newline:
            sys.stdout.write("\n")

        sys.stdout.flush()
    except KeyboardInterrupt:
        if reset:
            sys.stdout.write(reset)
        sys.stdout.write("\n")
        sys.stdout.flush()
        raise


def say(speaker: str, text: str, speaker_color: str = "lightyellow", text_color: str = "white") -> None:
    sys.stdout.write(colorize(f"{speaker}: ", speaker_color, True))
    sys.stdout.flush()
    typewriter(text, color=text_color)


def story(text: str, color: str = "lightmagenta") -> None:
    typewriter(text, color=color)


# =====================================================================
# Ввод
# =====================================================================

def safe_input(prompt: str = "") -> str:
    try:
        return input(colorize(prompt, "lightcyan"))
    except (EOFError, KeyboardInterrupt):
        print("Выход из игры.", color="red")
        sys.exit(0)


def choose_option(options: List[str], title: str = "Выберите действие", allow_back: bool = True) -> int:
    if not options:
        print("Нет доступных вариантов.", color="gray")
        return 0

    while True:
        print(title, color="lightcyan", bold=True)
        for i, opt in enumerate(options, 1):
            print(f"{colorize(str(i) + '.', 'yellow')} {opt}")
        if allow_back:
            print(colorize("0. Назад", "gray"))

        raw = safe_input("> ")
        if raw.strip().isdigit():
            num = int(raw.strip())
            if allow_back and num == 0:
                return 0
            if 1 <= num <= len(options):
                return num

        print("Неверный ввод. Введите номер пункта из списка.", color="red")


def ask_yes_no(question: str) -> bool:
    choice = choose_option(["Да", "Нет"], question, allow_back=False)
    return choice == 1


def pause() -> None:
    safe_input("Нажмите Enter, чтобы продолжить...")


# =====================================================================
# Константы
# =====================================================================

SAVE_VERSION = 3
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save.json")

XP_BASE = 25
XP_STEP = 25

MAP_CELL_WIDTH = 12
MAP_GAP = 3

COMMON = "обычный"
UNCOMMON = "необычный"
RARE = "редкий"
EPIC = "эпический"
LEGENDARY = "легендарный"

RARITY_ORDER = {
    COMMON: 0,
    UNCOMMON: 1,
    RARE: 2,
    EPIC: 3,
    LEGENDARY: 4,
}

RARITY_WEIGHTS = {
    COMMON: 60,
    UNCOMMON: 25,
    RARE: 10,
    EPIC: 4,
    LEGENDARY: 1,
}

TYPE_NAMES = {
    "weapon": "оружие",
    "armor": "броня",
    "helmet": "шлем",
    "boots": "ботинки",
    "accessory": "аксессуар",
    "consumable": "расходник",
    "material": "материал",
    "quest": "квестовый предмет",
}

EQUIPMENT_SLOTS = ["weapon", "armor", "helmet", "boots", "accessory"]

SLOT_NAMES = {
    "weapon": "Оружие",
    "armor": "Броня",
    "helmet": "Шлем",
    "boots": "Ботинки",
    "accessory": "Аксессуар",
}

FACTION_NAMES = {
    "light": "Свет",
    "balance": "Равновесие",
    "shadow": "Тьма",
}

STATUS_NAMES = {
    "poison": "яд",
    "burn": "ожог",
    "chill": "холод",
    "curse": "проклятие",
    "bless": "благословение",
}

DIFFICULTIES = {
    "easy": {"name": "Лёгкий", "enemy": 0.80, "reward": 1.15, "elite": 6},
    "normal": {"name": "Обычный", "enemy": 1.00, "reward": 1.00, "elite": 10},
    "nightmare": {"name": "Кошмар", "enemy": 1.25, "reward": 0.95, "elite": 18},
    "cursed": {"name": "Проклятый", "enemy": 1.50, "reward": 0.90, "elite": 30},
}

ELITE_NAMES = {
    "furious": "Яростный",
    "armored": "Бронированный",
    "ghostly": "Призрачный",
    "vampiric": "Вампирский",
    "toxic": "Токсичный",
    "cursed": "Проклятый",
}

PERKS = {
    "perk_might": {"name": "Мощь", "desc": "+3 к атаке."},
    "perk_guard": {"name": "Стена", "desc": "+3 к защите."},
    "perk_vitality": {"name": "Живучесть", "desc": "+25 к максимальному здоровью."},
    "perk_precision": {"name": "Точность", "desc": "+8% к шансу критического удара."},
    "perk_evasion": {"name": "Уклонение", "desc": "+8% к шансу уклонения."},
    "perk_fortune": {"name": "Удача", "desc": "+10% к поиску лута."},
    "perk_barter": {"name": "Торг", "desc": "Лучшие цены у торговцев."},
    "perk_alchemist": {"name": "Алхимик", "desc": "Шанс создать дополнительный расходник."},
    "perk_status": {"name": "Отравитель", "desc": "Ваши статусы действуют на 1 ход дольше."},
    "perk_companion": {"name": "Друг", "desc": "Спутник действует чаще."},
    "perk_dark": {"name": "Тёмный пакт", "desc": "+5 к атаке, -15 к максимальному здоровью."},
    "perk_light": {"name": "Светлая воля", "desc": "+2 к защите, +10 к максимальному здоровью."},
}

COMPANIONS = {
    "wolf": {"name": "Волчонок Серый", "dodge": 5, "crit": 0, "defense": 0, "chance": 15, "type": "attack"},
    "imp": {"name": "Тенёнок", "dodge": 0, "crit": 5, "defense": 0, "chance": 12, "type": "curse"},
    "sprite": {"name": "Осколок света", "dodge": 0, "crit": 0, "defense": 2, "chance": 12, "type": "heal"},
}

ENCHANTS = {
    "fire": {"name": "Пламя", "types": ["weapon"], "material": "dark_essence", "count": 1, "gold": 150},
    "frost": {"name": "Лёд", "types": ["weapon"], "material": "frost_shard", "count": 2, "gold": 120},
    "venom": {"name": "Яд", "types": ["weapon"], "material": "monster_fang", "count": 3, "gold": 100},
    "shadow": {"name": "Тень", "types": ["weapon"], "material": "dark_essence", "count": 2, "gold": 180},
    "stone": {"name": "Камень", "types": ["armor", "helmet", "boots"], "material": "scrap_metal", "count": 3, "gold": 80},
    "life": {"name": "Жизнь", "types": ["armor", "helmet", "boots"], "material": "gem", "count": 2, "gold": 140},
    "swift": {"name": "Скорость", "types": ["armor", "helmet", "boots"], "material": "monster_fang", "count": 3, "gold": 90},
}

CRAFT_RECIPES = {
    "potion": {"result": "potion", "materials": [("small_potion", 2), ("monster_fang", 1)]},
    "greater_potion": {"result": "greater_potion", "materials": [("potion", 2), ("gem", 1)]},
    "strength_elixir": {"result": "strength_elixir", "materials": [("monster_fang", 2), ("gem", 1)]},
    "shield_elixir": {"result": "shield_elixir", "materials": [("scrap_metal", 2), ("gem", 1)]},
    "poison_vial": {"result": "poison_vial", "materials": [("monster_fang", 2), ("dark_essence", 1)]},
    "firebomb": {"result": "firebomb", "materials": [("ash_heart", 2), ("scrap_metal", 1)]},
    "frostbomb": {"result": "frostbomb", "materials": [("frost_shard", 2), ("scrap_metal", 1)]},
    "holy_water": {"result": "holy_water", "materials": [("gem", 1), ("ancient_fragment", 1)]},
    "curse_scroll": {"result": "curse_scroll", "materials": [("dark_essence", 1), ("ancient_fragment", 1)]},
}

# =====================================================================
# Классы
# =====================================================================

CLASS_DATA = {
    "Воин": {
        "hp": 52, "attack": 7, "defense": 3, "crit": 5, "loot": 0, "dodge": 3,
        "hp_gain": 4, "atk_gain": 1, "def_gain": 2,
        "weapon": "iron_sword",
        "desc": "Больше максимального здоровья и базовой защиты.",
    },
    "Разбойник": {
        "hp": 42, "attack": 8, "defense": 2, "crit": 20, "loot": 5, "dodge": 8,
        "hp_gain": 2, "atk_gain": 2, "def_gain": 1,
        "weapon": "rogue_dagger",
        "desc": "Больше шанса критического эффекта и лучшее начальное оружие.",
    },
    "Маг": {
        "hp": 34, "attack": 12, "defense": 1, "crit": 5, "loot": 0, "dodge": 3,
        "hp_gain": 1, "atk_gain": 3, "def_gain": 0,
        "weapon": "magic_staff",
        "desc": "Больше урона, но меньше здоровья и защиты.",
    },
    "Следопыт": {
        "hp": 46, "attack": 8, "defense": 2, "crit": 10, "loot": 10, "dodge": 12,
        "hp_gain": 3, "atk_gain": 2, "def_gain": 1,
        "weapon": "hunting_bow",
        "desc": "Сбалансированные характеристики, бонус к уклонению и поиску лута.",
    },
}

# =====================================================================
# Вспомогательные функции статусов
# =====================================================================

def add_status(status_list: List[Dict[str, Any]], status_type: str, amount: int, duration: int) -> None:
    if duration <= 0:
        return

    for status in status_list:
        if status.get("type") == status_type:
            status["amount"] = max(status.get("amount", 0), amount)
            status["turns"] = max(status.get("turns", 0), duration)
            return

    status_list.append({"type": status_type, "amount": amount, "turns": duration})


def status_attack_mult(status_list: List[Dict[str, Any]]) -> float:
    mult = 1.0

    for status in status_list:
        if status.get("type") == "chill":
            mult *= 0.8
        if status.get("type") == "bless":
            mult *= 1.1

    return mult


def status_defense_mult(status_list: List[Dict[str, Any]]) -> float:
    mult = 1.0

    for status in status_list:
        if status.get("type") == "curse":
            mult *= 0.8
        if status.get("type") == "bless":
            mult *= 1.1

    return mult


def status_text(status_list: List[Dict[str, Any]]) -> str:
    if not status_list:
        return "нет"

    parts = []
    for status in status_list:
        name = STATUS_NAMES.get(status.get("type", ""), status.get("type", "?"))
        parts.append(f"{name}:{status.get('turns', 0)}")

    return ", ".join(parts)


# =====================================================================
# Шаблоны предметов
# =====================================================================

ITEM_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # Оружие первой главы
    "rusty_sword": {
        "name": "Ржавый меч", "item_type": "weapon",
        "description": "Старый меч, но всё ещё режет.",
        "weight": 3.0, "value": 8, "rarity": COMMON, "attack_bonus": 4, "req_level": 1,
    },
    "iron_sword": {
        "name": "Железный меч", "item_type": "weapon",
        "description": "Надёжное оружие солдата.",
        "weight": 3.0, "value": 25, "rarity": COMMON, "attack_bonus": 7, "req_level": 1,
    },
    "rogue_dagger": {
        "name": "Клинок разбойника", "item_type": "weapon",
        "description": "Лёгкий и смертельно точный клинок.",
        "weight": 1.5, "value": 40, "rarity": UNCOMMON, "attack_bonus": 9, "crit_bonus": 5, "req_level": 1,
    },
    "magic_staff": {
        "name": "Посох искр", "item_type": "weapon",
        "description": "Посох, усиливающий боевую магию.",
        "weight": 2.0, "value": 30, "rarity": COMMON, "attack_bonus": 10, "req_level": 1,
    },
    "hunting_bow": {
        "name": "Охотничий лук", "item_type": "weapon",
        "description": "Лук следопыта.",
        "weight": 2.0, "value": 30, "rarity": COMMON, "attack_bonus": 8, "loot_bonus": 5, "req_level": 1,
    },
    "steel_sword": {
        "name": "Стальной меч", "item_type": "weapon",
        "description": "Хорошая сталь для опасной дороги.",
        "weight": 3.5, "value": 70, "rarity": UNCOMMON, "attack_bonus": 11, "req_level": 3,
    },
    "forest_blade": {
        "name": "Лесной клинок", "item_type": "weapon",
        "description": "Клинок, выкованный для тихой охоты.",
        "weight": 2.0, "value": 100, "rarity": UNCOMMON, "attack_bonus": 13, "crit_bonus": 5, "req_level": 4,
    },
    "rune_axe": {
        "name": "Рунный топор", "item_type": "weapon",
        "description": "Топор с древними рунами.",
        "weight": 5.0, "value": 170, "rarity": RARE, "attack_bonus": 16, "req_level": 5,
    },
    "shadow_blade": {
        "name": "Теневой клинок", "item_type": "weapon",
        "description": "Клинок, пьющий свет.",
        "weight": 2.5, "value": 260, "rarity": EPIC, "attack_bonus": 19, "crit_bonus": 10, "req_level": 6,
    },
    "dawnbringer": {
        "name": "Рассветный меч", "item_type": "weapon",
        "description": "Легендарный меч против тьмы.",
        "weight": 4.0, "value": 500, "rarity": LEGENDARY,
        "attack_bonus": 23, "crit_bonus": 15, "loot_bonus": 5, "req_level": 8,
    },

    # Оружие второй главы и новых зон
    "ash_falchion": {
        "name": "Пепельная фальшион", "item_type": "weapon",
        "description": "Клинок, закалённый в пепле пустоши.",
        "weight": 3.0, "value": 240, "rarity": RARE, "attack_bonus": 21, "req_level": 8,
    },
    "frost_spear": {
        "name": "Ледяное копьё", "item_type": "weapon",
        "description": "Древко из вечного льда.",
        "weight": 4.5, "value": 380, "rarity": EPIC,
        "attack_bonus": 25, "crit_bonus": 5, "req_level": 9, "enchant": "frost",
    },
    "sanctified_mace": {
        "name": "Освящённая булава", "item_type": "weapon",
        "description": "Оружие хранителей света.",
        "weight": 5.0, "value": 420, "rarity": EPIC, "attack_bonus": 27, "req_level": 10,
    },
    "void_blade": {
        "name": "Клинок Пустоты", "item_type": "weapon",
        "description": "Лезвие, вырезанное из самого Забвения.",
        "weight": 3.0, "value": 800, "rarity": LEGENDARY,
        "attack_bonus": 31, "crit_bonus": 12, "loot_bonus": 5, "req_level": 11, "enchant": "shadow",
    },
    "spider_fang": {
        "name": "Клык королевы", "item_type": "weapon",
        "description": "Ядовитый клинок из паутины.",
        "weight": 2.0, "value": 260, "rarity": RARE,
        "attack_bonus": 18, "crit_bonus": 8, "req_level": 6, "enchant": "venom",
    },

    # Броня
    "leather_armor": {
        "name": "Кожаная броня", "item_type": "armor",
        "description": "Простая защита из кожи.",
        "weight": 4.0, "value": 20, "rarity": COMMON, "defense_bonus": 2, "req_level": 1,
    },
    "padded_armor": {
        "name": "Стёганая броня", "item_type": "armor",
        "description": "Мягкая, но полезная защита.",
        "weight": 5.0, "value": 35, "rarity": COMMON, "defense_bonus": 3, "req_level": 2,
    },
    "chainmail": {
        "name": "Кольчуга", "item_type": "armor",
        "description": "Проверенная защита наёмников.",
        "weight": 8.0, "value": 85, "rarity": UNCOMMON, "defense_bonus": 5, "req_level": 3,
    },
    "steel_plate": {
        "name": "Стальная броня", "item_type": "armor",
        "description": "Тяжёлые стальные пластины.",
        "weight": 10.0, "value": 170, "rarity": RARE, "defense_bonus": 7, "req_level": 5,
    },
    "rune_plate": {
        "name": "Рунная броня", "item_type": "armor",
        "description": "Броня, усиленная древними рунами.",
        "weight": 10.0, "value": 300, "rarity": EPIC, "defense_bonus": 9, "req_level": 7,
    },
    "wraith_mail": {
        "name": "Кольчуга призраков", "item_type": "armor",
        "description": "Холодное плетение, почти невесомое.",
        "weight": 6.0, "value": 400, "rarity": EPIC, "defense_bonus": 12, "req_level": 9,
    },
    "void_plate": {
        "name": "Плиты Пустоты", "item_type": "armor",
        "description": "Доспех, сотканный из отсутствия света.",
        "weight": 9.0, "value": 780, "rarity": LEGENDARY, "defense_bonus": 15, "req_level": 11, "enchant": "stone",
    },
    "dusk_mantle": {
        "name": "Плащ сумрака", "item_type": "armor",
        "description": "Плащ, который любит тишину.",
        "weight": 3.0, "value": 340, "rarity": EPIC, "defense_bonus": 10, "req_level": 8, "enchant": "swift",
    },

    # Шлемы
    "leather_cap": {
        "name": "Кожаный шлем", "item_type": "helmet",
        "description": "Лёгкая защита головы.",
        "weight": 1.0, "value": 10, "rarity": COMMON, "defense_bonus": 1, "req_level": 1,
    },
    "iron_helm": {
        "name": "Железный шлем", "item_type": "helmet",
        "description": "Простой железный шлем.",
        "weight": 2.0, "value": 30, "rarity": COMMON, "defense_bonus": 2, "req_level": 2,
    },
    "steel_helm": {
        "name": "Стальной шлем", "item_type": "helmet",
        "description": "Крепкий шлем из хорошей стали.",
        "weight": 3.0, "value": 75, "rarity": RARE, "defense_bonus": 3, "req_level": 4,
    },
    "frost_crown": {
        "name": "Ледяная корона", "item_type": "helmet",
        "description": "Венец павших вьюг.",
        "weight": 1.5, "value": 260, "rarity": RARE,
        "defense_bonus": 5, "crit_bonus": 5, "req_level": 9, "enchant": "life",
    },

    # Ботинки
    "leather_boots": {
        "name": "Кожаные ботинки", "item_type": "boots",
        "description": "Удобная обувь для дороги.",
        "weight": 1.0, "value": 10, "rarity": COMMON, "defense_bonus": 1, "req_level": 1,
    },
    "iron_greaves": {
        "name": "Железные поножи", "item_type": "boots",
        "description": "Защита ног из железа.",
        "weight": 2.0, "value": 30, "rarity": COMMON, "defense_bonus": 2, "req_level": 2,
    },
    "wind_boots": {
        "name": "Ботинки ветра", "item_type": "boots",
        "description": "Лёгкие ботинки, помогающие в поиске.",
        "weight": 1.0, "value": 90, "rarity": RARE,
        "defense_bonus": 2, "loot_bonus": 5, "req_level": 4,
    },
    "ash_treads": {
        "name": "Пепельные поступи", "item_type": "boots",
        "description": "Не оставляют следа в пепле.",
        "weight": 1.5, "value": 230, "rarity": RARE,
        "defense_bonus": 4, "loot_bonus": 5, "req_level": 8, "enchant": "swift",
    },

    # Аксессуары
    "lucky_charm": {
        "name": "Счастливый амулет", "item_type": "accessory",
        "description": "Немного удачи в тёмном краю.",
        "weight": 0.2, "value": 45, "rarity": UNCOMMON,
        "crit_bonus": 5, "loot_bonus": 5, "req_level": 2,
    },
    "amulet_of_life": {
        "name": "Амулет жизни", "item_type": "accessory",
        "description": "Тёплый камень поддерживает тело.",
        "weight": 0.2, "value": 80, "rarity": RARE, "hp_bonus": 15, "req_level": 3,
    },
    "ring_of_power": {
        "name": "Кольцо силы", "item_type": "accessory",
        "description": "Кольцо, усиливающее удар.",
        "weight": 0.1, "value": 80, "rarity": RARE, "attack_bonus": 2, "req_level": 3,
    },
    "warding_talisman": {
        "name": "Обережный талисман", "item_type": "accessory",
        "description": "Талисман, отводящий часть ударов.",
        "weight": 0.2, "value": 80, "rarity": RARE, "defense_bonus": 2, "req_level": 3,
    },
    "shadow_amulet": {
        "name": "Теневой амулет", "item_type": "accessory",
        "description": "Амулет, шепчущий во тьме.",
        "weight": 0.2, "value": 220, "rarity": EPIC,
        "attack_bonus": 2, "crit_bonus": 5, "hp_bonus": 10, "req_level": 6,
    },
    "orb_of_dusk": {
        "name": "Сфера Сумерек", "item_type": "accessory",
        "description": "Стекло, в котором застыл закат мира.",
        "weight": 0.4, "value": 460, "rarity": EPIC,
        "attack_bonus": 3, "defense_bonus": 3, "hp_bonus": 20, "req_level": 10,
    },
    "sigil_ring": {
        "name": "Перстень Печати", "item_type": "accessory",
        "description": "Носит отпечаток Сердца Тьмы.",
        "weight": 0.1, "value": 900, "rarity": LEGENDARY,
        "attack_bonus": 4, "crit_bonus": 10, "hp_bonus": 25, "loot_bonus": 10, "req_level": 11,
    },
    "beacon_charm": {
        "name": "Амулет маяка", "item_type": "accessory",
        "description": "Тёплый свет старого маяка.",
        "weight": 0.2, "value": 180, "rarity": RARE,
        "hp_bonus": 10, "loot_bonus": 10, "req_level": 5,
    },
    "drowned_idol": {
        "name": "Идол утопленников", "item_type": "accessory",
        "description": "Слышит шёпот мёртвой воды.",
        "weight": 0.4, "value": 260, "rarity": EPIC,
        "attack_bonus": 3, "defense_bonus": 3, "crit_bonus": 5, "req_level": 8,
    },
    "spider_ring": {
        "name": "Паучье кольцо", "item_type": "accessory",
        "description": "Плетёное кольцо из шёлка.",
        "weight": 0.1, "value": 200, "rarity": RARE,
        "crit_bonus": 8, "loot_bonus": 5, "req_level": 6,
    },

    # Расходники
    "small_potion": {
        "name": "Малое зелье лечения", "item_type": "consumable",
        "description": "Восстанавливает 15 здоровья.",
        "weight": 0.3, "value": 12, "rarity": COMMON, "heal": 15,
    },
    "potion": {
        "name": "Зелье лечения", "item_type": "consumable",
        "description": "Восстанавливает 35 здоровья.",
        "weight": 0.4, "value": 28, "rarity": UNCOMMON, "heal": 35,
    },
    "big_potion": {
        "name": "Большое зелье лечения", "item_type": "consumable",
        "description": "Восстанавливает 70 здоровья.",
        "weight": 0.6, "value": 60, "rarity": RARE, "heal": 70,
    },
    "greater_potion": {
        "name": "Великое зелье лечения", "item_type": "consumable",
        "description": "Восстанавливает 120 здоровья.",
        "weight": 0.7, "value": 110, "rarity": EPIC, "heal": 120,
    },
    "strength_elixir": {
        "name": "Эликсир силы", "item_type": "consumable",
        "description": "Повышает атаку на 3 на 3 хода боя.",
        "weight": 0.3, "value": 45, "rarity": UNCOMMON,
        "buff_stat": "attack", "buff_amount": 3, "buff_duration": 3,
    },
    "shield_elixir": {
        "name": "Эликсир щита", "item_type": "consumable",
        "description": "Повышает защиту на 3 на 3 хода боя.",
        "weight": 0.3, "value": 45, "rarity": UNCOMMON,
        "buff_stat": "defense", "buff_amount": 3, "buff_duration": 3,
    },
    "shadow_elixir": {
        "name": "Эликсир Тени", "item_type": "consumable",
        "description": "Повышает атаку на 5 на 4 хода боя.",
        "weight": 0.3, "value": 140, "rarity": EPIC,
        "buff_stat": "attack", "buff_amount": 5, "buff_duration": 4,
    },
    "poison_vial": {
        "name": "Флакон яда", "item_type": "consumable",
        "description": "Накладывает яд на врага.",
        "weight": 0.3, "value": 55, "rarity": UNCOMMON,
        "apply_status": "poison", "status_target": "enemy", "status_duration": 3, "status_amount": 4,
    },
    "firebomb": {
        "name": "Огненная бомба", "item_type": "consumable",
        "description": "Поджигает врага.",
        "weight": 0.5, "value": 70, "rarity": RARE,
        "apply_status": "burn", "status_target": "enemy", "status_duration": 2, "status_amount": 6,
    },
    "frostbomb": {
        "name": "Ледяная бомба", "item_type": "consumable",
        "description": "Замедляет врага холодом.",
        "weight": 0.5, "value": 70, "rarity": RARE,
        "apply_status": "chill", "status_target": "enemy", "status_duration": 2, "status_amount": 0,
    },
    "holy_water": {
        "name": "Святая вода", "item_type": "consumable",
        "description": "Лечит и благословляет.",
        "weight": 0.3, "value": 90, "rarity": RARE,
        "heal": 25, "apply_status": "bless", "status_target": "self", "status_duration": 3, "status_amount": 0,
    },
    "curse_scroll": {
        "name": "Свиток проклятия", "item_type": "consumable",
        "description": "Проклинает врага.",
        "weight": 0.1, "value": 80, "rarity": RARE,
        "apply_status": "curse", "status_target": "enemy", "status_duration": 3, "status_amount": 0,
    },

    # Материалы
    "scrap_metal": {
        "name": "Металлический лом", "item_type": "material",
        "description": "Куски металла для кузнеца.",
        "weight": 1.0, "value": 6, "rarity": COMMON,
    },
    "ancient_fragment": {
        "name": "Древний фрагмент", "item_type": "material",
        "description": "Обломок с рунами.",
        "weight": 1.0, "value": 15, "rarity": UNCOMMON,
    },
    "monster_fang": {
        "name": "Клык чудовища", "item_type": "material",
        "description": "Трофей с охоты.",
        "weight": 0.2, "value": 4, "rarity": COMMON,
    },
    "gem": {
        "name": "Самоцвет", "item_type": "material",
        "description": "Чистый камень, ценный у торговцев.",
        "weight": 0.1, "value": 35, "rarity": RARE,
    },
    "ash_heart": {
        "name": "Пепельное сердце", "item_type": "material",
        "description": "Ещё тёплое сердце порождения пустоши.",
        "weight": 0.5, "value": 30, "rarity": RARE,
    },
    "frost_shard": {
        "name": "Ледяной осколок", "item_type": "material",
        "description": "Осколок вечного льда.",
        "weight": 0.3, "value": 40, "rarity": RARE,
    },
    "dark_essence": {
        "name": "Тёмная эссенция", "item_type": "material",
        "description": "Сгусток чистой тьмы.",
        "weight": 0.2, "value": 90, "rarity": EPIC,
    },

    # Квестовые предметы
    "healing_herb": {
        "name": "Лечебная трава", "item_type": "quest",
        "description": "Трава, нужная целительнице.",
        "weight": 0.1, "value": 0, "rarity": COMMON, "quest_item": True,
    },
    "clue": {
        "name": "Улика культа", "item_type": "quest",
        "description": "Обрывок ткани со странным знаком.",
        "weight": 0.1, "value": 0, "rarity": COMMON, "quest_item": True,
    },
    "rusty_key": {
        "name": "Ржавый ключ", "item_type": "quest",
        "description": "Ключ из лагеря разбойников.",
        "weight": 0.1, "value": 0, "rarity": COMMON, "quest_item": True,
    },
    "black_sigil": {
        "name": "Чёрная печать", "item_type": "quest",
        "description": "Печать, открывающая путь к Цитадели.",
        "weight": 0.2, "value": 0, "rarity": UNCOMMON, "quest_item": True,
    },
    "family_medallion": {
        "name": "Семейный медальон", "item_type": "quest",
        "description": "Медальон, который ищет Дарен.",
        "weight": 0.2, "value": 0, "rarity": COMMON, "quest_item": True,
    },
    "letter": {
        "name": "Запечатанное письмо", "item_type": "quest",
        "description": "Письмо для старого шахтёра.",
        "weight": 0.1, "value": 0, "rarity": COMMON, "quest_item": True,
    },
    "archive_seal": {
        "name": "Печать Архива", "item_type": "quest",
        "description": "Печать, снятая с Хранителя Архива.",
        "weight": 0.2, "value": 0, "rarity": RARE, "quest_item": True,
    },
    "lost_relic": {
        "name": "Реликвия Склепа", "item_type": "quest",
        "description": "Древний артефакт, забытый в темноте.",
        "weight": 0.5, "value": 0, "rarity": EPIC, "quest_item": True,
    },
}

# =====================================================================
# Враги
# =====================================================================

ENEMY_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "hungry_wolf": {
        "name": "Голодный волк", "desc": "Тощий зверь с горящими глазами.",
        "level": 1, "max_hp": 24, "attack": 6, "defense": 1, "xp": 16,
        "gold_min": 0, "gold_max": 6, "loot_type": "beast", "side": "wild",
    },
    "bandit_thug": {
        "name": "Разбойник-головорез", "desc": "Грубый бандит с дубиной.",
        "level": 2, "max_hp": 36, "attack": 8, "defense": 2, "xp": 24,
        "gold_min": 8, "gold_max": 18, "loot_type": "bandit", "side": "dark",
    },
    "forest_wolf": {
        "name": "Лесной волк", "desc": "Крупный хищник заброшенного леса.",
        "level": 2, "max_hp": 34, "attack": 9, "defense": 2, "xp": 26,
        "gold_min": 0, "gold_max": 10, "loot_type": "beast", "side": "wild",
    },
    "giant_spider": {
        "name": "Гигантский паук", "desc": "Тварь из тёмной чащи.",
        "level": 3, "max_hp": 44, "attack": 11, "defense": 3, "xp": 34,
        "gold_min": 2, "gold_max": 14, "loot_type": "beast", "side": "wild",
    },
    "bandit_scout": {
        "name": "Разбойник-разведчик", "desc": "Быстрый и осторожный бандит.",
        "level": 3, "max_hp": 42, "attack": 12, "defense": 3, "xp": 36,
        "gold_min": 10, "gold_max": 24, "loot_type": "bandit", "side": "dark",
    },
    "bandit_raider": {
        "name": "Разбойник-налётчик", "desc": "Опытный боец лагеря.",
        "level": 4, "max_hp": 56, "attack": 14, "defense": 4, "xp": 48,
        "gold_min": 15, "gold_max": 35, "loot_type": "bandit", "side": "dark",
    },
    "bandit_archer": {
        "name": "Разбойник-лучник", "desc": "Стреляет без предупреждения.",
        "level": 4, "max_hp": 50, "attack": 16, "defense": 3, "xp": 50,
        "gold_min": 15, "gold_max": 38, "loot_type": "bandit", "side": "dark",
    },
    "ataman": {
        "name": "Атаман разбойников", "desc": "Главарь лагеря. У него есть ключ от древних дверей.",
        "level": 5, "max_hp": 105, "attack": 18, "defense": 6, "xp": 110,
        "gold_min": 70, "gold_max": 120, "loot_type": "bandit", "side": "dark",
        "is_boss": True, "no_flee": True,
    },
    "giant_rat": {
        "name": "Гигантская крыса", "desc": "Тварь из старых штреков.",
        "level": 3, "max_hp": 40, "attack": 10, "defense": 2, "xp": 30,
        "gold_min": 2, "gold_max": 12, "loot_type": "beast", "side": "wild",
    },
    "mine_ghoul": {
        "name": "Шахтный упырь", "desc": "Бледное существо, живущее во тьме шахты.",
        "level": 5, "max_hp": 70, "attack": 17, "defense": 6, "xp": 65,
        "gold_min": 12, "gold_max": 42, "loot_type": "undead", "side": "dark",
    },
    "zombie_miner": {
        "name": "Мёртвый шахтёр", "desc": "Тело, поднятое тёмной волей.",
        "level": 6, "max_hp": 82, "attack": 19, "defense": 7, "xp": 75,
        "gold_min": 14, "gold_max": 48, "loot_type": "undead", "side": "dark",
    },
    "cultist": {
        "name": "Культист", "desc": "Фанатик в чёрной мантии.",
        "level": 6, "max_hp": 78, "attack": 19, "defense": 7, "xp": 75,
        "gold_min": 20, "gold_max": 52, "loot_type": "cult", "side": "dark",
    },
    "zealot": {
        "name": "Фанатик культа", "desc": "Одержимый воин культа.",
        "level": 7, "max_hp": 95, "attack": 21, "defense": 8, "xp": 90,
        "gold_min": 28, "gold_max": 64, "loot_type": "cult", "side": "dark",
    },
    "skeleton_warrior": {
        "name": "Скелет-воин", "desc": "Древний страж руин.",
        "level": 7, "max_hp": 92, "attack": 22, "defense": 9, "xp": 95,
        "gold_min": 18, "gold_max": 58, "loot_type": "undead", "side": "dark",
    },
    "rune_golem": {
        "name": "Рунный голем", "desc": "Каменный страж, питаемый рунами.",
        "level": 8, "max_hp": 120, "attack": 25, "defense": 11, "xp": 120,
        "gold_min": 35, "gold_max": 80, "loot_type": "construct", "side": "dark",
    },
    "cult_emissary": {
        "name": "Культовый эмиссар", "desc": "Голос тьмы в древних руинах.",
        "level": 8, "max_hp": 165, "attack": 25, "defense": 10, "xp": 210,
        "gold_min": 90, "gold_max": 150, "loot_type": "cult", "side": "dark",
        "is_boss": True, "no_flee": True,
    },
    "shadow_guard": {
        "name": "Теневой страж", "desc": "Сгусток тьмы в доспехах.",
        "level": 9, "max_hp": 135, "attack": 28, "defense": 12, "xp": 145,
        "gold_min": 45, "gold_max": 100, "loot_type": "undead", "side": "dark",
    },
    "lord_morok": {
        "name": "Лорд Морок", "desc": "Тот, кто занял Цитадель Забвения.",
        "level": 10, "max_hp": 235, "attack": 30, "defense": 13, "xp": 420,
        "gold_min": 170, "gold_max": 280, "loot_type": "cult", "side": "dark",
        "is_boss": True, "no_flee": True,
    },

    # Вторая глава и новые зоны
    "ash_husk": {
        "name": "Пепельная оболочка", "desc": "Выжженная тварь, сохранившая лишь ярость.",
        "level": 8, "max_hp": 110, "attack": 24, "defense": 9, "xp": 110,
        "gold_min": 25, "gold_max": 60, "loot_type": "ash", "side": "wild",
    },
    "frost_wraith": {
        "name": "Ледяной призрак", "desc": "Стон вьюги, обретший форму.",
        "level": 9, "max_hp": 118, "attack": 27, "defense": 10, "xp": 125,
        "gold_min": 30, "gold_max": 70, "loot_type": "frost", "side": "wild",
    },
    "cult_adept": {
        "name": "Послушник культа", "desc": "Тот, кто уже отдал имя Забвению.",
        "level": 8, "max_hp": 105, "attack": 25, "defense": 9, "xp": 105,
        "gold_min": 30, "gold_max": 68, "loot_type": "cult", "side": "dark",
    },
    "archive_wraith": {
        "name": "Хранитель Архива", "desc": "Древний страж забытых знаний.",
        "level": 10, "max_hp": 200, "attack": 29, "defense": 13, "xp": 260,
        "gold_min": 100, "gold_max": 180, "loot_type": "archive", "side": "wild",
        "is_boss": True, "no_flee": True,
    },
    "heart_of_dark": {
        "name": "Сердце Тьмы", "desc": "Источник Забвения, бьющийся под Тронным Залом.",
        "level": 12, "max_hp": 340, "attack": 34, "defense": 16, "xp": 600,
        "gold_min": 260, "gold_max": 420, "loot_type": "archive", "side": "wild",
        "is_boss": True, "no_flee": True,
    },

    # Новые боссы и враги расширения
    "spider_queen": {
        "name": "Королева пауков", "desc": "Мать паутины, хозяйка гнезда.",
        "level": 8, "max_hp": 180, "attack": 24, "defense": 10, "xp": 220,
        "gold_min": 80, "gold_max": 140, "loot_type": "beast", "side": "wild",
        "is_boss": True, "no_flee": True,
    },
    "drowned_horror": {
        "name": "Утонувший ужас", "desc": "То, что поднимается из мёртвой воды.",
        "level": 9, "max_hp": 170, "attack": 27, "defense": 11, "xp": 240,
        "gold_min": 90, "gold_max": 160, "loot_type": "undead", "side": "wild",
        "is_boss": True, "no_flee": True,
    },
    "ice_tyrant": {
        "name": "Ледяной тиран", "desc": "Древний владыка перевала.",
        "level": 10, "max_hp": 230, "attack": 29, "defense": 14, "xp": 320,
        "gold_min": 120, "gold_max": 200, "loot_type": "frost", "side": "wild",
        "is_boss": True, "no_flee": True,
    },

    # Силы Света
    "village_militia": {
        "name": "Ополченец Сумеречного Брода", "desc": "Житель с вилами и горящими глазами.",
        "level": 6, "max_hp": 80, "attack": 18, "defense": 6, "xp": 70,
        "gold_min": 10, "gold_max": 30, "loot_type": "light", "side": "light",
    },
    "mercenary_blade": {
        "name": "Наёмный клинок Брана", "desc": "Торговец нанял защиту на случай худшего.",
        "level": 7, "max_hp": 95, "attack": 22, "defense": 8, "xp": 90,
        "gold_min": 20, "gold_max": 45, "loot_type": "light", "side": "light",
    },
    "dawn_knight": {
        "name": "Рыцарь Рассвета", "desc": "Воин ордена, пришедший истребить тьму.",
        "level": 9, "max_hp": 130, "attack": 27, "defense": 12, "xp": 140,
        "gold_min": 40, "gold_max": 90, "loot_type": "light", "side": "light",
    },
    "dawn_sentinel": {
        "name": "Светлый страж", "desc": "Существо чистого света, карающее предателей.",
        "level": 10, "max_hp": 165, "attack": 30, "defense": 14, "xp": 170,
        "gold_min": 55, "gold_max": 110, "loot_type": "light", "side": "light",
    },
}

# =====================================================================
# NPC
# =====================================================================

NPCS = {
    "elder": {
        "name": "Старейшина Гарольд", "kind": "elder", "side": "light",
        "aggressive": False, "hostile_enemy": "village_militia",
    },
    "merchant": {
        "name": "Торговец Бран", "kind": "merchant", "side": "light",
        "aggressive": True, "hostile_enemy": "mercenary_blade", "shop_key": "village",
    },
    "blacksmith": {
        "name": "Кузнец Торен", "kind": "blacksmith", "side": "light",
        "aggressive": True, "hostile_enemy": "village_militia",
    },
    "healer": {
        "name": "Целительница Мира", "kind": "healer", "side": "light",
        "aggressive": False, "hostile_enemy": "village_militia",
    },
    "villager": {
        "name": "Житель Дарен", "kind": "villager", "side": "light",
        "aggressive": False, "hostile_enemy": "village_militia",
    },
    "stranger": {
        "name": "Таинственный незнакомец", "kind": "stranger", "side": "neutral",
    },
    "miner": {
        "name": "Старый шахтёр", "kind": "miner", "side": "light",
        "aggressive": False, "hostile_enemy": "village_militia",
    },
    "warden": {
        "name": "Страж Разлома Илларион", "kind": "warden", "side": "neutral",
        "min_chapter": 2,
    },
    "smuggler": {
        "name": "Контрабандист Веш", "kind": "merchant", "side": "neutral",
        "min_chapter": 2, "shop_key": "port",
    },
    "alchemist": {
        "name": "Алхимик Селена", "kind": "alchemist", "side": "neutral",
        "min_chapter": 2,
    },
    "oracle": {
        "name": "Прорицательница Ним", "kind": "oracle", "side": "neutral",
        "min_chapter": 2,
    },
    "keeper": {
        "name": "Хранитель Света Аэон", "kind": "keeper", "side": "light",
        "aggressive": True, "hostile_enemy": "dawn_sentinel",
        "min_chapter": 2, "forbid_shadow": True,
    },
    "broker": {
        "name": "Серый посредник Кай", "kind": "merchant", "side": "neutral",
        "min_chapter": 2, "shop_key": "steppe",
    },
    "ally": {
        "name": "Атаман-соратник Гроз", "kind": "merchant", "side": "dark",
        "shop_key": "camp", "require_shadow": True,
    },
    "mentor": {
        "name": "Наставница культа Вейра", "kind": "merchant", "side": "dark",
        "shop_key": "cult", "require_shadow": True,
    },
    "chief": {
        "name": "Вождь Клык", "kind": "darkhealer", "side": "dark",
        "require_shadow": True,
    },
    "darksmith": {
        "name": "Оружейник Тьмы Морн", "kind": "blacksmith", "side": "dark",
        "require_shadow": True,
    },
    "herald": {
        "name": "Вестник Трона Азар", "kind": "herald", "side": "dark",
        "min_chapter": 2,
    },

    # Новые NPC расширения
    "lighthouse_keeper": {
        "name": "Смотритель маяка Элио", "kind": "lighthouse", "side": "neutral",
    },
    "black_dealer": {
        "name": "Теневой делец Моркан", "kind": "merchant", "side": "dark",
        "min_chapter": 2, "shop_key": "black_market",
    },
    "shard_spirit": {
        "name": "Дух Осколка", "kind": "spirit", "side": "light",
        "min_chapter": 2, "forbid_shadow": True,
    },
}

# =====================================================================
# Локации
# =====================================================================

LOCATIONS = {
    "village": {
        "name": "Деревня Сумеречный Брод", "short": "Деревня", "row": 0, "col": 0,
        "description": "Пограничная деревня у старой дороги. Здесь можно отдохнуть, торговать и получить вести.",
        "connections": ["trail"],
        "npcs": ["elder", "merchant", "blacksmith", "healer", "villager"],
        "enemies": [],
        "shadow_enemies": ["village_militia", "mercenary_blade"],
        "is_safe": True,
        "max_searches": 0,
    },
    "trail": {
        "name": "Тропа к руинам", "short": "Тропа", "row": 0, "col": 1,
        "description": "Разбитая тропа ведёт к лесу и старому лагерю. Здесь бродят волки и одинокие разбойники.",
        "connections": ["village", "forest", "camp"],
        "npcs": [],
        "enemies": ["hungry_wolf", "bandit_thug"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "forest": {
        "name": "Заброшенный лес", "short": "Лес", "row": 0, "col": 2,
        "description": "Тёмный лес с глухими тропами. Говорят, здесь пропадают люди и появляются странные знаки.",
        "connections": ["trail", "mine"],
        "npcs": [],
        "enemies": ["forest_wolf", "giant_spider", "bandit_scout"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 3,
    },
    "camp": {
        "name": "Разбойничий лагерь", "short": "Лагерь", "row": 1, "col": 1,
        "description": "Лагерь бандитов, устроенный на месте старого караула.",
        "connections": ["trail", "mine"],
        "npcs": ["ally"],
        "enemies": ["bandit_raider", "bandit_archer", "ataman"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "mine": {
        "name": "Старая шахта", "short": "Шахта", "row": 1, "col": 2,
        "description": "Сырые штреки, где когда-то добывали руду. Теперь здесь слышны шаги мёртвых.",
        "connections": ["forest", "camp", "cult", "web"],
        "npcs": ["miner", "chief"],
        "enemies": ["giant_rat", "mine_ghoul", "zombie_miner"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "web": {
        "name": "Паучье гнездо", "short": "Гнездо", "row": 1, "col": 3,
        "description": "Стены из паутины и тишина, в которой слышно, как кто-то дышит.",
        "connections": ["mine", "ruins"],
        "npcs": [],
        "enemies": ["giant_spider", "forest_wolf", "spider_queen"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "cult": {
        "name": "Культовая поляна", "short": "Поляна", "row": 2, "col": 2,
        "description": "Поляна с чёрными алтарями. Культисты собираются здесь перед входом в руины.",
        "connections": ["mine", "ruins"],
        "npcs": ["stranger", "mentor"],
        "enemies": ["cultist", "zealot"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "ruins": {
        "name": "Древние руины", "short": "Руины", "row": 2, "col": 3,
        "description": "Разрушенные залы древнего народа. Воздух здесь дрожит от забытой силы.",
        "connections": ["cult", "citadel", "web", "lighthouse"],
        "npcs": [],
        "enemies": ["skeleton_warrior", "rune_golem", "cult_emissary"],
        "shadow_enemies": ["dawn_knight"],
        "is_safe": False,
        "max_searches": 2,
    },
    "citadel": {
        "name": "Цитадель Забвения", "short": "Цитадель", "row": 2, "col": 4,
        "description": "Чёрная крепость над обрывом. Внутри ждёт источник тьмы.",
        "connections": ["ruins", "gate"],
        "npcs": [],
        "enemies": ["shadow_guard", "lord_morok"],
        "shadow_enemies": ["dawn_knight"],
        "is_safe": False,
        "max_searches": 2,
    },
    "gate": {
        "name": "Разлом", "short": "Разлом", "row": 3, "col": 4,
        "description": "Трещина в самом воздухе. Отсюда начинаются земли, которых нет на старых картах.",
        "connections": ["citadel", "pass", "lighthouse"],
        "npcs": ["warden"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "lighthouse": {
        "name": "Старый маяк", "short": "Маяк", "row": 3, "col": 3,
        "description": "Маяк на краю разлома. Его свет когда-то вёл путников, а теперь отгоняет тени.",
        "connections": ["ruins", "moor", "gate"],
        "npcs": ["lighthouse_keeper"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "pass": {
        "name": "Ледяной перевал", "short": "Перевал", "row": 4, "col": 4,
        "description": "Узкая тропа среди чёрного льда. Ветер приносит голоса погибших отрядов.",
        "connections": ["gate", "moor", "hall", "ice_palace"],
        "npcs": [],
        "enemies": ["frost_wraith"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "ice_palace": {
        "name": "Ледяной дворец", "short": "Дворец", "row": 4, "col": 5,
        "description": "Дворец из вечного льда. В его залах спит древний тиран.",
        "connections": ["pass"],
        "npcs": [],
        "enemies": ["frost_wraith", "ice_tyrant"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "moor": {
        "name": "Мёртвая пустошь", "short": "Пустошь", "row": 4, "col": 3,
        "description": "Бесконечное поле пепла, где когда-то стоял город.",
        "connections": ["pass", "port", "library", "lighthouse"],
        "npcs": [],
        "enemies": ["ash_husk"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 3,
    },
    "port": {
        "name": "Порт Пепла", "short": "Порт", "row": 4, "col": 2,
        "description": "Гавань беглецов и торговцев. Здесь не спрашивают, откуда ты пришёл.",
        "connections": ["moor", "crypt", "graveyard"],
        "npcs": ["smuggler", "alchemist"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "graveyard": {
        "name": "Кладбище кораблей", "short": "Кладбище", "row": 4, "col": 1,
        "description": "Ржавые остовы кораблей и вода, которая не отражает небо.",
        "connections": ["port", "black_market"],
        "npcs": [],
        "enemies": ["skeleton_warrior", "drowned_horror"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "black_market": {
        "name": "Чёрный рынок", "short": "Рынок", "row": 5, "col": 1,
        "description": "Рынок, которого нет на картах. Здесь продают то, что нельзя называть.",
        "connections": ["graveyard", "crypt"],
        "npcs": ["black_dealer"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "crypt": {
        "name": "Культовый склеп", "short": "Склеп", "row": 5, "col": 2,
        "description": "Подземелье, заваленное гробницами и забытыми обетами.",
        "connections": ["port", "library", "steppe", "black_market"],
        "npcs": [],
        "enemies": ["cult_adept", "ash_husk"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 3,
    },
    "library": {
        "name": "Древняя библиотека", "short": "Архив", "row": 5, "col": 3,
        "description": "Бесконечные ряды пыли и знаний. Здесь хранится правда о Забвении.",
        "connections": ["moor", "crypt", "hall", "vale", "steppe"],
        "npcs": ["oracle"],
        "enemies": ["archive_wraith"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 2,
    },
    "hall": {
        "name": "Зал Тени", "short": "Зал", "row": 5, "col": 4,
        "description": "Цитадель тех, кто добровольно отдал себя Тьме. Здесь тихо и тепло, как в могиле.",
        "connections": ["pass", "library"],
        "npcs": ["herald", "darksmith"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "steppe": {
        "name": "Серые Степи", "short": "Степи", "row": 6, "col": 2,
        "description": "Выцветшие просторы между светом и тьмой. Здесь торгуют тем, о чём не говорят вслух.",
        "connections": ["crypt", "library", "vale"],
        "npcs": ["broker"],
        "enemies": ["ash_husk", "frost_wraith"],
        "shadow_enemies": ["dawn_knight"],
        "is_safe": False,
        "max_searches": 2,
    },
    "vale": {
        "name": "Долина Света", "short": "Долина", "row": 6, "col": 3,
        "description": "Единственное место, куда не проникло Забвение. Свет здесь можно потрогать рукой.",
        "connections": ["library", "steppe", "throne", "oskolki"],
        "npcs": ["keeper"],
        "enemies": [],
        "shadow_enemies": ["dawn_sentinel"],
        "is_safe": True,
        "max_searches": 0,
    },
    "oskolki": {
        "name": "Осколки Света", "short": "Осколки", "row": 6, "col": 4,
        "description": "Поле светящихся осколков, оставшихся после первой битвы с Забвением.",
        "connections": ["vale"],
        "npcs": ["shard_spirit"],
        "enemies": [],
        "shadow_enemies": [],
        "is_safe": True,
        "max_searches": 0,
    },
    "throne": {
        "name": "Тронный Зал", "short": "Трон", "row": 7, "col": 3,
        "description": "Сердце Забвения. Стены дышат, и пол медленно пульсирует, как живое.",
        "connections": ["vale"],
        "npcs": [],
        "enemies": ["heart_of_dark"],
        "shadow_enemies": [],
        "is_safe": False,
        "max_searches": 1,
    },
}

# =====================================================================
# Квесты
# =====================================================================

QUESTS = {
    "main_1": {
        "title": "Тень пропавшего лорда", "type": "основной",
        "objectives": "Поговорите со старейшиной в деревне.",
        "reward_xp": 15, "reward_gold": 10, "reward_item": None,
    },
    "main_2": {
        "title": "Следы в лесу", "type": "основной",
        "objectives": "Найдите улику в Заброшенном лесу и вернитесь к старейшине.",
        "reward_xp": 30, "reward_gold": 20, "reward_item": None,
    },
    "main_3": {
        "title": "Лагерь разбойников", "type": "основной",
        "objectives": "Победите атамана в Разбойничьем лагере и принесите ключ старейшине.",
        "reward_xp": 60, "reward_gold": 50, "reward_item": None,
    },
    "main_4": {
        "title": "Древние руины", "type": "основной",
        "objectives": "Исследуйте Древние руины, победите культового эмиссара и решите судьбу чёрной печати.",
        "reward_xp": 100, "reward_gold": 80, "reward_item": "amulet_of_life",
    },
    "main_5": {
        "title": "Цитадель Забвения", "type": "основной",
        "objectives": "Войдите в Цитадель Забвения, победите Лорда Морока и решите судьбу края.",
        "reward_xp": 250, "reward_gold": 200, "reward_item": None,
    },
    "main_6": {
        "title": "Разлом", "type": "основной",
        "objectives": "Найдите Стража Разлома и узнайте, что лежит за Цитаделью.",
        "reward_xp": 120, "reward_gold": 90, "reward_item": "ash_treads",
    },
    "main_7": {
        "title": "Хранитель Архива", "type": "основной",
        "objectives": "Победите Хранителя Архива в Древней библиотеке и доложите Прорицательнице.",
        "reward_xp": 220, "reward_gold": 150, "reward_item": "frost_crown",
    },
    "main_8": {
        "title": "Дар Тьмы", "type": "основной",
        "objectives": "Встретьтесь с Вестником Трона в Зале Тени и примите решение о даре.",
        "reward_xp": 200, "reward_gold": 120, "reward_item": None,
    },
    "main_9": {
        "title": "Сердце Тьмы", "type": "основной",
        "objectives": "Спуститесь в Тронный Зал и покончите с Сердцем Тьмы.",
        "reward_xp": 500, "reward_gold": 400, "reward_item": "sigil_ring",
    },

    "side_herbs": {
        "title": "Лечебные травы", "type": "побочный",
        "objectives": "Соберите 3 лечебные травы на тропе или в лесу и вернитесь к целительнице.",
        "reward_xp": 30, "reward_gold": 20, "reward_item": "potion",
    },
    "side_medallion": {
        "title": "Семейный медальон", "type": "побочный",
        "objectives": "Найдите семейный медальон Дарена в Заброшенном лесу.",
        "reward_xp": 30, "reward_gold": 30, "reward_item": None,
    },
    "side_mine": {
        "title": "Очистить шахту", "type": "побочный",
        "objectives": "Победите 3 шахтных упырей и вернитесь к старому шахтёру.",
        "reward_xp": 60, "reward_gold": 40, "reward_item": "big_potion",
    },
    "side_letter": {
        "title": "Письмо в шахту", "type": "побочный",
        "objectives": "Доставьте письмо Дарена старому шахтёру в Старой шахте.",
        "reward_xp": 20, "reward_gold": 20, "reward_item": None,
    },
    "side_alchemy": {
        "title": "Пепельные сердца", "type": "побочный",
        "objectives": "Принесите 3 пепельных сердца Алхимику Селене в Порт Пепла.",
        "reward_xp": 120, "reward_gold": 100, "reward_item": "greater_potion",
    },
    "side_bounty": {
        "title": "Охота за призраками", "type": "побочный",
        "objectives": "Уничтожьте 3 призрачных существа и доложите Прорицательнице Ним.",
        "reward_xp": 150, "reward_gold": 120, "reward_item": "orb_of_dusk",
    },
    "side_relic": {
        "title": "Реликвия Склепа", "type": "побочный",
        "objectives": "Найдите реликвию в Культовом склепе и принесите её Ним.",
        "reward_xp": 140, "reward_gold": 130, "reward_item": "wraith_mail",
    },
    "side_shadow_hunt": {
        "title": "Охота на Рассвет", "type": "побочный",
        "objectives": "Убейте 2 Рыцарей Рассвета и доложите Вестнику Азару.",
        "reward_xp": 180, "reward_gold": 160, "reward_item": "shadow_elixir",
    },

    # Новые квесты расширения
    "side_beacon": {
        "title": "Свет маяка", "type": "побочный",
        "objectives": "Принесите 2 ледяных осколка Смотрителю маяка Элио.",
        "reward_xp": 100, "reward_gold": 90, "reward_item": "beacon_charm",
    },
    "side_spider": {
        "title": "Королева пауков", "type": "побочный",
        "objectives": "Найдите Паучье гнездо и уничтожьте Королеву пауков.",
        "reward_xp": 160, "reward_gold": 120, "reward_item": "spider_ring",
    },
}

# =====================================================================
# Лут и магазины
# =====================================================================

ROLL_LOOT = {
    1: (25, [COMMON]),
    2: (35, [COMMON]),
    3: (50, [COMMON, UNCOMMON]),
    4: (65, [UNCOMMON, RARE]),
    5: (80, [RARE, EPIC]),
    6: (100, [EPIC, LEGENDARY]),
}

LOOT_CATEGORY_WEIGHTS = {
    "beast": {"material": 65, "consumable": 25, "weapon": 5, "armor": 5},
    "bandit": {
        "weapon": 30, "armor": 20, "helmet": 10, "boots": 10,
        "consumable": 20, "material": 10,
    },
    "undead": {
        "material": 35, "weapon": 20, "armor": 15, "accessory": 15, "consumable": 15,
    },
    "cult": {
        "consumable": 25, "material": 20, "weapon": 20, "armor": 15, "accessory": 20,
    },
    "construct": {"material": 60, "weapon": 15, "armor": 15, "accessory": 10},
    "ash": {"material": 45, "consumable": 20, "weapon": 15, "armor": 10, "accessory": 10},
    "frost": {"material": 40, "consumable": 20, "weapon": 20, "helmet": 10, "accessory": 10},
    "archive": {"material": 30, "accessory": 25, "weapon": 20, "armor": 15, "consumable": 10},
    "light": {"consumable": 30, "weapon": 20, "armor": 20, "accessory": 20, "material": 10},
    "default": {
        "weapon": 20, "armor": 20, "consumable": 25, "material": 25, "accessory": 10,
    },
}

SHOP_STARTER_STOCK = {
    "village": [
        ("small_potion", 3), ("potion", 2), ("leather_armor", 1), ("leather_cap", 1),
        ("leather_boots", 1), ("iron_sword", 1), ("lucky_charm", 1), ("scrap_metal", 3),
    ],
    "port": [
        ("potion", 3), ("big_potion", 1), ("strength_elixir", 1), ("shield_elixir", 1),
        ("ash_falchion", 1), ("scrap_metal", 2),
    ],
    "steppe": [
        ("big_potion", 2), ("gem", 1), ("frost_crown", 1), ("ash_treads", 1),
        ("dark_essence", 1),
    ],
    "camp": [
        ("iron_sword", 1), ("steel_sword", 1), ("chainmail", 1), ("scrap_metal", 3),
        ("small_potion", 2),
    ],
    "cult": [
        ("shadow_elixir", 1), ("greater_potion", 1), ("amulet_of_life", 1),
        ("shadow_amulet", 1), ("dark_essence", 1),
    ],
    "black_market": [
        ("shadow_elixir", 2), ("curse_scroll", 1), ("dusk_mantle", 1),
        ("spider_ring", 1), ("dark_essence", 2), ("greater_potion", 1),
    ],
}

# =====================================================================
# Предмет
# =====================================================================

@dataclass
class Item:
    iid: int
    template_id: str
    name: str
    item_type: str
    description: str
    weight: float
    value: int
    rarity: str
    attack_bonus: int = 0
    defense_bonus: int = 0
    hp_bonus: int = 0
    crit_bonus: int = 0
    loot_bonus: int = 0
    heal: int = 0
    buff_stat: str = ""
    buff_amount: int = 0
    buff_duration: int = 0
    upgrade: int = 0
    count: int = 1
    req_level: int = 1
    quest_item: bool = False
    apply_status: str = ""
    status_target: str = ""
    status_duration: int = 0
    status_amount: int = 0
    enchant: str = ""

    def display_name(self) -> str:
        if self.upgrade > 0:
            return f"{self.name} +{self.upgrade}"
        return self.name

    def attack_bonus_total(self) -> int:
        if self.item_type == "weapon":
            return self.attack_bonus + self.upgrade
        return self.attack_bonus

    def defense_bonus_total(self) -> int:
        if self.item_type in ("armor", "helmet", "boots"):
            return self.defense_bonus + self.upgrade
        return self.defense_bonus

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        required = {"iid", "template_id", "name", "item_type", "description", "weight", "value", "rarity"}
        if not required.issubset(data.keys()):
            raise ValueError("Повреждённый предмет в сохранении")
        if data.get("template_id") not in ITEM_TEMPLATES:
            raise ValueError("Неизвестный предмет в сохранении")

        field_names = {f.name for f in fields(cls)}
        clean = {k: v for k, v in data.items() if k in field_names}
        return cls(**clean)


def item_stats_text(item: Item) -> str:
    parts: List[str] = []

    if item.attack_bonus_total() > 0:
        parts.append(f"Атака +{item.attack_bonus_total()}")
    if item.defense_bonus_total() > 0:
        parts.append(f"Защита +{item.defense_bonus_total()}")
    if item.hp_bonus > 0:
        parts.append(f"Здоровье +{item.hp_bonus}")
    if item.crit_bonus > 0:
        parts.append(f"Крит +{item.crit_bonus}%")
    if item.loot_bonus > 0:
        parts.append(f"Поиск лута +{item.loot_bonus}%")
    if item.heal > 0:
        parts.append(f"Лечение +{item.heal}")
    if item.buff_stat and item.buff_amount > 0:
        stat_name = "Атака" if item.buff_stat == "attack" else "Защита"
        parts.append(f"{stat_name} +{item.buff_amount} на {item.buff_duration} х.")
    if item.req_level > 1:
        parts.append(f"Требуемый уровень: {item.req_level}")
    if item.enchant and item.enchant in ENCHANTS:
        parts.append(f"Зачарование: {ENCHANTS[item.enchant]['name']}")
    if item.apply_status:
        target = "на врага" if item.status_target == "enemy" else "на себя"
        parts.append(f"Накладывает {STATUS_NAMES.get(item.apply_status, item.apply_status)} {target}")

    return ", ".join(parts) if parts else "нет эффектов"


def format_item_line(item: Item) -> str:
    rarity_color = RARITY_COLORS.get(item.rarity, "white")
    name = colorize(item.display_name(), rarity_color, bold=item.rarity in (EPIC, LEGENDARY))
    rarity = colorize(item.rarity, rarity_color)

    return (
        f"{name} [{rarity}] x{item.count}, "
        f"тип: {TYPE_NAMES.get(item.item_type, item.item_type)}, "
        f"вес {item.weight * item.count:.1f}, цена {item.value}. "
        f"{item_stats_text(item)}"
    )


# =====================================================================
# Игрок
# =====================================================================

@dataclass
class Player:
    name: str
    char_class: str
    level: int = 1
    xp: int = 0
    xp_to_next: int = XP_BASE
    hp: int = 10
    base_max_hp: int = 10
    base_attack: int = 5
    base_defense: int = 0
    gold: int = 20
    max_weight: int = 30
    max_slots: int = 12
    crit_bonus: int = 0
    loot_bonus: int = 0
    dodge_bonus: int = 0
    faction: str = "light"
    chapter: int = 1
    ending: str = ""
    ending_act2: str = ""
    difficulty: str = "normal"
    perk_points: int = 0
    perks: List[str] = field(default_factory=list)
    reputations: Dict[str, int] = field(default_factory=lambda: {"light": 0, "shadow": 0, "neutral": 0})
    companion: str = ""
    achievements: List[str] = field(default_factory=list)
    status_effects: List[Dict[str, Any]] = field(default_factory=list)
    inventory: List[Item] = field(default_factory=list)
    equipment: Dict[str, Optional[Item]] = field(
        default_factory=lambda: {slot: None for slot in EQUIPMENT_SLOTS}
    )
    quest_flags: Dict[str, str] = field(default_factory=dict)
    quest_counters: Dict[str, int] = field(default_factory=dict)
    active_effects: List[Dict[str, Any]] = field(default_factory=list)

    def has_perk(self, perk_id: str) -> bool:
        return perk_id in self.perks

    @property
    def max_hp(self) -> int:
        bonus = 0

        for item in self.equipment.values():
            if item is not None:
                bonus += item.hp_bonus
                if item.enchant == "life":
                    bonus += 15

        return self.base_max_hp + bonus

    def total_attack(self) -> int:
        bonus = 0

        for item in self.equipment.values():
            if item is not None:
                bonus += item.attack_bonus_total()

        for eff in self.active_effects:
            if eff.get("stat") == "attack":
                bonus += eff.get("amount", 0)

        base = self.base_attack + bonus
        return int(base * status_attack_mult(self.status_effects))

    def total_defense(self) -> int:
        bonus = 0

        for item in self.equipment.values():
            if item is not None:
                bonus += item.defense_bonus_total()
                if item.enchant == "stone":
                    bonus += 3

        for eff in self.active_effects:
            if eff.get("stat") == "defense":
                bonus += eff.get("amount", 0)

        comp = COMPANIONS.get(self.companion)
        if comp:
            bonus += comp.get("defense", 0)

        base = self.base_defense + bonus
        return int(base * status_defense_mult(self.status_effects))

    def total_crit(self) -> int:
        bonus = self.crit_bonus

        for item in self.equipment.values():
            if item is not None:
                bonus += item.crit_bonus

        if self.has_perk("perk_precision"):
            bonus += 8

        comp = COMPANIONS.get(self.companion)
        if comp:
            bonus += comp.get("crit", 0)

        return bonus

    def total_loot(self) -> int:
        bonus = self.loot_bonus

        for item in self.equipment.values():
            if item is not None:
                bonus += item.loot_bonus

        if self.has_perk("perk_fortune"):
            bonus += 10

        return bonus

    def total_dodge(self) -> int:
        bonus = self.dodge_bonus

        for item in self.equipment.values():
            if item is not None and item.enchant == "swift":
                bonus += 5

        if self.has_perk("perk_evasion"):
            bonus += 8

        comp = COMPANIONS.get(self.companion)
        if comp:
            bonus += comp.get("dodge", 0)

        return bonus

    def total_weight(self) -> float:
        return sum(it.weight * it.count for it in self.inventory)

    def slots_used(self) -> int:
        return len(self.inventory)

    def is_stackable(self, item: Item) -> bool:
        return item.item_type in ("consumable", "material", "quest")

    def can_add_item(self, item: Item, count: int = 1) -> bool:
        if count <= 0:
            return False

        if self.total_weight() + item.weight * count > self.max_weight + 1e-6:
            return False

        if self.is_stackable(item):
            for inv_item in self.inventory:
                if inv_item.template_id == item.template_id:
                    return True

        return self.slots_used() < self.max_slots

    def add_item(self, item: Item, count: Optional[int] = None) -> tuple[bool, str]:
        if count is None:
            count = item.count
        if count <= 0:
            return False, "Некорректное количество предмета"

        add_weight = item.weight * count
        if self.total_weight() + add_weight > self.max_weight + 1e-6:
            return False, "Слишком большой вес"

        if self.is_stackable(item):
            for inv_item in self.inventory:
                if inv_item.template_id == item.template_id:
                    inv_item.count += count
                    return True, "Предмет добавлен в стек"

        if self.slots_used() >= self.max_slots:
            return False, "Недостаточно места"

        item.count = count
        self.inventory.append(item)
        return True, "Предмет добавлен"

    def get_item_by_iid(self, iid: int) -> Optional[Item]:
        for item in self.inventory:
            if item.iid == iid:
                return item
        return None

    def remove_item_by_iid(self, iid: int, count: int = 1) -> bool:
        item = self.get_item_by_iid(iid)
        if item is None:
            return False
        if count <= 0:
            return False

        if item.count > count:
            item.count -= count
        else:
            self.inventory.remove(item)
        return True

    def has_template(self, template_id: str) -> bool:
        return any(item.template_id == template_id for item in self.inventory)

    def count_template(self, template_id: str) -> int:
        return sum(item.count for item in self.inventory if item.template_id == template_id)

    def remove_template(self, template_id: str, count: int) -> bool:
        remaining = count

        for item in list(self.inventory):
            if item.template_id != template_id:
                continue

            take = min(remaining, item.count)
            self.remove_item_by_iid(item.iid, take)
            remaining -= take

            if remaining <= 0:
                return True

        return False

    def equip_item(self, iid: int) -> tuple[bool, str]:
        item = self.get_item_by_iid(iid)
        if item is None:
            return False, "Предмет не найден."

        if item.item_type not in EQUIPMENT_SLOTS:
            return False, "Этот предмет нельзя надеть."

        if item.quest_item:
            return False, "Квестовый предмет нельзя надеть."

        if self.level < item.req_level:
            return False, f"Требуется уровень {item.req_level}."

        slot = item.item_type
        self.inventory.remove(item)
        old = self.equipment.get(slot)

        if old is not None:
            if not self.can_add_item(old, 1):
                self.inventory.append(item)
                return False, "Недостаточно места или веса, чтобы снять старый предмет."
            self.inventory.append(old)

        self.equipment[slot] = item

        if self.hp > self.max_hp:
            self.hp = self.max_hp

        return True, f"{item.display_name()} надет."

    def unequip_slot(self, slot: str) -> tuple[bool, str]:
        item = self.equipment.get(slot)
        if item is None:
            return False, "Слот пуст."

        if not self.can_add_item(item, 1):
            return False, "Недостаточно места или веса, чтобы снять предмет."

        self.equipment[slot] = None
        ok, msg = self.add_item(item)

        if not ok:
            self.equipment[slot] = item
            return False, msg

        if self.hp > self.max_hp:
            self.hp = self.max_hp

        return True, f"{item.display_name()} снят."

    def use_consumable(self, iid: int) -> str:
        item = self.get_item_by_iid(iid)
        if item is None:
            return "Предмет не найден."

        if item.item_type != "consumable":
            return "Этот предмет нельзя использовать."

        if item.quest_item:
            return "Квестовый предмет нельзя использовать."

        messages: List[str] = []

        if item.heal > 0:
            if self.hp >= self.max_hp and not item.buff_stat and not item.apply_status:
                return "Здоровье уже полное."

            healed = min(self.max_hp - self.hp, item.heal)
            if self.has_perk("perk_alchemist") and item.heal > 0:
                healed = int(healed * 1.15)

            self.hp += healed
            messages.append(f"Восстановлено здоровья: {healed}.")

        if item.buff_stat:
            self.active_effects.append({
                "stat": item.buff_stat,
                "amount": item.buff_amount,
                "turns": item.buff_duration,
            })
            stat_name = "атака" if item.buff_stat == "attack" else "защита"
            messages.append(f"Повышена {stat_name} на {item.buff_amount} на {item.buff_duration} х. боя.")

        if item.apply_status and item.status_target != "enemy":
            duration = item.status_duration
            if self.has_perk("perk_status"):
                duration += 1

            add_status(self.status_effects, item.apply_status, item.status_amount, duration)
            messages.append(f"Получен эффект: {STATUS_NAMES.get(item.apply_status, item.apply_status)}.")

        self.remove_item_by_iid(iid, 1)
        return " ".join(messages) if messages else "Предмет использован."

    def gain_xp(self, amount: int) -> List[str]:
        messages: List[str] = []
        self.xp += amount

        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = XP_BASE + (self.level - 1) * XP_STEP
            self.perk_points += 1

            class_data = CLASS_DATA[self.char_class]

            added_hp = 8 + class_data["hp_gain"]
            added_attack = 2 + class_data["atk_gain"]
            added_defense = 1 + class_data["def_gain"]

            self.base_max_hp += added_hp
            self.base_attack += added_attack
            self.base_defense += added_defense
            self.max_weight += 2
            self.max_slots += 1

            if self.level % 3 == 0:
                self.hp = self.max_hp
            else:
                self.hp = min(self.max_hp, self.hp + int(round(added_hp * 0.3)))

            messages.append(
                f"Новый уровень: {self.level}! "
                f"Здоровье +{added_hp}, атака +{added_attack}, защита +{added_defense}, "
                f"вес +2, слоты +1, очко таланта +1."
            )

        return messages

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        field_names = {f.name for f in fields(cls)}
        clean: Dict[str, Any] = {}

        for key, value in data.items():
            if key in field_names and key not in ("inventory", "equipment"):
                clean[key] = value

        if "name" not in clean or "char_class" not in clean:
            raise ValueError("Повреждённое сохранение персонажа")

        inventory = [Item.from_dict(x) for x in data.get("inventory", [])]

        raw_equipment = data.get("equipment", {})
        equipment: Dict[str, Optional[Item]] = {}
        for slot in EQUIPMENT_SLOTS:
            raw_item = raw_equipment.get(slot)
            equipment[slot] = Item.from_dict(raw_item) if raw_item else None

        clean["inventory"] = inventory
        clean["equipment"] = equipment
        return cls(**clean)


# =====================================================================
# Враг
# =====================================================================

@dataclass
class Enemy:
    template_id: str
    name: str
    description: str
    level: int
    max_hp: int
    attack: int
    defense: int
    xp: int
    gold_min: int
    gold_max: int
    loot_type: str
    side: str = "wild"
    is_boss: bool = False
    no_flee: bool = False
    dodge: int = 0
    elite: str = ""
    statuses: List[Dict[str, Any]] = field(default_factory=list)
    hp: int = 0

    def __post_init__(self) -> None:
        if self.hp <= 0:
            self.hp = self.max_hp


# =====================================================================
# Игра
# =====================================================================

class Game:
    def __init__(
        self,
        player: Player,
        location_id: str = "village",
        last_safe: str = "village",
        next_iid: int = 1,
        location_state: Optional[Dict[str, Dict[str, Any]]] = None,
        shop_stocks: Optional[Dict[str, List[Item]]] = None,
        defeated_bosses: Optional[List[str]] = None,
        visited: Optional[List[str]] = None,
        main_finished: bool = False,
        shop_refresh_level: Optional[Dict[str, int]] = None,
    ) -> None:
        self.player = player
        self.location_id = location_id
        self.last_safe = last_safe
        self.next_iid = next_iid
        self.location_state = location_state if location_state is not None else {}
        self.shop_stocks = shop_stocks if shop_stocks is not None else {}
        self.defeated_bosses = defeated_bosses if defeated_bosses is not None else []
        self.visited = visited if visited is not None else ["village"]
        self.main_finished = main_finished
        self.shop_refresh_level = shop_refresh_level if shop_refresh_level is not None else {}
        self.dirty = False
        self.current_shop_side = "neutral"

        for lid, ldata in LOCATIONS.items():
            if lid not in self.location_state:
                self.location_state[lid] = {"searches_left": ldata["max_searches"], "camp_used": 0}

    # -----------------------------------------------------------------
    # Создание игры
    # -----------------------------------------------------------------

    @classmethod
    def new_game(cls, name: str, char_class: str, difficulty: str) -> "Game":
        class_data = CLASS_DATA[char_class]

        player = Player(
            name=name,
            char_class=char_class,
            hp=class_data["hp"],
            base_max_hp=class_data["hp"],
            base_attack=class_data["attack"],
            base_defense=class_data["defense"],
            crit_bonus=class_data["crit"],
            loot_bonus=class_data["loot"],
            dodge_bonus=class_data["dodge"],
            difficulty=difficulty,
            gold=25,
        )

        game = cls(player)

        for qid in QUESTS:
            player.quest_flags[qid] = "not_started"
        player.quest_flags["main_1"] = "active"

        weapon = game.make_item(class_data["weapon"])
        armor = game.make_item("leather_armor")
        player.equipment["weapon"] = weapon
        player.equipment["armor"] = armor

        game.add_template_to_inventory("small_potion", 2)
        game.init_shops()
        game.dirty = False
        return game

    # -----------------------------------------------------------------
    # Базовые методы
    # -----------------------------------------------------------------

    def make_item(self, template_id: str, count: int = 1, upgrade: int = 0) -> Item:
        template = ITEM_TEMPLATES[template_id]
        data = template.copy()
        data["iid"] = self.next_iid
        self.next_iid += 1
        data["template_id"] = template_id
        data["count"] = count
        data["upgrade"] = upgrade
        return Item(**data)

    def add_template_to_inventory(self, template_id: str, count: int = 1) -> bool:
        item = self.make_item(template_id, count)
        ok, msg = self.player.add_item(item)
        if not ok:
            print(msg, color="red")
        return ok

    def current_location(self) -> Dict[str, Any]:
        return LOCATIONS[self.location_id]

    def add_to_stock(self, stock: List[Item], item: Item) -> None:
        if item.item_type in ("consumable", "material", "quest"):
            for existing in stock:
                if existing.template_id == item.template_id and existing.item_type == item.item_type:
                    existing.count += item.count
                    return
        stock.append(item)

    def has_perk(self, perk_id: str) -> bool:
        return self.player.has_perk(perk_id)

    def unlock(self, achievement: str) -> None:
        if achievement not in self.player.achievements:
            self.player.achievements.append(achievement)
            print(f"Достижение получено: {achievement}!", color="lightyellow", bold=True)
            self.dirty = True

    # -----------------------------------------------------------------
    # Сохранение и загрузка
    # -----------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": SAVE_VERSION,
            "player": self.player.to_dict(),
            "location_id": self.location_id,
            "last_safe": self.last_safe,
            "next_iid": self.next_iid,
            "location_state": self.location_state,
            "shop_stocks": {
                key: [item.to_dict() for item in items]
                for key, items in self.shop_stocks.items()
            },
            "defeated_bosses": self.defeated_bosses,
            "visited": self.visited,
            "main_finished": self.main_finished,
            "shop_refresh_level": self.shop_refresh_level,
        }

    def save(self) -> bool:
        try:
            data = self.to_dict()
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.dirty = False
            return True
        except OSError:
            print("Не удалось сохранить игру.", color="red")
            return False

    @classmethod
    def load(cls) -> Optional["Game"]:
        try:
            if not os.path.exists(SAVE_FILE):
                return None

            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            version = data.get("version")
            if version not in (1, 2, SAVE_VERSION):
                return None

            player = Player.from_dict(data.get("player", {}))
            if player.char_class not in CLASS_DATA:
                return None

            location_id = data.get("location_id")
            if location_id not in LOCATIONS:
                return None

            if version == 1:
                if not player.ending:
                    player.ending = str(player.quest_flags.pop("ending", ""))
                if player.quest_flags.get("main_5") == "completed":
                    player.chapter = 2
                if player.ending == "shadow":
                    player.faction = "shadow"

            if version < 3:
                if player.perk_points == 0 and player.level > 1:
                    player.perk_points = player.level - 1

            for key in ("light", "shadow", "neutral"):
                player.reputations.setdefault(key, 0)

            if player.difficulty not in DIFFICULTIES:
                player.difficulty = "normal"

            last_safe = data.get("last_safe", "village")
            if last_safe not in LOCATIONS:
                last_safe = "village"

            raw_state = data.get("location_state", {})
            location_state: Dict[str, Dict[str, Any]] = {}
            for lid, ldata in LOCATIONS.items():
                raw = raw_state.get(lid, {})
                if not isinstance(raw, dict):
                    raw = {}

                try:
                    searches_left = int(raw.get("searches_left", ldata["max_searches"]))
                except (TypeError, ValueError):
                    searches_left = ldata["max_searches"]

                try:
                    camp_used = int(raw.get("camp_used", 0))
                except (TypeError, ValueError):
                    camp_used = 0

                location_state[lid] = {"searches_left": searches_left, "camp_used": camp_used}

            shop_stocks: Dict[str, List[Item]] = {}
            for key, items_raw in data.get("shop_stocks", {}).items():
                if not isinstance(items_raw, list):
                    continue

                items: List[Item] = []
                for item_raw in items_raw:
                    item = Item.from_dict(item_raw)
                    if item.count > 0:
                        items.append(item)

                shop_stocks[key] = items

            defeated_bosses = list(data.get("defeated_bosses", []))
            visited = list(data.get("visited", []))
            if location_id not in visited:
                visited.append(location_id)

            main_finished = bool(data.get("main_finished", False))

            raw_refresh = data.get("shop_refresh_level", 1)
            if isinstance(raw_refresh, dict):
                shop_refresh_level = {str(k): int(v) for k, v in raw_refresh.items()}
            else:
                shop_refresh_level = {key: int(raw_refresh) for key in SHOP_STARTER_STOCK}

            for qid in QUESTS:
                if qid not in player.quest_flags:
                    player.quest_flags[qid] = "not_started"

            if player.faction not in ("light", "balance", "shadow"):
                player.faction = "light"

            if player.chapter < 1:
                player.chapter = 1

            if player.hp <= 0:
                player.hp = 1
            if player.hp > player.max_hp:
                player.hp = player.max_hp

            game = cls(
                player=player,
                location_id=location_id,
                last_safe=last_safe,
                next_iid=int(data.get("next_iid", 1000)),
                location_state=location_state,
                shop_stocks=shop_stocks,
                defeated_bosses=defeated_bosses,
                visited=visited,
                main_finished=main_finished,
                shop_refresh_level=shop_refresh_level,
            )

            max_id = game.next_iid
            for item in player.inventory:
                max_id = max(max_id, item.iid + 1)
            for item in player.equipment.values():
                if item is not None:
                    max_id = max(max_id, item.iid + 1)
            for stock in game.shop_stocks.values():
                for item in stock:
                    max_id = max(max_id, item.iid + 1)

            game.next_iid = max_id
            game.init_missing_shops()
            game.dirty = False
            return game

        except Exception:
            return None

    # -----------------------------------------------------------------
    # Магазины и репутация
    # -----------------------------------------------------------------

    def init_shops(self) -> None:
        for key, starter in SHOP_STARTER_STOCK.items():
            stock: List[Item] = []
            for template_id, count in starter:
                item = self.make_item(template_id, count)
                self.add_to_stock(stock, item)

            self.shop_stocks[key] = stock
            self.shop_refresh_level[key] = 1

    def init_missing_shops(self) -> None:
        for key, starter in SHOP_STARTER_STOCK.items():
            if key not in self.shop_stocks:
                stock: List[Item] = []
                for template_id, count in starter:
                    item = self.make_item(template_id, count)
                    self.add_to_stock(stock, item)
                self.shop_stocks[key] = stock

            if key not in self.shop_refresh_level:
                self.shop_refresh_level[key] = 1

    def random_shop_item(self) -> str:
        allowed_rarities = [COMMON, UNCOMMON, RARE]

        if self.player.level >= 7:
            allowed_rarities.append(EPIC)

        if self.player.level >= 11:
            allowed_rarities.append(LEGENDARY)

        categories = ["weapon", "armor", "helmet", "boots", "accessory", "consumable", "material"]
        weights = [15, 15, 10, 10, 10, 30, 10]
        category = random.choices(categories, weights=weights, k=1)[0]

        candidates = [
            tid
            for tid, t in ITEM_TEMPLATES.items()
            if t["item_type"] == category
            and not t.get("quest_item", False)
            and t.get("req_level", 1) <= self.player.level + 2
            and t["rarity"] in allowed_rarities
        ]

        if not candidates:
            return "small_potion"

        return random.choice(candidates)

    def refresh_shop(self, key: str) -> None:
        self.init_missing_shops()

        stock = self.shop_stocks[key]
        current = self.shop_refresh_level.get(key, 1)

        if current < self.player.level:
            for _ in range(3):
                template_id = self.random_shop_item()
                item = self.make_item(template_id, 1)
                self.add_to_stock(stock, item)

            self.shop_refresh_level[key] = self.player.level
            self.dirty = True

        if len(stock) < 4:
            for tid in ["small_potion", "potion", "scrap_metal"]:
                item = self.make_item(tid, 1)
                self.add_to_stock(stock, item)

    def add_reputation(self, side: str, amount: int) -> None:
        if side not in self.player.reputations:
            return

        self.player.reputations[side] = max(-100, min(100, self.player.reputations[side] + amount))
        self.dirty = True

    def price_multiplier(self, side: str) -> float:
        rep = self.player.reputations.get(side, 0)

        if self.player.faction == side:
            rep += 20

        mult = 1.0 - rep / 500.0

        if self.has_perk("perk_barter"):
            mult -= 0.05

        return max(0.70, min(1.30, mult))

    def sell_multiplier(self, side: str) -> float:
        rep = self.player.reputations.get(side, 0)

        if self.player.faction == side:
            rep += 20

        mult = 0.5 * (1.0 + rep / 1000.0)

        if self.has_perk("perk_barter"):
            mult += 0.03

        return max(0.35, min(0.80, mult))

    def merchant_npc_id(self) -> Optional[str]:
        for nid in self.location_npcs(self.location_id):
            data = NPCS[nid]
            if data.get("kind") == "merchant" and not self.is_npc_hostile(nid):
                return nid
        return None

    def has_merchant_here(self) -> bool:
        return self.merchant_npc_id() is not None

    def merchant_side(self) -> str:
        npc_id = self.merchant_npc_id()
        if npc_id is None:
            return "neutral"
        return NPCS[npc_id].get("side", "neutral")

    # -----------------------------------------------------------------
    # Фракции и доступность
    # -----------------------------------------------------------------

    def is_shadow(self) -> bool:
        return self.player.faction == "shadow"

    def is_safe_location(self, location_id: str) -> bool:
        loc = LOCATIONS.get(location_id)
        if loc is None:
            return False

        if not loc.get("is_safe", False):
            return False

        if self.is_shadow() and location_id == "village":
            return False

        return True

    def safe_home(self) -> str:
        candidates: List[str] = []

        if self.player.chapter >= 2:
            candidates.append("gate")
            if self.is_shadow():
                candidates.append("hall")

        if not self.is_shadow():
            candidates.append("village")
        else:
            candidates.append("hall")

        candidates.append("village")

        for candidate in candidates:
            if candidate in LOCATIONS:
                return candidate

        return "village"

    def current_safe_home(self) -> str:
        if self.is_safe_location(self.last_safe):
            return self.last_safe
        return self.safe_home()

    def npc_available(self, npc_id: str) -> bool:
        data = NPCS.get(npc_id)
        if data is None:
            return False

        if data.get("require_shadow") and not self.is_shadow():
            return False

        if data.get("forbid_shadow") and self.is_shadow():
            return False

        if int(data.get("min_chapter", 1)) > self.player.chapter:
            return False

        return True

    def location_npcs(self, location_id: str) -> List[str]:
        result: List[str] = []

        for nid in LOCATIONS[location_id].get("npcs", []):
            if self.npc_available(nid):
                result.append(nid)

        return result

    def is_npc_hostile(self, npc_id: str) -> bool:
        if not self.is_shadow():
            return False

        return NPCS[npc_id].get("side") == "light"

    def location_enemies(self, location_id: str) -> List[str]:
        loc = LOCATIONS[location_id]
        pool: List[str] = list(loc.get("enemies", []))

        if self.is_shadow():
            pool += list(loc.get("shadow_enemies", []))
            pool = [e for e in pool if ENEMY_TEMPLATES[e].get("side", "wild") != "dark"]

        return pool

    # -----------------------------------------------------------------
    # Прогресс и масштабирование
    # -----------------------------------------------------------------

    def story_progress(self) -> int:
        stage = 0
        last = len([q for q in QUESTS if q.startswith("main_")])

        for i in range(1, last + 1):
            qid = f"main_{i}"
            status = self.player.quest_flags.get(qid, "not_started")

            if status == "completed":
                stage = i
            elif status in ("active", "ready_to_complete") and stage < i - 1:
                stage = i - 1

        return stage

    def spawn_enemy(self, template_id: str) -> Enemy:
        base = ENEMY_TEMPLATES[template_id]
        stage = self.story_progress()
        p_level = self.player.level
        diff = DIFFICULTIES.get(self.player.difficulty, DIFFICULTIES["normal"])

        level = max(base["level"], min(p_level, base["level"] + 8))
        raw_diff = max(0, level - base["level"])

        max_hp = int(base["max_hp"] + base["max_hp"] * 0.22 * raw_diff + 6 * raw_diff + stage * 5)
        attack = base["attack"] + 2 * raw_diff + max(0, stage - 1)
        defense = base["defense"] + raw_diff + stage // 2
        xp = base["xp"] + 10 * raw_diff + stage * 6
        gold_min = base["gold_min"] + 4 * raw_diff + stage * 3
        gold_max = base["gold_max"] + 8 * raw_diff + stage * 5

        if base.get("is_boss", False):
            max_hp = int(max_hp * 1.18)
            attack += 2
            defense += 1

        enemy_mult = diff["enemy"]
        max_hp = int(max_hp * enemy_mult)
        attack = int(attack * enemy_mult)
        defense = int(defense * (1.0 + (enemy_mult - 1.0) * 0.7))

        elite = ""
        dodge = 0

        if not base.get("is_boss", False):
            elite_chance = diff["elite"] + stage
            if random.randint(1, 100) <= elite_chance:
                elite = random.choice(list(ELITE_NAMES.keys()))

                if elite == "furious":
                    attack = int(attack * 1.25)
                elif elite == "armored":
                    defense = int(defense * 1.40)
                elif elite == "ghostly":
                    dodge = 15
                elif elite in ("vampiric", "toxic", "cursed"):
                    max_hp = int(max_hp * 1.10)

        enemy = Enemy(
            template_id=template_id,
            name=base["name"],
            description=base["desc"],
            level=level,
            max_hp=max_hp,
            attack=attack,
            defense=defense,
            xp=xp,
            gold_min=gold_min,
            gold_max=gold_max,
            loot_type=base["loot_type"],
            side=base.get("side", "wild"),
            is_boss=base.get("is_boss", False),
            no_flee=base.get("no_flee", False),
            dodge=dodge,
            elite=elite,
        )

        if elite:
            enemy.name = f"{ELITE_NAMES[elite]} {enemy.name}"

        return enemy

    # -----------------------------------------------------------------
    # Квесты
    # -----------------------------------------------------------------

    def quest_status(self, qid: str) -> str:
        return self.player.quest_flags.get(qid, "not_started")

    def set_quest(self, qid: str, status: str) -> None:
        if qid in QUESTS:
            self.player.quest_flags[qid] = status
            self.dirty = True

    def complete_quest(self, qid: str) -> None:
        if qid not in QUESTS:
            return

        status = self.player.quest_flags.get(qid, "not_started")
        if status == "completed":
            return
        if status not in ("active", "ready_to_complete"):
            return

        quest = QUESTS[qid]
        self.player.quest_flags[qid] = "completed"
        print(f"Квест завершён: {quest['title']}!", color="green", bold=True)

        xp = quest.get("reward_xp", 0)
        gold = quest.get("reward_gold", 0)
        reward_item = quest.get("reward_item")

        if xp > 0:
            messages = self.player.gain_xp(xp)
            print(f"Опыт +{xp}.", color="green")
            for msg in messages:
                print(msg, color="green")

        if gold > 0:
            self.player.gold += gold
            print(f"Золото +{gold}.", color="yellow")

        if reward_item:
            item = self.make_item(reward_item, 1)
            self.handle_loot([item])

        self.dirty = True

    # -----------------------------------------------------------------
    # Карта
    # -----------------------------------------------------------------

    def location_known(self, location_id: str) -> bool:
        if location_id in self.visited:
            return True

        for other in self.visited:
            if other in LOCATIONS and location_id in LOCATIONS[other]["connections"]:
                return True

        return False

    def map_cell(self, location_id: str) -> str:
        inner_width = MAP_CELL_WIDTH - 2

        if not self.location_known(location_id):
            return colorize("[" + "???".center(inner_width) + "]", "gray")

        short = LOCATIONS[location_id]["short"]
        text = f"*{short}*" if location_id == self.location_id else short
        plain = "[" + text.center(inner_width) + "]"

        if location_id == self.location_id:
            return colorize(plain, "lightgreen", True)

        if self.is_safe_location(location_id):
            return colorize(plain, "lightblue")

        return colorize(plain, "cyan")

    def show_map(self) -> None:
        grid: Dict[tuple, str] = {}

        for lid, ldata in LOCATIONS.items():
            grid[(ldata["row"], ldata["col"])] = lid

        max_row = max(r for r, _ in grid)
        max_col = max(c for _, c in grid)

        print("Карта мира:", color="lightblue", bold=True)

        for row in range(max_row + 1):
            line = ""

            for col in range(max_col + 1):
                lid = grid.get((row, col))
                line += self.map_cell(lid) if lid else " " * MAP_CELL_WIDTH

                if col < max_col:
                    left = grid.get((row, col))
                    right = grid.get((row, col + 1))

                    if left and right and right in LOCATIONS[left]["connections"]:
                        line += colorize("-" * MAP_GAP, "gray")
                    else:
                        line += " " * MAP_GAP

            _print(line)

            if row < max_row:
                conn = ""
                pad_left = (MAP_CELL_WIDTH - 1) // 2

                for col in range(max_col + 1):
                    top = grid.get((row, col))
                    bottom = grid.get((row + 1, col))

                    if top and bottom and bottom in LOCATIONS[top]["connections"]:
                        conn += " " * pad_left + colorize("|", "gray") + " " * (MAP_CELL_WIDTH - 1 - pad_left)
                    else:
                        conn += " " * MAP_CELL_WIDTH

                    if col < max_col:
                        conn += " " * MAP_GAP

                _print(conn)

        print("* - вы здесь. [???] - неизвестная территория.", color="gray")

    def show_location_screen(self) -> None:
        loc = self.current_location()

        print(colorize("=" * 60, "gray"))
        self.show_map()
        print(colorize("=" * 60, "gray"))

        print(f"Локация: {loc['name']}", color="lightcyan", bold=True)
        print(loc["description"])

        p = self.player

        print(
            f"Уровень: {p.level} | HP: {p.hp}/{p.max_hp} | Золото: {p.gold} | "
            f"Вес: {p.total_weight():.1f}/{p.max_weight} | Слоты: {p.slots_used()}/{p.max_slots}",
            color="white"
        )

        print(
            f"Глава: {p.chapter} | Фракция: {FACTION_NAMES.get(p.faction, p.faction)} | "
            f"Сложность: {DIFFICULTIES[p.difficulty]['name']}",
            color="lightmagenta"
        )

        print(
            "Репутация: "
            f"Свет {p.reputations.get('light', 0)}, "
            f"Тьма {p.reputations.get('shadow', 0)}, "
            f"Нейтралы {p.reputations.get('neutral', 0)}",
            color="cyan"
        )

        if p.companion:
            print(f"Спутник: {COMPANIONS[p.companion]['name']}", color="lightgreen")

        npcs = self.location_npcs(self.location_id)
        if npcs:
            print("NPC в локации:", color="lightyellow")
            for i, nid in enumerate(npcs, 1):
                marker = colorize(" [враждебен]", "lightred") if self.is_npc_hostile(nid) else ""
                print(f"{colorize(str(i) + '.', 'yellow')} {NPCS[nid]['name']}{marker}")
        else:
            print("NPC: нет", color="gray")

        if loc["connections"]:
            connections = ", ".join(LOCATIONS[c]["name"] for c in loc["connections"])
            print("Переходы: " + connections, color="lightblue")
        else:
            print("Переходы: нет", color="gray")

        enemies = self.location_enemies(self.location_id)
        if enemies:
            names = ", ".join(ENEMY_TEMPLATES[e]["name"] for e in enemies)
            print("Возможные враги: " + names, color="lightred")

        if self.is_shadow():
            dark_here = [
                e for e in LOCATIONS[self.location_id].get("enemies", [])
                if ENEMY_TEMPLATES[e].get("side") == "dark"
            ]
            if dark_here:
                names = ", ".join(ENEMY_TEMPLATES[e]["name"] for e in dark_here)
                print("Союзники Тьмы рядом (не атакуют): " + names, color="lightmagenta")

    # -----------------------------------------------------------------
    # Игровой цикл локации
    # -----------------------------------------------------------------

    def location_menu(self) -> None:
        while True:
            self.show_location_screen()

            options = [
                "Осмотреться",
                "Искать предметы",
                "Вступить в бой",
                "Разбить лагерь",
                "Перейти в другую локацию",
                "Говорить с NPC",
                "Инвентарь и снаряжение",
                "Таланты",
                "Журнал квестов",
                "Карта мира",
                "Сохранить игру",
                "Выход в главное меню",
            ]

            choice = choose_option(options, "Действия", allow_back=False)

            if choice == 1:
                print(self.current_location()["description"])
                pause()
            elif choice == 2:
                self.search_location()
                pause()
            elif choice == 3:
                self.fight_menu()
                pause()
            elif choice == 4:
                self.camp_menu()
                pause()
            elif choice == 5:
                self.move_menu()
            elif choice == 6:
                self.talk_menu()
                pause()
            elif choice == 7:
                self.inventory_menu()
            elif choice == 8:
                self.perks_menu()
            elif choice == 9:
                self.quest_journal()
                pause()
            elif choice == 10:
                self.show_map()
                pause()
            elif choice == 11:
                if self.save():
                    print("Игра сохранена.", color="green")
                pause()
            elif choice == 12:
                if ask_yes_no("Сохранить игру перед выходом?"):
                    self.save()
                    return

                if ask_yes_no("Выйти без сохранения? Прогресс после последнего сохранения будет потерян."):
                    return

    # -----------------------------------------------------------------
    # Перемещение и события
    # -----------------------------------------------------------------

    def can_enter(self, location_id: str) -> tuple[bool, str]:
        p = self.player

        if location_id == "ruins" and not p.has_template("rusty_key"):
            return False, "Вход в Древние руины запечатан. Нужен ключ."

        if location_id == "citadel":
            has_path = (
                p.has_template("black_sigil")
                or self.quest_status("main_5") in ("active", "ready_to_complete", "completed")
            )

            if not has_path:
                return False, "Врата Цитадели закрыты. Нужна чёрная печать или открытое финальное задание."

            if p.level < 6:
                return False, "Вы чувствуете, что ещё слишком слабы. Нужен уровень 6."

            if self.quest_status("main_5") not in ("active", "ready_to_complete", "completed"):
                return False, "Сначала поговорите со старейшиной о Цитадели."

        if location_id in (
            "gate", "pass", "moor", "port", "crypt", "library", "hall", "steppe", "vale",
            "graveyard", "black_market", "ice_palace", "oskolki"
        ):
            if p.chapter < 2:
                return False, "Путь дальше преграждает разлом. Сначала завершите историю Цитадели."

        if location_id == "web" and p.level < 4:
            return False, "Паучье гнездо смертельно опасно. Нужен уровень 4."

        if location_id == "lighthouse" and p.level < 5:
            return False, "Дорога к маяку заросла и опасна. Нужен уровень 5."

        if location_id == "graveyard" and p.level < 6:
            return False, "Кладбище кораблей дышит смертью. Нужен уровень 6."

        if location_id == "black_market" and p.level < 6:
            return False, "Чёрный рынок не открывается для слабых. Нужен уровень 6."

        if location_id == "ice_palace" and p.level < 8:
            return False, "Ледяной дворец не пустит слабых. Нужен уровень 8."

        if location_id == "oskolki":
            if p.level < 8:
                return False, "Осколки Света признают только сильных. Нужен уровень 8."

            if self.is_shadow():
                return False, "Свет Осколков отталкивает вас."

        if location_id == "vale" and self.is_shadow():
            return False, "Свет Долины отталкивает вас. Вы больше не желанны здесь."

        if location_id == "throne":
            if self.quest_status("main_9") not in ("active", "ready_to_complete", "completed"):
                return False, "Тронный Зал закрыт. Решите судьбу дара у Вестника Трона."

            if p.level < 10:
                return False, "Зал ощущает вашу слабость. Нужен уровень 10."

        return True, ""

    def move_to(self, location_id: str) -> None:
        self.location_id = location_id

        if self.is_safe_location(location_id):
            self.last_safe = location_id

        if location_id not in self.visited:
            self.visited.append(location_id)

        self.location_state[location_id]["searches_left"] = LOCATIONS[location_id]["max_searches"]
        self.location_state[location_id]["camp_used"] = 0
        self.dirty = True

        print(f"Вы прибыли: {LOCATIONS[location_id]['name']}.", color="lightcyan")

        self.on_location_arrive(location_id)
        self.travel_event()

    def on_location_arrive(self, location_id: str) -> None:
        if location_id == "gate" and self.quest_status("main_6") == "not_started":
            self.set_quest("main_6", "active")
            story("Воздух дрожит. Где-то впереди слышен голос Стража Разлома.", color="lightcyan")

    def random_local_enemy(self) -> Optional[str]:
        enemies = [
            e for e in self.location_enemies(self.location_id)
            if not ENEMY_TEMPLATES[e].get("is_boss", False)
        ]

        if not enemies:
            return None

        return random.choice(enemies)

    def travel_event(self) -> None:
        if self.is_safe_location(self.location_id):
            return

        roll = random.randint(1, 100)

        if roll <= 15:
            enemy_id = self.random_local_enemy()
            if enemy_id:
                print("В пути на вас нападают!", color="red", bold=True)
                self.start_combat(enemy_id)
        elif roll <= 30:
            gold = random.randint(3, 8) + self.player.level
            self.player.gold += gold
            print(f"Вы находите {gold} золотых на дороге.", color="yellow")
        elif roll <= 45:
            item = self.random_search_item()
            if item:
                print("Вы находите предмет у дороги.", color="green")
                self.handle_loot([item])
        elif roll <= 55:
            self.try_gain_companion(self.location_id)
        elif roll <= 65:
            loss = max(1, int(self.player.max_hp * 0.05))
            self.player.hp = max(1, self.player.hp - loss)
            print(f"Ловушка! Вы теряете {loss} здоровья.", color="red")
        else:
            return

    # -----------------------------------------------------------------
    # Лагерь, крафт, зачарование, таланты
    # -----------------------------------------------------------------

    def camp_menu(self) -> None:
        safe = self.is_safe_location(self.location_id)
        state = self.location_state[self.location_id]

        if not safe and state.get("camp_used", 0):
            print("Вы уже разбивали лагерь в этой локации.", color="yellow")
            return

        options = [
            "Отдохнуть (восстановить здоровье)",
            "Создать предмет",
            "Медитация (очистить эффекты)",
            "Вернуться",
        ]

        choice = choose_option(options, "Лагерь")

        if choice == 0 or choice == 4:
            return

        if not safe:
            state["camp_used"] = 1
            self.dirty = True

        if choice == 1:
            healed = int(self.player.max_hp * 0.35)
            self.player.hp = min(self.player.max_hp, self.player.hp + healed)
            self.player.status_effects.clear()
            print(f"Вы отдыхаете у костра. Восстановлено здоровья: {healed}.", color="lightgreen")

            if not safe and random.randint(1, 100) <= 25:
                enemy_id = self.random_local_enemy()
                if enemy_id:
                    print("Ваш лагерь атакуют!", color="red", bold=True)
                    self.start_combat(enemy_id)

        elif choice == 2:
            self.craft_menu()

            if not safe and random.randint(1, 100) <= 10:
                enemy_id = self.random_local_enemy()
                if enemy_id:
                    print("Запахи костра привлекли врагов!", color="red", bold=True)
                    self.start_combat(enemy_id)

        elif choice == 3:
            self.player.status_effects.clear()
            healed = int(self.player.max_hp * 0.10)
            self.player.hp = min(self.player.max_hp, self.player.hp + healed)
            print("Вы приводите мысли в порядок. Негативные эффекты сняты.", color="lightblue")

            if not safe and random.randint(1, 100) <= 15:
                enemy_id = self.random_local_enemy()
                if enemy_id:
                    print("Тишина оказалась обманчивой!", color="red", bold=True)
                    self.start_combat(enemy_id)

    def craft_menu(self) -> None:
        while True:
            options: List[str] = []
            keys: List[str] = []

            for recipe_id, recipe in CRAFT_RECIPES.items():
                result = ITEM_TEMPLATES[recipe["result"]]
                materials = ", ".join(
                    f"{ITEM_TEMPLATES[m]['name']} x{c}"
                    for m, c in recipe["materials"]
                )
                options.append(f"{result['name']}: {materials}")
                keys.append(recipe_id)

            choice = choose_option(options, "Создание предметов")
            if choice == 0:
                return

            recipe = CRAFT_RECIPES[keys[choice - 1]]

            enough = True
            for material_id, count in recipe["materials"]:
                if self.player.count_template(material_id) < count:
                    enough = False
                    break

            if not enough:
                print("Недостаточно материалов.", color="red")
                continue

            for material_id, count in recipe["materials"]:
                self.player.remove_template(material_id, count)

            result_count = 1
            result_template = ITEM_TEMPLATES[recipe["result"]]

            if self.has_perk("perk_alchemist") and result_template["item_type"] == "consumable":
                if random.randint(1, 100) <= 30:
                    result_count = 2
                    print("Талант Алхимик: создан дополнительный предмет!", color="lightgreen")

            item = self.make_item(recipe["result"], result_count)
            self.handle_loot([item])
            self.unlock("Первый крафт")
            self.dirty = True

    def enchant_menu(self) -> None:
        items: List[tuple] = []

        for item in self.player.inventory:
            if item.item_type in EQUIPMENT_SLOTS and not item.quest_item:
                items.append((item, "инвентарь"))

        for slot in EQUIPMENT_SLOTS:
            item = self.player.equipment.get(slot)
            if item is not None:
                items.append((item, SLOT_NAMES[slot].lower()))

        if not items:
            print("Нет снаряжения для зачарования.", color="gray")
            return

        options = [f"{item.display_name()} ({where})" for item, where in items]
        choice = choose_option(options, "Какой предмет зачаровать?")
        if choice == 0:
            return

        item = items[choice - 1][0]

        enchant_options: List[str] = []
        enchant_keys: List[str] = []

        for eid, data in ENCHANTS.items():
            if item.item_type in data["types"]:
                material_name = ITEM_TEMPLATES[data["material"]]["name"]
                enchant_options.append(
                    f"{data['name']}: {data['gold']} золота и {material_name} x{data['count']}"
                )
                enchant_keys.append(eid)

        if not enchant_options:
            print("Для этого предмета нет доступных зачарований.", color="gray")
            return

        choice = choose_option(enchant_options, "Выберите зачарование")
        if choice == 0:
            return

        enchant_id = enchant_keys[choice - 1]
        data = ENCHANTS[enchant_id]

        if self.player.gold < data["gold"]:
            print("Недостаточно золота.", color="red")
            return

        if self.player.count_template(data["material"]) < data["count"]:
            print("Недостаточно материалов.", color="red")
            return

        if item.enchant and not ask_yes_no("Предмет уже зачарован. Заменить зачарование?"):
            return

        self.player.gold -= data["gold"]
        self.player.remove_template(data["material"], data["count"])
        item.enchant = enchant_id
        self.unlock("Первое зачарование")
        self.dirty = True

        print(f"Предмет зачарован: {item.display_name()} ({data['name']}).", color="green")

    def perks_menu(self) -> None:
        while True:
            p = self.player
            print(f"Очки талантов: {p.perk_points}", color="lightcyan", bold=True)

            if p.perks:
                owned = ", ".join(PERKS[pid]["name"] for pid in p.perks if pid in PERKS)
                print("Изучено: " + owned, color="gray")

            if p.perk_points <= 0:
                print("Нет очков талантов. Получайте уровни, чтобы открывать таланты.", color="yellow")
                return

            available = [pid for pid in PERKS if pid not in p.perks]

            if not available:
                print("Все таланты изучены.", color="green")
                return

            options = [f"{PERKS[pid]['name']} - {PERKS[pid]['desc']}" for pid in available]
            choice = choose_option(options, "Таланты")
            if choice == 0:
                return

            pid = available[choice - 1]
            p.perks.append(pid)
            p.perk_points -= 1

            if pid == "perk_might":
                p.base_attack += 3
            elif pid == "perk_guard":
                p.base_defense += 3
            elif pid == "perk_vitality":
                p.base_max_hp += 25
                p.hp = min(p.max_hp, p.hp + 25)
            elif pid == "perk_dark":
                p.base_attack += 5
                p.base_max_hp = max(1, p.base_max_hp - 15)
                if p.hp > p.max_hp:
                    p.hp = p.max_hp
            elif pid == "perk_light":
                p.base_defense += 2
                p.base_max_hp += 10
                p.hp = min(p.max_hp, p.hp + 10)

            print(f"Талант изучен: {PERKS[pid]['name']}.", color="green")
            self.dirty = True

    # -----------------------------------------------------------------
    # Спутники
    # -----------------------------------------------------------------

    def try_gain_companion(self, location_id: str) -> bool:
        p = self.player

        if p.companion:
            return False

        companion = ""

        if location_id == "forest" and random.randint(1, 100) <= 15:
            companion = "wolf"
        elif location_id == "hall" and self.is_shadow() and random.randint(1, 100) <= 25:
            companion = "imp"
        elif location_id in ("vale", "oskolki") and not self.is_shadow() and random.randint(1, 100) <= 25:
            companion = "sprite"
        elif location_id == "web" and random.randint(1, 100) <= 8:
            companion = "wolf"

        if not companion:
            return False

        p.companion = companion
        print(f"К вам присоединяется спутник: {COMPANIONS[companion]['name']}!", color="lightgreen", bold=True)
        self.unlock("Первый спутник")
        self.dirty = True
        return True

    def companion_action(self, enemy: Enemy) -> None:
        p = self.player
        comp = COMPANIONS.get(p.companion)

        if not comp:
            return

        chance = comp["chance"]

        if self.has_perk("perk_companion"):
            chance += 5

        if random.randint(1, 100) > chance:
            return

        if comp["type"] == "attack":
            damage = 2 + p.level // 2
            enemy.hp -= damage
            print(f"{comp['name']} атакует и наносит {damage} урона.", color="lightgreen")
        elif comp["type"] == "curse":
            add_status(enemy.statuses, "curse", 0, 2)
            print(f"{comp['name']} проклинает врага.", color="lightmagenta")
        elif comp["type"] == "heal":
            healed = 3 + p.level // 3
            p.hp = min(p.max_hp, p.hp + healed)
            print(f"{comp['name']} лечит вас на {healed}.", color="lightgreen")

    # -----------------------------------------------------------------
    # Статусы
    # -----------------------------------------------------------------

    def process_statuses(self, status_list: List[Dict[str, Any]]) -> int:
        dot_damage = 0

        for status in status_list:
            if status.get("type") in ("poison", "burn"):
                dot_damage += status.get("amount", 0)

        for status in status_list:
            status["turns"] = status.get("turns", 0) - 1

        status_list[:] = [status for status in status_list if status.get("turns", 0) > 0]

        return dot_damage

    def apply_enemy_status(self, enemy: Enemy, status_type: str, amount: int, duration: int) -> None:
        if self.has_perk("perk_status"):
            duration += 1

        add_status(enemy.statuses, status_type, amount, duration)

    def apply_player_status(self, status_type: str, amount: int, duration: int) -> None:
        add_status(self.player.status_effects, status_type, amount, duration)
        print(f"Вы получаете эффект: {STATUS_NAMES.get(status_type, status_type)}.", color="lightred")

    def enemy_on_hit_status(self, enemy: Enemy) -> None:
        if enemy.elite == "toxic":
            self.apply_player_status("poison", 3, 3)

        if enemy.elite == "cursed":
            self.apply_player_status("curse", 0, 2)

        tid = enemy.template_id

        if tid in ("giant_spider", "spider_queen"):
            self.apply_player_status("poison", 3, 3)
        elif tid in ("frost_wraith", "ice_tyrant"):
            self.apply_player_status("chill", 0, 2)
        elif tid in ("cultist", "zealot", "cult_adept", "cult_emissary", "heart_of_dark"):
            self.apply_player_status("curse", 0, 2)
        elif tid in ("ash_husk", "lord_morok"):
            self.apply_player_status("burn", 4, 2)

    # -----------------------------------------------------------------
    # Бой
    # -----------------------------------------------------------------

    def render_combat_tables(self, enemy: Enemy) -> None:
        p = self.player

        player_effects: List[str] = []

        for eff in p.active_effects:
            stat_name = "атака" if eff.get("stat") == "attack" else "защита"
            player_effects.append(f"{stat_name}+{eff.get('amount', 0)}({eff.get('turns', 0)})")

        if p.status_effects:
            player_effects.append(status_text(p.status_effects))

        if p.companion:
            player_effects.append(f"спутник: {COMPANIONS[p.companion]['name']}")

        player_effect_text = ", ".join(player_effects) if player_effects else "нет"

        enemy_effects: List[str] = []

        if enemy.is_boss:
            enemy_effects.append("босс")

        if enemy.elite:
            enemy_effects.append(ELITE_NAMES.get(enemy.elite, enemy.elite).lower())

        if enemy.statuses:
            enemy_effects.append(status_text(enemy.statuses))

        enemy_effect_text = ", ".join(enemy_effects) if enemy_effects else "нет"

        enemy_attack = int(enemy.attack * status_attack_mult(enemy.statuses))

        if enemy.template_id in ("lord_morok", "heart_of_dark") and enemy.hp < enemy.max_hp * 0.3:
            enemy_attack += 3
            enemy_effects.append("ярость: урон +3")

        rows = [
            (f"{p.name} (ур. {p.level})", f"{enemy.name} (ур. {enemy.level})"),
            (f"HP: {p.hp}/{p.max_hp}", f"HP: {enemy.hp}/{enemy.max_hp}"),
            (f"Урон: {p.total_attack()}", f"Урон: {enemy_attack}"),
            (f"Защита: {p.total_defense()}", f"Защита: {int(enemy.defense * status_defense_mult(enemy.statuses))}"),
            (f"Эффекты: {player_effect_text[:20]}", f"Эффекты: {enemy_effect_text[:20]}"),
        ]

        width = 30
        _print(colorize("-" * 80, "gray"))

        for i, (left, right) in enumerate(rows):
            left = str(left)[:width].ljust(width)
            right = str(right)[:width].ljust(width)
            line = f"| {left} | VS | {right} |" if i == 0 else f"| {left} |    | {right} |"

            if i == 0:
                _print(colorize(line, "lightcyan", True))
            elif "HP" in left:
                _print(colorize(line, "lightgreen"))
            elif "Урон" in left:
                _print(colorize(line, "yellow"))
            elif "Защита" in left:
                _print(colorize(line, "blue"))
            else:
                _print(colorize(line, "white"))

        _print(colorize("-" * 80, "gray"))

    def is_enemy_available(self, enemy_id: str) -> bool:
        template = ENEMY_TEMPLATES[enemy_id]

        if template.get("is_boss", False) and enemy_id in self.defeated_bosses:
            return False

        q = self.player.quest_flags

        if enemy_id == "ataman":
            return q.get("main_3") in ("active", "ready_to_complete")

        if enemy_id == "cult_emissary":
            return q.get("main_4") in ("active", "ready_to_complete")

        if enemy_id == "lord_morok":
            return q.get("main_5") in ("active", "ready_to_complete")

        if enemy_id == "archive_wraith":
            return q.get("main_7") in ("active", "ready_to_complete")

        if enemy_id == "heart_of_dark":
            return q.get("main_9") in ("active", "ready_to_complete")

        if enemy_id == "spider_queen":
            return q.get("side_spider") in ("active", "ready_to_complete")

        return True

    def fight_menu(self) -> None:
        enemies = self.location_enemies(self.location_id)

        if not enemies:
            print("Здесь нет врагов.", color="gray")
            return

        available = [eid for eid in enemies if self.is_enemy_available(eid)]

        if not available:
            print("Здесь нет доступных противников.", color="gray")
            return

        options: List[str] = []

        for enemy_id in available:
            preview = self.spawn_enemy(enemy_id)
            options.append(f"{preview.name} (ур. {preview.level})")

        choice = choose_option(options, "Выберите противника")
        if choice == 0:
            return

        self.start_combat(available[choice - 1])

    def enemy_choose_action(self, enemy: Enemy) -> str:
        enemy_percent = enemy.hp / enemy.max_hp
        player_percent = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 0

        if enemy_percent < 0.25 and random.random() < 0.40:
            return "defend"

        if player_percent < 0.30 and random.random() < 0.70:
            return "attack"

        return "attack" if random.random() < 0.75 else "defend"

    def defense_value_with_roll(self, base_defense: int, roll: int) -> int:
        if roll <= 2:
            return base_defense

        if roll <= 4:
            bonus = base_defense * 1.0
        elif roll == 5:
            bonus = base_defense * 1.2
        else:
            bonus = base_defense * 1.5

        return int(round(base_defense + bonus))

    def calculate_player_damage(self, enemy: Enemy, player_roll: int, enemy_action: str, enemy_roll: int) -> int:
        if player_roll <= 2:
            print("Вы промахиваетесь.", color="yellow")
            return 0

        if enemy.dodge > 0 and random.randint(1, 100) <= enemy.dodge:
            print(f"{enemy.name} уклоняется от вашего удара.", color="yellow")
            return 0

        attack = self.player.total_attack()
        defense = int(enemy.defense * status_defense_mult(enemy.statuses))

        if enemy_action == "defend":
            if enemy_roll <= 2:
                print(f"{enemy.name} пытается защититься, но неудачно.", color="yellow")
            defense = self.defense_value_with_roll(defense, enemy_roll)

        base_damage = max(1, attack - defense)

        if player_roll <= 4:
            mult = 1.0
        elif player_roll == 5:
            mult = 1.2
        else:
            mult = 1.5

        damage = int(round(base_damage * mult))

        crit_chance = self.player.total_crit()
        if damage > 0 and random.randint(1, 100) <= crit_chance:
            damage = int(round(damage * 1.25))
            print("Критический эффект! Урон усилен.", color="lightyellow", bold=True)

        weapon = self.player.equipment.get("weapon")
        if weapon and weapon.enchant in ("fire", "frost", "venom", "shadow") and damage > 0:
            if random.randint(1, 100) <= 25:
                if weapon.enchant == "fire":
                    self.apply_enemy_status(enemy, "burn", 3 + self.player.level // 3, 2)
                    print("Оружие охватывает врага пламенем.", color="lightred")
                elif weapon.enchant == "frost":
                    self.apply_enemy_status(enemy, "chill", 0, 2)
                    print("Оружие сковывает врага холодом.", color="lightblue")
                elif weapon.enchant == "venom":
                    self.apply_enemy_status(enemy, "poison", 2 + self.player.level // 4, 3)
                    print("Яд проникает в рану врага.", color="lightgreen")
                elif weapon.enchant == "shadow":
                    self.apply_enemy_status(enemy, "curse", 0, 2)
                    print("Тень опутывает врага.", color="lightmagenta")

        print(f"Вы наносите {damage} урона.", color="lightgreen")
        return damage

    def calculate_enemy_damage(
        self,
        enemy: Enemy,
        enemy_roll: int,
        player_defending: bool,
        player_roll: Optional[int] = None,
    ) -> int:
        if enemy_roll <= 2:
            print(f"{enemy.name} промахивается.", color="green")
            return 0

        if random.randint(1, 100) <= self.player.total_dodge():
            print("Вы уклоняетесь от атаки!", color="green")
            return 0

        attack = int(enemy.attack * status_attack_mult(enemy.statuses))

        if enemy.template_id in ("lord_morok", "heart_of_dark") and enemy.hp < enemy.max_hp * 0.3:
            attack += 3

        defense = self.player.total_defense()

        if player_defending and player_roll is not None:
            if player_roll <= 2:
                print("Ваша защита проваливается: бонус защиты не применяется.", color="red")
            defense = self.defense_value_with_roll(defense, player_roll)

        base_damage = max(1, attack - defense)

        if enemy_roll <= 4:
            mult = 1.0
        elif enemy_roll == 5:
            mult = 1.2
        else:
            mult = 1.5

        damage = int(round(base_damage * mult))

        if enemy.elite == "vampiric" and damage > 0:
            healed = max(1, int(damage * 0.3))
            enemy.hp = min(enemy.max_hp, enemy.hp + healed)
            print(f"{enemy.name} выпивает вашу жизнь и восстанавливает {healed}.", color="lightred")

        if damage > 0:
            self.enemy_on_hit_status(enemy)

        print(f"{enemy.name} наносит вам {damage} урона.", color="lightred")
        return damage

    def tick_effects(self) -> None:
        new_effects: List[Dict[str, Any]] = []

        for eff in self.player.active_effects:
            eff["turns"] = eff.get("turns", 0) - 1
            if eff["turns"] > 0:
                new_effects.append(eff)

        self.player.active_effects = new_effects

    def use_combat_item(self, enemy: Enemy) -> bool:
        consumables = [
            it for it in self.player.inventory
            if it.item_type == "consumable" and not it.quest_item
        ]

        if not consumables:
            print("У вас нет расходников.", color="gray")
            return False

        options = [format_item_line(it) for it in consumables]
        choice = choose_option(options, "Использовать предмет")
        if choice == 0:
            return False

        item = consumables[choice - 1]

        if item.status_target == "enemy" and item.apply_status:
            self.apply_enemy_status(enemy, item.apply_status, item.status_amount, item.status_duration)
            self.player.remove_item_by_iid(item.iid, 1)
            print(f"{item.name} накладывается на врага.", color="lightcyan")
            self.dirty = True
            return True

        message = self.player.use_consumable(item.iid)
        print(message, color="lightgreen")
        self.dirty = True
        return True

    def start_combat(self, enemy_id: str) -> None:
        enemy = self.spawn_enemy(enemy_id)

        _print(colorize("=" * 60, "red", True))
        print(f"Бой! {enemy.name} (ур. {enemy.level})", color="red", bold=True)
        print(enemy.description)
        _print(colorize("=" * 60, "red", True))

        last_enemy_roll = 1

        while True:
            self.render_combat_tables(enemy)

            flee_label = "Попытка убежать" if not enemy.no_flee else "Побег невозможен"
            options = ["Атака", "Защита", "Использовать предмет", flee_label]
            choice = choose_option(options, "Ваш ход", allow_back=False)

            if choice == 1:
                action = "attack"
            elif choice == 2:
                action = "defend"
            elif choice == 3:
                if not self.use_combat_item(enemy):
                    continue
                action = "item"
            elif choice == 4:
                if enemy.no_flee:
                    print("Отсюда нельзя сбежать!", color="red")
                    continue

                roll = random.randint(1, 6)
                print(f"Проверка побега: d6 = {roll}", color="cyan")

                if roll >= 4:
                    print("Вы успешно сбежали из боя.", color="green")
                    self.player.active_effects.clear()
                    self.player.status_effects.clear()

                    home = self.current_safe_home()
                    self.location_id = home
                    self.last_safe = home
                    self.location_state[home]["searches_left"] = LOCATIONS[home]["max_searches"]
                    self.location_state[home]["camp_used"] = 0
                    self.dirty = True
                    return

                print("Побег не удался! Враг атакует.", color="red")

                enemy_roll = random.randint(1, 6)
                last_enemy_roll = enemy_roll
                print(f"{enemy.name} бросает d6: {enemy_roll}", color="yellow")

                self.player.hp -= self.calculate_enemy_damage(enemy, enemy_roll, False, None)

                if self.player.hp <= 0:
                    self.defeat(enemy)
                    return

                self.tick_effects()
                continue
            else:
                continue

            player_roll: Optional[int] = None

            if action in ("attack", "defend"):
                player_roll = random.randint(1, 6)
                action_name = "атака" if action == "attack" else "защита"
                print(f"Ваш бросок d6: {player_roll} ({action_name})", color="cyan")

            enemy_action = self.enemy_choose_action(enemy)
            enemy_roll = random.randint(1, 6)
            last_enemy_roll = enemy_roll
            enemy_action_name = "атака" if enemy_action == "attack" else "защита"
            print(f"{enemy.name} выбирает: {enemy_action_name}. Бросок d6: {enemy_roll}", color="yellow")

            if action == "attack":
                enemy.hp -= self.calculate_player_damage(enemy, player_roll, enemy_action, enemy_roll)

                if enemy.hp <= 0:
                    self.victory(enemy, last_enemy_roll)
                    return

                self.companion_action(enemy)

                if enemy.hp <= 0:
                    self.victory(enemy, last_enemy_roll)
                    return

            dot = self.process_statuses(enemy.statuses)
            if dot > 0:
                enemy.hp -= dot
                print(f"{enemy.name} страдает от эффектов и теряет {dot} здоровья.", color="yellow")

                if enemy.hp <= 0:
                    self.victory(enemy, last_enemy_roll)
                    return

            if enemy_action == "attack":
                self.player.hp -= self.calculate_enemy_damage(enemy, enemy_roll, action == "defend", player_roll)

                if self.player.hp <= 0:
                    self.defeat(enemy)
                    return
            else:
                print(f"{enemy.name} укрепляет оборону.", color="blue")

            dot = self.process_statuses(self.player.status_effects)
            if dot > 0:
                self.player.hp -= dot
                print(f"Эффекты наносят вам {dot} урона.", color="yellow")

                if self.player.hp <= 0:
                    self.defeat(enemy)
                    return

            self.tick_effects()

    # -----------------------------------------------------------------
    # Лут
    # -----------------------------------------------------------------

    def choose_rarity(self, allowed: List[str], roll: int) -> str:
        if roll == 6:
            legendary_exists = any(
                t["rarity"] == LEGENDARY
                and not t.get("quest_item", False)
                and t.get("req_level", 1) <= self.player.level + 2
                for t in ITEM_TEMPLATES.values()
            )

            if LEGENDARY in allowed and random.random() < 0.18 and legendary_exists:
                return LEGENDARY

            if EPIC in allowed:
                return EPIC

        rarities: List[str] = []
        weights: List[int] = []

        for rarity in allowed:
            if rarity in RARITY_WEIGHTS:
                rarities.append(rarity)
                weights.append(RARITY_WEIGHTS[rarity])

        if not rarities:
            return COMMON

        return random.choices(rarities, weights=weights, k=1)[0]

    def choose_loot_category(self, loot_type: str) -> str:
        table = LOOT_CATEGORY_WEIGHTS.get(loot_type, LOOT_CATEGORY_WEIGHTS["default"])
        categories = list(table.keys())
        weights = list(table.values())
        return random.choices(categories, weights=weights, k=1)[0]

    def item_candidates(self, category: Optional[str], rarity: str) -> List[str]:
        result: List[str] = []

        for tid, t in ITEM_TEMPLATES.items():
            if t.get("quest_item", False):
                continue

            if category is not None and t["item_type"] != category:
                continue

            if t["rarity"] != rarity:
                continue

            if t.get("req_level", 1) > self.player.level + 2:
                continue

            result.append(tid)

        return result

    def pick_item_template(self, category: str, rarity: str) -> str:
        candidates = self.item_candidates(category, rarity)

        if not candidates:
            candidates = self.item_candidates(None, rarity)

        if not candidates:
            order = [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY]
            index = order.index(rarity) if rarity in order else 0

            for r in reversed(order[: index + 1]):
                candidates = self.item_candidates(None, r)
                if candidates:
                    break

        if not candidates:
            return "scrap_metal"

        return random.choice(candidates)

    def generate_loot(self, enemy: Enemy, last_roll: int) -> List[Item]:
        items: List[Item] = []

        chance, allowed = ROLL_LOOT.get(last_roll, (25, [COMMON]))
        chance = min(100, chance + self.player.total_loot())

        if enemy.elite:
            chance = min(100, chance + 20)

        if random.randint(1, 100) > chance:
            return items

        if last_roll <= 2 and random.random() < 0.6:
            rarity = COMMON
            category = "material"
        else:
            rarity = self.choose_rarity(allowed, last_roll)
            category = self.choose_loot_category(enemy.loot_type)

        template_id = self.pick_item_template(category, rarity)
        items.append(self.make_item(template_id, 1))

        if last_roll >= 5 and random.random() < 25:
            extra = ["scrap_metal", "monster_fang", "ancient_fragment"]

            if self.player.chapter >= 2:
                extra += ["frost_shard", "ash_heart", "dark_essence"]

            items.append(self.make_item(random.choice(extra), 1))

        if enemy.elite and random.random() < 40:
            elite_extra = ["dark_essence", "gem", "ancient_fragment"]
            items.append(self.make_item(random.choice(elite_extra), 1))

        return items

    def add_special_drops(self, enemy: Enemy, loot: List[Item]) -> None:
        p = self.player

        if enemy.template_id == "ataman" and not p.has_template("rusty_key"):
            loot.insert(0, self.make_item("rusty_key"))

            if self.quest_status("main_3") == "active":
                self.set_quest("main_3", "ready_to_complete")

        if enemy.template_id == "lord_morok":
            loot.insert(0, self.make_item("gem"))

        if enemy.template_id == "archive_wraith" and not p.has_template("archive_seal"):
            loot.insert(0, self.make_item("archive_seal"))

        if enemy.template_id == "spider_queen" and not p.has_template("spider_fang"):
            loot.insert(0, self.make_item("spider_fang"))

        if enemy.template_id == "drowned_horror" and not p.has_template("drowned_idol"):
            loot.insert(0, self.make_item("drowned_idol"))

        if enemy.template_id == "ice_tyrant" and not p.has_template("frost_spear"):
            loot.insert(0, self.make_item("frost_spear"))

    def handle_loot(self, items: List[Item]) -> None:
        if not items:
            return

        print("Предметы:", color="lightcyan")
        for item in items:
            print(" - " + format_item_line(item))

        failed: List[tuple] = []

        for item in items:
            ok, msg = self.player.add_item(item)
            if not ok:
                failed.append((item, msg))

        while failed:
            print("Не удалось подобрать часть предметов:", color="red")
            for item, msg in failed:
                print(f" - {item.display_name()}: {msg}", color="red")

            has_quest = any(item.quest_item for item, _ in failed)
            options = ["Открыть инвентарь"]

            if not has_quest:
                options.append("Оставить предметы")

            choice = choose_option(options, "Освободите место и попробуйте снова", allow_back=False)

            if choice == 1:
                self.inventory_menu()

                new_failed: List[tuple] = []
                for item, old_msg in failed:
                    ok, msg = self.player.add_item(item)
                    if not ok:
                        new_failed.append((item, msg))

                failed = new_failed
            else:
                break

        if failed:
            print("Предметы остались на месте боя.", color="yellow")
        else:
            print("Все предметы добавлены в инвентарь.", color="green")

    # -----------------------------------------------------------------
    # Сюжетные развилки и концовки
    # -----------------------------------------------------------------

    def ataman_choice(self) -> None:
        if self.player.quest_flags.get("branch_ataman") in ("killed", "spared"):
            return

        say("Атаман", "Хр-х... ты сильнее, чем я думал...", "lightred")

        choice = choose_option(
            ["Добить атамана", "Пощадить атамана"],
            "Атаман повержен",
            allow_back=False,
        )

        if choice == 1:
            self.player.quest_flags["branch_ataman"] = "killed"
            self.add_reputation("light", 5)
            self.add_reputation("shadow", -5)
            print("Вы добиваете атамана. Его банда больше не поднимется.", color="red")
        else:
            self.player.quest_flags["branch_ataman"] = "spared"
            self.add_reputation("neutral", 5)
            say("Атаман", "Забирай ключ. Мы уйдём из этих мест. Долг платежом красен.", "lightred")

        self.dirty = True

    def emissary_choice(self) -> None:
        p = self.player

        if p.quest_flags.get("branch_sigil") in ("destroy", "power", "elder"):
            if self.quest_status("main_4") == "active":
                self.set_quest("main_4", "ready_to_complete")
            return

        story("С тела культового эмиссара вы снимаете чёрную печать.", color="lightmagenta")
        self.handle_loot([self.make_item("black_sigil")])

        choice = choose_option(
            [
                "Уничтожить печать (светлый путь)",
                "Впитать силу печати (тёмный путь)",
                "Отнести печать старейшине (путь долга)",
            ],
            "Судьба чёрной печати",
            allow_back=False,
        )

        if choice == 1:
            p.remove_template("black_sigil", 1)
            p.quest_flags["branch_sigil"] = "destroy"
            p.base_defense += 1
            self.add_reputation("light", 10)
            self.add_reputation("shadow", -10)
            print("Печать рассыпается пеплом. Свет укрепляет вашу защиту. Защита +1.", color="lightgreen")
        elif choice == 2:
            p.quest_flags["branch_sigil"] = "power"
            p.base_attack += 2
            self.add_reputation("shadow", 10)
            self.add_reputation("light", -10)
            print("Тёмная сила входит в вас. Атака +2.", color="lightmagenta")
        else:
            p.quest_flags["branch_sigil"] = "elder"
            self.add_reputation("light", 5)
            print("Вы решаете отнести печать старейшине.", color="cyan")

        if self.quest_status("main_4") in ("active", "not_started"):
            self.set_quest("main_4", "ready_to_complete")

        self.dirty = True

    def final_branch_scene(self) -> None:
        p = self.player
        sigil_branch = p.quest_flags.get("branch_sigil", "elder")
        ataman_branch = p.quest_flags.get("branch_ataman", "killed")

        _print(colorize("=" * 60, "lightyellow", True))
        story("Лорд Морок повержен, но сила Цитадели всё ещё пульсирует в зале.")
        story("Перед вами чёрный кристалл - источник тьмы Пограничного края.")

        choice = choose_option(
            [
                "Уничтожить источник тьмы (Концовка Рассвета)",
                "Запечатать Цитадель (Концовка Равновесия)",
                "Занять трон (Концовка Тени)",
            ],
            "Решите судьбу Пограничного края",
            allow_back=False,
        )

        if choice == 1:
            p.ending = "light"
            self.add_reputation("light", 20)
            self.add_reputation("shadow", -20)
            story("Вы разбиваете чёрный кристалл. Свет разливается по Цитадели.", color="lightgreen")

            if sigil_branch == "destroy":
                story("Уничтоженная печать заставляет тьму угаснуть без остатка.", color="lightgreen")
            elif sigil_branch == "power":
                story("Тёмная сила внутри вас сопротивляется, но вы очищаете её светом.", color="lightyellow")
            else:
                story("Печать, принесённая старейшине, помогает завершить очищение.", color="lightgreen")

            if ataman_branch == "spared":
                story("Пощажённые разбойники помогают деревне восстанавливать дороги.", color="lightgreen")

            story("Пограничный край свободен. Начинается рассвет.", color="lightgreen")

        elif choice == 2:
            p.ending = "seal"
            self.add_reputation("neutral", 20)
            story("Вы произносите древние слова и запечатываете Цитадель.", color="lightblue")

            if sigil_branch == "destroy":
                story("Без печати крепость спит глубже, но вечных печатей не бывает.", color="lightblue")
            elif sigil_branch == "power":
                story("Ваша тёмная сила делает печать крепче, но оставляет след в сердце.", color="lightblue")
            else:
                story("Старейшина поможет хранить секрет этого места.", color="lightblue")

            if ataman_branch == "spared":
                story("Бывшие разбойники становятся стражами запечатанных врат.", color="lightblue")

            story("Тьма не уничтожена, но скована.", color="lightblue")

        else:
            p.ending = "shadow"
            p.faction = "shadow"
            self.add_reputation("shadow", 25)
            self.add_reputation("light", -25)
            self.unlock("Властелин Тени")

            story("Вы садитесь на трон Морока. Сила Цитадели склоняется перед вами.", color="lightmagenta")

            if sigil_branch == "power":
                story("Печать, впитанная в руинах, делает вашу власть почти абсолютной.", color="lightmagenta")
            elif sigil_branch == "destroy":
                story("Печать уничтожена, но ваша воля заменяет её.", color="lightmagenta")
            else:
                story("Старейшина будет молиться за вас. Или бояться вас.", color="lightmagenta")

            story("Пограничный край получил нового повелителя.", color="lightmagenta")
            story("Жители деревни больше не встретят вас как гостя.", color="lightred")

        self.start_second_chapter()

        _print(colorize("=" * 60, "lightyellow", True))
        print("Первая глава завершена. Вы можете продолжать игру.", color="green", bold=True)
        pause()

    def start_second_chapter(self) -> None:
        self.player.chapter = 2
        self.main_finished = True

        if self.quest_status("main_6") == "not_started":
            self.set_quest("main_6", "active")

        if self.player.faction != "shadow" and self.player.ending == "shadow":
            self.player.faction = "shadow"

        self.unlock("Глава вторая: Разлом")

        story("За Цитаделью открывается Разлом - путь в земли, которых нет на картах.", color="lightcyan")
        story("Новая глава началась.", color="lightmagenta")

    def accept_dark_gift(self, accept: bool) -> None:
        p = self.player

        if accept:
            p.faction = "shadow"
            p.base_attack += 4
            p.base_max_hp += 15
            p.hp = p.max_hp
            self.add_reputation("shadow", 20)
            self.add_reputation("light", -20)
            self.unlock("Дар Тьмы")
            print("Тьма принимает вас. Атака +4, здоровье +15, раны закрыты.", color="lightmagenta")
            story("Нейтральные жители теперь видят в вас врага. Приспешники Тьмы склоняют голову.", color="lightred")
        else:
            if p.ending == "shadow":
                p.faction = "balance"
            else:
                p.faction = "light"

            p.base_defense += 3
            p.base_max_hp += 10
            p.hp = p.max_hp
            self.add_reputation("light", 15)
            self.add_reputation("shadow", -15)
            print("Вы отвергли дар. Защита +3, здоровье +10, раны закрыты.", color="lightgreen")
            story("Вы остались тем, кто борется со тьмой, а не служит ей.", color="lightgreen")

        if self.quest_status("main_8") in ("active", "ready_to_complete"):
            self.complete_quest("main_8")

        self.set_quest("main_9", "active")
        story("Тронный Зал открыт. Сердце Тьмы ждёт.", color="lightred")
        self.dirty = True

    def final_act2_scene(self) -> None:
        p = self.player

        _print(colorize("=" * 60, "lightmagenta", True))
        story("Сердце Тьмы замедляется. Весь Разлом затихает в ожидании.")

        if p.faction == "shadow":
            options = [
                "Поглотить Сердце и стать Владыкой Забвения",
                "Разрушить Сердце изнутри и искупить выбор",
            ]
        else:
            options = [
                "Запечатать Сердце навсегда",
                "Принять Тьму окончательно и занять её трон",
            ]

        choice = choose_option(options, "Последний выбор", allow_back=False)

        if p.faction == "shadow":
            if choice == 1:
                p.ending_act2 = "dark_lord"
                p.base_attack += 5
                self.unlock("Владыка Забвения")
                story("Сердце растворяется в вас. Теперь Забвение смотрит вашими глазами.", color="lightmagenta")
                story("Мир получил бога тьмы. Мир этого не переживёт.", color="lightred")
            else:
                p.ending_act2 = "redemption"
                p.base_defense += 3
                self.unlock("Искупление")
                story("Вы разрываете Сердце изнутри, разрывая и собственную тьму.", color="lightgreen")
                story("Искупление возможно даже для того, кто выбрал Тьму.", color="lightgreen")
        else:
            if choice == 1:
                p.ending_act2 = "sealed_forever"
                p.base_max_hp += 10
                self.unlock("Вечная печать")
                story("Печать ложится на Сердце. Впервые за века Забвение молчит.", color="lightblue")
                story("Вы остались тем, кто держит границу. Граница держит вас.", color="lightcyan")
            else:
                p.ending_act2 = "consumed"
                p.faction = "shadow"
                p.base_attack += 6
                self.unlock("Поглощённый Тьмой")
                story("Вы принимаете Тьму полностью. Свет отступает из вашей груди.", color="lightmagenta")
                story("Трон занят. Новая эпоха началась.", color="lightred")

        story("Вторая глава завершена. Мир остался открыт для странствий.", color="green")
        _print(colorize("=" * 60, "lightmagenta", True))
        pause()

    # -----------------------------------------------------------------
    # Победа, поражение, квестовые убийства
    # -----------------------------------------------------------------

    def on_enemy_killed(self, enemy: Enemy) -> None:
        p = self.player

        if enemy.side == "dark":
            self.add_reputation("light", 2)
            self.add_reputation("shadow", -2)
        elif enemy.side == "light":
            self.add_reputation("shadow", 2)
            self.add_reputation("light", -2)
        else:
            self.add_reputation("neutral", 1)

        if enemy.template_id == "mine_ghoul" and self.quest_status("side_mine") == "active":
            p.quest_counters["side_mine"] = p.quest_counters.get("side_mine", 0) + 1
            print(f"Прогресс квеста 'Очистить шахту': {p.quest_counters['side_mine']}/3.", color="magenta")

            if p.quest_counters["side_mine"] >= 3:
                self.set_quest("side_mine", "ready_to_complete")

        if self.quest_status("side_bounty") == "active" and enemy.template_id in (
            "frost_wraith", "cult_adept", "archive_wraith"
        ):
            p.quest_counters["side_bounty"] = p.quest_counters.get("side_bounty", 0) + 1
            print(f"Прогресс квеста 'Охота за призраками': {p.quest_counters['side_bounty']}/3.", color="magenta")

            if p.quest_counters["side_bounty"] >= 3:
                self.set_quest("side_bounty", "ready_to_complete")

        if self.quest_status("side_shadow_hunt") == "active" and enemy.template_id in ("dawn_knight", "dawn_sentinel"):
            p.quest_counters["side_shadow_hunt"] = p.quest_counters.get("side_shadow_hunt", 0) + 1
            print(f"Прогресс квеста 'Охота на Рассвет': {p.quest_counters['side_shadow_hunt']}/2.", color="magenta")

            if p.quest_counters["side_shadow_hunt"] >= 2:
                self.set_quest("side_shadow_hunt", "ready_to_complete")

        if enemy.template_id == "archive_wraith" and self.quest_status("main_7") == "active":
            self.set_quest("main_7", "ready_to_complete")

        if enemy.template_id == "spider_queen" and self.quest_status("side_spider") == "active":
            self.set_quest("side_spider", "ready_to_complete")

        if enemy.template_id == "lord_morok" and self.quest_status("main_5") in ("active", "ready_to_complete"):
            self.complete_quest("main_5")

        if enemy.template_id == "heart_of_dark" and self.quest_status("main_9") in ("active", "ready_to_complete"):
            self.complete_quest("main_9")
            self.unlock("Сердце Тьмы побеждено")

        if enemy.template_id == "ataman":
            self.unlock("Первый босс побеждён")

    def victory(self, enemy: Enemy, last_roll: int) -> None:
        _print(colorize("=" * 50, "green", True))
        print(f"Победа! Вы одолели: {enemy.name}.", color="green", bold=True)

        if enemy.template_id == "ataman":
            self.ataman_choice()

        if enemy.template_id == "cult_emissary":
            self.emissary_choice()

        diff = DIFFICULTIES.get(self.player.difficulty, DIFFICULTIES["normal"])

        xp = int((enemy.xp + random.randint(0, 5)) * diff["reward"])
        gold = int(random.randint(enemy.gold_min, enemy.gold_max) * diff["reward"])

        self.player.gold += gold
        self.on_enemy_killed(enemy)

        messages = self.player.gain_xp(xp)
        print(f"Получено опыта: {xp}.", color="green")
        print(f"Получено золота: {gold}.", color="yellow")

        for msg in messages:
            print(msg, color="green")

        loot = self.generate_loot(enemy, last_roll)
        self.add_special_drops(enemy, loot)

        if loot:
            self.handle_loot(loot)
        else:
            print("Враг не оставил ничего ценного.", color="gray")

        if enemy.is_boss and enemy.template_id not in self.defeated_bosses:
            self.defeated_bosses.append(enemy.template_id)

        self.player.active_effects.clear()
        self.player.status_effects.clear()
        self.dirty = True

        if enemy.template_id == "lord_morok":
            self.final_branch_scene()

        if enemy.template_id == "heart_of_dark":
            self.final_act2_scene()

    def defeat(self, enemy: Enemy) -> None:
        _print(colorize("=" * 50, "red", True))
        story("Вы пали в бою...", color="red")
        time.sleep(0.4)

        loss = int(self.player.gold * 0.1)
        self.player.gold = max(0, self.player.gold - loss)
        self.player.hp = max(1, int(round(self.player.max_hp * 0.5)))
        self.player.active_effects.clear()
        self.player.status_effects.clear()

        home = self.safe_home()
        self.location_id = home
        self.last_safe = home
        self.location_state[home]["searches_left"] = LOCATIONS[home]["max_searches"]
        self.location_state[home]["camp_used"] = 0
        self.dirty = True

        print(f"Вы очнулись в локации: {LOCATIONS[home]['name']}.", color="lightcyan")
        print(f"Потеряно золота: {loss}. Инвентарь и квесты сохранены.", color="yellow")

    # -----------------------------------------------------------------
    # Исследование
    # -----------------------------------------------------------------

    def search_location(self) -> None:
        if self.is_safe_location(self.location_id):
            print("Здесь безопасно. Искать нечего.", color="gray")
            return

        state = self.location_state[self.location_id]

        if state["searches_left"] <= 0:
            print("Вы уже обыскали всё здесь. Перейдите в другую локацию, чтобы продолжить поиски.", color="yellow")
            return

        state["searches_left"] -= 1
        self.dirty = True

        print("Вы осматриваете окрестности...", color="cyan")
        time.sleep(0.3)

        if self.search_quest_event():
            return

        roll = random.randint(1, 100)
        enemies = self.location_enemies(self.location_id)

        if roll <= 20 and enemies:
            ambush_pool = [e for e in enemies if not ENEMY_TEMPLATES[e].get("is_boss", False)]
            if ambush_pool:
                enemy_id = random.choice(ambush_pool)
                print("Внезапно на вас нападает враг!", color="red", bold=True)
                self.start_combat(enemy_id)
                return

        if roll <= 45:
            gold = random.randint(2, 4) + self.player.level
            self.player.gold += gold
            print(f"Вы нашли {gold} золотых.", color="yellow")
            return

        if roll <= 70:
            item = self.random_search_item()
            if item is not None:
                print("Вы находите предмет.", color="green")
                self.handle_loot([item])
                return

        if roll <= 80:
            if self.try_gain_companion(self.location_id):
                return

        print("Вы ничего не нашли.", color="gray")

    def search_quest_event(self) -> bool:
        p = self.player
        loc = self.location_id

        if loc == "forest":
            if self.quest_status("main_2") == "active" and not p.has_template("clue"):
                item = self.make_item("clue")
                print("Вы находите обрывок ткани с культовым знаком. Это улика.", color="magenta")
                self.handle_loot([item])
                self.set_quest("main_2", "ready_to_complete")
                return True

            if (
                self.quest_status("side_medallion") == "active"
                and not p.has_template("family_medallion")
                and random.random() < 0.5
            ):
                item = self.make_item("family_medallion")
                print("Вы находите семейный медальон.", color="magenta")
                self.handle_loot([item])
                self.set_quest("side_medallion", "ready_to_complete")
                return True

            if self.quest_status("side_herbs") == "active":
                if p.count_template("healing_herb") < 3 and random.random() < 0.6:
                    item = self.make_item("healing_herb")
                    print("Вы находите лечебную траву.", color="lightgreen")
                    self.handle_loot([item])

                    if p.count_template("healing_herb") >= 3:
                        self.set_quest("side_herbs", "ready_to_complete")

                    return True

        if loc == "trail" and self.quest_status("side_herbs") == "active":
            if p.count_template("healing_herb") < 3 and random.random() < 0.35:
                item = self.make_item("healing_herb")
                print("Вы находите лечебную траву.", color="lightgreen")
                self.handle_loot([item])

                if p.count_template("healing_herb") >= 3:
                    self.set_quest("side_herbs", "ready_to_complete")

                return True

        if loc == "ruins" and self.quest_status("main_4") == "active" and "cult_emissary" not in self.defeated_bosses:
            story("Вы находите древний алтарь. Из теней выходит культовый эмиссар!", color="lightred")
            pause()
            self.start_combat("cult_emissary")
            return True

        if loc == "moor" and self.quest_status("side_alchemy") == "active":
            if p.count_template("ash_heart") < 3 and random.random() < 0.55:
                item = self.make_item("ash_heart")
                print("В пепле вы находите ещё тёплое сердце.", color="lightgreen")
                self.handle_loot([item])
                return True

        if loc == "crypt" and self.quest_status("side_relic") == "active" and not p.has_template("lost_relic"):
            item = self.make_item("lost_relic")
            print("В нише за гробницами блеснула реликвия.", color="magenta")
            self.handle_loot([item])
            self.set_quest("side_relic", "ready_to_complete")
            return True

        if loc == "library" and self.quest_status("main_7") == "active" and "archive_wraith" not in self.defeated_bosses:
            story("Пыль взмывает в воздух. Из рядов стеллажей встаёт Хранитель Архива!", color="lightred")
            pause()
            self.start_combat("archive_wraith")
            return True

        return False

    def random_search_item(self) -> Optional[Item]:
        loc = self.location_id

        if loc in ("mine", "ruins", "citadel"):
            pool = [
                ("scrap_metal", 40), ("ancient_fragment", 20), ("gem", 5),
                ("potion", 15), ("small_potion", 20),
            ]
        elif loc in ("pass", "moor", "crypt", "library", "steppe", "throne", "graveyard", "ice_palace"):
            pool = [
                ("frost_shard", 25), ("ash_heart", 20), ("dark_essence", 10),
                ("big_potion", 15), ("gem", 10), ("ancient_fragment", 20),
            ]
        elif loc == "web":
            pool = [
                ("monster_fang", 40), ("small_potion", 20), ("potion", 15),
                ("spider_ring", 5), ("gem", 10), ("ancient_fragment", 10),
            ]
        else:
            pool = [
                ("small_potion", 30), ("scrap_metal", 20), ("monster_fang", 25),
                ("potion", 10), ("ancient_fragment", 5), ("gem", 2),
                ("strength_elixir", 4), ("shield_elixir", 4),
            ]

        items, weights = zip(*pool)
        template_id = random.choices(items, weights=weights, k=1)[0]
        return self.make_item(template_id, 1)

    # -----------------------------------------------------------------
    # Инвентарь
    # -----------------------------------------------------------------

    def print_player_stats(self) -> None:
        p = self.player

        print(f"{p.name}, {p.char_class}, уровень {p.level}", color="lightcyan", bold=True)
        print(
            f"HP: {p.hp}/{p.max_hp} | Атака: {p.total_attack()} | Защита: {p.total_defense()} | "
            f"Крит: {p.total_crit()}% | Уклонение: {p.total_dodge()}% | Поиск лута: {p.total_loot()}%",
            color="white"
        )
        print(
            f"Опыт: {p.xp}/{p.xp_to_next} | Золото: {p.gold} | "
            f"Вес: {p.total_weight():.1f}/{p.max_weight} | Слоты: {p.slots_used()}/{p.max_slots}",
            color="yellow"
        )
        print(
            f"Глава: {p.chapter} | Фракция: {FACTION_NAMES.get(p.faction, p.faction)} | "
            f"Сложность: {DIFFICULTIES[p.difficulty]['name']}",
            color="lightmagenta"
        )

        print(
            "Репутация: "
            f"Свет {p.reputations.get('light', 0)}, "
            f"Тьма {p.reputations.get('shadow', 0)}, "
            f"Нейтралы {p.reputations.get('neutral', 0)}",
            color="cyan"
        )

        if p.companion:
            print(f"Спутник: {COMPANIONS[p.companion]['name']}", color="lightgreen")

    def print_equipment(self) -> None:
        print("Снаряжение:", color="lightblue")

        for slot in EQUIPMENT_SLOTS:
            item = self.player.equipment.get(slot)
            slot_name = SLOT_NAMES[slot]

            if item is None:
                print(f" - {slot_name}: пусто", color="gray")
            else:
                print(f" - {slot_name}: {format_item_line(item)}")

    def print_inventory(self) -> None:
        if not self.player.inventory:
            print("Инвентарь пуст.", color="gray")
            return

        print("Инвентарь:", color="lightblue")
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{colorize(str(i) + '.', 'yellow')} {format_item_line(item)}")

    def choose_inventory_item(self, filter_func, title: str) -> Optional[Item]:
        items = [it for it in self.player.inventory if filter_func(it)]

        if not items:
            print("Нет подходящих предметов.", color="gray")
            return None

        options = [format_item_line(it) for it in items]
        choice = choose_option(options, title)

        if choice == 0:
            return None

        return items[choice - 1]

    def inventory_menu(self) -> None:
        while True:
            _print(colorize("=" * 50, "gray"))
            self.print_player_stats()
            self.print_equipment()
            self.print_inventory()

            labels = [
                "Надеть предмет",
                "Снять предмет",
                "Использовать предмет",
                "Выбросить предмет",
            ]
            actions = ["equip", "unequip", "use", "drop"]

            if self.has_merchant_here():
                labels.append("Продать предмет")
                actions.append("sell")

            labels.append("Сортировать инвентарь")
            actions.append("sort")

            choice = choose_option(labels, "Инвентарь")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "equip":
                item = self.choose_inventory_item(
                    lambda it: it.item_type in EQUIPMENT_SLOTS and not it.quest_item,
                    "Какой предмет надеть?",
                )

                if item is not None:
                    ok, msg = self.player.equip_item(item.iid)
                    print(msg, color="green" if ok else "red")
                    if ok:
                        self.dirty = True

            elif action == "unequip":
                slots_with_items = [
                    slot for slot in EQUIPMENT_SLOTS if self.player.equipment.get(slot) is not None
                ]

                if not slots_with_items:
                    print("Нет надетых предметов.", color="gray")
                    continue

                options = [
                    f"{SLOT_NAMES[slot]}: {self.player.equipment[slot].display_name()}"
                    for slot in slots_with_items
                ]

                choice = choose_option(options, "Какой слот разгрузить?")
                if choice == 0:
                    continue

                ok, msg = self.player.unequip_slot(slots_with_items[choice - 1])
                print(msg, color="green" if ok else "red")
                if ok:
                    self.dirty = True

            elif action == "use":
                item = self.choose_inventory_item(
                    lambda it: it.item_type == "consumable" and not it.quest_item,
                    "Какой предмет использовать?",
                )

                if item is None:
                    continue

                if item.status_target == "enemy":
                    print("Этот предмет можно использовать только в бою.", color="red")
                    continue

                msg = self.player.use_consumable(item.iid)
                print(msg, color="lightgreen")
                self.dirty = True

            elif action == "drop":
                item = self.choose_inventory_item(
                    lambda it: not it.quest_item,
                    "Какой предмет выбросить?",
                )

                if item is None:
                    continue

                if item.quest_item:
                    print("Квестовый предмет нельзя выбросить.", color="red")
                    continue

                if ask_yes_no(f"Выбросить {item.display_name()} x1?"):
                    self.player.remove_item_by_iid(item.iid, 1)
                    print("Предмет выброшен.", color="gray")
                    self.dirty = True

            elif action == "sell":
                self.sell_item_menu()

            elif action == "sort":
                choice = choose_option(
                    ["По редкости", "По типу", "По весу", "По ценности"],
                    "Сортировка",
                )

                if choice == 0:
                    continue

                if choice == 1:
                    self.player.inventory.sort(key=lambda it: (RARITY_ORDER.get(it.rarity, 99), it.name))
                elif choice == 2:
                    self.player.inventory.sort(key=lambda it: (it.item_type, it.name))
                elif choice == 3:
                    self.player.inventory.sort(key=lambda it: (it.weight, it.name))
                elif choice == 4:
                    self.player.inventory.sort(key=lambda it: (-it.value, it.name))

                print("Инвентарь отсортирован.", color="green")

    def sell_item_menu(self) -> None:
        item = self.choose_inventory_item(lambda it: not it.quest_item, "Какой предмет продать?")

        if item is None:
            return

        side = self.merchant_side()
        price = max(1, int(item.value * self.sell_multiplier(side)))

        if not ask_yes_no(f"Продать {item.display_name()} x1 за {price} золотых?"):
            return

        if item.count > 1:
            self.player.remove_item_by_iid(item.iid, 1)
            stock_item = self.make_item(item.template_id, 1)
        else:
            self.player.inventory.remove(item)
            stock_item = item

        self.player.gold += price

        npc_id = self.merchant_npc_id()
        key = NPCS[npc_id].get("shop_key", "village") if npc_id else "village"

        stock = self.shop_stocks.setdefault(key, [])
        self.add_to_stock(stock, stock_item)
        self.dirty = True
        print("Предмет продан.", color="green")

    # -----------------------------------------------------------------
    # Журнал квестов и достижения
    # -----------------------------------------------------------------

    def quest_journal(self) -> None:
        p = self.player

        def quest_progress(qid: str) -> str:
            if qid == "side_herbs":
                return f"Собрано трав: {p.count_template('healing_herb')}/3"

            if qid == "side_mine":
                return f"Убито шахтных упырей: {p.quest_counters.get('side_mine', 0)}/3"

            if qid == "side_alchemy":
                return f"Пепельных сердец: {p.count_template('ash_heart')}/3"

            if qid == "side_bounty":
                return f"Призраков уничтожено: {p.quest_counters.get('side_bounty', 0)}/3"

            if qid == "side_shadow_hunt":
                return f"Рыцарей Рассвета: {p.quest_counters.get('side_shadow_hunt', 0)}/2"

            if qid == "side_beacon":
                return f"Ледяных осколков: {p.count_template('frost_shard')}/2"

            if qid == "side_spider":
                if self.quest_status(qid) == "ready_to_complete":
                    return "Королева пауков убита"
                return "Королева пауков ещё жива"

            return ""

        def show_quest(qid: str) -> None:
            q = QUESTS[qid]

            print(f" - {q['title']} ({q['type']})", color="lightmagenta")
            print(f"   Цель: {q['objectives']}")

            progress = quest_progress(qid)
            if progress:
                print(f"   Прогресс: {progress}", color="cyan")

            reward_parts = []

            if q.get("reward_xp", 0) > 0:
                reward_parts.append(f"опыт {q['reward_xp']}")

            if q.get("reward_gold", 0) > 0:
                reward_parts.append(f"золото {q['reward_gold']}")

            if q.get("reward_item"):
                reward_parts.append(f"предмет: {ITEM_TEMPLATES[q['reward_item']]['name']}")

            if reward_parts:
                print("   Награда: " + ", ".join(reward_parts), color="yellow")

        for title, status in (
            ("Активные квесты", "active"),
            ("Готовы к завершению", "ready_to_complete"),
            ("Выполненные квесты", "completed"),
        ):
            print(title + ":", color="lightcyan", bold=True)
            ids = [qid for qid in QUESTS if p.quest_flags.get(qid) == status]

            if not ids:
                print(" - нет", color="gray")
            else:
                for qid in ids:
                    show_quest(qid)

        available_side = [
            qid for qid, q in QUESTS.items()
            if q["type"] == "побочный" and p.quest_flags.get(qid, "not_started") == "not_started"
        ]

        if available_side:
            print("Возможные побочные задания (нужно поговорить с NPC):", color="lightyellow")
            for qid in available_side:
                print(f" - {QUESTS[qid]['title']}", color="magenta")

        if p.achievements:
            print("Достижения: " + ", ".join(p.achievements), color="lightyellow")
        else:
            print("Достижения: пока нет", color="gray")

    # -----------------------------------------------------------------
    # NPC: общий вход
    # -----------------------------------------------------------------

    def talk_menu(self) -> None:
        npcs = self.location_npcs(self.location_id)

        if not npcs:
            print("Здесь нет NPC.", color="gray")
            return

        options = [NPCS[nid]["name"] for nid in npcs]
        choice = choose_option(options, "С кем поговорить?")

        if choice == 0:
            return

        self.talk_npc(npcs[choice - 1])

    def talk_npc(self, npc_id: str) -> None:
        if self.is_npc_hostile(npc_id):
            name = NPCS[npc_id]["name"]
            say(name, "Ты... ты один из них. Уходи, тварь!", "lightred")

            if NPCS[npc_id].get("aggressive", True):
                print("Они нападают!", color="red", bold=True)
                self.start_combat(NPCS[npc_id].get("hostile_enemy", "village_militia"))

            return

        kind = NPCS[npc_id]["kind"]

        if kind == "elder":
            self.elder_dialog()
        elif kind == "merchant":
            self.merchant_dialog(npc_id)
        elif kind == "blacksmith":
            self.blacksmith_dialog(npc_id)
        elif kind == "healer":
            self.healer_dialog()
        elif kind == "darkhealer":
            self.dark_healer_dialog()
        elif kind == "villager":
            self.villager_dialog()
        elif kind == "stranger":
            self.stranger_dialog()
        elif kind == "miner":
            self.miner_dialog()
        elif kind == "warden":
            self.warden_dialog()
        elif kind == "alchemist":
            self.alchemist_dialog()
        elif kind == "oracle":
            self.oracle_dialog()
        elif kind == "keeper":
            self.keeper_dialog()
        elif kind == "herald":
            self.herald_dialog()
        elif kind == "lighthouse":
            self.lighthouse_dialog()
        elif kind == "spirit":
            self.spirit_dialog()

    # -----------------------------------------------------------------
    # Диалоги первой главы
    # -----------------------------------------------------------------

    def elder_dialog(self) -> None:
        p = self.player
        q = self.quest_status

        if q("main_1") == "active":
            say("Старейшина Гарольд", "Наш лорд исчез, а древние руины проснулись. По дорогам рыщут разбойники и культисты.", "lightmagenta")

            if ask_yes_no("Выслушать старейшину и взять задание?"):
                self.complete_quest("main_1")
                self.set_quest("main_2", "active")
                say("Старейшина Гарольд", "Найди улику в Заброшенном лесу. Это первый след.", "lightmagenta")

            return

        if q("main_2") == "active":
            say("Старейшина Гарольд", "Ищи улику в Заброшенном лесу. Без неё мы не поймём, кто стоит за набегами.", "lightmagenta")
            return

        if q("main_2") == "ready_to_complete":
            say("Старейшина Гарольд", "Это знак культа Забвения... Значит, слухи были правдой.", "lightmagenta")
            self.complete_quest("main_2")
            self.set_quest("main_3", "active")
            say("Старейшина Гарольд", "Разберись с разбойничьим лагерем. Их атаман носит странный ключ.", "lightmagenta")
            return

        if q("main_3") == "active":
            say("Старейшина Гарольд", "Разбойники засели в лагере. Их атаман носит ключ от древних дверей.", "lightmagenta")
            return

        if q("main_3") == "ready_to_complete":
            say("Старейшина Гарольд", "Ты добыл ключ... Теперь путь в Древние руины открыт.", "lightmagenta")
            self.complete_quest("main_3")
            self.set_quest("main_4", "active")
            say("Старейшина Гарольд", "Исследуй руины и останови культового эмиссара.", "lightmagenta")
            return

        if q("main_4") == "active":
            say("Старейшина Гарольд", "Руины опасны. Найди источник культа внутри и уничтожь его.", "lightmagenta")
            return

        if q("main_4") == "ready_to_complete":
            branch = p.quest_flags.get("branch_sigil", "elder")

            if branch == "destroy":
                say("Старейшина Гарольд", "Ты уничтожил печать... Свет помог тебе.", "lightmagenta")
            elif branch == "power":
                say("Старейшина Гарольд", "Я чувствую тёмную силу в тебе... Но выбора больше нет.", "lightmagenta")
            else:
                say("Старейшина Гарольд", "Печать у тебя. Я открою путь к Цитадели.", "lightmagenta")

            self.complete_quest("main_4")
            self.set_quest("main_5", "active")
            say("Старейшина Гарольд", "Войди в Цитадель Забвения и останови Лорда Морока.", "lightmagenta")
            return

        if q("main_5") == "active":
            say("Старейшина Гарольд", "Цитадель ждёт тебя. Будь осторожен: Лорд Морок не прощает ошибок.", "lightmagenta")
            return

        if q("main_5") == "completed":
            if p.ending == "light":
                say("Старейшина Гарольд", "Ты принёс нам рассвет. Деревня будет помнить это всегда.", "lightmagenta")
            elif p.ending == "seal":
                say("Старейшина Гарольд", "Печать крепка, но мы будем нести дозор вечно.", "lightmagenta")
            else:
                say("Старейшина Гарольд", "Ты стал тем, кого мы боялись. Уходи, пока я добродушен.", "lightred")
            return

        say("Старейшина Гарольд", "Не ходи ночью за околицу, путник.", "lightmagenta")

    def merchant_dialog(self, npc_id: str) -> None:
        name = NPCS[npc_id]["name"]
        say(name, "Смотри, что есть. Торговля - единственная честная война.", "yellow")
        self.trade_menu(NPCS[npc_id].get("shop_key", "village"), NPCS[npc_id].get("side", "neutral"))

    def trade_menu(self, shop_key: str, side: str) -> None:
        self.current_shop_side = side

        while True:
            choice = choose_option(
                [
                    "Купить предметы",
                    "Продать предметы из инвентаря",
                    "Посмотреть свои деньги и вес",
                    "Поговорить",
                    "Вернуться",
                ],
                "Торговля",
            )

            if choice == 1:
                self.buy_menu(shop_key, side)
            elif choice == 2:
                self.sell_item_menu()
            elif choice == 3:
                p = self.player
                print(f"Золото: {p.gold}", color="yellow")
                print(f"Вес инвентаря: {p.total_weight():.1f}/{p.max_weight}", color="cyan")
                print(f"Слоты: {p.slots_used()}/{p.max_slots}", color="cyan")
            elif choice == 4:
                say("Торговец", "В этих краях стало опасно, но за хорошую плату я привезу что угодно.", "yellow")
            elif choice == 5 or choice == 0:
                return

    def buy_menu(self, shop_key: str, side: Optional[str] = None) -> None:
        self.refresh_shop(shop_key)

        if side is None:
            side = self.current_shop_side

        stock = self.shop_stocks.get(shop_key, [])

        if not stock:
            print("Товаров нет.", color="gray")
            return

        multiplier = self.price_multiplier(side)

        while True:
            options: List[str] = []

            for item in stock:
                price = max(1, int(item.value * multiplier))

                if item.count > 1:
                    options.append(
                        f"{item.display_name()} [{item.rarity}] доступно {item.count}, "
                        f"цена за шт. {price}. {item_stats_text(item)}"
                    )
                else:
                    options.append(
                        f"{item.display_name()} [{item.rarity}], цена {price}. {item_stats_text(item)}"
                    )

            choice = choose_option(options, "Купить")
            if choice == 0:
                return

            item = stock[choice - 1]
            price = max(1, int(item.value * multiplier))

            if self.player.gold < price:
                print("Недостаточно золота.", color="red")
                continue

            if item.item_type in ("consumable", "material", "quest"):
                new_item = self.make_item(item.template_id, 1)

                if not self.player.can_add_item(new_item, 1):
                    print("Недостаточно места или веса.", color="red")
                    continue

                self.player.gold -= price
                item.count -= 1

                if item.count <= 0:
                    stock.remove(item)

                self.player.add_item(new_item)
            else:
                if not self.player.can_add_item(item, 1):
                    print("Недостаточно места или веса.", color="red")
                    continue

                self.player.gold -= price
                stock.remove(item)
                self.player.add_item(item)

            self.dirty = True
            print("Покупка совершена.", color="green")

    def blacksmith_dialog(self, npc_id: str) -> None:
        name = NPCS[npc_id]["name"]
        say(name, "Могу улучшить оружие и броню. Нужны золото и металлический лом.", "lightred")

        while True:
            choice = choose_option(
                ["Улучшить снаряжение", "Зачаровать предмет", "Посмотреть материалы", "Вернуться"],
                name,
            )

            if choice == 1:
                self.upgrade_menu()
            elif choice == 2:
                self.enchant_menu()
            elif choice == 3:
                count = self.player.count_template("scrap_metal")
                print(f"Металлический лом: {count}", color="cyan")
                say(name, "Для улучшения нужен металлический лом и золото.", "lightred")
            elif choice == 4 or choice == 0:
                return

    def upgrade_menu(self) -> None:
        items: List[tuple] = []

        for item in self.player.inventory:
            if item.item_type in ("weapon", "armor", "helmet", "boots") and not item.quest_item:
                items.append((item, "инвентарь"))

        for slot in EQUIPMENT_SLOTS:
            item = self.player.equipment.get(slot)
            if item is not None and item.item_type in ("weapon", "armor", "helmet", "boots"):
                items.append((item, SLOT_NAMES[slot].lower()))

        if not items:
            print("Нет подходящего снаряжения для улучшения.", color="gray")
            return

        options = [
            f"{item.display_name()} ({where}), улучшение +{item.upgrade}"
            for item, where in items
        ]

        choice = choose_option(options, "Какой предмет улучшить?")
        if choice == 0:
            return

        item = items[choice - 1][0]

        if item.upgrade >= 5:
            print("Этот предмет уже улучшен до предела.", color="yellow")
            return

        next_level = item.upgrade + 1
        gold_cost = 40 * next_level
        material_cost = next_level

        print(
            f"Улучшение до +{next_level}: {gold_cost} золота и {material_cost} шт. металлического лома.",
            color="cyan",
        )

        if not ask_yes_no("Улучшить предмет?"):
            return

        if self.player.gold < gold_cost:
            print("Недостаточно золота.", color="red")
            return

        if self.player.count_template("scrap_metal") < material_cost:
            print("Недостаточно металлического лома.", color="red")
            return

        self.player.gold -= gold_cost
        self.player.remove_template("scrap_metal", material_cost)
        item.upgrade += 1
        item.value += 60
        self.dirty = True

        print(f"Предмет улучшен: {item.display_name()}.", color="green")

    def heal_service(self, cost: int, speaker: str, friendly: bool) -> None:
        if self.player.hp >= self.player.max_hp:
            say(speaker, "Вы здоровы. Зачем тратить зелья и время?", "lightgreen" if friendly else "lightmagenta")
            return

        if self.player.gold < cost:
            print("Недостаточно золота.", color="red")
            return

        self.player.gold -= cost
        self.player.hp = self.player.max_hp
        self.player.status_effects.clear()
        self.dirty = True

        if friendly:
            say(speaker, "Раны затягиваются. Вы полностью здоровы.", "lightgreen")
        else:
            say(speaker, "Тьма зашивает то, что рвёт свет.", "lightmagenta")

    def healer_dialog(self) -> None:
        say("Целительница Мира", "Чем помочь? Есть лечение и травы.", "lightgreen")

        while True:
            cost = 6 + self.player.level * 4
            choice = choose_option(
                [f"Вылечиться ({cost} золотых)", "Квест: лечебные травы", "Вернуться"],
                "Целительница Мира",
            )

            if choice == 1:
                self.heal_service(cost, "Целительница Мира", True)
            elif choice == 2:
                self.herbs_quest_dialog()
            elif choice == 3 or choice == 0:
                return

    def dark_healer_dialog(self) -> None:
        say("Вождь Клык", "Тьма лечит быстрее света. Но цена выше.", "lightmagenta")

        while True:
            cost = 20 + self.player.level * 6
            choice = choose_option(
                [f"Тёмный ритуал ({cost} золотых)", "Поговорить", "Вернуться"],
                "Вождь Клык",
            )

            if choice == 1:
                self.heal_service(cost, "Вождь Клык", False)
            elif choice == 2:
                say("Вождь Клык", "Мы служили Забвению ещё до культа. Мы просто помним порядок.", "lightmagenta")
            elif choice == 3 or choice == 0:
                return

    def herbs_quest_dialog(self) -> None:
        p = self.player
        status = self.quest_status("side_herbs")

        if status == "not_started":
            say("Целительница Мира", "В лесу и на тропе растёт лечебная трава. Принесите 3 штуки.", "lightgreen")

            if ask_yes_no("Взять задание?"):
                self.set_quest("side_herbs", "active")
                print("Задание получено: соберите 3 лечебные травы.", color="magenta")

            return

        if status == "completed":
            say("Целительница Мира", "Спасибо за травы. Они помогут многим.", "lightgreen")
            return

        count = p.count_template("healing_herb")
        print(f"Собрано трав: {count}/3.", color="cyan")

        if count >= 3:
            p.remove_template("healing_herb", 3)
            self.complete_quest("side_herbs")
        else:
            say("Целительница Мира", "Принесите ещё травы.", "lightgreen")

    def villager_dialog(self) -> None:
        while True:
            options: List[str] = []
            actions: List[str] = []

            med_status = self.quest_status("side_medallion")
            letter_status = self.quest_status("side_letter")

            if med_status == "not_started":
                options.append("Расспросить о пропаже медальона")
                actions.append("med_start")
            elif med_status in ("active", "ready_to_complete"):
                if med_status == "ready_to_complete":
                    options.append("Отдать семейный медальон")
                    actions.append("med_complete")
                else:
                    options.append("Спросить о поисках медальона")
                    actions.append("med_progress")

            if letter_status == "not_started":
                options.append("Предложить доставку письма")
                actions.append("letter_start")
            elif letter_status == "active":
                options.append("Спросить о письме")
                actions.append("letter_progress")

            options.append("Поговорить о жизни")
            actions.append("talk")

            choice = choose_option(options, "Житель Дарен")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "med_start":
                say("Житель Дарен", "Я потерял семейный медальон в лесу. Найдите его, пожалуйста.", "white")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_medallion", "active")
                    print("Задание получено: найдите семейный медальон.", color="magenta")

            elif action == "med_progress":
                say("Житель Дарен", "Ищите медальон в Заброшенном лесу.", "white")

            elif action == "med_complete":
                if self.player.has_template("family_medallion"):
                    self.player.remove_template("family_medallion", 1)
                    self.complete_quest("side_medallion")
                    say("Житель Дарен", "Спасибо! Вы вернули мне память о семье.", "white")
                else:
                    say("Житель Дарен", "У вас нет медальона...", "white")

            elif action == "letter_start":
                say("Житель Дарен", "Отнесите письмо старому шахтёру в шахту.", "white")

                letter = self.make_item("letter")
                if self.player.can_add_item(letter, 1):
                    self.player.add_item(letter)
                    self.set_quest("side_letter", "active")
                    print("Вы получили письмо. Доставьте его старому шахтёру.", color="magenta")
                else:
                    print("Недостаточно места в инвентаре.", color="red")

            elif action == "letter_progress":
                say("Житель Дарен", "Письмо нужно доставить старому шахтёру в Старой шахте.", "white")

            elif action == "talk":
                if self.is_shadow():
                    say("Житель Дарен", "Уходи. Мы слышали, что стало с Цитаделью.", "lightred")
                else:
                    say("Житель Дарен", "Раньше здесь было тихо. Теперь даже днём люди боятся ходить в лес.", "white")

    def miner_dialog(self) -> None:
        while True:
            options: List[str] = []
            actions: List[str] = []

            mine_status = self.quest_status("side_mine")
            letter_status = self.quest_status("side_letter")

            if mine_status == "not_started":
                options.append("Спросить о проблеме в шахте")
                actions.append("mine_start")
            elif mine_status == "active":
                options.append("Спросить об упырях")
                actions.append("mine_progress")
            elif mine_status == "ready_to_complete":
                options.append("Сообщить об уничтожении упырей")
                actions.append("mine_complete")

            if letter_status == "active" and self.player.has_template("letter"):
                options.append("Отдать письмо Дарена")
                actions.append("letter_deliver")

            options.append("Поговорить")
            actions.append("talk")

            choice = choose_option(options, "Старый шахтёр")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "mine_start":
                say("Старый шахтёр", "В шахте завелись упыри. Убейте троих, и я в долгу не останусь.", "cyan")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_mine", "active")
                    self.player.quest_counters["side_mine"] = 0
                    self.dirty = True
                    print("Задание получено: уничтожьте 3 шахтных упырей.", color="magenta")

            elif action == "mine_progress":
                kills = self.player.quest_counters.get("side_mine", 0)
                print(f"Убито шахтных упырей: {kills}/3.", color="cyan")

            elif action == "mine_complete":
                kills = self.player.quest_counters.get("side_mine", 0)

                if kills >= 3:
                    self.complete_quest("side_mine")
                    say("Старый шахтёр", "Теперь в шахте стало тише. Спасибо.", "cyan")
                else:
                    say("Старый шахтёр", f"Пока рано. Убито: {kills}/3.", "cyan")

            elif action == "letter_deliver":
                self.player.remove_template("letter", 1)
                self.complete_quest("side_letter")
                say("Старый шахтёр", "Письмо от Дарена... Передай ему спасибо.", "cyan")

            elif action == "talk":
                say("Старый шахтёр", "Шахта кормила деревню, пока тьма не полезла из камней.", "cyan")

    def stranger_dialog(self) -> None:
        sigil_branch = self.player.quest_flags.get("branch_sigil")

        if self.quest_status("main_4") == "active":
            say("Таинственный незнакомец", "В руинах тебя ждёт эмиссар культа. Он охраняет чёрную печать.", "magenta")
        elif self.quest_status("main_5") == "active":
            if sigil_branch == "destroy":
                say("Таинственный незнакомец", "Ты уничтожил печать, но Цитадель всё равно откроется. Свет ведёт тебя.", "magenta")
            elif sigil_branch == "power":
                say("Таинственный незнакомец", "Тьма уже в тебе. Цитадель узнает своего.", "magenta")
            else:
                say("Таинственный незнакомец", "Цитадель Забвения ждёт. Не доверяй старым словам слишком сильно.", "magenta")
        elif self.player.chapter >= 2:
            if self.is_shadow():
                say("Таинственный незнакомец", "Ты выбрал Тьму. Тогда Разлом откроется тебе без сопротивления.", "lightmagenta")
            else:
                say("Таинственный незнакомец", "За Цитаделью - Разлом. Там решится, кем ты стал на самом деле.", "magenta")
        else:
            say("Таинственный незнакомец", "Не задерживайся здесь надолго. Поляна слушает каждый шаг.", "magenta")

    # -----------------------------------------------------------------
    # Диалоги второй главы
    # -----------------------------------------------------------------

    def warden_dialog(self) -> None:
        if self.quest_status("main_6") == "active":
            say("Страж Разлома Илларион", "Ты прошёл Цитадель. Значит, ты готов услышать правду о Разломе.", "lightcyan")
            say("Страж Разлома Илларион", "Забвение не умерло. Оно просто сменило хозяина. Дальше - Пепельный Путь.", "lightcyan")
            self.complete_quest("main_6")
            self.set_quest("main_7", "active")
            say("Страж Разлома Илларион", "В Древней библиотеке сидит Хранитель. Он знает, как закончить это.", "lightcyan")
            return

        if self.player.ending == "shadow" and not self.is_shadow():
            say("Страж Разлома Илларион", "Ты занял трон, но не принял Тьму. Ты опаснее обоих.", "lightcyan")
        elif self.is_shadow():
            say("Страж Разлома Илларион", "Тёмный. Я не держу тебя. Но знай: Сердце требует платы.", "lightmagenta")
        else:
            say("Страж Разлома Илларион", "Иди дальше, к Архиву. Там правда о Забвении.", "lightcyan")

    def alchemist_dialog(self) -> None:
        say("Алхимик Селена", "Пепел пустоши лечит лучше любых трав. Если умеешь с ним работать.", "lightgreen")

        while True:
            choice = choose_option(
                ["Купить зелья", "Создать предмет", "Квест: пепельные сердца", "Вернуться"],
                "Алхимик Селена",
            )

            if choice == 1:
                self.buy_menu("port", "neutral")
            elif choice == 2:
                self.craft_menu()
            elif choice == 3:
                self.alchemy_quest_dialog()
            elif choice == 4 or choice == 0:
                return

    def alchemy_quest_dialog(self) -> None:
        status = self.quest_status("side_alchemy")

        if status == "not_started":
            say("Алхимик Селена", "Принеси 3 пепельных сердца с Мёртвой пустоши.", "lightgreen")

            if ask_yes_no("Взять задание?"):
                self.set_quest("side_alchemy", "active")
                print("Задание получено: соберите 3 пепельных сердца.", color="magenta")

            return

        if status == "completed":
            say("Алхимик Селена", "Твои сердца ушли в зелья. Мир стал чуть менее мёртвым.", "lightgreen")
            return

        count = self.player.count_template("ash_heart")
        print(f"Пепельных сердец: {count}/3.", color="cyan")

        if count >= 3:
            self.player.remove_template("ash_heart", 3)
            self.complete_quest("side_alchemy")
        else:
            say("Алхимик Селена", "Ищи их в пепле пустоши или в оболочках.", "lightgreen")

    def oracle_dialog(self) -> None:
        say("Прорицательница Ним", "Я вижу все твои дороги одновременно. Некоторые из них очень тёмные.", "magenta")

        while True:
            options: List[str] = []
            actions: List[str] = []

            if self.quest_status("main_7") == "ready_to_complete":
                options.append("Отдать Печать Архива")
                actions.append("main7")
            elif self.quest_status("main_7") == "active":
                options.append("Спросить о Хранителе Архива")
                actions.append("main7_info")

            bounty_status = self.quest_status("side_bounty")
            if bounty_status == "not_started":
                options.append("Квест: охота за призраками")
                actions.append("bounty_start")
            elif bounty_status == "active":
                options.append("Спросить о призраках")
                actions.append("bounty_progress")
            elif bounty_status == "ready_to_complete":
                options.append("Доложить о призраках")
                actions.append("bounty_done")

            relic_status = self.quest_status("side_relic")
            if relic_status == "not_started":
                options.append("Квест: реликвия Склепа")
                actions.append("relic_start")
            elif relic_status == "active":
                options.append("Спросить о реликвии")
                actions.append("relic_progress")
            elif relic_status == "ready_to_complete":
                options.append("Отдать реликвию")
                actions.append("relic_done")

            spider_status = self.quest_status("side_spider")
            if spider_status == "not_started":
                options.append("Квест: королева пауков")
                actions.append("spider_start")
            elif spider_status == "active":
                options.append("Спросить о королеве пауков")
                actions.append("spider_progress")
            elif spider_status == "ready_to_complete":
                options.append("Доложить о королеве пауков")
                actions.append("spider_done")

            options.append("Поговорить")
            actions.append("talk")

            choice = choose_option(options, "Прорицательница Ним")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "main7":
                if self.player.has_template("archive_seal"):
                    self.player.remove_template("archive_seal", 1)
                    self.complete_quest("main_7")
                    self.set_quest("main_8", "active")
                    say("Прорицательница Ним", "Печать открыта. Теперь иди в Зал Тени - там ждёт Вестник.", "magenta")
                else:
                    say("Прорицательница Ним", "Где печать? Хранитель должен был её оставить.", "magenta")

            elif action == "main7_info":
                say("Прорицательница Ним", "Хранитель встаёт, стоит тебе коснуться его полок. Он не отступает.", "magenta")

            elif action == "bounty_start":
                say("Прорицательница Ним", "Уничтожь 3 призрачных существа: ледяных, культовых или Хранителя.", "magenta")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_bounty", "active")
                    self.player.quest_counters["side_bounty"] = 0
                    self.dirty = True
                    print("Задание получено: уничтожьте 3 призрачных существа.", color="magenta")

            elif action == "bounty_progress":
                kills = self.player.quest_counters.get("side_bounty", 0)
                print(f"Призраков уничтожено: {kills}/3.", color="cyan")

            elif action == "bounty_done":
                kills = self.player.quest_counters.get("side_bounty", 0)

                if kills >= 3:
                    self.complete_quest("side_bounty")
                else:
                    print(f"Пока рано. Убито: {kills}/3.", color="yellow")

            elif action == "relic_start":
                say("Прорицательница Ним", "В Культовом склепе спрятана реликвия. Принеси её мне.", "magenta")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_relic", "active")
                    print("Задание получено: найдите реликвию в Склепе.", color="magenta")

            elif action == "relic_progress":
                say("Прорицательница Ним", "Склеп на востоке от Порта. Ищи в нишах за гробницами.", "magenta")

            elif action == "relic_done":
                if self.player.has_template("lost_relic"):
                    self.player.remove_template("lost_relic", 1)
                    self.complete_quest("side_relic")
                    say("Прорицательница Ним", "Она пела, когда я взяла её. Теперь поёт тише.", "magenta")
                else:
                    say("Прорицательница Ним", "Реликвии при тебе нет.", "magenta")

            elif action == "spider_start":
                say("Прорицательница Ним", "В Паучьем гнезде проснулась королева. Убей её, пока паутина не оплела руины.", "magenta")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_spider", "active")
                    print("Задание получено: убейте Королеву пауков.", color="magenta")

            elif action == "spider_progress":
                say("Прорицательница Ним", "Гнездо находится к востоку от шахты. Она чувствует страх.", "magenta")

            elif action == "spider_done":
                self.complete_quest("side_spider")
                say("Прорицательница Ним", "Паутина рвётся. Даже тьма иногда боится огня.", "magenta")

            elif action == "talk":
                if self.is_shadow():
                    say("Прорицательница Ним", "Я видела, кем ты станешь. Не вини меня за этот образ.", "lightmagenta")
                else:
                    say("Прорицательница Ним", "Все дороги ведут в Тронный Зал. Разница лишь в том, кем ты туда войдёшь.", "magenta")

    def keeper_dialog(self) -> None:
        say("Хранитель Света Аэон", "Ты прошёл сквозь Забвение и не стал им. Редкая удача.", "lightyellow")

        while True:
            choice = choose_option(
                ["Освящение (бесплатно)", "Поговорить", "Вернуться"],
                "Хранитель Света Аэон",
            )

            if choice == 1:
                if self.player.hp >= self.player.max_hp:
                    say("Хранитель Света Аэон", "Ты и так цел.", "lightyellow")
                else:
                    self.player.hp = self.player.max_hp
                    self.player.status_effects.clear()
                    self.dirty = True
                    say("Хранитель Света Аэон", "Свет входит в тебя. Раны закрыты без цены.", "lightyellow")

            elif choice == 2:
                if self.player.ending == "light":
                    say("Хранитель Света Аэон", "Твой рассвет осветил и Долину. Спасибо.", "lightyellow")
                elif self.player.ending == "seal":
                    say("Хранитель Света Аэон", "Печать - тоже форма мужества. Но не отдыхай.", "lightyellow")
                else:
                    say("Хранитель Света Аэон", "Ты правил тьмой и вернулся. Свет помнит такие шаги.", "lightyellow")

            elif choice == 3 or choice == 0:
                return

    def herald_dialog(self) -> None:
        status = self.quest_status("main_8")

        if status == "not_started":
            say("Вестник Трона Азар", "Ты ещё не готов к дару. Вернись, когда узнаешь правду.", "lightmagenta")
            return

        if status in ("active", "ready_to_complete"):
            say("Вестник Трона Азар", "Сердце Тьмы предлагает дар. Примешь - станешь одним из нас.", "lightmagenta")
            say("Вестник Трона Азар", "Отвергнешь - останешься врагом, но свободным. Выбирай.", "lightmagenta")

            choice = choose_option(
                [
                    "Принять дар Тьмы (стать тёмным)",
                    "Отвергнуть дар (продолжить борьбу)",
                ],
                "Дар Тьмы",
                allow_back=False,
            )

            if choice == 1:
                self.accept_dark_gift(True)
            else:
                self.accept_dark_gift(False)

            return

        hunt_status = self.quest_status("side_shadow_hunt")

        while True:
            options: List[str] = []
            actions: List[str] = []

            if hunt_status == "not_started":
                options.append("Квест: охота на Рассвет")
                actions.append("hunt_start")
            elif hunt_status == "active":
                options.append("Спросить о Рыцарях Рассвета")
                actions.append("hunt_progress")
            elif hunt_status == "ready_to_complete":
                options.append("Доложить об охоте")
                actions.append("hunt_done")

            options.append("Напутствие перед Тронным Залом")
            actions.append("advice")
            options.append("Вернуться")
            actions.append("back")

            choice = choose_option(options, "Вестник Трона Азар")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "hunt_start":
                if not self.is_shadow():
                    say("Вестник Трона Азар", "Охота на Рассвет нужна только тем, кто выбрал Тьму.", "lightmagenta")
                    continue

                say("Вестник Трона Азар", "Рыцари Рассвета пришли выжечь Разлом. Убей двоих.", "lightmagenta")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_shadow_hunt", "active")
                    self.player.quest_counters["side_shadow_hunt"] = 0
                    self.dirty = True
                    print("Задание получено: убейте 2 Рыцарей Рассвета.", color="magenta")

            elif action == "hunt_progress":
                kills = self.player.quest_counters.get("side_shadow_hunt", 0)
                print(f"Рыцарей Рассвета: {kills}/2.", color="cyan")

            elif action == "hunt_done":
                kills = self.player.quest_counters.get("side_shadow_hunt", 0)

                if kills >= 2:
                    self.complete_quest("side_shadow_hunt")
                else:
                    print(f"Пока рано. Убито: {kills}/2.", color="yellow")

            elif action == "advice":
                if self.is_shadow():
                    say("Вестник Трона Азар", "Сердце узнает своего. Но оно всё равно попытается тебя сожрать.", "lightmagenta")
                else:
                    say("Вестник Трона Азар", "Сердце бьётся в такт твоему страху. Не давай ему ритма.", "lightmagenta")

            elif action == "back":
                return

    # -----------------------------------------------------------------
    # Новые диалоги расширения
    # -----------------------------------------------------------------

    def lighthouse_dialog(self) -> None:
        say("Смотритель маяка Элио", "Маяк гаснет без света. Лёд в перевале хранит его осколки.", "lightblue")

        status = self.quest_status("side_beacon")

        while True:
            options: List[str] = []
            actions: List[str] = []

            if status == "not_started":
                options.append("Помочь маяку")
                actions.append("start")
            elif status == "active":
                options.append("Показать ледяные осколки")
                actions.append("progress")
            elif status == "completed":
                options.append("Поговорить о маяке")
                actions.append("done")

            options.append("Вернуться")
            actions.append("back")

            choice = choose_option(options, "Смотритель маяка Элио")
            if choice == 0:
                return

            action = actions[choice - 1]

            if action == "start":
                say("Смотритель маяка Элио", "Принеси 2 ледяных осколка. Я зажгу свет, чтобы тьма не прошла через разлом.", "lightblue")

                if ask_yes_no("Взять задание?"):
                    self.set_quest("side_beacon", "active")
                    print("Задание получено: принесите 2 ледяных осколка.", color="magenta")
                    return

            elif action == "progress":
                count = self.player.count_template("frost_shard")
                print(f"Ледяных осколков: {count}/2.", color="cyan")

                if count >= 2:
                    self.player.remove_template("frost_shard", 2)
                    self.complete_quest("side_beacon")
                    say("Смотритель маяка Элио", "Свет вспыхивает! Пусть он ведёт тебя даже сквозь Забвение.", "lightblue")
                    return
                else:
                    say("Смотритель маяка Элио", "Ищи осколки на Ледяном перевале или в дворце.", "lightblue")

            elif action == "done":
                say("Смотритель маяка Элио", "Пока горит маяк, часть мира ещё помнит свет.", "lightblue")

            elif action == "back":
                return

    def spirit_dialog(self) -> None:
        say("Дух Осколка", "Ты принёс сюда пыль дорог. Я могу коснуться твоих ран.", "lightyellow")

        while True:
            choice = choose_option(
                ["Благословение осколков", "Поговорить", "Вернуться"],
                "Дух Осколка",
            )

            if choice == 1:
                add_status(self.player.status_effects, "bless", 0, 5)
                self.player.hp = min(self.player.max_hp, self.player.hp + int(self.player.max_hp * 0.1))
                self.dirty = True
                say("Дух Осколка", "Свет ложится на твои плечи. Ты чувствуешь поддержку.", "lightyellow")
            elif choice == 2:
                say("Дух Осколка", "Забвение не зло. Это голод. И у голода всегда есть цена.", "lightyellow")
            elif choice == 3 or choice == 0:
                return


# =====================================================================
# Справка
# =====================================================================

def show_help() -> None:
    _print(colorize("=" * 60, "cyan", True))
    print("Управление и правила", color="cyan", bold=True)
    _print(colorize("=" * 60, "cyan", True))

    print("Игра управляется цифрами меню. Введите номер пункта и нажмите Enter.")
    print("В бою доступны: 1 - Атака, 2 - Защита, 3 - Использовать предмет, 4 - Побег.")
    print("Броски d6:")
    print("1-2: промах атаки или провал защитного бонуса", color="yellow")
    print("3-4: обычный эффект", color="green")
    print("5: эффект умножается на 1.2", color="lightyellow")
    print("6: эффект умножается на 1.5", color="lightred")

    print("Новые механики расширения:", color="lightmagenta", bold=True)
    print("- Сложность: Лёгкий, Обычный, Кошмар, Проклятый.")
    print("- Таланты: получайте очки при уровнях и открывайте перки.")
    print("- Статусы: яд, ожог, холод, проклятие, благословение.")
    print("- Элитные враги: яростные, бронированные, призрачные, вампирские и другие.")
    print("- Крафт: создавайте зелья, бомбы и эликсиры в лагере или у алхимика.")
    print("- Зачарование: кузнец и оружейник тьмы могут зачаровывать снаряжение.")
    print("- Спутники: волчонок, тенёнок или осколок света могут помочь в бою.")
    print("- Лагерь: отдых, крафт и медитация в опасных зонах, но есть риск засады.")
    print("- Репутация: Свет, Тьма и Нейтралы реагируют на ваши поступки и цены.")
    print("- Новые локации: Паучье гнездо, Маяк, Кладбище кораблей, Чёрный рынок, Ледяной дворец, Осколки Света.")
    print("- Достижения: фиксируют важные моменты пути.")

    print("Сохранение создаётся в файле save.json рядом с rpg.py.", color="gray")
    print("Квестовые предметы нельзя продать, выбросить или использовать.", color="gray")
    print("Цвет текста отключается переменной окружения NO_COLOR.", color="gray")


# =====================================================================
# Создание персонажа и главное меню
# =====================================================================

def ask_name() -> str:
    while True:
        name = safe_input("Введите имя героя (до 24 символов): ").strip()

        if not name:
            print("Имя не может быть пустым.", color="red")
        elif len(name) > 24:
            print("Имя слишком длинное. Максимум 24 символа.", color="red")
        else:
            return name


def ask_difficulty() -> str:
    keys = list(DIFFICULTIES.keys())
    options = [DIFFICULTIES[k]["name"] for k in keys]

    choice = choose_option(options, "Выберите сложность", allow_back=False)
    return keys[choice - 1]


def main() -> None:
    _print(colorize("=" * 60, "magenta", True))
    print("Тёмное фэнтези: Пограничный край — Расширенная версия", color="lightmagenta", bold=True)
    print("Две главы, фракции, таланты, крафт, спутники и несколько концовок", color="cyan")
    _print(colorize("=" * 60, "magenta", True))

    while True:
        choice = choose_option(
            ["Новая игра", "Продолжить", "Управление и правила", "Выход"],
            "Главное меню",
            allow_back=False,
        )

        if choice == 1:
            if os.path.exists(SAVE_FILE):
                if not ask_yes_no("Найдено сохранение. Начать новую игру и перезаписать его?"):
                    continue

            name = ask_name()
            difficulty = ask_difficulty()

            class_names = list(CLASS_DATA.keys())
            print("Классы:", color="lightcyan", bold=True)

            for i, class_name in enumerate(class_names, 1):
                print(f"{colorize(str(i) + '.', 'yellow')} {class_name} - {CLASS_DATA[class_name]['desc']}")

            class_choice = choose_option(class_names, "Выберите класс")
            if class_choice == 0:
                continue

            char_class = class_names[class_choice - 1]
            game = Game.new_game(name, char_class, difficulty)

            _print(colorize("=" * 60, "cyan", True))
            story(f"{game.player.name}, вы прибываете в деревню Сумеречный Брод.")
            story("Старый лорд исчез, древние руины ожили, а по дорогам бродят разбойники.")
            story("Поговорите со старейшиной, чтобы узнать больше.")
            _print(colorize("=" * 60, "cyan", True))
            pause()

            game.location_menu()

        elif choice == 2:
            game = Game.load()

            if game is None:
                print("Сохранение не найдено, повреждено или несовместимо.", color="red")
                print("Можно начать новую игру.", color="cyan")
            else:
                print("Игра загружена.", color="green")
                game.location_menu()

        elif choice == 3:
            show_help()
            pause()

        elif choice == 4:
            print("Выход из игры.", color="red")
            break


if __name__ == "__main__":
    main()
