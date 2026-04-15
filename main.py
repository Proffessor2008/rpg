#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
                    МИР ВЕЧНЫХ ТЕНЕЙ - УЛЬТИМАТИВНАЯ ВЕРСИЯ
                        Ultimate Text RPG Experience
═══════════════════════════════════════════════════════════════════════════════

Полностью переработанная текстовая RPG с улучшенными механиками:
- Глубокая система боя с комбо и специальными атаками
- Расширенная система репутации с фракциями
- Динамическая экономика и торговля
- Система крафта и улучшения предметов
- Квесты с ветвящимися сюжетами
- Улучшенные ASCII модели персонажей и локаций
- Система достижений
- Дневник событий
- Погодная система
- Система выживания (голод, усталость)
"""

import json
import os
import random
import sqlite3
import textwrap
import time
import hashlib
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# ЦВЕТОВАЯ ПАЛИТРА И ВИЗУАЛЬНЫЕ ЭЛЕМЕНТЫ
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;129m"
    GOLD = "\033[38;5;220m"
    SILVER = "\033[38;5;250m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    @classmethod
    def colorize(cls, text: str, color: str, bg: str = None, effects: List[str] = None) -> str:
        """Apply color and effects to text"""
        result = color
        if bg:
            result += bg
        if effects:
            for effect in effects:
                result += effect
        result += text + cls.RESET
        return result


# Визуальные границы и разделители
class Borders:
    """Decorative border characters"""
    SINGLE = "─"
    DOUBLE = "═"
    THICK = "█"
    STAR = "✦"
    HEART = "♥"
    DIAMOND = "◆"
    CIRCLE = "●"
    SQUARE = "■"
    TRIANGLE = "▲"
    
    @classmethod
    def box(cls, title: str, width: int = 80, style: str = "double") -> str:
        """Create a decorative box with title"""
        if style == "double":
            h_line = cls.DOUBLE
            corner_tl = "╔"
            corner_tr = "╗"
            corner_bl = "╚"
            corner_br = "╝"
        elif style == "single":
            h_line = cls.SINGLE
            corner_tl = "┌"
            corner_tr = "┐"
            corner_bl = "└"
            corner_br = "┘"
        else:
            h_line = cls.STAR
            corner_tl = corner_tr = corner_bl = corner_br = cls.STAR
        
        padding = (width - len(title) - 4) // 2
        top = f"{corner_tl}{h_line * (padding)} {title} {h_line * (width - padding - len(title) - 3)}{corner_tr}"
        bottom = f"{corner_bl}{h_line * (width - 2)}{corner_br}"
        return f"\n{top}\n{bottom}"


# ═══════════════════════════════════════════════════════════════════════════════
# ИКОНКИ И СИМВОЛЫ
# ═══════════════════════════════════════════════════════════════════════════════

ICONS = {
    # Характеристики
    "health": "❤️", "max_health": "💖", "mana": "💙", "max_mana": "💎",
    "stamina": "⚡", "max_stamina": "🔋", "hunger": "🍖", "thirst": "💧",
    "attack": "⚔️", "defense": "🛡️", "magic_power": "🔮", "speed": "💨",
    "critical": "⭐", "dodge": "💫", "luck": "🍀", "level": "🏅",
    "experience": "✨", "gold": "💰", "silver": "🪙", "copper": "🔸",
    
    # Типы предметов
    "weapon_sword": "🗡️", "weapon_axe": "🪓", "weapon_mace": "🏑",
    "weapon_dagger": "🔪", "weapon_bow": "🏹", "weapon_staff": "🪄",
    "weapon_wand": "🪄", "armor_head": "🪖", "armor_chest": "🦺",
    "armor_legs": "👖", "armor_feet": "👢", "armor_shield": "🛡️",
    "accessory_ring": "💍", "accessory_amulet": "📿", "accessory_cloak": "🧥",
    "consumable_potion": "🧪", "consumable_food": "🍞", "consumable_scroll": "📜",
    "material_ore": "ite", "material_gem": "💎", "material_herb": "🌿",
    "material_leather": "🟤", "material_cloth": "🧵", "quest_item": "📦",
    
    # Действия
    "explore": "🔍", "travel": "🚶", "talk": "💬", "battle": "⚔️",
    "inventory": "🎒", "equipment": "🛠️", "quests": "📋", "party": "👥",
    "map": "🗺️", "rest": "⛺", "stats": "📊", "save": "💾", "load": "📂",
    "craft": "🔨", "trade": "💱", "skill": "🎯", "magic": "✨",
    
    # Статусы
    "buff": "✅", "debuff": "❌", "poison": "☠️", "burn": "🔥",
    "freeze": "❄️", "stun": "💫", "bleed": "🩸", "regenerate": "💚",
    
    # Локации
    "city": "🏰", "village": "🏡", "forest": "🌲", "cave": "🕳️",
    "dungeon": "🏛️", "mountain": "⛰️", "river": "🌊", "lake": "🏞️",
    "desert": "🏜️", "swamp": "🐊", "ruins": "🏚️", "tower": "🗼",
    
    # NPC и существа
    "human": "👤", "elf": "🧝", "dwarf": "🧔", "orc": "👹",
    "goblin": "👺", "skeleton": "💀", "ghost": "👻", "dragon": "🐉",
    "wolf": "🐺", "bear": "🐻", "snake": "🐍", "bird": "🦅",
    "merchant": "🧙", "guard": "💂", "king": "👑", "priest": "🙏",
    "blacksmith": "🔨", "alchemist": "⚗️", "innkeeper": "🍺",
    
    # Редкость предметов
    "common": "⚪", "uncommon": "🟢", "rare": "🔵",
    "epic": "🟣", "legendary": "🟠", "artifact": "🔴",
    
    # Погода
    "sun": "☀️", "cloud": "☁️", "rain": "🌧️", "snow": "❄️",
    "storm": "⛈️", "fog": "🌫️", "wind": "💨", "night": "🌙",
}


# ═══════════════════════════════════════════════════════════════════════════════
# КОНСТАНТЫ ИГРЫ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GameConfig:
    """Configuration constants for the game"""
    # Базовые значения
    BASE_HEALTH: int = 100
    BASE_MANA: int = 50
    BASE_STAMINA: int = 100
    BASE_ATTACK: int = 10
    BASE_DEFENSE: int = 5
    
    # Прогрессия
    XP_PER_LEVEL_BASE: int = 100
    XP_MULTIPLIER: float = 1.5
    HEALTH_PER_LEVEL: int = 20
    MANA_PER_LEVEL: int = 10
    STAT_POINTS_PER_LEVEL: int = 3
    SKILL_POINTS_PER_LEVEL: int = 1
    
    # Выживание
    MAX_HUNGER: int = 100
    MAX_THIRST: int = 100
    HUNGER_DECAY_RATE: int = 2  # per hour
    THIRST_DECAY_RATE: int = 3  # per hour
    STARVATION_DAMAGE: int = 5  # per hour when hunger = 0
    DEHYDRATION_DAMAGE: int = 8  # per hour when thirst = 0
    
    # Инвентарь
    BASE_INVENTORY_SLOTS: int = 20
    PARTY_MAX_SIZE: int = 4
    
    # Бой
    CRITICAL_HIT_BASE_CHANCE: float = 0.05
    DODGE_BASE_CHANCE: float = 0.03
    BLOCK_BASE_CHANCE: float = 0.10
    PARRY_BASE_CHANCE: float = 0.05
    
    # Экономика
    GOLD_START: int = 100
    PRICE_BUY_MULTIPLIER: float = 1.0
    PRICE_SELL_MULTIPLIER: float = 0.5
    
    # Репутация
    REP_NEUTRAL: int = 0
    REP_FRIENDLY: int = 50
    REP_HOSTILE: int = -50
    REP_MAX: int = 100
    REP_MIN: int = -100
    
    # Крафт
    CRAFT_SUCCESS_BASE: float = 0.8
    CRAFT_CRIT_CHANCE: float = 0.1


CONFIG = GameConfig()


# ═══════════════════════════════════════════════════════════════════════════════
# ПЕРЕЧИСЛЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

class Rarity(Enum):
    COMMON = ("common", "Обычный", 1.0, COLORS.WHITE)
    UNCOMMON = ("uncommon", "Необычный", 1.5, COLORS.GREEN)
    RARE = ("rare", "Редкий", 2.5, COLORS.BLUE)
    EPIC = ("epic", "Эпический", 4.0, COLORS.PURPLE)
    LEGENDARY = ("legendary", "Легендарный", 7.0, COLORS.GOLD)
    ARTIFACT = ("artifact", "Артефакт", 15.0, COLORS.RED)
    
    def __init__(self, key: str, name_ru: str, multiplier: float, color: str):
        self.key = key
        self.name_ru = name_ru
        self.multiplier = multiplier
        self.color = color


class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"
    ARCANE = "arcane"


class CombatAction(Enum):
    ATTACK = "attack"
    HEAVY_ATTACK = "heavy_attack"
    QUICK_ATTACK = "quick_attack"
    DEFEND = "defend"
    BLOCK = "block"
    PARRY = "parry"
    DODGE = "dodge"
    USE_ITEM = "use_item"
    CAST_SPELL = "cast_spell"
    SPECIAL_ABILITY = "special"
    FLEE = "flee"
    TAUNT = "taunt"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    CHARGE = "charge"
    COUNTER = "counter"


class CharacterRace(Enum):
    HUMAN = ("human", "Человек", "Универсальность", {"charisma": 2, "all_stats": 1})
    ELF = ("elf", "Эльф", "Магическая связь", {"intelligence": 3, "speed": 2, "constitution": -1})
    DWARF = ("dwarf", "Гном", "Каменная кожа", {"constitution": 3, "strength": 2, "intelligence": -1})
    ORC = ("orc", "Орк", "Боевая ярость", {"strength": 4, "constitution": 2, "intelligence": -2})
    FAIRY = ("fairy", "Фея", "Природная магия", {"intelligence": 3, "charisma": 3, "strength": -2})
    DARK_ELF = ("dark_elf", "Тёмный эльф", "Ночное зрение", {"agility": 3, "intelligence": 2, "charisma": -1})
    TIEFLING = ("tiefling", "Тифлинг", "Дьявольское наследие", {"charisma": 3, "intelligence": 2, "constitution": -1})
    DRAGONBORN = ("dragonborn", "Драконорождённый", "Дыхание дракона", {"strength": 3, "constitution": 3, "agility": -1})
    
    def __init__(self, key: str, name_ru: str, ability: str, stat_bonus: Dict[str, int]):
        self.key = key
        self.name_ru = name_ru
        self.ability = ability
        self.stat_bonus = stat_bonus


class CharacterClass(Enum):
    WARRIOR = ("warrior", "Воин", "Мастер оружия", ["strength", "constitution"])
    MAGE = ("mage", "Маг", "Повелитель стихий", ["intelligence", "wisdom"])
    ARCHER = ("archer", "Лучник", "Смертоносная точность", ["agility", "perception"])
    ROGUE = ("rogue", "Вор", "Тень смерти", ["agility", "charisma"])
    PALADIN = ("paladin", "Паладин", "Святой защитник", ["strength", "charisma"])
    CLERIC = ("cleric", "Жрец", "Божественная сила", ["wisdom", "constitution"])
    DRUID = ("druid", "Друид", "Хранитель природы", ["wisdom", "intelligence"])
    BARD = ("bard", "Бард", "Магия музыки", ["charisma", "agility"])
    NECROMANCER = ("necromancer", "Некромант", "Власть над смертью", ["intelligence", "constitution"])
    MONK = ("monk", "Монах", "Путь пустоты", ["agility", "wisdom"])
    
    def __init__(self, key: str, name_ru: str, ability: str, primary_stats: List[str]):
        self.key = key
        self.name_ru = name_ru
        self.ability = ability
        self.primary_stats = primary_stats


class GameDifficulty(Enum):
    PEACEFUL = ("peaceful", "Мирный", 0.5, 2.0, 0.0)
    EASY = ("easy", "Лёгкий", 0.75, 1.5, 0.1)
    NORMAL = ("normal", "Нормальный", 1.0, 1.0, 0.2)
    HARD = ("hard", "Сложный", 1.5, 0.75, 0.35)
    NIGHTMARE = ("nightmare", "Кошмар", 2.5, 0.5, 0.5)
    
    def __init__(self, key: str, name_ru: str, damage_mult: float, xp_mult: float, crit_chance_add: float):
        self.key = key
        self.name_ru = name_ru
        self.damage_multiplier = damage_mult
        self.xp_multiplier = xp_mult
        self.extra_crit_chance = crit_chance_add


class WeatherType(Enum):
    SUNNY = ("sunny", "Ясно", {"visibility": 1.2, "fire_damage": 1.1})
    CLOUDY = ("cloudy", "Облачно", {})
    RAINY = ("rainy", "Дождь", {"visibility": 0.8, "fire_damage": 0.7, "lightning_damage": 1.2})
    STORMY = ("stormy", "Гроза", {"visibility": 0.6, "fire_damage": 0.5, "lightning_damage": 1.5})
    SNOWY = ("snowy", "Снегопад", {"visibility": 0.7, "ice_damage": 1.2, "movement": 0.8})
    FOGGY = ("foggy", "Туман", {"visibility": 0.5, "stealth": 1.3})
    WINDY = ("windy", "Ветрено", {"ranged_accuracy": 0.8, "movement": 0.9})
    
    def __init__(self, key: str, name_ru: str, effects: Dict[str, float]):
        self.key = key
        self.name_ru = name_ru
        self.effects = effects


class TimeOfDay(Enum):
    DAWN = ("dawn", "Рассвет", 5, 7)
    MORNING = ("morning", "Утро", 7, 12)
    AFTERNOON = ("afternoon", "День", 12, 17)
    EVENING = ("evening", "Вечер", 17, 21)
    NIGHT = ("night", "Ночь", 21, 5)
    
    def __init__(self, key: str, name_ru: str, start_hour: int, end_hour: int):
        self.key = key
        self.name_ru = name_ru
        self.start_hour = start_hour
        self.end_hour = end_hour


# ═══════════════════════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause_game(message: str = "\nНажмите Enter для продолжения..."):
    """Pause the game with a custom message"""
    input(message)


def format_number(num: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def format_currency(gold: int) -> str:
    """Format gold amount with proper display"""
    if gold >= 1000000:
        return f"{ICONS['gold']} {gold / 1000000:.2f}M"
    elif gold >= 1000:
        return f"{ICONS['gold']} {gold / 1000:.1f}K"
    return f"{ICONS['gold']} {gold}"


def roll_dice(sides: int, count: int = 1, modifier: int = 0) -> int:
    """Roll dice with modifier"""
    total = sum(random.randint(1, sides) for _ in range(count))
    return total + modifier


def chance_success(probability: float) -> bool:
    """Check if an event succeeds based on probability"""
    return random.random() < probability


def weighted_choice(choices: List[Tuple[Any, float]]) -> Any:
    """Choose from weighted options"""
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        upto += weight
        if upto >= r:
            return choice
    return choices[-1][0]


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points"""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation"""
    return start + (end - start) * clamp(t, 0, 1)


def generate_id() -> str:
    """Generate unique ID"""
    timestamp = datetime.now().isoformat()
    random_data = str(random.random())
    combined = f"{timestamp}{random_data}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА СОБЫТИЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GameEvent:
    """Represents a game event for the event log"""
    id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str
    location: str
    participants: List[str]
    rewards: Dict[str, Any]
    icon: str


class EventLog:
    """Manages game event history"""
    
    def __init__(self, max_events: int = 100):
        self.events: List[GameEvent] = []
        self.max_events = max_events
    
    def add_event(self, event_type: str, title: str, description: str,
                  location: str = "", participants: List[str] = None,
                  rewards: Dict[str, Any] = None, icon: str = "📝"):
        """Add a new event to the log"""
        event = GameEvent(
            id=generate_id(),
            timestamp=datetime.now(),
            event_type=event_type,
            title=title,
            description=description,
            location=location,
            participants=participants or [],
            rewards=rewards or {},
            icon=icon
        )
        self.events.insert(0, event)
        if len(self.events) > self.max_events:
            self.events.pop()
    
    def get_recent_events(self, count: int = 10, event_type: str = None) -> List[GameEvent]:
        """Get recent events, optionally filtered by type"""
        events = self.events[:count]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events
    
    def clear(self):
        """Clear all events"""
        self.events.clear()
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "events": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "title": e.title,
                    "description": e.description,
                    "location": e.location,
                    "participants": e.participants,
                    "rewards": e.rewards,
                    "icon": e.icon
                }
                for e in self.events
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EventLog':
        """Deserialize from dictionary"""
        log = cls()
        for e in data.get("events", []):
            event = GameEvent(
                id=e["id"],
                timestamp=datetime.fromisoformat(e["timestamp"]),
                event_type=e["event_type"],
                title=e["title"],
                description=e["description"],
                location=e["location"],
                participants=e["participants"],
                rewards=e["rewards"],
                icon=e["icon"]
            )
            log.events.append(event)
        return log


# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА ДОСТИЖЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Achievement:
    """Represents an achievement"""
    id: str
    name: str
    description: str
    category: str
    requirement: Dict[str, Any]
    reward_xp: int
    reward_gold: int
    reward_title: Optional[str]
    icon: str
    unlocked: bool = False
    unlock_date: Optional[datetime] = None


class AchievementSystem:
    """Manages player achievements"""
    
    ACHIEVEMENTS = {
        "first_blood": Achievement(
            id="first_blood",
            name="Первая кровь",
            description="Победите первого врага",
            category="combat",
            requirement={"type": "kills", "count": 1},
            reward_xp=50,
            reward_gold=100,
            reward_title=None,
            icon="🩸"
        ),
        "slayer_10": Achievement(
            id="slayer_10",
            name="Убийца",
            description="Победите 10 врагов",
            category="combat",
            requirement={"type": "kills", "count": 10},
            reward_xp=200,
            reward_gold=500,
            reward_title="Убийца",
            icon="⚔️"
        ),
        "slayer_100": Achievement(
            id="slayer_100",
            name="Воин смерти",
            description="Победите 100 врагов",
            category="combat",
            requirement={"type": "kills", "count": 100},
            reward_xp=1000,
            reward_gold=2500,
            reward_title="Жнец душ",
            icon="💀"
        ),
        "treasure_hunter": Achievement(
            id="treasure_hunter",
            name="Искатель сокровищ",
            description="Найдите 50 сокровищ",
            category="exploration",
            requirement={"type": "treasures", "count": 50},
            reward_xp=300,
            reward_gold=1000,
            reward_title="Кладоискатель",
            icon="💎"
        ),
        "level_10": Achievement(
            id="level_10",
            name="Опытный искатель",
            description="Достигните 10 уровня",
            category="progression",
            requirement={"type": "level", "count": 10},
            reward_xp=500,
            reward_gold=1000,
            reward_title="Ветеран",
            icon="🏅"
        ),
        "level_50": Achievement(
            id="level_50",
            name="Мастер",
            description="Достигните 50 уровня",
            category="progression",
            requirement={"type": "level", "count": 50},
            reward_xp=5000,
            reward_gold=10000,
            reward_title="Легенда",
            icon="👑"
        ),
        "rich": Achievement(
            id="rich",
            name="Богач",
            description="Накопите 10000 золота",
            category="economy",
            requirement={"type": "gold", "count": 10000},
            reward_xp=500,
            reward_gold=0,
            reward_title="Магнат",
            icon="💰"
        ),
        "quest_master": Achievement(
            id="quest_master",
            name="Герой",
            description="Завершите 25 квестов",
            category="quests",
            requirement={"type": "quests_completed", "count": 25},
            reward_xp=1000,
            reward_gold=2000,
            reward_title="Защитник",
            icon="📜"
        ),
        "explorer": Achievement(
            id="explorer",
            name="Исследователь",
            description="Откройте все локации",
            category="exploration",
            requirement={"type": "locations_discovered", "count": 20},
            reward_xp=750,
            reward_gold=1500,
            reward_title="Первопроходец",
            icon="🗺️"
        ),
        "craftsman": Achievement(
            id="craftsman",
            name="Мастер-ремесленник",
            description="Создайте 50 предметов",
            category="crafting",
            requirement={"type": "items_crafted", "count": 50},
            reward_xp=600,
            reward_gold=1200,
            reward_title="Артификар",
            icon="🔨"
        ),
    }
    
    def __init__(self):
        self.unlocked: Dict[str, Achievement] = {}
        self.progress: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def check_achievement(self, achievement_id: str) -> bool:
        """Check if an achievement is unlocked"""
        return achievement_id in self.unlocked
    
    def update_progress(self, stat_type: str, value: int = 1) -> List[Achievement]:
        """Update progress for a statistic and return newly unlocked achievements"""
        newly_unlocked = []
        
        for ach_id, achievement in self.ACHIEVEMENTS.items():
            if ach_id in self.unlocked:
                continue
            
            req = achievement.requirement
            if req["type"] == stat_type:
                self.progress[stat_type][ach_id] += value
                
                if self.progress[stat_type][ach_id] >= req["count"]:
                    self.unlock_achievement(ach_id)
                    newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement"""
        if achievement_id not in self.ACHIEVEMENTS:
            return False
        
        if achievement_id in self.unlocked:
            return False
        
        achievement = self.ACHIEVEMENTS[achievement_id]
        achievement.unlocked = True
        achievement.unlock_date = datetime.now()
        self.unlocked[achievement_id] = achievement
        
        return True
    
    def get_unlocked(self) -> List[Achievement]:
        """Get list of unlocked achievements"""
        return list(self.unlocked.values())
    
    def get_locked(self) -> List[Achievement]:
        """Get list of locked achievements"""
        return [a for a in self.ACHIEVEMENTS.values() if a.id not in self.unlocked]
    
    def get_completion_percentage(self) -> float:
        """Get percentage of achievements unlocked"""
        if not self.ACHIEVEMENTS:
            return 0.0
        return (len(self.unlocked) / len(self.ACHIEVEMENTS)) * 100
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "unlocked": list(self.unlocked.keys()),
            "progress": dict(self.progress)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AchievementSystem':
        """Deserialize from dictionary"""
        system = cls()
        for ach_id in data.get("unlocked", []):
            if ach_id in cls.ACHIEVEMENTS:
                achievement = cls.ACHIEVEMENTS[ach_id]
                achievement.unlocked = True
                system.unlocked[ach_id] = achievement
        
        for stat_type, achievements in data.get("progress", {}).items():
            for ach_id, count in achievements.items():
                system.progress[stat_type][ach_id] = count
        
        return system


# Продолжение следует...


# ═══════════════════════════════════════════════════════════════════════════════
# КЛАССЫ ПРЕДМЕТОВ И ЭКИПИРОВКИ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Item:
    """Base item class"""
    id: str
    name: str
    description: str
    item_type: str
    rarity: Rarity
    value: int
    weight: float
    icon: str
    stackable: bool = True
    max_stack: int = 99
    quantity: int = 1
    
    def get_display_name(self) -> str:
        """Get colored display name based on rarity"""
        return f"{self.rarity.color}{self.name}{Colors.RESET}"
    
    def get_icon(self) -> str:
        """Get item icon"""
        return self.icon
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "rarity": self.rarity.key,
            "value": self.value,
            "weight": self.weight,
            "icon": self.icon,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Deserialize from dictionary"""
        rarity = Rarity[data["rarity"].upper()] if isinstance(data["rarity"], str) else data["rarity"]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            rarity=rarity,
            value=data["value"],
            weight=data["weight"],
            icon=data.get("icon", "📦"),
            stackable=data.get("stackable", True),
            max_stack=data.get("max_stack", 99),
            quantity=data.get("quantity", 1)
        )


@dataclass
class Weapon(Item):
    """Weapon item with combat stats"""
    damage_min: int = 5
    damage_max: int = 10
    attack_speed: float = 1.0
    critical_chance: float = 0.05
    critical_damage: float = 2.0
    damage_type: DamageType = DamageType.PHYSICAL
    required_strength: int = 0
    required_agility: int = 0
    required_level: int = 0
    enchantments: List[Dict] = field(default_factory=list)
    
    def get_dps(self) -> float:
        """Calculate damage per second"""
        avg_damage = (self.damage_min + self.damage_max) / 2
        return avg_damage / self.attack_speed
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "damage_min": self.damage_min,
            "damage_max": self.damage_max,
            "attack_speed": self.attack_speed,
            "critical_chance": self.critical_chance,
            "critical_damage": self.critical_damage,
            "damage_type": self.damage_type.value,
            "required_strength": self.required_strength,
            "required_agility": self.required_agility,
            "required_level": self.required_level,
            "enchantments": self.enchantments
        })
        return base
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Weapon':
        """Deserialize from dictionary"""
        weapon = super().from_dict(data)
        weapon.damage_min = data.get("damage_min", 5)
        weapon.damage_max = data.get("damage_max", 10)
        weapon.attack_speed = data.get("attack_speed", 1.0)
        weapon.critical_chance = data.get("critical_chance", 0.05)
        weapon.critical_damage = data.get("critical_damage", 2.0)
        weapon.damage_type = DamageType(data.get("damage_type", "physical"))
        weapon.required_strength = data.get("required_strength", 0)
        weapon.required_agility = data.get("required_agility", 0)
        weapon.required_level = data.get("required_level", 0)
        weapon.enchantments = data.get("enchantments", [])
        return weapon


@dataclass
class Armor(Item):
    """Armor item with defense stats"""
    defense: int = 5
    magic_resist: int = 0
    durability: int = 100
    max_durability: int = 100
    armor_slot: str = "chest"
    required_strength: int = 0
    required_level: int = 0
    enchantments: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "defense": self.defense,
            "magic_resist": self.magic_resist,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "armor_slot": self.armor_slot,
            "required_strength": self.required_strength,
            "required_level": self.required_level,
            "enchantments": self.enchantments
        })
        return base
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Armor':
        """Deserialize from dictionary"""
        armor = super().from_dict(data)
        armor.defense = data.get("defense", 5)
        armor.magic_resist = data.get("magic_resist", 0)
        armor.durability = data.get("durability", 100)
        armor.max_durability = data.get("max_durability", 100)
        armor.armor_slot = data.get("armor_slot", "chest")
        armor.required_strength = data.get("required_strength", 0)
        armor.required_level = data.get("required_level", 0)
        armor.enchantments = data.get("enchantments", [])
        return armor


@dataclass
class Consumable(Item):
    """Consumable item with effects"""
    effect_type: str = "heal"
    effect_value: int = 50
    effect_duration: int = 0
    cooldown: int = 0
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "effect_duration": self.effect_duration,
            "cooldown": self.cooldown
        })
        return base
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Consumable':
        """Deserialize from dictionary"""
        consumable = super().from_dict(data)
        consumable.effect_type = data.get("effect_type", "heal")
        consumable.effect_value = data.get("effect_value", 50)
        consumable.effect_duration = data.get("effect_duration", 0)
        consumable.cooldown = data.get("cooldown", 0)
        return consumable


@dataclass
class Material(Item):
    """Crafting material"""
    material_type: str = "ore"
    quality: int = 1
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "material_type": self.material_type,
            "quality": self.quality
        })
        return base
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Material':
        """Deserialize from dictionary"""
        material = super().from_dict(data)
        material.material_type = data.get("material_type", "ore")
        material.quality = data.get("quality", 1)
        return material


@dataclass
class QuestItem(Item):
    """Quest-related item"""
    quest_id: str = ""
    quest_stage: int = 0
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        base = super().to_dict()
        base.update({
            "quest_id": self.quest_id,
            "quest_stage": self.quest_stage
        })
        return base
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestItem':
        """Deserialize from dictionary"""
        quest_item = super().from_dict(data)
        quest_item.quest_id = data.get("quest_id", "")
        quest_item.quest_stage = data.get("quest_stage", 0)
        return quest_item


# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА СТАТУСНЫХ ЭФФЕКТОВ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StatusEffect:
    """Represents a status effect (buff or debuff)"""
    id: str
    name: str
    description: str
    effect_type: str  # buff, debuff
    stat_modifiers: Dict[str, float]
    duration: int  # in turns/seconds
    remaining_duration: int
    stacks: int = 1
    max_stacks: int = 99
    tick_effect: Optional[Dict] = None  # Effect applied each turn
    
    def is_expired(self) -> bool:
        """Check if effect has expired"""
        return self.remaining_duration <= 0
    
    def tick(self) -> Optional[Dict]:
        """Apply tick effect and reduce duration"""
        self.remaining_duration -= 1
        return self.tick_effect if self.tick_effect and self.remaining_duration >= 0 else None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "effect_type": self.effect_type,
            "stat_modifiers": self.stat_modifiers,
            "duration": self.duration,
            "remaining_duration": self.remaining_duration,
            "stacks": self.stacks,
            "max_stacks": self.max_stacks,
            "tick_effect": self.tick_effect
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StatusEffect':
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            effect_type=data["effect_type"],
            stat_modifiers=data["stat_modifiers"],
            duration=data["duration"],
            remaining_duration=data["remaining_duration"],
            stacks=data.get("stacks", 1),
            max_stacks=data.get("max_stacks", 99),
            tick_effect=data.get("tick_effect")
        )


# ═══════════════════════════════════════════════════════════════════════════════
# БАЗА ДАННЫХ ПРЕДМЕТОВ
# ═══════════════════════════════════════════════════════════════════════════════

class ItemDatabase:
    """Database of all items in the game"""
    
    WEAPONS = {
        "rusty_sword": Weapon(
            id="rusty_sword", name="Ржавый меч", description="Старый, покрытый ржавчиной меч",
            item_type="weapon", rarity=Rarity.COMMON, value=10, weight=3.0, icon="🗡️",
            damage_min=3, damage_max=6, attack_speed=1.2, required_level=1
        ),
        "iron_sword": Weapon(
            id="iron_sword", name="Железный меч", description="Надёжный меч из кованого железа",
            item_type="weapon", rarity=Rarity.COMMON, value=50, weight=4.0, icon="🗡️",
            damage_min=8, damage_max=12, attack_speed=1.0, required_strength=5, required_level=3
        ),
        "steel_sword": Weapon(
            id="steel_sword", name="Стальной меч", description="Острый меч из качественной стали",
            item_type="weapon", rarity=Rarity.UNCOMMON, value=150, weight=3.5, icon="⚔️",
            damage_min=12, damage_max=18, attack_speed=1.0, required_strength=10, required_level=5
        ),
        "silver_blade": Weapon(
            id="silver_blade", name="Серебряный клинок", description="Благородный клинок, эффективен против нежити",
            item_type="weapon", rarity=Rarity.RARE, value=400, weight=3.0, icon="✨",
            damage_min=15, damage_max=22, attack_speed=1.1, critical_chance=0.08,
            required_strength=15, required_level=10
        ),
        "dragon_slayer": Weapon(
            id="dragon_slayer", name="Убийца драконов", description="Легендарный меч, созданный для охоты на драконов",
            item_type="weapon", rarity=Rarity.LEGENDARY, value=5000, weight=5.0, icon="🐉",
            damage_min=40, damage_max=60, attack_speed=0.9, critical_chance=0.15, critical_damage=3.0,
            required_strength=30, required_level=25
        ),
        "shadow_dagger": Weapon(
            id="shadow_dagger", name="Кинжал тени", description="Тихий и смертоносный кинжал ассасина",
            item_type="weapon", rarity=Rarity.EPIC, value=2000, weight=1.0, icon="🗡️",
            damage_min=20, damage_max=30, attack_speed=1.8, critical_chance=0.25, critical_damage=2.5,
            required_agility=25, required_level=20
        ),
        "battle_axe": Weapon(
            id="battle_axe", name="Боевой топор", description="Мощный топор для сокрушительных ударов",
            item_type="weapon", rarity=Rarity.UNCOMMON, value=200, weight=6.0, icon="🪓",
            damage_min=15, damage_max=25, attack_speed=1.5, required_strength=12, required_level=7
        ),
        "war_hammer": Weapon(
            id="war_hammer", name="Военный молот", description="Тяжёлый молот, пробивающий любую броню",
            item_type="weapon", rarity=Rarity.RARE, value=500, weight=8.0, icon="🏑",
            damage_min=20, damage_max=35, attack_speed=1.8, required_strength=20, required_level=12
        ),
        "elven_bow": Weapon(
            id="elven_bow", name="Эльфийский лук", description="Изящный лук эльфийской работы",
            item_type="weapon", rarity=Rarity.RARE, value=600, weight=2.0, icon="🏹",
            damage_min=18, damage_max=28, attack_speed=1.3, critical_chance=0.12,
            required_agility=18, required_level=12
        ),
        "staff_of_fire": Weapon(
            id="staff_of_fire", name="Посох огня", description="Магический посох, усиливающий огненные заклинания",
            item_type="weapon", rarity=Rarity.EPIC, value=1500, weight=3.0, icon="🔥",
            damage_min=25, damage_max=40, attack_speed=1.0, damage_type=DamageType.FIRE,
            required_strength=5, required_level=18
        ),
    }
    
    ARMORS = {
        "cloth_tunic": Armor(
            id="cloth_tunic", name="Тканая туника", description="Простая одежда из грубой ткани",
            item_type="armor", rarity=Rarity.COMMON, value=15, weight=1.0, icon="👕",
            defense=2, magic_resist=1, armor_slot="chest", required_level=1
        ),
        "leather_armor": Armor(
            id="leather_armor", name="Кожаная броня", description="Гибкая броня из выделанной кожи",
            item_type="armor", rarity=Rarity.COMMON, value=80, weight=3.0, icon="🦺",
            defense=5, magic_resist=2, armor_slot="chest", required_level=3
        ),
        "chain_mail": Armor(
            id="chain_mail", name="Кольчуга", description="Надёжная кольчуга из стальных колец",
            item_type="armor", rarity=Rarity.UNCOMMON, value=250, weight=8.0, icon="🛡️",
            defense=12, magic_resist=3, armor_slot="chest", required_strength=8, required_level=8
        ),
        "plate_armor": Armor(
            id="plate_armor", name="Латная броня", description="Тяжёлая броня из цельных пластин",
            item_type="armor", rarity=Rarity.RARE, value=800, weight=15.0, icon="🦾",
            defense=25, magic_resist=5, armor_slot="chest", required_strength=20, required_level=15
        ),
        "dragon_scale_armor": Armor(
            id="dragon_scale_armor", name="Броня из чешуи дракона", description="Невероятно прочная броня из драконьей чешуи",
            item_type="armor", rarity=Rarity.LEGENDARY, value=8000, weight=12.0, icon="🐉",
            defense=50, magic_resist=25, armor_slot="chest", required_strength=35, required_level=30
        ),
        "iron_helmet": Armor(
            id="iron_helmet", name="Железный шлем", description="Защищает голову от ударов",
            item_type="armor", rarity=Rarity.COMMON, value=60, weight=3.0, icon="🪖",
            defense=4, magic_resist=1, armor_slot="head", required_level=3
        ),
        "steel_boots": Armor(
            id="steel_boots", name="Стальные сапоги", description="Прочные сапоги для долгих походов",
            item_type="armor", rarity=Rarity.UNCOMMON, value=120, weight=4.0, icon="👢",
            defense=6, magic_resist=2, armor_slot="feet", required_level=6
        ),
    }
    
    CONSUMABLES = {
        "health_potion_small": Consumable(
            id="health_potion_small", name="Малое зелье здоровья", description="Восстанавливает 50 здоровья",
            item_type="consumable", rarity=Rarity.COMMON, value=25, weight=0.5, icon="🧪",
            effect_type="heal", effect_value=50, stackable=True, max_stack=20
        ),
        "health_potion_medium": Consumable(
            id="health_potion_medium", name="Среднее зелье здоровья", description="Восстанавливает 150 здоровья",
            item_type="consumable", rarity=Rarity.UNCOMMON, value=75, weight=0.5, icon="🧪",
            effect_type="heal", effect_value=150, stackable=True, max_stack=20
        ),
        "health_potion_large": Consumable(
            id="health_potion_large", name="Большое зелье здоровья", description="Восстанавливает 500 здоровья",
            item_type="consumable", rarity=Rarity.RARE, value=200, weight=0.5, icon="🧪",
            effect_type="heal", effect_value=500, stackable=True, max_stack=10
        ),
        "mana_potion": Consumable(
            id="mana_potion", name="Зелье маны", description="Восстанавливает 100 маны",
            item_type="consumable", rarity=Rarity.UNCOMMON, value=50, weight=0.5, icon="💙",
            effect_type="restore_mana", effect_value=100, stackable=True, max_stack=20
        ),
        "stamina_potion": Consumable(
            id="stamina_potion", name="Зелье выносливости", description="Восстанавливает 100 выносливости",
            item_type="consumable", rarity=Rarity.UNCOMMON, value=40, weight=0.5, icon="⚡",
            effect_type="restore_stamina", effect_value=100, stackable=True, max_stack=20
        ),
        "bread": Consumable(
            id="bread", name="Хлеб", description="Простая еда, восстанавливает голод",
            item_type="consumable", rarity=Rarity.COMMON, value=5, weight=0.3, icon="🍞",
            effect_type="food", effect_value=20, stackable=True, max_stack=10
        ),
        "meat": Consumable(
            id="meat", name="Жареное мясо", description="Сытная еда, хорошо восстанавливает силы",
            item_type="consumable", rarity=Rarity.COMMON, value=15, weight=0.5, icon="🍖",
            effect_type="food", effect_value=50, stackable=True, max_stack=10
        ),
        "antidote": Consumable(
            id="antidote", name="Противоядие", description="Снимает эффект отравления",
            item_type="consumable", rarity=Rarity.UNCOMMON, value=30, weight=0.3, icon="💊",
            effect_type="cure_poison", effect_value=0, stackable=True, max_stack=10
        ),
        "strength_elixir": Consumable(
            id="strength_elixir", name="Эликсир силы", description="Временно увеличивает силу на 30 секунд",
            item_type="consumable", rarity=Rarity.RARE, value=150, weight=0.3, icon="💪",
            effect_type="buff_strength", effect_value=10, effect_duration=30, stackable=True, max_stack=5
        ),
    }
    
    MATERIALS = {
        "iron_ore": Material(
            id="iron_ore", name="Железная руда", description="Руда для выплавки железа",
            item_type="material", rarity=Rarity.COMMON, value=10, weight=2.0, icon="ite",
            material_type="ore", quality=1
        ),
        "gold_ore": Material(
            id="gold_ore", name="Золотая руда", description="Ценная руда с содержанием золота",
            item_type="material", rarity=Rarity.UNCOMMON, value=50, weight=2.0, icon="✨",
            material_type="ore", quality=2
        ),
        "diamond": Material(
            id="diamond", name="Алмаз", description="Драгоценный камень высшей качества",
            item_type="material", rarity=Rarity.RARE, value=500, weight=0.1, icon="💎",
            material_type="gem", quality=5
        ),
        "leather_strip": Material(
            id="leather_strip", name="Кожаные полосы", description="Полосы кожи для крафта",
            item_type="material", rarity=Rarity.COMMON, value=5, weight=0.5, icon="🟤",
            material_type="leather", quality=1
        ),
        "herb": Material(
            id="herb", name="Лекарственная трава", description="Трава для создания зелий",
            item_type="material", rarity=Rarity.COMMON, value=8, weight=0.2, icon="🌿",
            material_type="herb", quality=1
        ),
        "wood": Material(
            id="wood", name="Древесина", description="Обычная древесина для крафта",
            item_type="material", rarity=Rarity.COMMON, value=3, weight=1.0, icon="🪵",
            material_type="wood", quality=1
        ),
    }
    
    QUEST_ITEMS = {
        "ancient_key": QuestItem(
            id="ancient_key", name="Древний ключ", description="Странный ключ с древними символами",
            item_type="quest_item", rarity=Rarity.RARE, value=0, weight=0.5, icon="🔑",
            stackable=False
        ),
        "dragon_egg": QuestItem(
            id="dragon_egg", name="Яйцо дракона", description="Тёплое яйцо с пульсирующей энергией",
            item_type="quest_item", rarity=Rarity.LEGENDARY, value=0, weight=3.0, icon="🥚",
            stackable=False
        ),
        "kings_letter": QuestItem(
            id="kings_letter", name="Письмо короля", description="Запечатанное письмо с королевской печатью",
            item_type="quest_item", rarity=Rarity.UNCOMMON, value=0, weight=0.1, icon="📜",
            stackable=False
        ),
    }
    
    @classmethod
    def get_all_items(cls) -> Dict[str, Item]:
        """Get all items from database"""
        all_items = {}
        all_items.update(cls.WEAPONS)
        all_items.update(cls.ARMORS)
        all_items.update(cls.CONSUMABLES)
        all_items.update(cls.MATERIALS)
        all_items.update(cls.QUEST_ITEMS)
        return all_items
    
    @classmethod
    def get_item(cls, item_id: str) -> Optional[Item]:
        """Get specific item by ID"""
        all_items = cls.get_all_items()
        return all_items.get(item_id)
    
    @classmethod
    def create_item(cls, item_id: str, quantity: int = 1) -> Optional[Item]:
        """Create a new instance of an item"""
        item = cls.get_item(item_id)
        if item:
            # Create a copy with specified quantity
            item_copy = type(item)(**item.to_dict())
            item_copy.quantity = quantity
            return item_copy
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА РЕПУТАЦИИ И ФРАКЦИЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Faction:
    """Represents a faction in the game world"""
    id: str
    name: str
    description: str
    leader: str
    headquarters: str
    symbol: str
    colors: Tuple[str, str]
    starting_reputation: int = 0
    
    HATED_THRESHOLD: int = -80
    HOSTILE_THRESHOLD: int = -40
    NEUTRAL_THRESHOLD: int = -10
    FRIENDLY_THRESHOLD: int = 30
    ALLIED_THRESHOLD: int = 70
    
    def get_relation_status(self, reputation: int) -> str:
        if reputation <= self.HATED_THRESHOLD:
            return "Ненависть"
        elif reputation <= self.HOSTILE_THRESHOLD:
            return "Вражда"
        elif reputation <= self.NEUTRAL_THRESHOLD:
            return "Нейтралитет"
        elif reputation <= self.FRIENDLY_THRESHOLD:
            return "Дружелюбие"
        elif reputation <= self.ALLIED_THRESHOLD:
            return "Союз"
        else:
            return "Почтение"
    
    def get_relation_icon(self, reputation: int) -> str:
        status = self.get_relation_status(reputation)
        icons = {"Ненависть": "💀", "Вражда": "⚔️", "Нейтралитет": "😐",
                 "Дружелюбие": "😊", "Союз": "🤝", "Почтение": "👑"}
        return icons.get(status, "❓")
    
    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name, "description": self.description,
                "leader": self.leader, "headquarters": self.headquarters,
                "symbol": self.symbol, "colors": self.colors,
                "starting_reputation": self.starting_reputation}


class ReputationSystem:
    """Manages player reputation with factions"""
    
    FACTIONS = {
        "kingdom_guard": Faction("kingdom_guard", "Королевская стража",
            "Защитники королевства и его жителей", "Генерал Маркус",
            "Королевский замок", "🛡️", (Colors.BLUE, Colors.GOLD), 0),
        "thieves_guild": Faction("thieves_guild", "Гильдия воров",
            "Тайная организация мастеров теневого ремесла", "Тень",
            "Подземелья города", "🗡️", (Colors.PURPLE, Colors.BLACK), -20),
        "mages_circle": Faction("mages_circle", "Круг магов",
            "Хранители магических знаний и тайн", "Архимаг Элдрион",
            "Башня магов", "🔮", (Colors.CYAN, Colors.PURPLE), 10),
        "merchants_guild": Faction("merchants_guild", "Гильдия торговцев",
            "Могущественное объединение купцов и банкиров", "Лорд Голдберри",
            "Торговый квартал", "💰", (Colors.GREEN, Colors.GOLD), 5),
        "hunters_lodge": Faction("hunters_lodge", "Ложа охотников",
            "Мастера выслеживания и охоты на монстров", "Охотник Гарретт",
            "Охотничий домик", "🏹", (Colors.GREEN, Colors.WHITE), 0),
        "necromancers": Faction("necromancers", "Некроманты",
            "Тёмные маги, изучающие смерть и нежить", "Лич Морган",
            "Склеп теней", "💀", (Colors.BLACK, Colors.PURPLE), -50),
        "druids_grove": Faction("druids_grove", "Роща друидов",
            "Защитники природы и древних традиций", "Старейшина Лиф",
            "Священная роща", "🌿", (Colors.GREEN, Colors.CYAN), 15),
        "paladins_order": Faction("paladins_order", "Орден паладинов",
            "Священные воины света и справедливости", "Верховный паладин Артос",
            "Храм света", "⚜️", (Colors.GOLD, Colors.WHITE), 20),
    }
    
    def __init__(self):
        self.reputation: Dict[str, int] = {}
        self.discovered_factions: Set[str] = set()
        for faction_id, faction in self.FACTIONS.items():
            self.reputation[faction_id] = faction.starting_reputation
    
    def get_reputation(self, faction_id: str) -> int:
        return self.reputation.get(faction_id, 0)
    
    def modify_reputation(self, faction_id: str, amount: int, reason: str = "") -> int:
        if faction_id not in self.FACTIONS:
            return 0
        old_rep = self.reputation.get(faction_id, 0)
        new_rep = clamp(old_rep + amount, CONFIG.REP_MIN, CONFIG.REP_MAX)
        self.reputation[faction_id] = new_rep
        self.discover_faction(faction_id)
        return new_rep - old_rep
    
    def discover_faction(self, faction_id: str):
        self.discovered_factions.add(faction_id)
    
    def is_discovered(self, faction_id: str) -> bool:
        return faction_id in self.discovered_factions
    
    def get_relation_status(self, faction_id: str) -> str:
        if faction_id not in self.FACTIONS:
            return "Неизвестно"
        faction = self.FACTIONS[faction_id]
        rep = self.get_reputation(faction_id)
        return faction.get_relation_status(rep)
    
    def get_all_relations(self) -> List[Dict]:
        relations = []
        for faction_id, faction in self.FACTIONS.items():
            rep = self.get_reputation(faction_id)
            relations.append({
                "faction": faction, "reputation": rep,
                "status": faction.get_relation_status(rep),
                "icon": faction.get_relation_icon(rep),
                "discovered": self.is_discovered(faction_id)
            })
        return sorted(relations, key=lambda x: x["reputation"], reverse=True)
    
    def can_access_faction_services(self, faction_id: str, service_level: str) -> bool:
        rep = self.get_reputation(faction_id)
        requirements = {"basic": -50, "standard": 0, "advanced": 30, "elite": 70, "leader": 90}
        return rep >= requirements.get(service_level, 0)
    
    def to_dict(self) -> Dict:
        return {"reputation": self.reputation, "discovered_factions": list(self.discovered_factions)}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReputationSystem':
        system = cls()
        system.reputation = data.get("reputation", {})
        system.discovered_factions = set(data.get("discovered_factions", []))
        return system


# ═══════════════════════════════════════════════════════════════════════════════
# СИСТЕМА НАВЫКОВ И УМЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Skill:
    """Represents a player skill"""
    id: str
    name: str
    description: str
    category: str
    max_level: int = 100
    current_level: int = 0
    experience: int = 0
    xp_to_next_level: int = 100
    bonus_per_level: Dict[str, float] = field(default_factory=dict)
    
    def add_experience(self, amount: int) -> Tuple[int, bool]:
        self.experience += amount
        leveled_up = False
        while self.experience >= self.xp_to_next_level and self.current_level < self.max_level:
            self.experience -= self.xp_to_next_level
            self.current_level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.2)
            leveled_up = True
        overflow = self.experience if self.current_level >= self.max_level else 0
        return overflow, leveled_up
    
    def get_bonus(self, stat: str) -> float:
        return self.bonus_per_level.get(stat, 0) * self.current_level
    
    def get_total_bonus(self) -> Dict[str, float]:
        return {stat: bonus * self.current_level for stat, bonus in self.bonus_per_level.items()}
    
    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name, "description": self.description,
                "category": self.category, "max_level": self.max_level,
                "current_level": self.current_level, "experience": self.experience,
                "xp_to_next_level": self.xp_to_next_level, "bonus_per_level": self.bonus_per_level}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        return cls(id=data["id"], name=data["name"], description=data["description"],
                   category=data["category"], max_level=data.get("max_level", 100),
                   current_level=data.get("current_level", 0), experience=data.get("experience", 0),
                   xp_to_next_level=data.get("xp_to_next_level", 100),
                   bonus_per_level=data.get("bonus_per_level", {}))


class SkillSystem:
    """Manages player skills"""
    
    SKILLS = {
        "swordsmanship": Skill("swordsmanship", "Фехтование", "Мастерство владения мечами",
            "combat", bonus_per_level={"sword_damage": 0.02, "attack_speed": 0.005}),
        "archery": Skill("archery", "Стрельба из лука", "Точность и урон луков",
            "combat", bonus_per_level={"bow_damage": 0.02, "critical_chance": 0.002}),
        "magic": Skill("magic", "Магия", "Сила заклинаний и запас маны",
            "combat", bonus_per_level={"spell_power": 0.03, "max_mana": 0.02}),
        "defense": Skill("defense", "Защита", "Умение блокировать и уклоняться",
            "combat", bonus_per_level={"block_chance": 0.01, "dodge_chance": 0.005}),
        "blacksmithing": Skill("blacksmithing", "Кузнечное дело", "Создание оружия и брони",
            "crafting", bonus_per_level={"craft_quality": 0.01, "material_yield": 0.005}),
        "alchemy": Skill("alchemy", "Алхимия", "Создание зелий и эликсиров",
            "crafting", bonus_per_level={"potion_power": 0.02, "craft_chance": 0.01}),
        "barter": Skill("barter", "Торговля", "Умение торговаться",
            "social", bonus_per_level={"buy_discount": 0.005, "sell_bonus": 0.01}),
        "stealth": Skill("stealth", "Скрытность", "Перемещение незамеченным",
            "survival", bonus_per_level={"stealth_effectiveness": 0.02, "backstab_damage": 0.03}),
        "lockpicking": Skill("lockpicking", "Взлом замков", "Открытие замков без ключа",
            "survival", bonus_per_level={"lockpick_success": 0.02}),
        "survival": Skill("survival", "Выживание", "Навыки жизни в дикой природе",
            "survival", bonus_per_level={"hunger_decay": -0.01, "thirst_decay": -0.01}),
    }
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_points: int = 0
        for skill_id, skill_template in self.SKILLS.items():
            self.skills[skill_id] = Skill(
                id=skill_id, name=skill_template.name, description=skill_template.description,
                category=skill_template.category, bonus_per_level=skill_template.bonus_per_level.copy()
            )
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)
    
    def add_skill_xp(self, skill_id: str, amount: int) -> Tuple[int, bool]:
        if skill_id not in self.skills:
            return 0, False
        return self.skills[skill_id].add_experience(amount)
    
    def upgrade_skill(self, skill_id: str) -> bool:
        if skill_id not in self.skills or self.skill_points <= 0:
            return False
        skill = self.skills[skill_id]
        if skill.current_level >= skill.max_level:
            return False
        skill.current_level += 1
        self.skill_points -= 1
        return True
    
    def get_total_bonuses(self) -> Dict[str, float]:
        bonuses = defaultdict(float)
        for skill in self.skills.values():
            for stat, bonus in skill.get_total_bonus().items():
                bonuses[stat] += bonus
        return dict(bonuses)
    
    def to_dict(self) -> Dict:
        return {"skills": {sid: s.to_dict() for sid, s in self.skills.items()},
                "skill_points": self.skill_points}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SkillSystem':
        system = cls()
        system.skill_points = data.get("skill_points", 0)
        for skill_id, skill_data in data.get("skills", {}).items():
            if skill_id in cls.SKILLS:
                template = cls.SKILLS[skill_id]
                system.skills[skill_id] = Skill(
                    id=skill_id, name=skill_data.get("name", template.name),
                    description=skill_data.get("description", template.description),
                    category=skill_data.get("category", template.category),
                    max_level=skill_data.get("max_level", template.max_level),
                    current_level=skill_data.get("current_level", 0),
                    experience=skill_data.get("experience", 0),
                    xp_to_next_level=skill_data.get("xp_to_next_level", template.xp_to_next_level),
                    bonus_per_level=skill_data.get("bonus_per_level", template.bonus_per_level.copy())
                )
        return system


# Продолжение следует...
