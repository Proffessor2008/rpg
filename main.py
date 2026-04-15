import json
import os
import random
import sqlite3
import textwrap
import time
from enum import Enum
from typing import Dict, List, Any

# Color constants for visual enhancement
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_WHITE = "\033[97m"

# Улучшенные границы и разделители
BANNER_BORDER = "✦" * 60
LOCATION_BORDER = "♥" * 80
BATTLE_BORDER = "⚔️" * 25 + " БИТВА " + "⚔️" * 25
MENU_BORDER = "•" * 50
SECTION_BORDER = "─" * 40

# Улучшенные иконки для инвентаря
INVENTORY_ICONS = {
    "weapon": "⚔️",
    "armor": "🛡️",
    "shield": "🔰",
    "consumable": "💊",
    "material": "🔧",
    "quest_item": "📜",
    "key": "🔑",
    "artifact": "🔮",
    "other": "📦"
}

# Улучшенные иконки для характеристик
STATS_ICONS = {
    "health": "❤️",
    "attack": "⚔️",
    "defense": "🛡️",
    "critical_chance": "⭐",
    "dodge_chance": "💫",
    "level": "🏅",
    "experience": "⚡",
    "gold": "💰",
    "inventory": "🎒",
    "quests": "📜"
}

# Улучшенные иконки для способностей
ABILITY_ICONS = {
    "strength": "💪",
    "agility": "🏃",
    "intelligence": "🧠",
    "charisma": "💬",
    "stamina": "🔋"
}

# Улучшенные иконки для навыков
SKILL_ICONS = {
    "swordsmanship": "⚔️",
    "archery": "🏹",
    "magic": "🔮",
    "stealth": "👤",
    "alchemy": "🧪",
    "barter": "💎"
}

# Улучшенные иконки для рас
RACE_ICONS = {
    "человек": "👤",
    "эльф": "🧝",
    "гном": "🧔",
    "орк": "👹",
    "фея": "🧚"
}

# Улучшенные иконки для действий
ACTION_ICONS = {
    "explore": "🔍",
    "travel": "🚶",
    "talk": "🗣️",
    "battle": "⚔️",
    "inventory": "🎒",
    "equipment": "🛡️",
    "quests": "📜",
    "party": "👥",
    "map": "🌍",
    "rest": "⛺",
    "stats": "📊",
    "save": "💾"
}


class GameConstants:
    """Game constants and configuration values"""
    MAX_HEALTH = 100
    XP_PER_LEVEL = 100
    STARTING_GOLD = 50
    CRITICAL_HIT_CHANCE_BASE = 0.1
    DODGE_CHANCE_BASE = 0.05
    INVENTORY_CAPACITY = 20
    PARTY_MAX_SIZE = 3
    SKILL_POINTS_PER_LEVEL = 1


class CombatAction(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    USE_ITEM = "use_item"
    SPECIAL = "special"
    FLEE = "flee"


class CharacterRace(Enum):
    HUMAN = "человек"
    ELF = "эльф"
    DWARF = "гном"
    ORC = "орк"
    FAIRY = "фея"


class CharacterClass(Enum):
    WARRIOR = "воин"
    MAGE = "маг"
    ARCHER = "лучник"
    ROGUE = "вор"
    HEALER = "целитель"
    PALADIN = "паладин"


class GameDifficulty(Enum):
    EASY = "легкая"
    NORMAL = "нормальная"
    HARD = "сложная"


def init_database():
    """Инициализация базы данных SQLite для сохранения игрового прогресса"""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    # Создаем таблицу, если она не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rpg_progress (
        user_id INTEGER PRIMARY KEY,
        current_location TEXT,
        inventory TEXT,
        health INTEGER,
        level INTEGER,
        experience INTEGER,
        gold INTEGER,
        story_progress TEXT,
        player_name TEXT,
        player_class TEXT,
        race TEXT,
        abilities TEXT,
        skills TEXT,
        armor_slots TEXT,
        active_quests TEXT,
        completed_quests TEXT,
        reputation TEXT,
        party_members TEXT,
        artifacts TEXT,
        difficulty TEXT
    )
    ''')
    conn.commit()
    conn.close()


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def colorful_print(text):
    """Print text with color formatting"""
    print(f"{text}")


def typewriter_effect(text, delay=0.03):
    """Display text with typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def pause_game(message="Нажмите Enter, чтобы продолжить..."):
    """Pause the game with a custom message"""
    input(f"\n{message}")


def format_currency(amount):
    """Format gold amount with currency symbol"""
    return f"💰 {amount} золота"


def show_loading_animation(message="Загрузка", duration=2):
    """Show a loading animation with a message"""
    print(f"\n{message}", end='', flush=True)
    for _ in range(duration * 2):
        print(".", end='', flush=True)
        time.sleep(0.5)
    print(f"\n")


def display_ascii_art(art_type):
    """Display ASCII art based on type with improved models"""
    art_dict = {
        "title": """
╔══════════════════════════════════════════════════════════════════════════════╗
║    ███╗   ███╗██╗██╗  ██╗███████╗███████╗██╗   ██╗    ██████╗ ███████╗██████╗  ║
║    ████╗ ████║██║██║ ██╔╝██╔════╝██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝██╔══██╗ ║
║    ██╔████╔██║██║█████╔╝ █████╗  █████╗   ╚████╔╝     ██████╔╝█████╗  ██████╔╝ ║
║    ██║╚██╔╝██║██║██╔═██╗ ██╔══╝  ██╔══╝    ╚██╔╝      ██╔══██╗██╔══╝  ██╔══██╗ ║
║    ██║ ╚═╝ ██║██║██║  ██╗███████╗███████╗   ██║       ██████╔╝███████╗██║  ██║ ║
║    ╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═════╝ ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║                  ТЕКСТОВАЯ РПГ "МИР ВЕЧНЫХ ТЕНЕЙ" v2.0                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
""",
        "warrior": """
    ╔══════════════════╗
    ║    ⚔️ ВОИН ⚔️    ║
    ╚══════════════════╝
         /¯¯¯¯¯¯¯\\
        | /     \\ |
        | |     | |
        | |     | |
        | \\_____/ |
        |  |   |  |
        |  |   |  |
       /|  |   |  |\\
      / |  |   |  | \\
     / /|  |   |  |\\ \\
    / / |  |___|  | \\ \\
   / /  |         |  \\ \\
  / /   |         |   \\ \\
 /_/    |_________|    \\_\\
""",
        "mage": """
    ╔══════════════════╗
    ║    🔮 МАГ 🔮    ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ⬤ ⬤  |
         |   ▴   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /      |      \\
    /_______|_______\\
          /   \\
         /     \\
        /       \\
""",
        "archer": """
    ╔══════════════════╗
    ║   🏹 ЛУЧНИК 🏹   ║
    ╚══════════════════╝
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /      |      \\
    |    🎯 | 🎯    |
    |       |       |
     \\     / \\     /
      \\   /   \\   /
       \\ /     \\ /
        |       |
        |       |
       /|       |\\
      / |       | \\
""",
        "rogue": """
    ╔══════════════════╗
    ║    🗡️ ВОР 🗡️    ║
    ╚══════════════════╝
           /\\
          /  \\
         /    \\
        /      \\
       /        \\
      /          \\
     /    ◉   ◉   \\
    |       ▴      |
     \\     ▾▾▾    /
      \\__________/
       /        \\
      /          \\
     /            \\
    /              \\
   /                \\
  /__________________\\
        |      |
        |      |
       /|      |\\
""",
        "battle": """
 ╔═══════════════════════════════════════════════════╗
 ║                  ⚔️ БИТВА НАЧАЛАСЬ! ⚔️           ║
 ╚═══════════════════════════════════════════════════╝
        /\\          /\\          /\\
       /  \\        /  \\        /  \\
      /    \\      /    \\      /    \\
     /      \\    /      \\    /      \\
    /        \\  /        \\  /        \\
   /__________\\/__________\\/__________\\
  |                                    |
  |    ⚔️ СРАЖЕНИЕ С МОНСТРОМ ⚔️     |
  |____________________________________|
   \\                                  /
    \\                                /
     \\                              /
      \\                            /
       \\                          /
        \\________________________/
""",
        "victory": """
 ╔═══════════════════════════════════════════════════╗
 ║                🎉 ПОБЕДА ОДЕРЖАНА! 🎉           ║
 ╚═══════════════════════════════════════════════════╝
          ★★★★★★★★★★★★★★★★★★★
         ★                         ★
        ★        🏆 ПОБЕДА! 🏆       ★
         ★                         ★
          ★★★★★★★★★★★★★★★★★★★
               \\            /
                \\    ★    /
                 \\  ★★★  /
                  \\★★★★★/
                   \\★★★/
                    \\★/
                     |
                     |
                    / \\
                   /   \\
                  /     \\
                 /       \\
                /_________\\
""",
        "defeat": """
 ╔═══════════════════════════════════════════════════╗
 ║               💀 ПУТЬ ОБОРВАЛСЯ 💀              ║
 ╚═══════════════════════════════════════════════════╝
          ███████████████████████
         █                     █
        █      П О Р А Ж Е Н И Е     █
         █                     █
          ███████████████████████
                ▄▄▄▄▄▄▄▄
               █      █
              █   ☠   █
               █      █
                ▀▀▀▀▀▀
                 |    |
                 |    |
                /      \\
               /        \\
              /          \\
             /            \\
            /______________\\
           |  R.I.P. HERO  |
           |               |
           |  💀 1989-2023 💀 |
"""
    }

    # Добавляем дополнительные ASCII-арты для других классов и NPC
    additional_arts = {
        "healer": """
    ╔══════════════════╗
    ║  ✨ ЦЕЛИТЕЛЬ ✨  ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ╭─╮  |
         |  │ ╰╮ |
         |  ╰─╯  |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /      |      \\
    /_______|_______\\
         |     |
         |  ❤  |
         |     |
        /|     |\\
       / |     | \\
""",
        "paladin": """
    ╔══════════════════╗
    ║  ⚜️ ПАЛАДИН ⚜️  ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ╭─╮  |
         |  │╬│  |
         |  ╰─╯  |
          \\___/ 
         /|\\ /|\\
        / | X | \\
       /  |/ \\|  \\
      /   |   |   \\
     /    |   |    \\
    /     |   |     \\
   /______|___|______\\
        |       |
        |   ╬   |
        |       |
       /|\\     /|\\
      / | \\   / | \\
""",
        "druid": """
    ╔══════════════════╗
    ║   🌿 ДРУИД 🌿   ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ◉ ◉  |
         |   ▴   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /  🍃  |  🍃  \\
    /_______|_______\\
         |     |
         |  🍂 |
         |     |
        /|\\   /|\\
       / | \\ / | \\
""",
        "elf_elder": """
    ╔══════════════════╗
    ║  👑 ЭЛЬФ-СТАРЕЙШИНА  ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ◉ ◉  |
         |   ▽   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /  ✨  |  ✨  \\
    /_______|_______\\
         |     |
         |  🌟 |
         |     |
        / \\   / \\
       /   \\ /   \\
""",
        "water_spirit": """
    ╔══════════════════╗
    ║  🌊 ДУХ ВОДЫ 🌊  ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ~ ~  |
         |   ◡   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /  💧 | 💧  \\
    🌊/_____|_____🌊
         |     |
         |  🌊 |
         |     |
        / \\   / \\
       /   \\ /   \\
""",
        "wolf": """
    ╔══════════════════╗
    ║    🐺 ВОЛК 🐺    ║
    ╚══════════════════╝
           /\\ /\\
          /  V  \\
         /   ▴   \\
        /        \\
       /          \\
      /            \\
     /  ◉       ◉  \\
    |               |
     \\     ▴▴▴     /
      \\___________/
       /         \\
      /           \\
     /             \\
    /               \\
   /_________________\\
        |       |
        |       |
       /|\\     /|\\
""",
        "goblin": """
    ╔══════════════════╗
    ║   👺 ГОБЛИН 👺   ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ◉ ◉  |
         |   ▴   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /  💀  |  💀  \\
    /_______|_______\\
         |     |
         |  🗡️ |
         |     |
        / \\   / \\
       /   \\ /   \\
""",
        "skeleton": """
    ╔══════════════════╗
    ║   💀 СКЕЛЕТ 💀   ║
    ╚══════════════════╝
          /¯¯¯¯¯\\
         |  ⬤ ⬤  |
         |   ▴   |
          \\___/ 
           /|\\
          / | \\
         /  |  \\
        /   |   \\
       /    |    \\
      /     |     \\
     /  ☠️  |  ☠️  \\
    /_______|_______\\
         |     |
         |  ⚰️  |
         |     |
        / \\   / \\
       /   \\ /   \\
""",
        "treasure": """
    ╔══════════════════╗
    ║   💎 СОКРОВИЩЕ 💎  ║
    ╚══════════════════╝
         █████████████
        █           █
       █   💎💰💍✨  █
        █           █
         █████████████
           |       |
           |   🔑  |
           |       |
          / \\     / \\
         /   \\   /   \\
        /     \\ /     \\
       /_______ _______\\
      |                 |
      |   СУНДУК  🎁   |
      |_________________|
""",
        "forest": """
    ╔══════════════════╗
    ║   🌲 ЛЕС 🌲   ║
    ╚══════════════════╝
          🌳🌲🌳🌲🌳
         🌲/🌳\\🌳\\🌲/🌳
        🌳/🌲\\🌳/🌲\\🌳/🌲
       🌲/🌳\\🌲/🌳\\🌲/🌳\\🌲
      🌳🌲🌳🌲🌳🌲🌳🌲🌳🌲🌳
        |\\     /|\\     /|
        | \\   / | \\   / |
        |  \\ /  |  \\ /  |
        |   🚶  |   |   |
        |  / \\  |  / \\  |
        | /   \\ | /   \\ |
        |/     \\|/     \\|
""",
        "cave": """
    ╔══════════════════╗
    ║   🕳️ ПЕЩЕРА 🕳️   ║
    ╚══════════════════╝
          /¯¯¯¯¯¯¯¯¯¯\\
         /            \\
        /              \\
       /    🕯️     🕯️    \\
      /        🔦        \\
     /                  \\
    /                    \\
   /                      \\
  /________________________\\
  |                        |
  |      ТЕМНЫЕ ХОДЫ      |
  |________________________|
   \\                      /
    \\                    /
     \\                  /
      \\                /
       \\              /
        \\____________/
""",
        "village": """
    ╔══════════════════╗
    ║   🏡 ДЕРЕВНЯ 🏡   ║
    ╚══════════════════╝
        🏠🏠🏠🏠🏠
       🏠/🏠\\🏠/🏠\\🏠
      🏠/🏠\\🏠/🏠\\🏠/🏠
     🏠🏠🏠🏠🏠🏠🏠🏠🏠
      |\\     /|\\     /|
      | \\   / | \\   / |
      |  \\ /  |  \\ /  |
      |   👤  |   👤  |
      |  / \\  |  / \\  |
      | /   \\ | /   \\ |
      |/     \\|/     \\|
     🏪      🏥      🏦
"""
    }

    # Объединяем основные и дополнительные арты
    full_art_dict = {**art_dict, **additional_arts}

    if art_type in full_art_dict:
        print(f"{full_art_dict[art_type]}")
    else:
        print(f"ASCII art for {art_type} not available")


def wrap_text(text, width=78):
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        if paragraph.strip() == '':
            wrapped_paragraphs.append('')
            continue

        # Handle special formatting like bold or color codes
        wrapped_lines = textwrap.wrap(paragraph, width=width,
                                      replace_whitespace=False,
                                      break_long_words=False,
                                      break_on_hyphens=False)
        wrapped_paragraphs.append('\n'.join(wrapped_lines))

    return '\n\n'.join(wrapped_paragraphs)


class Artifact:

    def __init__(self, name: str, description: str, rarity: str, effects: Dict[str, Any],
                 activation: str = "passive", cooldown: int = 0):
        self.name = name
        self.description = description
        self.rarity = rarity  # common, rare, epic, legendary
        self.effects = effects  # Dictionary of stat bonuses and special effects
        self.activation = activation  # passive, active, conditional
        self.cooldown = cooldown  # For active abilities
        self.current_cooldown = 0

    def apply_effect(self, character) -> str:
        result = []

        # Handle stat bonuses
        for stat, value in self.effects.items():
            if hasattr(character, stat):
                current_value = getattr(character, stat)
                if isinstance(value, (int, float)):
                    setattr(character, stat, current_value + value)
                    result.append(f"+{value} to {stat}")

        # Handle special effects (placeholder for future implementation)
        if "special" in self.effects:
            result.append(f"Special effect: {self.effects['special']}")

        return "\n".join(result)

    def use_active_ability(self, character, target=None) -> str:
        """Use the artifact's active ability"""
        if self.activation != "active":
            return f"{self.name} doesn't have an active ability!"

        if self.current_cooldown > 0:
            return f"{self.name} is on cooldown for {self.current_cooldown} turns!"

        # Apply ability effects (placeholder logic)
        result = f"🔮 {character.name} used {self.name}'s power!"

        # Example of applying a heal effect
        if "heal" in self.effects:
            heal_amount = self.effects["heal"]
            character.heal(heal_amount)
            result += f"\n💖 Healed for {heal_amount} HP!"

        # Example of damage effect
        if "damage" in self.effects and target:
            damage = self.effects["damage"]
            target.take_damage(damage)
            result += f"\n💥 Dealt {damage} damage to {target.name}!"

        # Set cooldown
        self.current_cooldown = self.cooldown

        return result

    def tick_cooldown(self):
        """Reduce cooldown by 1 turn"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create an Artifact instance from dictionary data"""
        return cls(
            name=data["name"],
            description=data["description"],
            rarity=data["rarity"],
            effects=data["effects"],
            activation=data.get("activation", "passive"),
            cooldown=data.get("cooldown", 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "effects": self.effects,
            "activation": self.activation,
            "cooldown": self.cooldown,
            "current_cooldown": self.current_cooldown
        }


class Companion:
    """Class representing NPC companions that can join the player's party"""

    def __init__(self, name: str, race: str, character_class: str, level: int,
                 health: int, max_health: int, attack: int, defense: int,
                 skills: Dict[str, int], inventory: List[str], description: str,
                 loyalty: int = 50, special_ability: str = None):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.level = level
        self.health = health
        self.max_health = max_health
        self.attack = attack
        self.defense = defense
        self.skills = skills
        self.inventory = inventory
        self.description = description
        self.loyalty = loyalty  # 0-100, affects willingness to follow orders and stay with party
        self.special_ability = special_ability
        self.join_condition = None  # Condition needed to recruit this companion

    def take_damage(self, damage: int) -> int:
        """Apply damage to companion, return remaining health"""
        actual_damage = max(1, damage - self.defense // 2)
        self.health -= actual_damage
        return self.health

    def heal(self, amount: int):
        """Heal companion by specified amount"""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        """Check if companion is alive"""
        return self.health > 0

    def perform_special_ability(self, target=None) -> str:
        """Perform companion's special ability"""
        if not self.special_ability:
            return f"{self.name} has no special ability!"

        result = f"✨ {self.name} uses {self.special_ability}!"

        # This would be expanded with actual ability effects
        # For now, it's just a placeholder

        return result

    def gain_loyalty(self, amount: int):
        """Increase companion loyalty"""
        self.loyalty = min(100, self.loyalty + amount)

    def lose_loyalty(self, amount: int):
        """Decrease companion loyalty"""
        self.loyalty = max(0, self.loyalty - amount)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a Companion instance from dictionary data"""
        return cls(
            name=data["name"],
            race=data["race"],
            character_class=data["character_class"],
            level=data["level"],
            health=data["health"],
            max_health=data["max_health"],
            attack=data["attack"],
            defense=data["defense"],
            skills=data["skills"],
            inventory=data["inventory"],
            description=data["description"],
            loyalty=data.get("loyalty", 50),
            special_ability=data.get("special_ability")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert companion to dictionary for serialization"""
        return {
            "name": self.name,
            "race": self.race,
            "character_class": self.character_class,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "skills": self.skills,
            "inventory": self.inventory,
            "description": self.description,
            "loyalty": self.loyalty,
            "special_ability": self.special_ability
        }


class Monster:
    """Class representing monsters/enemies in the game"""

    def __init__(self, name: str, health: int, attack: int, defense: int,
                 level: int, xp_reward: int, gold_reward: int, drops: List[Dict[str, Any]],
                 special_attacks: List[Dict[str, Any]] = None, description: str = "",
                 weakness: str = None, resistance: str = None):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.level = level
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.drops = drops  # List of dicts with 'item', 'chance'
        self.special_attacks = special_attacks or []
        self.description = description
        self.weakness = weakness
        self.resistance = resistance

    def take_damage(self, damage: int, damage_type: str = None) -> int:
        """Apply damage to monster, considering resistances/weaknesses"""
        # Apply resistance/weakness modifiers
        modifier = 1.0
        if damage_type:
            if self.resistance == damage_type:
                modifier = 0.5  # 50% resistance
            elif self.weakness == damage_type:
                modifier = 1.5  # 50% extra damage

        actual_damage = max(1, int((damage - self.defense) * modifier))
        self.health -= actual_damage
        return actual_damage

    def is_alive(self) -> bool:
        """Check if monster is still alive"""
        return self.health > 0

    def get_random_attack(self) -> Dict[str, Any]:
        """Get a random attack (basic or special)"""
        # Higher chance for basic attack
        if not self.special_attacks or random.random() < 0.7:
            return {
                "name": "Basic Attack",
                "damage": self.attack,
                "type": "physical",
                "description": f"{self.name} attacks!"
            }
        else:
            return random.choice(self.special_attacks)

    def get_drops(self) -> List[str]:
        """Get items dropped by monster based on chance"""
        drops = []
        for drop in self.drops:
            if random.random() < drop["chance"]:
                if isinstance(drop["item"], list):
                    drops.append(random.choice(drop["item"]))
                else:
                    drops.append(drop["item"])
        return drops

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a Monster instance from dictionary data"""
        return cls(
            name=data["name"],
            health=data["health"],
            attack=data["attack"],
            defense=data["defense"],
            level=data["level"],
            xp_reward=data["xp_reward"],
            gold_reward=data["gold_reward"],
            drops=data["drops"],
            special_attacks=data.get("special_attacks"),
            description=data.get("description", ""),
            weakness=data.get("weakness"),
            resistance=data.get("resistance")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert monster to dictionary for serialization"""
        return {
            "name": self.name,
            "health": self.health,
            "attack": self.attack,
            "defense": self.defense,
            "level": self.level,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
            "drops": self.drops,
            "special_attacks": self.special_attacks,
            "description": self.description,
            "weakness": self.weakness,
            "resistance": self.resistance
        }


class PlayerCharacter:
    """Main player character class with all attributes and methods"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = ""
        self.character_class = ""
        self.race = ""
        self.level = 1
        self.experience = 0
        self.health = GameConstants.MAX_HEALTH
        self.max_health = GameConstants.MAX_HEALTH
        self.gold = GameConstants.STARTING_GOLD
        self.inventory = []
        self.abilities = {
            "strength": 5,  # Physical damage and carrying capacity
            "agility": 5,  # Dodge chance and critical hit chance
            "intelligence": 5,  # Magic damage and mana pool
            "charisma": 5,  # NPC interaction and prices
            "stamina": 5  # Health and endurance
        }
        self.skills = {
            "swordsmanship": 0,  # Melee weapon proficiency
            "archery": 0,  # Bow and arrow proficiency
            "magic": 0,  # Spell casting proficiency
            "stealth": 0,  # Sneaking and thievery
            "alchemy": 0,  # Potion making and identification
            "barter": 0  # Trading and persuasion
        }
        self.armor_slots = {
            "head": None,
            "chest": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "weapon": None,
            "shield": None,
            "amulet": None,
            "ring": None
        }
        self.current_location = "начало"
        self.active_quests = []
        self.completed_quests = []
        self.reputation = {
            "kingdom": 0,
            "guild_of_thieves": 0,
            "mages_guild": 0,
            "merchants": 0,
            "druid_circle": 0
        }
        self.party_members = []  # List of Companion objects
        self.artifacts = []  # List of Artifact objects
        self.story_progress = {"main_quest": "начало"}
        self.skill_points = 0
        self.difficulty = GameDifficulty.NORMAL.value
        self.buffs = {}  # Temporary stat buffs
        self.debuffs = {}  # Temporary stat debuffs

        # Load game world data
        self.load_game_data()
        # Load player progress if exists
        self.load_progress()

    def load_game_data(self):
        """Load all game data including locations, NPCs, monsters, items, etc."""
        self.init_world()

    def init_world(self):
        """Initialize the game world with all locations, NPCs, monsters, and items"""
        self.init_locations()
        self.init_npcs()
        self.init_monsters()
        self.init_items()
        self.init_quests()
        self.init_artifacts()
        self.init_companions()

    def init_locations(self):
        """Initialize all game locations"""
        self.locations = {
            "начало": {
                "name": "Распутье Судьбы",
                "display_name": f"🌟 Распутье Судьбы",
                "description": "Ты стоишь на перекрестке дорог, ведущих в разные части королевства Элдарию. Три пути расходятся перед тобой: один ведет в древний лес, другой в горы, а третий к морскому побережью. В центре перекрестка горит костер, у которого сидит таинственный старец.",
                "long_description": "Ты стоишь на перекрестке дорог, ведущих в разные части королевства Элдарию. Три пути расходятся перед тобой: один ведет в древний лес, другой в горы, а третий к морскому побережью. В центре перекрестка, где сходятся все дороги, горит небольшой костер, у которого сидит таинственный старец в простой одежде. Его глаза светятся мудростью веков, и кажется, будто он ждал именно тебя. Дороги выглядят изношенными, но хорошо протоптанными — видимо, здесь часто проходят путешественники. Ветер доносит запахи из разных уголков королевства: аромат лесных трав, горной свежести и соленого морского бриза.",
                "exits": ["лес", "горы", "море", "деревня"],
                "npcs": ["друид_альдар"],
                "items": [],
                "encounter_chance": 0.0,
                "map": """
                   🌄
                    |
    🏞️ --🔥-- 🏖️
                    |
                   🏡
                """
            },
            "лес": {
                "name": "Тёмный Лес Вечных Теней",
                "display_name": f"🌲 Тёмный Лес Вечных Теней",
                "description": "Густой, древний лес, где даже в полдень царит полумрак. Тропы переплетаются между могучих дубов, а в тишине слышны шорохи невидимых созданий. Воздух наполнен магическими частицами и древними тайнами.",
                "long_description": "Густой, древний лес, где даже в полдень царит полумрак. Могучие дубы и сосны смыкаются кронами так плотно, что солнечный свет лишь изредка пробивается к земле, создавая причудливые узоры на покрытой мхом земле. Тропы переплетаются между деревьями, и легко потерять направление, если не знать дороги. В тишине слышны шорохи невидимых созданий, перезвон ручьев вдалеке и иногда — странные напевы, которые невозможно объяснить. Воздух наполнен магией и тайнами. Местные жители называют этот лес проклятым, но в то же время священным. Здесь живут древние духи природы, и говорят, что лес помнит всё, что происходило на его территории за тысячелетия.",
                "exits": ["начало", "пещера", "эльфийская_роща", "древнее_святилище"],
                "npcs": [],
                "monsters": ["волк", "лесной_дух", "паук-ловчий"],
                "items": ["ветка", "гриб", "ягоды", "светлячок"],
                "encounter_chance": 0.6,
                "map": """
      🍄  🌲  🦌
        \  |  /
    🌲---🌲---🌲
         / \\
    🌲--🌲   🌲--🌲
        |     |
      🌲🌲   🌲🌲🌲
    """
            },
            "пещера": {
                "name": "Пещера Забытых Сокровищ",
                "display_name": f"🕳️ Пещера Забытых Сокровищ",
                "description": "Мрачная пещера с мерцающими кристаллами на стенах. Воздух влажный и прохладный, а где-то в глубине слышится плеск воды. На полу видны следы различных существ и древние символы.",
                "long_description": "Мрачная пещера с мерцающими кристаллами на стенах, которые излучают тусклый голубоватый свет. Воздух влажный и прохладный, отдающий затхлостью и древностью. Где-то в глубине слышится плеск воды и эхо капель, падающих с каменного потолка. На полу видны следы различных существ, включая когти гоблинов и странные знаки, оставленные кем-то много веков назад. Стены украшены вырезанными символами на забытом языке, которые, кажется, светятся при приближении. В некоторых местах видны обломки старых факелов и обугленные остатки костров. Говорят, что эта пещера когда-то служила убежищем для древнего клана гномов, которые скрывали здесь свои сокровища от завоевателей. Но теперь здесь обитают более темные создания.",
                "exits": ["лес", "подземелье"],
                "npcs": [],
                "monsters": ["гоблин", "летучая_мышь", "каменный_голем"],
                "items": ["факел", "золотая_монета", "редкий_камень", "древний_свиток"],
                "encounter_chance": 0.8,
                "map": """
        🕯️
         |
    🧌-🕳️-💧
         |
        🚪
    """
            },
            "подземелье": {
                "name": "Подземелье Павших Героев",
                "display_name": f"🏰 Подземелье Павших Героев",
                "description": "Тёмные коридоры подземелья, где многие герои нашли свою смерть. Стены украшены затухающими магическими символами, а воздух пропитан запахом сырости и опасности.",
                "long_description": "Тёмные коридоры подземелья, где многие герои нашли свою смерть, теперь покоятся их кости. Стены украшены затухающими магическими символами, которые когда-то защищали это место. Воздух пропитан запахом сырости, плесени и чего-то более древнего — запахом забвения. Где-то вдалеке слышен скрип ржавых дверей и шарканье невидимых существ. Пол вымощен каменными плитами, на которых видны следы многочисленных сражений. В некоторых местах зияют провалы, где рухнули своды, открывая доступ в еще более глубокие и опасные уровни. Говорят, что духи павших воинов до сих пор бродят здесь, защищая свои сокровища и не давая покоя тем, кто осмеливается нарушить их покой.",
                "exits": ["пещера", "сокровищница"],
                "npcs": [],
                "monsters": ["скелет-воин", "зомби", "подземный_трогг"],
                "items": ["ржавый_меч", "череп", "магический_кристалл", "ключ_от_сокровищницы"],
                "encounter_chance": 0.85,
                "map": """
        💀
         |
    ⚔️-🏰-🛡️
         |
        ⚰️
    """
            },
            "сокровищница": {
                "name": "Тайная Сокровищница Короля",
                "display_name": f"👑 Тайная Сокровищница Короля",
                "description": "Роскошное подземное помещение, набитое золотом, драгоценностями и древними артефактами. В центре стоит огромный сундук, запертый на магический замок.",
                "long_description": "Роскошное подземное помещение, высеченное в твердой скале и украшенное колоннами из чистого мрамора. Стены сверкают золотой и серебряной инкрустацией, отражая свет от магических кристаллов, вделанных в потолок. Помещение набито золотом, драгоценностями и древними артефактами — горы монет и кубков, статуи из чистого золота, шкатулки с самоцветами и свитки с забытыми знаниями. В центре залы стоит огромный сундук из темного дерева и железа, украшенный драгоценными камнями, запертый на сложный магический замок, который мерцает синим светом. По углам залы стоят статуи стражей, которые, кажется, следят за каждым движением. Воздух здесь необычайно чист и пахнет ладаном и благовониями, несмотря на то, что это подземелье.",
                "exits": ["подземелье"],
                "npcs": [],
                "items": ["королевская_корона", "драконий_амулет", "манускрипт_мага", "золотой_слиток"],
                "locked": True,
                "required_item": "ключ_от_сокровищницы",
                "encounter_chance": 0.2,
                "map": """
       ✨✨✨
        👑
    ✨--💎--✨
        📜
       ✨✨✨
    """
            },
            "эльфийская_роща": {
                "name": "Священная Роща Эльфов",
                "display_name": f"🧚 Священная Роща Эльфов",
                "description": "Волшебное место, где время течёт иначе. Величественные серебристые деревья излучают мягкое сияние, а в воздухе плавают светящиеся споры. Здесь царит гармония и древняя мудрость.",
                "long_description": "Волшебное место, где время течёт иначе, и законы природы подчиняются древней магии. Величественные серебристые деревья с кронами, похожими на облака, излучают мягкое сияние, наполняя рощу волшебным светом. В воздухе плавают светящиеся споры, напоминающие маленьких фей, а цветы на земле поют тихие мелодии, едва слышные человеческому уху. Здесь царит гармония и древняя мудрость — каждый камень, каждый листок хранит знания веков. В центре рощи стоит древний алтарь, вырезанный из единого кристалла, который пульсирует с ритмом сердца Земли. Эльфы приходят сюда, чтобы медитировать, общаться с духами природы и искать ответы на самые сложные вопросы. Говорят, что те, кто проводит ночь в этой роще, получают видения будущего.",
                "exits": ["лес"],
                "npcs": ["старейшина_лиана", "хранительница_вод"],
                "items": ["кристалл_природы", "цветок_бессмертия", "эльфийский_лук"],
                "encounter_chance": 0.2,
                "map": """
       🌸✨🌸
         🌳
    ✨--🧚--✨
         🌸
       🌳✨🌳
    """
            }
        }

    def init_npcs(self):
        """Initialize all NPCs in the game"""
        self.npcs = {
            "друид_альдар": {
                "name": "Друид Альдар",
                "display_name": f"🌿 Друид Альдар",
                "description": "Мудрый старик в зелёной мантии, с посохом из древнего дерева. Его глаза хранят знания веков.",
                "long_description": "Мудрый старик в зелёной мантии, сотканной из листьев и живых виноградных лоз, с посохом из древнего дуба. Его глаза, цвета лесной зелени, хранят знания веков и горят внутренним светом. Лице испещрено морщинами, каждая из которых рассказывает свою историю. В его присутствии воздух становится чище, а звуки природы — отчетливее. Он говорит мягко, но каждое его слово наполнено глубоким смыслом. Друид Альдар — один из последних хранителей древних знаний, связанных с природой и магией земли. Он наблюдает за равновесием в мире и лишь изредка вмешивается в дела смертных.",
                "dialogue": [
                    "Добро пожаловать, путник. Я Альдар, хранитель равновесия в этом мире.",
                    "Я вижу, что ты избран судьбой. Мир полон опасностей, но и возможностей тоже.",
                    "Прежде чем отправиться в путь, выбери свою судьбу - кто ты есть?"
                ],
                "options": ["воин", "маг", "лучник", "вор", "целитель", "паладин"],
                "class_quests": {
                    "воин": "Защити деревню от разбойников, что нападают на дорогах.",
                    "маг": "Найди древний магический фолиант в подземелье заброшенного замка.",
                    "лучник": "Помоги лесникам выследить опасного зверя в Тёмном Лесу.",
                    "вор": "Добудь карту подземелий из кабинета городского начальника.",
                    "целитель": "Собери редкие целебные травы для больницы в деревне Мира.",
                    "паладин": "Очисти древнее святилище от присутствия тёмной энергии."
                },
                "quest": "Найди три священных артефакта: Камень Природы, Жемчужину Морей и Огненный Кристалл.",
                "reward": "благословение_природы"
            },
            "старейшина_лиана": {
                "name": "Старейшина Лиана",
                "display_name": f"👑 Старейшина Лиана",
                "description": "Эльфийка с серебряными волосами и глазами цвета леса. Её кожа излучает мягкий свет.",
                "long_description": "Эльфийка с серебряными волосами, ниспадающими до пояса, и глазами цвета молодой листвы. Её кожа излучает мягкий серебристый свет, особенно в темноте. Лицо безупречно красиво и в то же время несет на себе печать многих столетий жизни. Она облачена в одеяние из шелковистых листьев и живых цветов, которые никогда не увядают. Её голос похож на шелест листвы на ветру, а движения грациозны и плавны, как течение реки. Старейшина Лиана — одна из древнейших эльфов в мире, хранительница знаний о магии природы и защитница священных земель.",
                "dialogue": [
                    "Приветствую тебя, странник. Я Лиана, хранительница леса эльфов.",
                    "Наш лес хранит древние тайны и магию. Но сейчас он в опасности.",
                    "Тёмные силы проникают в наши земли, искажая магию природы."
                ],
                "quest": "Собери три светящихся цветка чистоты для очищения святилища.",
                "reward": "эльфийский_амулет_защиты",
                "requirements": {"quest": "защита_леса"},
                "trader": {
                    "buy": {"эльфийский_лук": 50, "лесной_плащ": 75, "эликсир_невидимости": 100},
                    "sell": {"кристалл_природы": 30, "цветок_бессмертия": 45}
                }
            },
            "хранительница_вод": {
                "name": "Хранительница Вод Нерисса",
                "display_name": f"🌊 Хранительница Вод Нерисса",
                "description": "Прекрасная нимфа с кожей цвета морской волны и волосами из водорослей.",
                "long_description": "Прекрасная нимфа с кожей цвета морской волны и волосами, похожими на живые водоросли, которые колышутся даже без ветра. Её глаза меняют цвет в зависимости от настроения — от глубокого синего до нежно-бирюзового. Тело мерцает, как поверхность воды на солнце, и кажется, что она постоянно окружена легким туманом. Её голос напоминает шум прибоя и журчание ручья одновременно. Нерисса — древний дух воды, который охраняет священный источник в эльфийской роще. Она связана с водной стихией и может управлять потоками воды на значительном расстоянии. Её мудрость так же глубока, как океан, а сердце чисто, как горный родник.",
                "dialogue": [
                    "Я Нерисса, дух воды этого священного озера.",
                    "Тёмная магия отравляет наши воды, и я слабею с каждым днём.",
                    "Помоги очистить источник жизни."
                ],
                "quest": "Найди три чистых кристалла, чтобы очистить источник воды.",
                "reward": "амулет_морской_глубины",
                "requires": {"item": "кристалл_природы"}
            },
            "староста_грум": {
                "name": "Староста Грум",
                "display_name": f"🧙 Староста Грум",
                "description": "Пузатый гном с длинной седой бородой и ярко-красной шапкой. Всегда ходит с посохом.",
                "long_description": "Пузатый гном с длинной седой бородой, заплетенной в несколько косичек, и ярко-красной шапкой-колпаком. Его лицо покрыто морщинами от смеха и труда, глаза блестят добродушием и мудростью. Всегда ходит с посохом из железного дерева, украшенным медными кольцами и резными символами. За поясом у него висит кожаная сумка с травами и зельями. Грум — уважаемый староста горной деревни гномов и известный лекарь. Несмотря на свой возраст (а ему уже за 200 лет), он полон энергии и всегда готов помочь советом или делом. Его хижина всегда открыта для путников, и у него всегда найдется горячий чай и интересная история.",
                "dialogue": [
                    "А, новое лицо в наших горах! Я Грум, староста этой деревни.",
                    "У нас проблемы - тёмные создания всё чаще выходят из подземелий.",
                    "Мы гномы - отважные воины, но нас слишком мало для такой угрозы."
                ],
                "quest": "Очисти вход в гномьи шахты от троллей и гоблинов.",
                "reward": "гномий_секрет"
            }
        }

    def init_monsters(self):
        """Initialize all monsters in the game"""
        self.monsters = {
            "волк": {
                "name": "Лесной волк",
                "display_name": f"🐺 Лесной волк",
                "health": 20,
                "attack": 5,
                "defense": 2,
                "level": 1,
                "xp_reward": 10,
                "gold_reward": 5,
                "drops": [
                    {"item": "шкура волка", "chance": 0.8},
                    {"item": "клык волка", "chance": 0.3}
                ],
                "description": "Агрессивный хищник, обитающий в лесах. Охотится стаями, но иногда встречается и одинокий волк.",
                "weakness": "огонь",
                "resistance": "холод"
            },
            "лесной_дух": {
                "name": "Лесной дух",
                "display_name": f"🌲 Лесной дух",
                "health": 15,
                "attack": 3,
                "defense": 1,
                "level": 1,
                "xp_reward": 8,
                "gold_reward": 2,
                "drops": [
                    {"item": "эссенция природы", "chance": 0.7}
                ],
                "description": "Дух природы, охраняющий лесные пределы. Обычно миролюбив, но атакует тех, кто причиняет вред лесу.",
                "weakness": "тьма",
                "resistance": "природа"
            },
            "паук-ловчий": {
                "name": "Паук-ловчий",
                "display_name": f"🕷️ Паук-ловчий",
                "health": 25,
                "attack": 6,
                "defense": 3,
                "level": 2,
                "xp_reward": 15,
                "gold_reward": 8,
                "drops": [
                    {"item": "паутина", "chance": 0.9},
                    {"item": "яд паука", "chance": 0.4}
                ],
                "description": "Крупный паук, плетущий ловушки на тропах. Ядовит, но его яд ценится алхимиками.",
                "weakness": "огонь",
                "resistance": None
            },
            "гоблин": {
                "name": "Гоблин-разбойник",
                "display_name": f"👺 Гоблин-разбойник",
                "health": 30,
                "attack": 8,
                "defense": 3,
                "level": 2,
                "xp_reward": 25,
                "gold_reward": 12,
                "drops": [
                    {"item": "гоблинская монета", "chance": 1.0},
                    {"item": "ржавый нож", "chance": 0.6}
                ],
                "description": "Мелкое, но вероломное существо, орудующее в лесах и подземельях. Любит засады и численное превосходство.",
                "weakness": "свет",
                "resistance": "тьма"
            },
            "летучая_мышь": {
                "name": "Гигантская летучая мышь",
                "display_name": f"🦇 Гигантская летучая мышь",
                "health": 10,
                "attack": 4,
                "defense": 1,
                "level": 1,
                "xp_reward": 5,
                "gold_reward": 1,
                "drops": [
                    {"item": "крыло летучей мыши", "chance": 0.7}
                ],
                "description": "Крупная летучая мышь, обитающая в пещерах и подземельях. Атакует путников в темноте.",
                "weakness": "свет",
                "resistance": "тьма"
            },
            "каменный_голем": {
                "name": "Каменный голем",
                "display_name": f"🗿 Каменный голем",
                "health": 60,
                "attack": 12,
                "defense": 10,
                "level": 4,
                "xp_reward": 40,
                "gold_reward": 20,
                "drops": [
                    {"item": "каменный осколок", "chance": 0.8}
                ],
                "description": "Искусственное существо, созданное из камня древними магами. Охраняет важные места.",
                "weakness": "земля",
                "resistance": "физический"
            },
            "скелет-воин": {
                "name": "Скелет-воин",
                "display_name": f"💀 Скелет-воин",
                "health": 35,
                "attack": 7,
                "defense": 4,
                "level": 3,
                "xp_reward": 20,
                "gold_reward": 15,
                "drops": [
                    {"item": "кость воина", "chance": 0.9},
                    {"item": "ржавый меч", "chance": 0.5}
                ],
                "description": "Восставший из мертвых воин, все еще облаченный в доспехи. Неуязвим для боли.",
                "weakness": "свет",
                "resistance": "тьма"
            },
            "зомби": {
                "name": "Зомби",
                "display_name": f"🧟 Зомби",
                "health": 40,
                "attack": 6,
                "defense": 2,
                "level": 2,
                "xp_reward": 18,
                "gold_reward": 8,
                "drops": [
                    {"item": "гнилая плоть", "chance": 0.8},
                    {"item": "проклятый амулет", "chance": 0.2}
                ],
                "description": "Медлительное, но живучее создание тьмы. Распространяет болезни своим прикосновением.",
                "weakness": "огонь",
                "resistance": "яд"
            },
            "подземный_трогг": {
                "name": "Подземный трогг",
                "display_name": f"👹 Подземный трогг",
                "health": 50,
                "attack": 9,
                "defense": 6,
                "level": 4,
                "xp_reward": 35,
                "gold_reward": 25,
                "drops": [
                    {"item": "шкура трогга", "chance": 0.7},
                    {"item": "пещерный гриб", "chance": 0.4}
                ],
                "description": "Примитивное подземное существо с толстой кожей и огромной силой. Обитает в самых глубоких пещерах.",
                "weakness": "свет",
                "resistance": "тьма"
            }
        }

    def init_items(self):
        """Initialize all items in the game"""
        self.items = {
            # Weapons
            "дубинка": {
                "name": "Дубинка новичка",
                "type": "weapon",
                "attack": 3,
                "value": 10,
                "description": "Простая деревянная дубинка для начинающих воинов.",
                "slot": "weapon"
            },
            "деревянный_меч": {
                "name": "Древесный меч",
                "type": "weapon",
                "attack": 5,
                "value": 15,
                "description": "Тренировочный меч из твердых пород дерева.",
                "slot": "weapon"
            },
            "стальной_меч": {
                "name": "Стальной меч",
                "type": "weapon",
                "attack": 10,
                "value": 50,
                "description": "Надежный стальной меч для настоящих воинов.",
                "slot": "weapon"
            },
            "эльфийский_лук": {
                "name": "Эльфийский лук",
                "type": "weapon",
                "attack": 8,
                "value": 40,
                "description": "Легкий и точный лук, созданный мастерами-эльфами.",
                "slot": "weapon",
                "special": "increased_crit",
                "crit_bonus": 0.1  # 10% increased critical chance
            },
            "магический_жезл": {
                "name": "Магический жезл",
                "type": "weapon",
                "attack": 7,
                "value": 35,
                "description": "Жезл, усиливающий магические способности владельца.",
                "slot": "weapon",
                "special": "mana_regeneration"
            },
            "ржавый_нож": {
                "name": "Ржавый нож",
                "type": "weapon",
                "attack": 4,
                "value": 8,
                "description": "Старый ржавый нож, найденный в подземелье.",
                "slot": "weapon"
            },
            "ржавый_меч": {
                "name": "Ржавый меч",
                "type": "weapon",
                "attack": 6,
                "value": 12,
                "description": "Старый меч, покрытый ржавчиной, но все еще опасный.",
                "slot": "weapon"
            },
            "гномий_топор": {
                "name": "Гномий топор",
                "type": "weapon",
                "attack": 9,
                "value": 45,
                "description": "Тяжелый топор, выкованный гномами-мастерами.",
                "slot": "weapon"
            },
            "посох_целителя": {
                "name": "Посох целителя",
                "type": "weapon",
                "attack": 3,
                "value": 30,
                "description": "Деревянный посох, усиливающий целительные способности.",
                "slot": "weapon",
                "special": "healing_bonus"
            },
            # Armor - Head
            "кожаная_шапка": {
                "name": "Кожаная шапка",
                "type": "armor",
                "slot": "head",
                "defense": 2,
                "value": 10,
                "description": "Простая кожаная шапка, обеспечивающая минимальную защиту."
            },
            "шлем_воина": {
                "name": "Шлем воина",
                "type": "armor",
                "slot": "head",
                "defense": 5,
                "value": 25,
                "description": "Стальной шлем, защищающий голову воина в бою."
            },
            "шлем_мага": {
                "name": "Шлем мага",
                "type": "armor",
                "slot": "head",
                "defense": 3,
                "value": 40,
                "description": "Легкий шлем с инкрустацией магическими символами.",
                "special": "mana_boost"
            },
            # Armor - Chest
            "куртка": {
                "name": "Кожаная куртка",
                "type": "armor",
                "slot": "chest",
                "defense": 3,
                "value": 15,
                "description": "Простая кожаная куртка для защиты от небольших повреждений."
            },
            "кожаный_доспех": {
                "name": "Кожаный доспех",
                "type": "armor",
                "slot": "chest",
                "defense": 6,
                "value": 30,
                "description": "Укрепленный кожаный доспех, обеспечивающий хорошую защиту при сохранении подвижности."
            },
            "стальной_нагрудник": {
                "name": "Стальной нагрудник",
                "type": "armor",
                "slot": "chest",
                "defense": 12,
                "value": 80,
                "description": "Надежный стальной нагрудник для воинов на передовой."
            },
            "лесной_плащ": {
                "name": "Лесной плащ",
                "type": "armor",
                "slot": "chest",
                "defense": 4,
                "value": 35,
                "description": "Плащ из прочной ткани, обеспечивающий защиту и маскировку в лесу."
            },
            # Shields
            "стальной_щит": {
                "name": "Стальной щит",
                "type": "shield",
                "slot": "shield",
                "defense": 8,
                "value": 40,
                "description": "Надежный стальной щит для защиты от атак."
            },
            # Consumables
            "хлеб": {
                "name": "Свежий хлеб",
                "type": "consumable",
                "effect": "health",
                "value": 10,
                "description": "Свежеиспеченный хлеб, восстанавливает немного здоровья."
            },
            "фляга_воды": {
                "name": "Фляга чистой воды",
                "type": "consumable",
                "effect": "health",
                "value": 5,
                "description": "Фляга с чистой родниковой водой."
            },
            "зелье_здоровья": {
                "name": "Зелье здоровья",
                "type": "consumable",
                "effect": "health",
                "value": 30,
                "description": "Магическое зелье, быстро восстанавливающее здоровье."
            },
            "эликсир_невидимости": {
                "name": "Эликсир невидимости",
                "type": "consumable",
                "effect": "invisibility",
                "value": 100,
                "description": "Магический эликсир, делающий потребителя невидимым на короткое время."
            },
            # Materials
            "ветка": {
                "name": "Свежая ветка",
                "type": "material",
                "value": 1,
                "description": "Обычная ветка с дерева. Может пригодиться для костра."
            },
            "камень": {
                "name": "Обычный камень",
                "type": "material",
                "value": 1,
                "description": "Небольшой камень. Можно использовать как примитивное оружие."
            },
            "гриб": {
                "name": "Лесной гриб",
                "type": "material",
                "value": 3,
                "description": "Съедобный гриб, найденный в лесу."
            },
            "ягоды": {
                "name": "Свежие ягоды",
                "type": "material",
                "value": 2,
                "description": "Сладкие лесные ягоды."
            },
            "светлячок": {
                "name": "Светлячок",
                "type": "material",
                "value": 5,
                "description": "Светящееся насекомое, может осветить путь в темноте."
            },
            "факел": {
                "name": "Факел",
                "type": "material",
                "value": 8,
                "description": "Зажженный факел для освещения темных мест."
            },
            "золотая_монета": {
                "name": "Золотая монета",
                "type": "material",
                "value": 10,
                "description": "Старинная золотая монета."
            },
            "редкий_камень": {
                "name": "Редкий камень",
                "type": "material",
                "value": 25,
                "description": "Красивый редкий камень, ценится коллекционерами."
            },
            "древний_свиток": {
                "name": "Древний свиток",
                "type": "material",
                "value": 50,
                "description": "Старинный свиток с непонятными письменами."
            },
            "шкура_волка": {
                "name": "Шкура волка",
                "type": "material",
                "value": 15,
                "description": "Прочная волчья шкура."
            },
            "клык_волка": {
                "name": "Клык волка",
                "type": "material",
                "value": 8,
                "description": "Острый волчий клык."
            },
            "эссенция_природы": {
                "name": "Эссенция природы",
                "type": "material",
                "value": 20,
                "description": "Концентрированная магия природы."
            },
            "паутина": {
                "name": "Паутина",
                "type": "material",
                "value": 5,
                "description": "Прочная паутина паука-ловца."
            },
            "яд_паука": {
                "name": "Яд паука",
                "type": "material",
                "value": 12,
                "description": "Токсин паука-ловца."
            },
            "гоблинская_монета": {
                "name": "Гоблинская монета",
                "type": "material",
                "value": 3,
                "description": "Грубая монета гоблинов."
            },
            "крыло_летучей_мыши": {
                "name": "Крыло летучей мыши",
                "type": "material",
                "value": 4,
                "description": "Кожаное крыло гигантской летучей мыши."
            },
            "каменный_осколок": {
                "name": "Каменный осколок",
                "type": "material",
                "value": 15,
                "description": "Осколок каменного голема."
            },
            "кость_воина": {
                "name": "Кость воина",
                "type": "material",
                "value": 10,
                "description": "Прочная кость скелета-воина."
            },
            "гнилая_плоть": {
                "name": "Гнилая плоть",
                "type": "material",
                "value": 5,
                "description": "Разлагающаяся плоть зомби."
            },
            "проклятый_амулет": {
                "name": "Проклятый амулет",
                "type": "material",
                "value": 30,
                "description": "Амулет с тёмной энергией."
            },
            "шкура_трогга": {
                "name": "Шкура трогга",
                "type": "material",
                "value": 20,
                "description": "Толстая шкура подземного трогга."
            },
            "пещерный_гриб": {
                "name": "Пещерный гриб",
                "type": "material",
                "value": 8,
                "description": "Съедобный гриб из подземелья."
            },
            "череп": {
                "name": "Череп",
                "type": "material",
                "value": 5,
                "description": "Череп неизвестного существа."
            },
            # Quest items
            "ключ_от_сокровищницы": {
                "name": "Ключ от сокровищницы",
                "type": "key",
                "value": 0,
                "description": "Старинный ключ с магической руной. Должен подходить к замку в сокровищнице."
            },
            "кристалл_природы": {
                "name": "Кристалл природы",
                "type": "quest_item",
                "value": 80,
                "description": "Сияющий зеленый кристалл, наполненный магией природы."
            },
            "цветок_бессмертия": {
                "name": "Цветок бессмертия",
                "type": "quest_item",
                "value": 60,
                "description": "Редкий цветок с целебными свойствами."
            },
            "королевская_корона": {
                "name": "Королевская корона",
                "type": "quest_item",
                "value": 200,
                "description": "Корона древнего короля, украшенная драгоценными камнями."
            },
            "драконий_амулет": {
                "name": "Драконий амулет",
                "type": "quest_item",
                "value": 150,
                "description": "Амулет из драконьей чешуи с магическими свойствами."
            },
            "манускрипт_мага": {
                "name": "Манускрипт мага",
                "type": "quest_item",
                "value": 120,
                "description": "Древняя книга с заклинаниями."
            },
            "золотой_слиток": {
                "name": "Золотой слиток",
                "type": "quest_item",
                "value": 100,
                "description": "Чистый золотой слиток."
            },
            # Special items
            "благословение_природы": {
                "name": "Благословение природы",
                "type": "special",
                "value": 0,
                "description": "Благословение друида, дающее силу природы."
            },
            "эльфийский_амулет_защиты": {
                "name": "Эльфийский амулет защиты",
                "type": "amulet",
                "slot": "amulet",
                "defense": 5,
                "value": 80,
                "description": "Изящный эльфийский амулет, обеспечивающий защиту от темных сил."
            },
            "амулет_морской_глубины": {
                "name": "Амулет морской глубины",
                "type": "amulet",
                "slot": "amulet",
                "defense": 3,
                "value": 70,
                "description": "Амулет из морской раковины, дающий защиту от водных опасностей."
            },
            "гномий_секрет": {
                "name": "Гномий секрет",
                "type": "special",
                "value": 0,
                "description": "Секретное знание гномов о подземных сокровищах."
            }
        }

    def init_quests(self):
        """Initialize all quests in the game"""
        self.quests = {
            "защита_леса": {
                "id": "защита_леса",
                "name": "Защита Леса Эльфов",
                "description": "Помоги эльфам защитить их священный лес от тёмных сил.",
                "requirements": {"location": "эльфийская_роща"},
                "objectives": [
                    {"type": "collect", "item": "светящийся_цветок", "quantity": 3},
                    {"type": "kill", "monster": "тёмный_призрак", "quantity": 5}
                ],
                "completed": False,
                "reward": {"exp": 100, "gold": 50, "item": "эльфийский_амулет_защиты"},
                "next_quest": "тайна_заброшенного_храма"
            },
            "тайна_заброшенного_храма": {
                "id": "тайна_заброшенного_храма",
                "name": "Тайна Заброшенного Храма",
                "description": "Расследуй заброшенный храм и узнай, что там происходит.",
                "requirements": {"location": "заброшенный_храм", "quest_completed": "защита_леса"},
                "objectives": [
                    {"type": "discover", "target": "тёмный_алтарь"},
                    {"type": "kill", "monster": "тёмный_жрец", "quantity": 1}
                ],
                "completed": False,
                "reward": {"exp": 150, "gold": 75, "item": "священный_амулет_защиты"},
                "next_quest": "защита_королевства"
            },
            "защита_королевства": {
                "id": "защита_королевства",
                "name": "Защита Королевства",
                "description": "Помоги королю защитить королевство от набега тёмных сил.",
                "requirements": {"reputation": {"kingdom": 30}, "quest_completed": "тайна_заброшенного_храма"},
                "objectives": [
                    {"type": "collect", "item": "драконий_амулет", "quantity": 1},
                    {"type": "collect", "item": "амулет_морской_глубины", "quantity": 1},
                    {"type": "collect", "item": "огненный_кристалл", "quantity": 1}
                ],
                "completed": False,
                "reward": {"exp": 200, "gold": 100, "item": "королевская_печать", "reputation": {"kingdom": 20}},
                "next_quest": "финальная_битва"
            },
            "финальная_битва": {
                "id": "финальная_битва",
                "name": "Финальная Битва",
                "description": "Останови армию тёмных сил и спаси мир!",
                "requirements": {"level": 10, "quest_completed": "защита_королевства"},
                "objectives": [
                    {"type": "boss", "monster": "древний_дракон"}
                ],
                "completed": False,
                "reward": {"exp": 500, "gold": 500, "item": "легендарный_артефакт", "title": "Спаситель Мира"},
                "next_quest": None
            }
        }

    def init_artifacts(self):
        """Initialize special artifacts in the game"""
        self.artifact_templates = {
            "амулет_природы": Artifact(
                name="Амулет Природы",
                description="Древний амулет, содержащий силу лесов и полей.",
                rarity="rare",
                effects={
                    "health": 20,
                    "agility": 2,
                    "special": "nature_protection"
                },
                activation="passive"
            ),
            "кольцо_огня": Artifact(
                name="Кольцо Огня",
                description="Магическое кольцо, излучающее тепло и огненную энергию.",
                rarity="rare",
                effects={
                    "attack": 3,
                    "special": "fire_damage"
                },
                activation="passive"
            ),
            "кристалл_времени": Artifact(
                name="Кристалл Времени",
                description="Таинственный кристалл, позволяющий замедлять время вокруг владельца.",
                rarity="epic",
                effects={
                    "agility": 5,
                    "special": "time_slow"
                },
                activation="active",
                cooldown=5
            )
        }

    def init_companions(self):
        """Initialize potential companions for the player"""
        self.companion_templates = {
            "элвин": Companion(
                name="Элвин",
                race="эльф",
                character_class="лучник",
                level=1,
                health=40,
                max_health=40,
                attack=6,
                defense=3,
                skills={"archery": 8, "stealth": 6},
                inventory=["эльфийский_лук", "колчан_со_стрелами"],
                description="Ловкий эльф-лучник с острым зрением и верным луком.",
                loyalty=50,
                special_ability="Точный выстрел"
            ),
            "грум": Companion(
                name="Грум",
                race="гном",
                character_class="воин",
                level=1,
                health=60,
                max_health=60,
                attack=5,
                defense=7,
                skills={"swordsmanship": 7, "mining": 9},
                inventory=["гномий_топор", "стальной_щит"],
                description="Сильный и выносливый гном-воин, мастер ближнего боя.",
                loyalty=50,
                special_ability="Боевой клич"
            ),
            "мира": Companion(
                name="Мира",
                race="человек",
                character_class="целитель",
                level=1,
                health=30,
                max_health=30,
                attack=2,
                defense=2,
                skills={"magic": 6, "alchemy": 8},
                inventory=["посох_целителя", "зелье_здоровья"],
                description="Добрая целительница с даром исцеления и магии поддержки.",
                loyalty=50,
                special_ability="Исцеляющий свет"
            )
        }

    def load_progress(self):
        """Загрузка прогресса игрока из базы данных, если он существует"""
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM rpg_progress WHERE user_id = ?', (self.user_id,))
            row = cursor.fetchone()

            if row:
                # Загружаем существующий прогресс
                self.current_location = row[1]
                self.inventory = json.loads(row[2]) if row[2] else []
                self.health = row[3]
                self.level = row[4]
                self.experience = row[5]
                self.gold = row[6]
                self.story_progress = json.loads(row[7]) if row[7] else {"main_quest": "начало"}
                self.name = row[8] or ""
                self.character_class = row[9] or ""
                self.race = row[10] or ""
                self.abilities = json.loads(row[11]) if row[11] else {
                    "strength": 5, "agility": 5, "intelligence": 5, "charisma": 5, "stamina": 5
                }
                self.skills = json.loads(row[12]) if row[12] else {
                    "swordsmanship": 0, "archery": 0, "magic": 0, "stealth": 0, "alchemy": 0, "barter": 0
                }
                self.armor_slots = json.loads(row[13]) if row[13] else {
                    "head": None, "chest": None, "hands": None, "legs": None, "feet": None,
                    "weapon": None, "shield": None, "amulet": None, "ring": None
                }
                self.active_quests = json.loads(row[14]) if row[14] else []
                self.completed_quests = json.loads(row[15]) if row[15] else []
                self.reputation = json.loads(row[16]) if row[16] else {
                    "kingdom": 0, "guild_of_thieves": 0, "mages_guild": 0, "merchants": 0, "druid_circle": 0
                }
                self.party_members = []
                if row[17]:
                    party_data = json.loads(row[17])
                    for member_data in party_data:
                        self.party_members.append(Companion.from_dict(member_data))

                self.artifacts = []
                if row[18]:
                    artifacts_data = json.loads(row[18])
                    for artifact_data in artifacts_data:
                        self.artifacts.append(Artifact.from_dict(artifact_data))

                self.difficulty = row[19] or GameDifficulty.NORMAL.value

                # Рассчитываем максимальное здоровье на основе уровня и выносливости
                self.max_health = GameConstants.MAX_HEALTH + ((self.level - 1) * 10)
                if self.race == CharacterRace.DWARF.value:
                    self.max_health = int(self.max_health * 1.2)
                if self.character_class == CharacterClass.PALADIN.value:
                    self.max_health += 10
                elif self.character_class == CharacterClass.HEALER.value:
                    self.max_health -= 5

                # Убеждаемся, что здоровье не превышает максимум
                if self.health > self.max_health:
                    self.health = self.max_health

                # Рассчитываем очки навыков на основе уровня
                self.skill_points = (self.level - 1) * GameConstants.SKILL_POINTS_PER_LEVEL

                print(f"\n🎮 Загружен существующий персонаж: {self.name}")
                time.sleep(1)
                return True
            else:
                # Создаем нового персонажа
                self.initialize_new_character()
                return False
        finally:
            conn.close()

    def initialize_new_character(self):
        """Initialize a new character with default values"""
        self.health = GameConstants.MAX_HEALTH
        self.max_health = GameConstants.MAX_HEALTH
        self.level = 1
        self.experience = 0
        self.gold = GameConstants.STARTING_GOLD
        self.inventory = ["хлеб", "фляга_воды"]
        self.skill_points = 0
        self.story_progress = {"main_quest": "начало"}

    def save_progress(self):
        """Полное сохранение прогресса игрока в базу данных"""
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        try:
            # Преобразуем сложные структуры данных в JSON строки
            inventory_str = json.dumps(self.inventory)
            abilities_str = json.dumps(self.abilities)
            skills_str = json.dumps(self.skills)
            armor_slots_str = json.dumps(self.armor_slots)
            active_quests_str = json.dumps(self.active_quests)
            completed_quests_str = json.dumps(self.completed_quests)
            reputation_str = json.dumps(self.reputation)
            party_members_str = json.dumps([member.to_dict() for member in self.party_members])
            artifacts_str = json.dumps([artifact.to_dict() for artifact in self.artifacts])
            story_progress_str = json.dumps(self.story_progress)

            # Проверяем, существует ли запись для этого пользователя
            cursor.execute('SELECT user_id FROM rpg_progress WHERE user_id = ?', (self.user_id,))
            exists = cursor.fetchone()

            if exists:
                # Обновляем существующую запись
                cursor.execute('''
                UPDATE rpg_progress SET
                    current_location = ?, inventory = ?, health = ?, level = ?, experience = ?,
                    gold = ?, story_progress = ?, player_name = ?, player_class = ?, race = ?,
                    abilities = ?, skills = ?, armor_slots = ?, active_quests = ?, completed_quests = ?,
                    reputation = ?, party_members = ?, artifacts = ?, difficulty = ?
                WHERE user_id = ?
                ''', (
                    self.current_location, inventory_str, self.health, self.level, self.experience,
                    self.gold, story_progress_str, self.name, self.character_class, self.race,
                    abilities_str, skills_str, armor_slots_str, active_quests_str, completed_quests_str,
                    reputation_str, party_members_str, artifacts_str, self.difficulty,
                    self.user_id
                ))
            else:
                # Создаем новую запись
                cursor.execute('''
                INSERT INTO rpg_progress (
                    user_id, current_location, inventory, health, level, experience, gold, story_progress,
                    player_name, player_class, race, abilities, skills, armor_slots, active_quests,
                    completed_quests, reputation, party_members, artifacts, difficulty
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.user_id, self.current_location, inventory_str, self.health, self.level, self.experience,
                    self.gold, story_progress_str, self.name, self.character_class, self.race,
                    abilities_str, skills_str, armor_slots_str, active_quests_str, completed_quests_str,
                    reputation_str, party_members_str, artifacts_str, self.difficulty
                ))

            conn.commit()
            print(f"\n💾 Прогресс успешно сохранен для игрока {self.name} (ID: {self.user_id})!")
            return True
        except Exception as e:
            print(f"\n❌ Ошибка при сохранении прогресса: {str(e)}")
            return False
        finally:
            conn.close()

    def select_character(self):
        """Character creation process"""
        clear_screen()
        display_ascii_art("title")

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("ДОБРО ПОЖАЛОВАТЬ В МИР ВЕЧНЫХ ТЕНЕЙ!", 0.02)
        colorful_print(BANNER_BORDER)

        # Character name
        self.name = input(f"\nКак тебя зовут, путник? ").strip()
        if not self.name:
            self.name = "Неизвестный Герой"

        # Character class selection
        self.select_class()

        # Character race selection
        self.select_race()

        # Set initial stats based on class and race
        self.apply_initial_stats()

        # Add starting equipment
        self.add_starting_equipment()

        # Create initial quest from druid
        self.create_initial_quest()

        clear_screen()
        colorful_print(
            f"\n🎉 {self.name}, {self.race} {self.character_class}, добро пожаловать в наш мир!")
        time.sleep(2)

    def select_class(self):
        """Select character class"""
        clear_screen()
        colorful_print("\n" + SECTION_BORDER)
        typewriter_effect("ВЫБЕРИ СВОЙ ПУТЬ", 0.02)
        colorful_print(SECTION_BORDER)

        classes = [
            {"name": CharacterClass.WARRIOR.value,
             "description": "Мастер ближнего боя, обладающий высокой защитой и силой. Идеален для новичков.",
             "ascii": "warrior"},
            {"name": CharacterClass.MAGE.value,
             "description": "Повелитель магических стихий, наносящий огромный урон, но с низкой защитой.",
             "ascii": "mage"},
            {"name": CharacterClass.ARCHER.value,
             "description": "Стрелок издалека с высокой ловкостью и точностью. Может атаковать из укрытия.",
             "ascii": "archer"},
            {"name": CharacterClass.ROGUE.value,
             "description": "Скрытный воин, мастер критических ударов и уклонения. Идеален для скрытных прохождений.",
             "ascii": "rogue"},
            {"name": CharacterClass.HEALER.value,
             "description": "Поддерживающий персонаж с мощными восстановительными заклинаниями и защитной магией.",
             "ascii": "healer"},
            {"name": CharacterClass.PALADIN.value,
             "description": "Священный воин с балансом между атакой и защитой. Способен исцелять и защищать союзников.",
             "ascii": "paladin"}
        ]

        for i, cls in enumerate(classes, 1):
            print(f"\n{i}. {cls['name'].capitalize()}")
            print(f"   {cls['description']}")
            if cls["ascii"]:
                display_ascii_art(cls["ascii"])

        while True:
            choice = input(f"\nВыбери класс (1-{len(classes)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(classes):
                self.character_class = classes[int(choice) - 1]["name"]
                break
            print(f"Неверный выбор. Попробуй снова.")

    def select_race(self):
        """Select character race"""
        clear_screen()
        colorful_print("\n" + SECTION_BORDER)
        typewriter_effect("ВЫБЕРИ СВОЮ РАСУ", 0.02)
        colorful_print(SECTION_BORDER)

        races = [
            {"name": CharacterRace.HUMAN.value,
             "description": "Сбалансированная раса со способностью к адаптации. +10% к золоту за продажу.",
             "bonus": "+10% gold from selling"},
            {"name": CharacterRace.ELF.value,
             "description": "Ловкие и магически одаренные существа. +1 к критическому урону и +2 к интеллекту.",
             "bonus": "+1 critical damage, +2 intelligence"},
            {"name": CharacterRace.DWARF.value,
             "description": "Крепкие и выносливые создания. +20% к максимальному здоровью и сопротивление ядам.",
             "bonus": "+20% max health, poison resistance"},
            {"name": CharacterRace.ORC.value, "description": "Сильные и агрессивные воины. +2 к силе, но -1 к харизме.",
             "bonus": "+2 strength, -1 charisma"},
            {"name": CharacterRace.FAIRY.value,
             "description": "Маленькие магические существа. +3 к ловкости и способность становиться невидимыми.",
             "bonus": "+3 agility, invisibility ability"}
        ]

        for i, race in enumerate(races, 1):
            print(f"\n{i}. {race['name'].capitalize()}")
            print(f"   {race['description']}")
            print(f"   Бонус: {race['bonus']}")

        while True:
            choice = input(f"\nВыбери расу (1-{len(races)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(races):
                self.race = races[int(choice) - 1]["name"]
                break
            print(f"Неверный выбор. Попробуй снова.")

    def apply_initial_stats(self):
        """Apply initial stats based on class and race"""
        # Base stats
        self.abilities = {
            "strength": 5,
            "agility": 5,
            "intelligence": 5,
            "charisma": 5,
            "stamina": 5
        }

        # Class bonuses
        class_bonuses = {
            CharacterClass.WARRIOR.value: {"strength": 3, "stamina": 3},
            CharacterClass.MAGE.value: {"intelligence": 5, "charisma": 2},
            CharacterClass.ARCHER.value: {"agility": 4, "intelligence": 2},
            CharacterClass.ROGUE.value: {"agility": 5, "charisma": 2},
            CharacterClass.HEALER.value: {"intelligence": 4, "charisma": 4},
            CharacterClass.PALADIN.value: {"strength": 2, "stamina": 2, "charisma": 3}
        }

        if self.character_class in class_bonuses:
            for stat, bonus in class_bonuses[self.character_class].items():
                self.abilities[stat] += bonus

        # Race bonuses
        race_bonuses = {
            CharacterRace.HUMAN.value: {"charisma": 2},
            CharacterRace.ELF.value: {"agility": 2, "intelligence": 2},
            CharacterRace.DWARF.value: {"strength": 1, "stamina": 3},
            CharacterRace.ORC.value: {"strength": 3, "stamina": 2},
            CharacterRace.FAIRY.value: {"agility": 4, "intelligence": 2}
        }

        if self.race in race_bonuses:
            for stat, bonus in race_bonuses[self.race].items():
                self.abilities[stat] += bonus

        # Apply health bonuses
        self.max_health = GameConstants.MAX_HEALTH
        if self.race == CharacterRace.DWARF.value:
            self.max_health = int(self.max_health * 1.2)
        if self.character_class == CharacterClass.PALADIN.value:
            self.max_health += 10
        elif self.character_class == CharacterClass.HEALER.value:
            self.max_health -= 5

        self.health = self.max_health

    def add_starting_equipment(self):
        """Add starting equipment based on class"""
        # Weapons based on class
        class_weapons = {
            CharacterClass.WARRIOR.value: "деревянный_меч",
            CharacterClass.MAGE.value: "магический_жезл",
            CharacterClass.ARCHER.value: "эльфийский_лук",
            CharacterClass.ROGUE.value: "ржавый_нож",
            CharacterClass.HEALER.value: "посох_целителя",
            CharacterClass.PALADIN.value: "стальной_меч"
        }

        if self.character_class in class_weapons:
            weapon = class_weapons[self.character_class]
            if weapon in self.items:
                self.inventory.append(weapon)
                self.armor_slots["weapon"] = weapon

        # Armor based on class
        class_armor = {
            CharacterClass.WARRIOR.value: "кожаный_доспех",
            CharacterClass.MAGE.value: "шлем_мага",
            CharacterClass.ARCHER.value: "куртка",
            CharacterClass.ROGUE.value: "куртка",
            CharacterClass.HEALER.value: "шлем_мага",
            CharacterClass.PALADIN.value: "кожаный_доспех"
        }

        if self.character_class in class_armor:
            armor = class_armor[self.character_class]
            if armor in self.items and self.items[armor]["type"] == "armor":
                slot = self.items[armor]["slot"]
                self.armor_slots[slot] = armor
                # Remove from inventory if it was added there
                if armor in self.inventory:
                    self.inventory.remove(armor)

    def create_initial_quest(self):
        """Create initial quest based on character class"""
        if self.character_class in ["воин", "маг", "лучник", "вор", "целитель", "паладин"]:
            quest_name = f"начальный_квест_{self.character_class}"
            quest_description = self.npcs["друид_альдар"]["class_quests"][self.character_class]

            self.active_quests.append({
                "id": quest_name,
                "name": f"Классовый квест: {quest_description}",
                "description": quest_description,
                "completed": False
            })

    def get_total_stats(self):
        """Calculate total stats with bonuses from equipment, race, class, etc."""
        stats = {
            "attack": 5,
            "defense": 2,
            "health": self.health,
            "max_health": self.max_health,
            "critical_chance": GameConstants.CRITICAL_HIT_CHANCE_BASE,
            "dodge_chance": GameConstants.DODGE_CHANCE_BASE
        }

        # Add base ability modifiers
        stats["attack"] += self.abilities["strength"] // 2
        stats["defense"] += self.abilities["stamina"] // 3
        stats["critical_chance"] += self.abilities["agility"] * 0.01
        stats["dodge_chance"] += self.abilities["agility"] * 0.005

        # Add equipment bonuses
        for slot, item_name in self.armor_slots.items():
            if item_name and item_name in self.items:
                item = self.items[item_name]
                if item["type"] == "weapon":
                    stats["attack"] += item.get("attack", 0)
                    if "crit_bonus" in item:
                        stats["critical_chance"] += item["crit_bonus"]
                elif item["type"] in ["armor", "shield"]:
                    stats["defense"] += item.get("defense", 0)

        # Apply race bonuses
        if self.race == CharacterRace.ELF.value:
            stats["critical_chance"] += 0.05  # +5% critical chance
        elif self.race == CharacterRace.DWARF.value:
            stats["defense"] += 2  # +2 defense

        # Apply class bonuses
        if self.character_class == CharacterClass.WARRIOR.value:
            stats["defense"] += 3
        elif self.character_class == CharacterClass.MAGE.value:
            stats["attack"] += 5
            stats["defense"] -= 2
        elif self.character_class == CharacterClass.ARCHER.value:
            stats["critical_chance"] += 0.1  # +10% critical chance

        # Apply artifact bonuses
        for artifact in self.artifacts:
            for stat, value in artifact.effects.items():
                if stat in stats:
                    if isinstance(value, (int, float)):
                        stats[stat] += value

        # Clamp values to reasonable ranges
        stats["critical_chance"] = min(0.8, stats["critical_chance"])  # Max 80% critical chance
        stats["dodge_chance"] = min(0.6, stats["dodge_chance"])  # Max 60% dodge chance
        stats["attack"] = max(1, stats["attack"])
        stats["defense"] = max(0, stats["defense"])

        return stats

    def show_character_sheet(self):
        """Display detailed character information"""
        clear_screen()
        stats = self.get_total_stats()

        colorful_print("\n" + BANNER_BORDER)
        colorful_print(f"👤 {self.name} - {self.race.capitalize()} {self.character_class.capitalize()}")
        colorful_print(BANNER_BORDER)

        # Health and basic stats
        health_bar = self.create_health_bar(self.health, stats["max_health"])
        print(f"\n❤️  Здоровье: {health_bar} {self.health}/{stats['max_health']}")
        print(f"⚔️  Атака: {stats['attack']}")
        print(f"🛡️  Защита: {stats['defense']}")
        print(f"⭐ Крит. шанс: {stats['critical_chance']:.0%}")
        print(f"💫 Шанс уворота: {stats['dodge_chance']:.0%}")
        print(f"\n🏅 Уровень: {self.level}")
        print(f"⚡ Опыт: {self.experience}/{GameConstants.XP_PER_LEVEL}")
        print(f"💰 Золото: {self.gold}")

        # Abilities
        colorful_print("\n📊 Способности:")
        for ability, value in self.abilities.items():
            bar = self.create_stat_bar(value, 20)
            print(f"  {ability.capitalize()}: {bar} {value}")

        # Skills
        colorful_print("\n🎯 Навыки:")
        for skill, value in self.skills.items():
            if value > 0:
                bar = self.create_stat_bar(value, 20)
                print(f"  {skill.capitalize()}: {bar} {value}")

        # Equipment
        colorful_print("\n🎭 Снаряжение:")
        equipped_items = 0
        for slot, item_name in self.armor_slots.items():
            if item_name:
                equipped_items += 1
                item = self.items.get(item_name, {})
                slot_name = slot.capitalize()
                item_name_display = item.get("name", item_name.replace("_", " ").capitalize())

                if item["type"] == "weapon":
                    stats_str = f"(Атака: +{item['attack']})"
                elif item["type"] in ["armor", "shield"]:
                    stats_str = f"(Защита: +{item['defense']})"
                else:
                    stats_str = ""

                print(f"  {slot_name}: {item_name_display} {stats_str}")

        if equipped_items == 0:
            print("  Нет снаряженных предметов")

        # Inventory
        colorful_print(f"\n🎒 Инвентарь ({len(self.inventory)}/{GameConstants.INVENTORY_CAPACITY}):")
        if not self.inventory:
            print("  Пусто")
        else:
            # Group items by type
            grouped_items = {}
            for item_name in self.inventory:
                item = self.items.get(item_name, {})
                item_type = item.get("type", "other")
                if item_type not in grouped_items:
                    grouped_items[item_type] = []
                grouped_items[item_type].append((item_name, item))

            # Display grouped items
            type_names = {
                "weapon": "Оружие",
                "armor": "Броня",
                "consumable": "Расходники",
                "material": "Материалы",
                "key": "Ключи",
                "quest_item": "Квестовые предметы"
            }

            for item_type, items in grouped_items.items():
                type_name = type_names.get(item_type, item_type.capitalize())
                print(f"\n  {type_name}:")
                for i, (item_name, item) in enumerate(items, 1):
                    item_name_display = item.get("name", item_name.replace("_", " ").capitalize())

                    if item_type == "consumable" and item.get("effect") == "health":
                        stats_str = f"(Лечит: +{item['value']} HP)"
                    elif item_type == "weapon":
                        stats_str = f"(Атака: +{item['attack']})"
                    elif item_type in ["armor", "shield"]:
                        stats_str = f"(Защита: +{item['defense']})"
                    else:
                        stats_str = f"(Цена: {item.get('value', 0)} золота)"

                    print(f"    {i}. {item_name_display} {stats_str}")

        # Party members
        if self.party_members:
            colorful_print(f"\n👥 Члены отряда ({len(self.party_members)}/{GameConstants.PARTY_MAX_SIZE}):")
            for member in self.party_members:
                health_bar = self.create_health_bar(member.health, member.max_health)
                print(f"  {member.name} - {member.race} {member.character_class}")
                print(f"    ❤️ Здоровье: {health_bar} {member.health}/{member.max_health}")
                print(f"    💯 Лояльность: {self.create_health_bar(member.loyalty, 100, 10)} {member.loyalty}/100")

        # Artifacts
        if self.artifacts:
            colorful_print("\n🔮 Артефакты:")
            for artifact in self.artifacts:
                rarity_color = {
                    "common": COLOR_WHITE,
                    "rare": COLOR_BLUE,
                    "epic": COLOR_MAGENTA,
                    "legendary": COLOR_YELLOW
                }.get(artifact.rarity)

                activation_str = f"({artifact.activation}, {artifact.cooldown}s cooldown)" if artifact.activation == "active" else f"({artifact.activation})"
                print(f"  {rarity_color}{artifact.name} {activation_str}")
                print(f"    {artifact.description}")

        # Active quests
        colorful_print(f"\n📜 Активные квесты ({len(self.active_quests)}):")
        if not self.active_quests:
            print("  Нет активных квестов")
        else:
            for i, quest in enumerate(self.active_quests, 1):
                status = "✅" if quest.get("completed", False) else "🔄"
                print(f"  {i}. {status} {quest['name']}")

        print("\n" + BANNER_BORDER)
        pause_game()

    def create_health_bar(self, current, maximum, length=20):
        """Create a visual health bar"""
        filled = int((current / maximum) * length)
        empty = length - filled
        color = COLOR_GREEN if current / maximum > 0.6 else COLOR_YELLOW if current / maximum > 0.3 else COLOR_RED
        return f"{color}{'█' * filled}{'░' * empty}{COLOR_RESET} ({current}/{maximum})"

    def create_stat_bar(self, value, maximum, length=10):
        """Create a visual stat bar"""
        filled = int((value / maximum) * length)
        empty = length - filled
        return f"{'█' * filled}{'░' * empty}"

    def display_world_map(self):
        """Display the world map with visual ASCII art"""
        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("КАРТА МИРА ЭЛДАРИИ", 0.02)
        colorful_print(BANNER_BORDER)

        # Create a visual map representation
        map_art = """
                      🏔️ Горы Айрона
                         |
                         |
       🌲 Лес Вечных Теней -- 🌟 Распутье Судьбы -- 🏖️ Берег Бездны
                         |           |
                         |           |
                  🏡 Деревня Мира   🏰 Замок Короля
        """

        print(f"{map_art}")

        # List accessible locations
        print(f"\nДОСТУПНЫЕ ЛОКАЦИИ:")

        # Group locations by region
        regions = {
            "Центральные земли": ["начало", "деревня", "королевский_замок"],
            "Лесные территории": ["лес", "эльфийская_роща", "древнее_святилище", "пещера"],
            "Горные хребты": ["горы", "горная_деревня", "крепость", "драконья_вершина"],
            "Морские владения": ["море", "порт", "подводное_царство"],
            "Подземные глубины": ["подземелье", "сокровищница", "заброшенный_храм"]
        }

        current_loc_id = self.current_location
        current_location = self.locations.get(current_loc_id, {})

        for region, loc_ids in regions.items():
            print(f"\n📍 {region}")
            for loc_id in loc_ids:
                if loc_id not in self.locations:
                    continue

                location = self.locations[loc_id]
                loc_name = location.get("display_name", location["name"])
                status = ""
                is_locked = location.get("locked", False)

                # Determine status icon
                if loc_id == current_loc_id:
                    status = f"➡️ Текущее местоположение"
                elif is_locked:
                    status = f"🔒 Требуются условия"
                else:
                    status = f"✅ Доступно"

                print(f"  {loc_name}: {status}")

                # Show requirements if locked
                if is_locked:
                    requirements = []
                    if location.get("required_item"):
                        requirements.append(f"Предмет: {location['required_item'].replace('_', ' ')}")
                    if location.get("required_reputation"):
                        for faction, rep in location["required_reputation"].items():
                            requirements.append(f"Репутация с {faction}: {rep}")
                    if location.get("required_quest"):
                        requirements.append(f"Квест: {location['required_quest']}")

                    if requirements:
                        print(f"    Требуется: {', '.join(requirements)}")

        # Display location description
        if current_location:
            print(f"\nТВОЁ ТЕКУЩЕЕ МЕСТОПОЛОЖЕНИЕ:")
            print(f"  {current_location.get('display_name', current_location['name'])}")
            print(f"  {current_location['description']}")

            # Show location map if available
            if "map" in current_location:
                print(f"\n{current_location['map']}")

            # Show exits
            if "exits" in current_location and current_location["exits"]:
                print(f"\nДОСТУПНЫЕ ВЫХОДЫ:")
                for exit_id in current_location["exits"]:
                    if exit_id in self.locations:
                        exit_loc = self.locations[exit_id]
                        exit_name = exit_loc.get("display_name", exit_loc["name"])
                        status = "✅"
                        if exit_loc.get("locked", False):
                            status = "🔒"
                        print(f"  {status} {exit_name}")

        print("\n" + BANNER_BORDER)
        pause_game()

    def rest_at_location(self):
        """Rest at current location to recover health"""
        clear_screen()

        # Calculate healing amount
        stats = self.get_total_stats()
        healing = int(stats["max_health"] * 0.3)  # Heal 30% of max health
        new_health = min(stats["max_health"], self.health + healing)
        healed_amount = new_health - self.health
        self.health = new_health

        # Heal party members
        party_heal_messages = []
        for member in self.party_members:
            if member.is_alive():
                member_healing = int(member.max_health * 0.3)
                member.heal(member_healing)
                party_heal_messages.append(f"{member.name} восстановил {member_healing} здоровья")

        # Display rest animation
        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("ОТДЫХ В БЕЗОПАСНОМ МЕСТЕ", 0.02)
        colorful_print(BANNER_BORDER)

        print(f"\n🌿 Ты нашел укромное место для отдыха.")
        time.sleep(1)
        print(f"🌙 Ночь прошла спокойно, и ты восстановил свои силы.")
        time.sleep(1)

        if healed_amount > 0:
            print(f"\n💖 Ты восстановил {healed_amount} здоровья!")

        for message in party_heal_messages:
            print(f"👥 {message}")

        # Random event during rest
        if random.random() < 0.3:  # 30% chance for random event
            events = [
                "Во время отдыха ты услышал странный шепот на ветру...",
                "К тебе подошел местный житель и дал немного еды.",
                "Ты заметил в небе падающую звезду и загадал желание.",
                "Во сне тебе привиделся древний символ..."
            ]
            event = random.choice(events)
            print(f"\n💫 {event}")

            if "дал немного еды" in event:
                self.inventory.append("хлеб")
                print(f"🍞 Ты получил хлеб!")

        print("\n" + BANNER_BORDER)
        pause_game()

    def handle_combat(self, monster_name):
        """Handle combat with a monster using turn-based system"""
        if monster_name not in self.monsters:
            return f"Нет такого монстра!"

        # Create monster instance
        monster_data = self.monsters[monster_name]
        monster = Monster.from_dict(monster_data)

        # Apply level scaling to monster
        level_diff = self.level - monster.level
        if level_diff > 0:
            scale_factor = 1 + (level_diff * 0.1)
            monster.health = int(monster.health * scale_factor)
            monster.attack = int(monster.attack * scale_factor)
            monster.defense = int(monster.defense * scale_factor)
            monster.xp_reward = int(monster.xp_reward * (1 + level_diff * 0.05))
            monster.gold_reward = int(monster.gold_reward * (1 + level_diff * 0.05))

        monster.max_health = monster.health

        clear_screen()
        display_ascii_art("battle")

        colorful_print("\n" + BATTLE_BORDER)
        typewriter_effect(f"⚔️ БИТВА С {monster.name.upper()}!", 0.02)
        colorful_print(BATTLE_BORDER)

        print(f"\n{monster.description}\n")

        combat_active = True
        turn = 1

        while combat_active:
            stats = self.get_total_stats()

            # Display combat status
            self.display_combat_status(monster, turn)

            # Player turn
            print(f"\n🎯 ТВОЙ ХОД (Ход #{turn})")
            action = self.get_combat_action(monster)

            if action == CombatAction.FLEE:
                if random.random() < 0.5:  # 50% chance to flee successfully
                    colorful_print("\n💨 Ты успешно сбежал от битвы!")
                    combat_active = False
                    return "\nВы сбежали от битвы."
                else:
                    print("\n" + COLOR_RED + "❌ Не удалось сбежать! Монстр атакует!" + COLOR_RESET)

            elif action == CombatAction.ATTACK:
                damage = self.calculate_damage(stats, monster)
                actual_damage = monster.take_damage(damage)
                print(f"\n⚔️ Ты атаковал {monster.name} и нанес {actual_damage} урона!")

                # Critical hit effect
                if random.random() < stats["critical_chance"]:
                    print(f"✨ КРИТИЧЕСКИЙ УДАР!")

            elif action == CombatAction.DEFEND:
                print(
                    f"\n🛡️ Ты готовишься к защите! Следующая атака монстра будет наносить меньше урона.")
                # This would apply a defense buff in a more complex system

            elif action == CombatAction.USE_ITEM:
                self.use_item_in_combat()
                # Monster still gets to attack after item use

            elif action == CombatAction.SPECIAL and self.character_class == "маг":
                self.use_special_ability(monster)

            # Check if monster is defeated
            if not monster.is_alive():
                return self.handle_victory(monster)

            # Monster turn
            self.handle_monster_turn(monster, stats)

            # Check if player is defeated
            if self.health <= 0:
                return self.handle_defeat(monster)

            # Apply cooldowns to artifacts
            for artifact in self.artifacts:
                artifact.tick_cooldown()

            turn += 1
            time.sleep(1)

        return ""

    def display_combat_status(self, monster, turn):
        """Display current combat status"""
        stats = self.get_total_stats()

        # Player health bar
        player_health_bar = self.create_health_bar(self.health, stats["max_health"])
        # Monster health bar
        monster_health_bar = self.create_health_bar(monster.health, monster.max_health)

        print(f"\n╔{'═' * 30}╗")
        print(f"║  Игрок: {self.name}        ║")
        print(f"║  {player_health_bar}  ║")
        print(f"║  Атака: {stats['attack']}  Защита: {stats['defense']}  ║")
        print(f"╚{'═' * 30}╝")

        print(f"\n╔{'═' * 30}╗")
        print(f"║  Монстр: {monster.name}     ║")
        print(f"║  {monster_health_bar}  ║")
        print(f"║  Уровень: {monster.level}  Сила: {monster.attack}  ║")
        print(f"╚{'═' * 30}╝")

    def get_combat_action(self, monster):
        """Get player's combat action choice"""
        print("\nДоступные действия:")
        print("1. ⚔️ Атаковать")
        print("2. 🛡️ Защищаться")

        # Show items that can be used in combat
        usable_items = [item for item in self.inventory if self.items.get(item, {}).get("type") == "consumable"]
        if usable_items:
            print("3. 💊 Использовать предмет")

        # Show special abilities based on class
        if self.character_class == "маг":
            print("4. 🔮 Использовать магию")

        print("5. 🏃 Сбежать")

        while True:
            choice = input(f"\nВаш выбор (1-5): ").strip()
            if choice == "1":
                return CombatAction.ATTACK
            elif choice == "2":
                return CombatAction.DEFEND
            elif choice == "3" and usable_items:
                return CombatAction.USE_ITEM
            elif choice == "4" and self.character_class == "маг":
                return CombatAction.SPECIAL
            elif choice == "5":
                return CombatAction.FLEE
            print(f"Неверный выбор. Попробуйте снова.")

    def calculate_damage(self, stats, monster):
        """Calculate damage dealt to monster"""
        base_damage = stats["attack"]

        # Apply critical hit chance
        if random.random() < stats["critical_chance"]:
            base_damage *= 2

        # Apply random variation (0.8-1.2x)
        base_damage *= random.uniform(0.8, 1.2)

        return int(base_damage)

    def use_item_in_combat(self):
        """Use an item during combat"""
        usable_items = [item for item in self.inventory if self.items.get(item, {}).get("type") == "consumable"]

        print("\nДоступные предметы:")
        for i, item_name in enumerate(usable_items, 1):
            item = self.items[item_name]
            print(f"{i}. {item['name']} - {item['description']}")

        print("0. Отмена")

        choice = input(f"\nВыберите предмет (0-{len(usable_items)}): ").strip()
        if choice == "0" or not choice:
            return

        if choice.isdigit() and 1 <= int(choice) <= len(usable_items):
            item_name = usable_items[int(choice) - 1]
            item = self.items[item_name]

            if item["effect"] == "health":
                heal = item["value"]
                old_health = self.health
                self.health = min(self.get_total_stats()["max_health"], self.health + heal)
                heal_amount = self.health - old_health
                print(
                    f"\n💖 Ты использовал {item['name']} и восстановил {heal_amount} здоровья!")

                # Remove item from inventory
                if item_name in self.inventory:
                    self.inventory.remove(item_name)

    def use_special_ability(self, monster):
        """Use class-specific special ability"""
        if self.character_class == "маг":
            # Fireball spell
            damage = 15 + self.abilities["intelligence"] * 2
            monster.take_damage(damage)
            print(f"\n🔥 Ты сотворил ОГНЕННЫЙ ШАР и нанес {damage} урона {monster.name}!")

    def handle_monster_turn(self, monster, stats):
        """Handle monster's turn in combat"""
        attack = monster.get_random_attack()
        damage = max(1, attack["damage"] - stats["defense"] // 2)

        # Apply dodge chance
        if random.random() < stats["dodge_chance"]:
            print(f"\n💨 Ты уклонился от атаки {monster.name}!")
            return

        self.health -= damage
        print(f"\n⚔️ {monster.name} атаковал тебя и нанес {damage} урона!")

        # Special attack message
        if attack["name"] != "Basic Attack":
            print(f"  {attack['description']}")

    def handle_victory(self, monster):
        """Handle victory over a monster"""
        clear_screen()
        display_ascii_art("victory")

        xp_gain = monster.xp_reward
        gold_gain = monster.gold_reward
        loot = monster.get_drops()

        # Apply party XP split
        party_size = len([m for m in self.party_members if m.is_alive()]) + 1
        xp_gain = int(xp_gain / party_size)
        gold_gain = int(gold_gain / party_size)

        # Award XP and level up if needed
        self.experience += xp_gain
        level_up_message = ""

        if self.experience >= GameConstants.XP_PER_LEVEL:
            levels_gained = self.experience // GameConstants.XP_PER_LEVEL
            self.level += levels_gained
            self.experience %= GameConstants.XP_PER_LEVEL
            self.skill_points += levels_gained * GameConstants.SKILL_POINTS_PER_LEVEL
            self.max_health += levels_gained * 10
            self.health = self.max_health  # Full heal on level up
            level_up_message = f"\n🌟 ПОВЫШЕНИЕ УРОВНЯ! Теперь ты {self.level} уровня!"
            level_up_message += f"\n✨ Получено {self.skill_points} очков навыков!"

        # Award rewards
        self.gold += gold_gain
        for item in loot:
            self.inventory.append(item)

        # Heal party members slightly
        for member in self.party_members:
            if member.is_alive():
                heal_amount = int(member.max_health * 0.1)
                member.heal(heal_amount)

        # Display victory message
        colorful_print("\n" + BATTLE_BORDER)
        typewriter_effect(f"🎉 ПОБЕДА НАД {monster.name.upper()}!", 0.02)
        colorful_print(BATTLE_BORDER)

        print(f"\n🏆 Награды:")
        print(f"  Опыт: {xp_gain}")
        print(f"  Золото: {gold_gain}")

        if loot:
            print(f"  Добыча: {', '.join(loot)}")

        if level_up_message:
            print(level_up_message)

        print("\n" + BANNER_BORDER)
        pause_game()

        return f"\n✅ Победа! Получено {xp_gain} опыта и {gold_gain} золота."

    def interact_with_npc(self, npc_id):
        """Interact with an NPC in the current location"""
        if npc_id not in self.npcs:
            return f"Нет такого NPC!"

        npc = self.npcs[npc_id]

        # Check requirements to interact with NPC
        requirements_met = True
        missing_requirements = []

        if "requires" in npc:
            requirements = npc["requires"]
            if "item" in requirements and requirements["item"] not in self.inventory:
                requirements_met = False
                missing_requirements.append(f"предмет: {requirements['item'].replace('_', ' ')}")
            if "reputation" in requirements:
                for faction, required_rep in requirements["reputation"].items():
                    current_rep = self.reputation.get(faction, 0)
                    if current_rep < required_rep:
                        requirements_met = False
                        missing_requirements.append(f"репутация с {faction}: {required_rep} (у вас {current_rep})")

        if not requirements_met:
            return f"❌ Ты не можешь поговорить с {npc['name']}. Требуется: {', '.join(missing_requirements)}"

        clear_screen()

        # Display NPC interaction
        colorful_print("\n" + BANNER_BORDER)
        npc_display_name = npc.get("display_name", npc["name"])
        typewriter_effect(f"🗣️  ВЗАИМОДЕЙСТВИЕ С {npc_display_name.upper()}", 0.02)
        colorful_print(BANNER_BORDER)

        # Show NPC description
        long_desc = npc.get("long_description", npc["description"])
        wrapped_desc = wrap_text(long_desc)
        print(f"\n{wrapped_desc}")

        # Show dialogue
        print(f"\n💬 Диалог:")
        for line in npc["dialogue"]:
            typewriter_effect(f"  {line}", 0.03)
            time.sleep(0.2)

        # Handle class selection if this is the druid at the beginning
        if npc_id == "друид_альдар" and not self.character_class:
            self.select_character()
            return "\nТы выбрал свой путь! Теперь ты готов к приключениям."

        # Offer quests if available and requirements met
        quest_given = False
        if "quest" in npc and not any(q["name"] == npc["quest"] for q in self.active_quests + self.completed_quests):
            print(f"\n📜 {npc['name']} предлагает квест: {npc['quest']}")
            accept = input(f"Принять квест? (да/нет): ").lower().strip()

            if accept.startswith('д'):
                self.active_quests.append({
                    "id": f"quest_{npc_id}",
                    "name": npc["quest"],
                    "description": npc["quest"],
                    "completed": False
                })
                print(f"✅ Квест '{npc['quest']}' добавлен в твой дневник!")
                quest_given = True

        # Handle trading if NPC is a trader
        if not quest_given and "trader" in npc:
            print(f"\n💰 {npc['name']} готов торговать с тобой.")
            trade = input(f"Начать торговлю? (да/нет): ").lower().strip()

            if trade.startswith('д'):
                self.trade_with_npc(npc_id)

        print("\n" + BANNER_BORDER)
        pause_game()

        return ""

    def trade_with_npc(self, npc_id):
        """Handle trading with an NPC"""
        if npc_id not in self.npcs or "trader" not in self.npcs[npc_id]:
            return f"Этот NPC не торгует!"

        npc = self.npcs[npc_id]
        trader = npc["trader"]

        trading = True
        while trading:
            clear_screen()

            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect(f"💰 ТОРГОВЛЯ С {npc['name'].upper()}", 0.02)
            colorful_print(BANNER_BORDER)

            print(f"\n💰 У тебя: {self.gold} золота")

            # Show buy options
            colorful_print("\n🛒 ТОВАРЫ ДЛЯ ПОКУПКИ:")
            buy_items = trader.get("buy", {})
            for i, (item_id, price) in enumerate(buy_items.items(), 1):
                item = self.items.get(item_id, {})
                item_name = item.get("name", item_id.replace("_", " ").capitalize())
                item_desc = item.get("description", "Нет описания")
                print(f"{i}. {item_name} - {price} золота")
                print(f"   {item_desc}")

            # Show sell options
            colorful_print(f"\n🏷️  ПРЕДМЕТЫ ДЛЯ ПРОДАЖИ ({len(self.inventory)}/{GameConstants.INVENTORY_CAPACITY}):")
            sellable_items = []

            for item_id in self.inventory:
                item = self.items.get(item_id, {})
                sell_price = trader.get("sell", {}).get(item_id, item.get("value", 1) // 2)
                if sell_price > 0:
                    sellable_items.append((item_id, item, sell_price))

            if sellable_items:
                for i, (item_id, item, price) in enumerate(sellable_items, 1):
                    item_name = item.get("name", item_id.replace("_", " ").capitalize())
                    item_desc = item.get("description", "Нет описания")
                    print(f"{i + len(buy_items)}. {item_name} - {price} золота")
                    print(f"   {item_desc}")
            else:
                print("  Нет предметов для продажи")

            print(f"\n{len(buy_items) + len(sellable_items) + 1}. Назад")

            choice = input(
                f"\nТвой выбор (1-{len(buy_items) + len(sellable_items) + 1}): ").strip()

            if not choice:
                continue

            choice_num = int(choice) if choice.isdigit() else -1
            total_options = len(buy_items) + len(sellable_items) + 1

            if choice_num == total_options:
                trading = False
            elif 1 <= choice_num <= len(buy_items):
                # Buy item
                item_id = list(buy_items.keys())[choice_num - 1]
                price = buy_items[item_id]

                if self.gold >= price:
                    self.gold -= price
                    self.inventory.append(item_id)
                    print(f"✅ Куплен {item_id.replace('_', ' ')} за {price} золота!")
                else:
                    print(f"❌ Недостаточно золота!")
            elif len(buy_items) < choice_num <= len(buy_items) + len(sellable_items):
                # Sell item
                sell_index = choice_num - len(buy_items) - 1
                item_id, item, price = sellable_items[sell_index]

                self.inventory.remove(item_id)
                self.gold += price
                print(f"✅ Продан {item_id.replace('_', ' ')} за {price} золота!")
            else:
                print(f"❌ Неверный выбор!")

            time.sleep(1)

    def show_quest_log(self):
        """Show quest log with detailed information"""
        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("📜 ЖУРНАЛ КВЕСТОВ", 0.02)
        colorful_print(BANNER_BORDER)

        # Show active quests
        colorful_print(f"\n🟡 АКТИВНЫЕ КВЕСТЫ ({len(self.active_quests)}):")
        if not self.active_quests:
            print("  Нет активных квестов")

        for i, quest in enumerate(self.active_quests, 1):
            status = "✅" if quest.get("completed", False) else "🔄"
            print(f"\n{i}. {status} {quest['name']}")
            print(f"   {quest['description']}")

            # Show objectives if available
            if "objectives" in quest:
                print(f"   Цели:")
                for j, objective in enumerate(quest["objectives"], 1):
                    obj_status = "✅" if objective.get("completed", False) else "🔲"
                    if objective.get("type") == "kill":
                        obj_text = f"Убить {objective.get('quantity', 1)} {objective.get('monster', '').replace('_', ' ')}"
                    elif objective.get("type") == "collect":
                        obj_text = f"Собрать {objective.get('quantity', 1)} {objective.get('item', '').replace('_', ' ')}"
                    elif objective.get("type") == "discover":
                        obj_text = f"Найти {objective.get('target', '').replace('_', ' ')}"
                    else:
                        obj_text = f"Неизвестная цель"

                    print(f"     {j}. {obj_status} {obj_text}")

        # Show completed quests
        if self.completed_quests:
            colorful_print(f"\n🟢 ЗАВЕРШЕННЫЕ КВЕСТЫ ({len(self.completed_quests)}):")
            for i, quest in enumerate(self.completed_quests[-5:], 1):  # Show last 5 completed quests
                print(f"\n{i}. ✅ {quest['name']}")
                print(f"   {quest['description']}")
                if "reward" in quest:
                    reward = quest["reward"]
                    rewards_text = []
                    if "exp" in reward:
                        rewards_text.append(f"{reward['exp']} опыта")
                    if "gold" in reward:
                        rewards_text.append(f"{reward['gold']} золота")
                    if "item" in reward:
                        rewards_text.append(f"предмет {reward['item'].replace('_', ' ')}")
                    if rewards_text:
                        print(f"   Награда: {', '.join(rewards_text)}")

        print("\n" + BANNER_BORDER)
        pause_game()

    def talk_to_party_member(self):
        """Talk to a party member to build rapport or get information"""
        if not self.party_members:
            print(f"{COLOR_RED}❌ В твоем отряде нет членов для разговора!{COLOR_RESET}")
            time.sleep(1)
            return

        clear_screen()
        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("🗣️ РАЗГОВОР С ЧЛЕНОМ ОТРЯДА", 0.02)
        colorful_print(BANNER_BORDER)

        print(f"\n{COLOR_YELLOW}Выбери члена отряда для разговора:{COLOR_RESET}")
        for i, member in enumerate(self.party_members, 1):
            status = "❤️" if member.is_alive() else "💀"
            print(f"{i}. {status} {member.name} - {member.race} {member.character_class}")
            print(f"   💯 Лояльность: {self.create_health_bar(member.loyalty, 100, 10)} {member.loyalty}/100")

        print(f"\n{len(self.party_members) + 1}. Назад")

        choice = input(f"\n{COLOR_CYAN}Твой выбор (1-{len(self.party_members) + 1}): {COLOR_RESET}").strip()
        if not choice or choice == str(len(self.party_members) + 1):
            return

        if choice.isdigit() and 1 <= int(choice) <= len(self.party_members):
            member = self.party_members[int(choice) - 1]

            clear_screen()
            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect(f"🗣️ РАЗГОВОР С {member.name.upper()}", 0.02)
            colorful_print(BANNER_BORDER)

            # Display member portrait/description
            print(
                f"\n{COLOR_CYAN}{member.name}{COLOR_RESET} - {member.race.capitalize()} {member.character_class.capitalize()}")
            print(f"{COLOR_WHITE}{member.description}{COLOR_RESET}")

            # Show loyalty status
            loyalty_status = ""
            if member.loyalty >= 80:
                loyalty_status = f"{COLOR_GREEN}Предан тебе безгранично{COLOR_RESET}"
            elif member.loyalty >= 60:
                loyalty_status = f"{COLOR_CYAN}Верный союзник{COLOR_RESET}"
            elif member.loyalty >= 40:
                loyalty_status = f"{COLOR_YELLOW}Нейтральное отношение{COLOR_RESET}"
            elif member.loyalty >= 20:
                loyalty_status = f"{COLOR_RED}Сомневается в тебе{COLOR_RESET}"
            else:
                loyalty_status = f"{COLOR_RED}На грани предательства{COLOR_RESET}"

            print(f"\n{COLOR_MAGENTA}💔 Отношение: {loyalty_status}{COLOR_RESET}")
            print(f"💯 Лояльность: {self.create_health_bar(member.loyalty, 100, 10)} {member.loyalty}/100")

            # Character-specific dialogue based on current quest/story progress
            dialogue_options = [
                f"Расскажи о себе, {member.name}",
                "Что ты думаешь о нашей текущей миссии?",
                "Какие у тебя навыки и способности?",
            ]

            if member.race == "эльф":
                dialogue_options.append("Что ты знаешь о древних лесах?")
            elif member.race == "гном":
                dialogue_options.append("Что ты знаешь о горных туннелях и подземельях?")
            elif member.race == "человек":
                dialogue_options.append("Что ты знаешь о королевстве и его проблемах?")

            if member.character_class == "воин":
                dialogue_options.append("Как ты стал воином?")
            elif member.character_class == "маг":
                dialogue_options.append("Как ты научился магии?")
            elif member.character_class == "целитель":
                dialogue_options.append("Как ты помогаешь раненым?")

            dialogue_options.append("Поблагодарить за службу")
            dialogue_options.append("Предложить золото за верность")

            print(f"\n{COLOR_CYAN}Варианты диалога:{COLOR_RESET}")
            for i, option in enumerate(dialogue_options, 1):
                print(f"{i}. {option}")
            print(f"\n{len(dialogue_options) + 1}. Закончить разговор")

            dialogue_choice = input(
                f"\n{COLOR_CYAN}Выбери реплику (1-{len(dialogue_options) + 1}): {COLOR_RESET}").strip()
            if dialogue_choice.isdigit():
                choice_num = int(dialogue_choice)
                if 1 <= choice_num <= len(dialogue_options):
                    # Handle dialogue choice
                    if choice_num == 1:  # Personal story
                        responses = {
                            "элвин": "Я родился в эльфийской роще, когда еще не было теней. Моя семья служила защитниками леса многие столетия. Когда тьма начала проникать в наши земли, я поклялся сражаться с ней до конца.",
                            "грум": "Я из древнего гномьего клана горного королевства. Наш народ славится мастерством в кузнечном деле и добыче руды. Но когда подземные создания начали выходить на поверхность, я решил стать защитником своего народа.",
                            "мира": "Я выросла в деревне Мира, где нас учили заботиться друг о друге. Когда болезнь поразила нашу деревню, я изучила целительское искусство, чтобы спасти людей. Теперь я путешествую, чтобы помогать всем нуждающимся."
                        }
                        response = responses.get(member.name.lower(),
                                                 f"Я не могу рассказать тебе свою историю, {self.name}. Некоторые тайны должны оставаться скрытыми.")
                        print(f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"{response}\"")
                        member.gain_loyalty(5)
                        print(f"{COLOR_GREEN}✨ Лояльность {member.name} увеличена на 5!{COLOR_RESET}")

                    elif choice_num == 2:  # Current mission opinion
                        if member.loyalty > 50:
                            print(
                                f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Я верю в нашу миссию, {self.name}. Вместе мы сможем победить тьму, угрожающую этим землям.\"")
                        else:
                            print(
                                f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Я надеюсь, что наши действия действительно принесут пользу. Иногда мне кажется, что мы слишком рискуем.\"")
                        member.gain_loyalty(3)

                    elif choice_num == len(dialogue_options) - 1:  # Thank for service
                        print(
                            f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Спасибо за доверие, {self.name}. Я буду сражаться за наш общий идеал до последнего вздоха.\"")
                        member.gain_loyalty(10)
                        print(f"{COLOR_GREEN}✨ Лояльность {member.name} увеличена на 10!{COLOR_RESET}")

                    elif choice_num == len(dialogue_options):  # Offer gold
                        if self.gold >= 20:
                            print(
                                f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Золото? Спасибо, но я следую за тобой не ради богатства. Хотя... это поможет моей семье.\"")
                            self.gold -= 20
                            member.gain_loyalty(15)
                            print(f"{COLOR_GREEN}💰 Ты отдал 20 золота {member.name}!")
                            print(f"✨ Лояльность {member.name} увеличена на 15!{COLOR_RESET}")
                        else:
                            print(f"{COLOR_RED}❌ У тебя недостаточно золота для этого предложения!{COLOR_RESET}")

            # Special dialogue if loyalty is very high
            if member.loyalty >= 90:
                print(f"\n{COLOR_MAGENTA}✨ {member.name} поделился с тобой секретом:{COLOR_RESET}")
                secrets = {
                    "элвин": "В древних текстах говорится о скрытом пути в заброшенный храм через лесную поляну. Там можно найти артефакт, способный усилить нашу магию.",
                    "грум": "Я слышал, что в глубинах горной крепости спрятана карта подземных туннелей. С ней мы сможем обойти вражеские посты.",
                    "мира": "Старейшина деревни знает способ создать особое зелье, которое временно усилит все способности отряда. Но для этого нужны редкие ингредиенты."
                }
                secret = secrets.get(member.name.lower(),
                                     "Я не могу рассказать тебе этого сейчас, но знай, что я верю в нашу победу.")
                print(f"{COLOR_WHITE}\"{secret}\"{COLOR_RESET}")

            pause_game()

    def remove_party_member(self):
        """Remove a member from the party"""
        if not self.party_members:
            print(f"{COLOR_RED}❌ В твоем отряде нет членов для исключения!{COLOR_RESET}")
            time.sleep(1)
            return

        clear_screen()
        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("👋 ИСКЛЮЧЕНИЕ ЧЛЕНА ОТРЯДА", 0.02)
        colorful_print(BANNER_BORDER)

        print(f"\n{COLOR_YELLOW}Выбери члена отряда для исключения:{COLOR_RESET}")
        for i, member in enumerate(self.party_members, 1):
            status = "❤️" if member.is_alive() else "💀"
            print(f"{i}. {status} {member.name} - {member.race} {member.character_class}")
            print(f"   💯 Лояльность: {self.create_health_bar(member.loyalty, 100, 10)} {member.loyalty}/100")
            print(f"   {member.description}")

        print(f"\n{len(self.party_members) + 1}. Отмена")

        choice = input(f"\n{COLOR_CYAN}Твой выбор (1-{len(self.party_members) + 1}): {COLOR_RESET}").strip()
        if not choice or choice == str(len(self.party_members) + 1):
            return

        if choice.isdigit() and 1 <= int(choice) <= len(self.party_members):
            member = self.party_members[int(choice) - 1]

            confirm = input(
                f"{COLOR_RED}Точно исключить {member.name} из отряда? (да/нет): {COLOR_RESET}").lower().strip()
            if confirm.startswith('д'):
                # Handle removal consequences based on loyalty
                if member.loyalty >= 70:
                    print(
                        f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Я понимаю твое решение, {self.name}. Если понадобится помощь в будущем, я не откажу в ней тебе.\"")
                    print(
                        f"{COLOR_YELLOW}✨ {member.name} обещает помочь тебе в будущем при необходимости.{COLOR_RESET}")
                elif member.loyalty >= 40:
                    print(f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Как прикажешь, лидер. Береги себя.\"")
                else:
                    print(
                        f"\n{COLOR_CYAN}{member.name}:{COLOR_RESET} \"Наконец-то я свободен от этого отряда! Ты пожалеешь об этом!\"")
                    print(f"{COLOR_RED}⚠️ {member.name} может стать твоим врагом в будущем!{COLOR_RESET}")

                # Add items back to inventory if they had equipment
                for item in member.inventory:
                    if item not in self.inventory and len(self.inventory) < GameConstants.INVENTORY_CAPACITY:
                        self.inventory.append(item)
                        print(f"{COLOR_GREEN}🎒 Предмет '{item}' добавлен в твой инвентарь.{COLOR_RESET}")

                # Remove from party
                self.party_members.pop(int(choice) - 1)
                print(f"\n{COLOR_GREEN}✅ {member.name} исключен из отряда.{COLOR_RESET}")
                time.sleep(2)

    def use_party_member_ability(self):
        """Use a party member's special ability"""
        # Check if in combat
        in_combat = False
        # This would need to be set from the combat system
        # For now, we'll assume we're not in combat unless specified

        clear_screen()
        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("✨ СПОСОБНОСТИ ОТРЯДА", 0.02)
        colorful_print(BANNER_BORDER)

        # Filter members with abilities
        members_with_abilities = [
            (i, member) for i, member in enumerate(self.party_members)
            if member.is_alive() and member.special_ability
        ]

        if not members_with_abilities:
            print(f"{COLOR_RED}❌ В твоем отряде нет членов со специальными способностями!{COLOR_RESET}")
            pause_game()
            return

        print(f"\n{COLOR_YELLOW}Выбери члена отряда для использования способности:{COLOR_RESET}")
        for idx, (i, member) in enumerate(members_with_abilities, 1):
            print(f"{idx}. {member.name} - {member.race} {member.character_class}")
            print(f"   ✨ Способность: {member.special_ability}")
            print(f"   💯 Лояльность: {self.create_health_bar(member.loyalty, 100, 10)} {member.loyalty}/100")

        print(f"\n{len(members_with_abilities) + 1}. Назад")

        choice = input(f"\n{COLOR_CYAN}Твой выбор (1-{len(members_with_abilities) + 1}): {COLOR_RESET}").strip()
        if not choice or choice == str(len(members_with_abilities) + 1):
            return

        if choice.isdigit() and 1 <= int(choice) <= len(members_with_abilities):
            member_index = members_with_abilities[int(choice) - 1][0]
            member = self.party_members[member_index]

            # Check loyalty requirement for using abilities
            if member.loyalty < 30:
                print(
                    f"{COLOR_RED}❌ {member.name} отказывается использовать свою способность! Лояльность слишком низкая.{COLOR_RESET}")
                time.sleep(2)
                return

            # Use the ability
            result = member.perform_special_ability()
            print(f"\n{COLOR_MAGENTA}✨ {result}{COLOR_RESET}")

            # Decrease loyalty slightly for using abilities (they get tired)
            member.lose_loyalty(3)
            print(f"{COLOR_YELLOW}💔 Лояльность {member.name} уменьшилась на 3.{COLOR_RESET}")

            # Handle specific abilities effects
            ability_effects = {
                "Точный выстрел": lambda: print(
                    f"{COLOR_GREEN}🎯 Элвин сделал точный выстрел! Все противники получат -2 к защите в следующем раунде!{COLOR_RESET}"),
                "Боевой клич": lambda: print(
                    f"{COLOR_GREEN}🛡️ Грум издал боевой клич! Все члены отряда получают +5 к защите на 3 раунда!{COLOR_RESET}"),
                "Исцеляющий свет": lambda: (
                    self.health == min(self.get_total_stats()["max_health"], self.health + 25),
                    print(f"{COLOR_GREEN}💖 Мира способность исцелила тебя на 25 HP!{COLOR_RESET}")
                )
            }

            if member.special_ability in ability_effects:
                ability_effects[member.special_ability]()

            # Special effect for high loyalty
            if member.loyalty >= 80:
                print(
                    f"{COLOR_CYAN}🌟 {member.name} выполняет свою способность с особым усердием благодаря высокой лояльности!{COLOR_RESET}")

            pause_game()

    def handle_party_management(self):
        """Manage party members (companions)"""
        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("👥 УПРАВЛЕНИЕ ОТРЯДОМ", 0.02)
        colorful_print(BANNER_BORDER)

        print(
            f"\nТекущие члены отряда ({len(self.party_members)}/{GameConstants.PARTY_MAX_SIZE}):")

        if not self.party_members:
            print("  Нет членов отряда")
        else:
            for i, member in enumerate(self.party_members, 1):
                health_bar = self.create_health_bar(member.health, member.max_health)
                loyalty_bar = self.create_health_bar(member.loyalty, 100, 10)
                print(f"\n{i}. {member.name} - {member.race} {member.character_class}")
                print(f"   ❤️  Здоровье: {health_bar} {member.health}/{member.max_health}")
                print(f"   💯 Лояльность: {loyalty_bar} {member.loyalty}/100")
                print(f"   💪 Атака: {member.attack}, 🛡️ Защита: {member.defense}")
                if member.special_ability:
                    print(f"   ✨ Особая способность: {member.special_ability}")

        if len(self.party_members) < GameConstants.PARTY_MAX_SIZE:
            print(f"\n💡 Ты можешь пригласить новых членов в отряд!")

        print(f"\nДоступные действия:")
        print("1. Разговаривать с членом отряда")
        print("2. Исключить члена отряда")
        print("3. Использовать способность члена отряда")
        print("4. Найти новых членов отряда")
        print("5. Назад")

        choice = input(f"\nВыбери действие (1-5): ").strip()

        if choice == "1" and self.party_members:
            self.talk_to_party_member()
        elif choice == "2" and self.party_members:
            self.remove_party_member()
        elif choice == "3" and self.party_members:
            self.use_party_member_ability()
        elif choice == "4" and len(self.party_members) < GameConstants.PARTY_MAX_SIZE:
            self.find_new_party_members()
        # else: return to main menu

    def handle_defeat(self, monster):
        """Handle defeat in combat"""
        clear_screen()
        display_ascii_art("defeat")

        # Calculate XP penalty
        xp_penalty = monster.xp_reward // 2

        # Apply defeat effects
        self.health = max(1, self.max_health // 4)  # Restore to 25% health
        self.experience = max(0, self.experience - xp_penalty)

        colorful_print("\n" + BATTLE_BORDER)
        typewriter_effect("💀 ПОРАЖЕНИЕ!", 0.02)
        colorful_print(BATTLE_BORDER)

        print(f"\nТы был побежден {monster.name}!")
        print(f"\n✨ Мудрый друид нашел тебя и привел в безопасное место.")
        print(f"💔 Ты потерял {xp_penalty} опыта.")
        print(f"❤️  Здоровье восстановлено до {self.health}.")

        print("\n" + BANNER_BORDER)
        pause_game()

        return f"\n❌ Поражение! Потеряно {xp_penalty} опыта."

    def explore_location(self):
        """Explore the current location"""
        location = self.locations.get(self.current_location)
        if not location:
            return f"Недопустимая локация!"

        # Check if location is locked
        if location.get("locked", False):
            unlock_conditions = []
            if location.get("required_item"):
                unlock_conditions.append(f"найти предмет '{location['required_item'].replace('_', ' ')}'")
            if location.get("required_reputation"):
                for faction, rep in location["required_reputation"].items():
                    unlock_conditions.append(f"набрать {rep} репутации с '{faction}'")
            if location.get("required_quest"):
                unlock_conditions.append(f"завершить квест '{location['required_quest']}'")

            conditions_text = " и ".join(unlock_conditions)
            return f"🔒 Эта локация заперта. Чтобы открыть её, нужно {conditions_text}."

        clear_screen()

        # Display location with ASCII art if available
        colorful_print("\n" + LOCATION_BORDER)
        location_name = location.get("display_name", location["name"])
        typewriter_effect(f"📍 {location_name}", 0.02)
        colorful_print(LOCATION_BORDER)

        # Show detailed description
        description = location.get("long_description", location["description"])
        wrapped_description = wrap_text(description)
        print(f"\n{wrapped_description}")

        # Show location map if available
        if "map" in location:
            print(f"\n{location['map']}")

        # Determine exploration outcome
        outcome = ""
        encounter_roll = random.random()

        # 1. Find items
        if "items" in location and location["items"] and encounter_roll < 0.3:
            if location["items"]:  # Проверка, что список не пустой
                item_name = random.choice(location["items"])
                if item_name in self.items:
                    self.inventory.append(item_name)
                    item = self.items[item_name]
                    outcome = f"\n🔍 Ты нашел {item['name']}!"
                else:
                    self.inventory.append(item_name)
                    outcome = f"\n🔍 Ты нашел {item_name.replace('_', ' ')}!"

        # 2. Encounter NPCs
        elif "npcs" in location and location["npcs"] and encounter_roll < 0.6:
            npc_id = random.choice(location["npcs"])
            if npc_id in self.npcs:
                npc = self.npcs[npc_id]
                outcome = f"\n👤 Ты встретил {npc['name']}."
                # Check if requirements are met to interact with NPC
                requirements_met = True

                if "requires" in npc:
                    if "item" in npc["requires"] and npc["requires"]["item"] not in self.inventory:
                        requirements_met = False
                    if "reputation" in npc["requires"]:
                        for faction, required_rep in npc["requires"]["reputation"].items():
                            if self.reputation.get(faction, 0) < required_rep:
                                requirements_met = False

                if requirements_met:
                    outcome += f"\n[Диалог доступен]"
                else:
                    outcome += f"\n[Требуются дополнительные условия для диалога]"

        # 3. Encounter monsters
        elif "monsters" in location and location["monsters"] and encounter_roll < 0.8:
            if random.random() < location.get("encounter_chance", 0.5):
                monster_id = random.choice(location["monsters"])
                if monster_id in self.monsters:
                    outcome = self.handle_combat(monster_id)

        # 4. Special location events
        elif self.current_location == "эльфийская_роща" and random.random() < 0.2:
            outcome = f"\n✨ Ты почувствовал магическую энергию рощи. Твое здоровье частично восстановлено!"
            heal_amount = int(self.max_health * 0.2)
            self.health = min(self.max_health, self.health + heal_amount)

        elif self.current_location == "древнее_святилище" and "кристалл_природы" in self.inventory and random.random() < 0.3:
            outcome = f"\n🔮 Кристалл природы засветился в присутствии древней магии святилища!"
            self.experience += 25
            outcome += f"\n✨ Получено 25 опыта!"

        else:
            outcome = f"\n🔍 Ты внимательно осмотрел местность, но ничего особенного не нашел."

        # Check for quest progress
        quest_updates = self.check_quest_progress(location)
        if quest_updates:
            outcome += quest_updates

        print(outcome)
        print("\n" + LOCATION_BORDER)
        pause_game()

        return outcome

    def check_quest_progress(self, location):
        """Check and update quest progress based on current location"""
        updates = ""

        for quest in self.active_quests:
            if quest.get("completed", False):
                continue

            # Check location-based objectives
            if "location" in quest.get("requirements", {}):
                required_location = quest["requirements"]["location"]
                if self.current_location == required_location:
                    # Mark location requirement as fulfilled
                    quest.setdefault("progress", {})["location_visited"] = True
                    updates += f"\n📜 Квест обновлен: Ты достиг нужной локации для '{quest['name']}'"

            # Check collect objectives
            if "objectives" in quest:
                for objective in quest["objectives"]:
                    if objective.get("type") == "collect" and objective.get("item"):
                        item_name = objective["item"]
                        required_quantity = objective.get("quantity", 1)

                        # Count items in inventory
                        item_count = sum(1 for item in self.inventory if item_name in item)

                        if item_count >= required_quantity:
                            objective["completed"] = True
                            updates += f"\n✅ Квест '{quest['name']}': Собрано {required_quantity} предметов '{item_name.replace('_', ' ')}'"

        return updates

    def travel_to_location(self, location_id):
        """Travel to a new location"""
        if location_id not in self.locations:
            return f"❌ Нет такой локации!"

        current_location = self.locations[self.current_location]
        new_location = self.locations[location_id]

        # Check if location is accessible from current location
        if location_id not in current_location.get("exits", []):
            return f"❌ Нельзя напрямую попасть в {new_location['name']} из {current_location['name']}."

        # Check if location is locked
        if new_location.get("locked", False):
            # Check if player has the required item
            required_item = new_location.get("required_item")
            if required_item and required_item in self.inventory:
                # Automatically use the key to unlock the location
                self.inventory.remove(required_item)
                new_location["locked"] = False
                print(f"🔑 Ты использовал {required_item.replace('_', ' ')} чтобы открыть {new_location['name']}!")
            else:
                unlock_conditions = []
                if new_location.get("required_item"):
                    unlock_conditions.append(f"найти предмет '{new_location['required_item'].replace('_', ' ')}'")
                if new_location.get("required_reputation"):
                    for faction, rep in new_location["required_reputation"].items():
                        unlock_conditions.append(f"набрать {rep} репутации с '{faction}'")
                if new_location.get("required_quest"):
                    unlock_conditions.append(f"завершить квест '{new_location['required_quest']}'")

                conditions_text = " и ".join(unlock_conditions)
                return f"🔒 Локация '{new_location['name']}' заперта. Чтобы открыть её, нужно {conditions_text}."

        # Move to new location
        self.current_location = location_id

        # Travel description
        direction = self.get_direction_between_locations(current_location, new_location)
        colorful_print(f"\n🚶 ПУТЕШЕСТВИЕ")
        typewriter_effect(f"Ты отправляешься {direction} в {new_location.get('display_name', new_location['name'])}...",
                          0.03)

        # Random event during travel
        if random.random() < 0.2:  # 20% chance for travel event
            events = [
                "По пути тебе попался странствующий торговец. Он продал тебе немного провизии со скидкой.",
                "Ты нашел на дороге несколько золотых монет!",
                "В лесу ты заметил редкое растение и собрал его.",
                "Ты услышал странный звук вдалеке, но решил не рисковать и продолжил путь."
            ]
            event = random.choice(events)
            print(f"\n🌟 Событие в пути: {event}")

            if "несколько золотых монет" in event:
                gold_found = random.randint(5, 15)
                self.gold += gold_found
                print(f"💰 Найдено {gold_found} золота!")
            elif "редкое растение" in event:
                self.inventory.append("гриб")
                print(f"🌿 Получен лесной гриб!")

        time.sleep(1.5)
        return f"✅ Ты прибыл в {new_location.get('display_name', new_location['name'])}."

    def get_direction_between_locations(self, current_loc, new_loc):
        """Get the direction between two locations for travel description"""
        # This is a simplified version - in a real game, this would use coordinates
        location_pairs = {
            ("начало", "лес"): "на север",
            ("начало", "горы"): "на восток",
            ("начало", "море"): "на юг",
            ("начало", "деревня"): "на запад",
            ("лес", "начало"): "на юг",
            ("горы", "начало"): "на запад",
            ("море", "начало"): "на север",
            ("деревня", "начало"): "на восток"
        }

        pair = (current_loc["name"], new_loc["name"])
        return location_pairs.get(pair, "вперед")

    def manage_equipment(self):
        """Manage character equipment"""
        while True:
            clear_screen()

            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect("🛡️  УПРАВЛЕНИЕ СНАРЯЖЕНИЕМ", 0.02)
            colorful_print(BANNER_BORDER)

            stats = self.get_total_stats()

            # Show current stats
            print(f"\n📊 ТЕКУЩИЕ ХАРАКТЕРИСТИКИ:")
            print(f"  ⚔️  Атака: {stats['attack']}")
            print(f"  🛡️  Защита: {stats['defense']}")
            print(f"  ❤️  Здоровье: {self.health}/{stats['max_health']}")
            print(f"  ⭐ Крит. шанс: {stats['critical_chance']:.0%}")

            # Show equipment slots
            colorful_print("\n🎭 СЛОТЫ СНАРЯЖЕНИЯ:")
            slots = list(self.armor_slots.keys())
            for i, slot in enumerate(slots, 1):
                item_name = self.armor_slots[slot]
                if item_name and item_name in self.items:
                    item = self.items[item_name]
                    item_display = item.get("name", item_name.replace("_", " "))
                    if item["type"] == "weapon":
                        stats_str = f"(Атака: +{item['attack']})"
                    elif item["type"] in ["armor", "shield"]:
                        stats_str = f"(Защита: +{item['defense']})"
                    else:
                        stats_str = ""
                    print(f"{i}. {slot.capitalize()}: {item_display} {stats_str}")
                else:
                    print(f"{i}. {slot.capitalize()}: Пусто")

            print(f"\n{len(slots) + 1}. Назад")

            choice = input(f"\nВыбери слот для изменения (1-{len(slots) + 1}): ").strip()

            if not choice:
                continue

            if choice == str(len(slots) + 1):
                break

            if choice.isdigit() and 1 <= int(choice) <= len(slots):
                slot = slots[int(choice) - 1]
                self.equip_item_to_slot(slot)

        # Update health based on new equipment
        stats = self.get_total_stats()
        if self.health > stats["max_health"]:
            self.health = stats["max_health"]

    def equip_item_to_slot(self, slot):
        """Equip an item to a specific slot"""
        # Get items that can go in this slot
        compatible_items = []

        slot_types = {
            "head": ["armor"],
            "chest": ["armor"],
            "hands": ["armor"],
            "legs": ["armor"],
            "feet": ["armor"],
            "weapon": ["weapon"],
            "shield": ["shield"],
            "amulet": ["amulet"],
            "ring": ["ring"]
        }

        allowed_types = slot_types.get(slot, [])

        for item_name in self.inventory:
            item = self.items.get(item_name, {})
            if item.get("type") in allowed_types or (slot == "weapon" and item.get("type") == "weapon"):
                compatible_items.append((item_name, item))

        if not compatible_items:
            print(f"❌ В инвентаре нет предметов для этого слота!")
            time.sleep(1)
            return

        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect(f"🎽 ЭКИПИРОВКА В СЛОТ: {slot.capitalize()}", 0.02)
        colorful_print(BANNER_BORDER)

        # Show currently equipped item
        current_item = self.armor_slots[slot]
        if current_item:
            item = self.items.get(current_item, {})
            item_name = item.get("name", current_item.replace("_", " "))
            print(f"\nТекущий предмет: {item_name}")
        else:
            print(f"\nСлот пуст")

        # Show compatible items
        colorful_print(f"\n📋 ДОСТУПНЫЕ ПРЕДМЕТЫ ({len(compatible_items)}):")
        for i, (item_name, item) in enumerate(compatible_items, 1):
            item_display = item.get("name", item_name.replace("_", " "))
            item_desc = item.get("description", "Нет описания")

            if item["type"] == "weapon":
                stats_str = f"(Атака: +{item['attack']})"
            elif item["type"] in ["armor", "shield"]:
                stats_str = f"(Защита: +{item['defense']})"
            else:
                stats_str = ""

            print(f"{i}. {item_display} {stats_str}")
            print(f"   {item_desc}")

        print(f"\n{len(compatible_items) + 1}. Снять предмет")
        print(f"{len(compatible_items) + 2}. Назад")

        choice = input(f"\nВыбери предмет (1-{len(compatible_items) + 2}): ").strip()

        if not choice:
            return

        choice_num = int(choice) if choice.isdigit() else -1
        total_options = len(compatible_items) + 2

        if choice_num == total_options:
            return  # Back

        if choice_num == len(compatible_items) + 1:
            # Unequip item
            if current_item:
                self.inventory.append(current_item)
                self.armor_slots[slot] = None
                print(f"✅ Предмет снят и перемещен в инвентарь!")
                time.sleep(1)
            return

        if 1 <= choice_num <= len(compatible_items):
            # Equip new item
            new_item = compatible_items[choice_num - 1][0]

            # Move current item to inventory if exists
            if current_item:
                self.inventory.append(current_item)

            # Remove new item from inventory
            if new_item in self.inventory:
                self.inventory.remove(new_item)

            # Equip new item
            self.armor_slots[slot] = new_item

            item = self.items.get(new_item, {})
            item_name = item.get("name", new_item.replace("_", " "))
            print(f"✅ {item_name} экипирован в слот {slot.capitalize()}!")
            time.sleep(1)

    def manage_skills(self):
        """Manage skill points distribution"""
        if self.skill_points <= 0:
            print(f"ℹ️  У тебя нет очков навыков для распределения.")
            time.sleep(1)
            return

        while self.skill_points > 0:
            clear_screen()

            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect("📊 РАСПРЕДЕЛЕНИЕ ОЧКОВ НАВЫКОВ", 0.02)
            colorful_print(BANNER_BORDER)

            print(f"\nОчков навыков доступно: {self.skill_points}")

            # Show abilities
            colorful_print("\n⚡ СПОСОБНОСТИ:")
            for i, (ability, value) in enumerate(self.abilities.items(), 1):
                bar = self.create_stat_bar(value, 20)
                print(f"{i}. {ability.capitalize()}: {bar} {value}")

            # Show skills
            colorful_print("\n🎯 НАВЫКИ:")
            for i, (skill, value) in enumerate(self.skills.items(), len(self.abilities) + 1):
                if value > 0 or self.character_class in ["воин", "маг", "лучник", "вор", "целитель", "паладин"]:
                    bar = self.create_stat_bar(value, 20)
                    print(f"{i}. {skill.capitalize()}: {bar} {value}")

            print(f"\n{len(self.abilities) + len(self.skills) + 1}. Пропустить")

            choice = input(
                f"\nВыбери характеристику для улучшения (1-{len(self.abilities) + len(self.skills) + 1}): ").strip()

            if not choice:
                continue

            choice_num = int(choice) if choice.isdigit() else -1
            total_options = len(self.abilities) + len(self.skills) + 1

            if choice_num == total_options:
                break

            if 1 <= choice_num <= len(self.abilities):
                # Improve ability
                ability = list(self.abilities.keys())[choice_num - 1]
                self.abilities[ability] += 1
                self.skill_points -= 1
                print(f"✨ {ability.capitalize()} улучшен до {self.abilities[ability]}!")

            elif len(self.abilities) < choice_num <= len(self.abilities) + len(self.skills):
                # Improve skill
                skill_index = choice_num - len(self.abilities) - 1
                skill = list(self.skills.keys())[skill_index]
                self.skills[skill] += 1
                self.skill_points -= 1
                print(f"✨ Навык '{skill.capitalize()}' улучшен до {self.skills[skill]}!")

            else:
                print(f"❌ Неверный выбор!")

            time.sleep(1)

    def find_new_party_members(self):
        """Find and recruit new party members"""
        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("👥 ПОИСК НОВЫХ ЧЛЕНОВ ОТРЯДА", 0.02)
        colorful_print(BANNER_BORDER)

        available_companions = []

        # Check which companions are available based on story progress and location
        for comp_id, companion in self.companion_templates.items():
            if len(self.party_members) >= GameConstants.PARTY_MAX_SIZE:
                continue

            # Check if companion is already in party
            if any(m.name == companion.name for m in self.party_members):
                continue

            # Check location requirements
            location_requirements = {
                "элвин": "эльфийская_роща",
                "грум": "горная_деревня",
                "мира": "деревня"
            }

            required_location = location_requirements.get(comp_id)
            if required_location and self.current_location != required_location:
                continue

            available_companions.append((comp_id, companion))

        if not available_companions:
            print(f"\n🔍 Пока нет доступных кандидатов для отряда в этой локации.")
            pause_game()
            return

        print(f"\nДоступные кандидаты ({len(available_companions)}):")
        for i, (comp_id, companion) in enumerate(available_companions, 1):
            print(f"\n{i}. {companion.name} - {companion.race} {companion.character_class}")
            print(f"   {companion.description}")
            print(f"   💪 Атака: {companion.attack}, 🛡️ Защита: {companion.defense}")
            print(f"   ❤️  Здоровье: {companion.health}/{companion.max_health}")
            if companion.special_ability:
                print(f"   ✨ Особая способность: {companion.special_ability}")

        print(f"\n{len(available_companions) + 1}. Назад")

        choice = input(f"\nВыбери кандидата (1-{len(available_companions) + 1}): ").strip()

        if not choice or choice == str(len(available_companions) + 1):
            return

        if choice.isdigit() and 1 <= int(choice) <= len(available_companions):
            comp_id, companion_template = available_companions[int(choice) - 1]

            # Create a copy of the companion
            new_companion = Companion.from_dict(companion_template.to_dict())

            # Add to party
            self.party_members.append(new_companion)

            print(f"\n🎉 {new_companion.name} присоединился к твоему отряду!")
            time.sleep(1)

    def start_game(self):
        """Start the game main loop"""
        # Initialize database
        init_database()
        # Create a new character if needed
        if not self.name:
            self.select_character()
        game_active = True
        while game_active:
            clear_screen()
            # Check for level up opportunities
            if self.skill_points > 0:
                self.manage_skills()
            # Display current location
            current_loc = self.locations.get(self.current_location, {})
            location_name = current_loc.get("display_name", current_loc.get("name", "Неизвестное место"))
            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect(f"🌍 {location_name.upper()}", 0.02)
            colorful_print(BANNER_BORDER)
            # Show location description
            if current_loc:
                short_desc = current_loc.get("description", "Нет описания")
                print(f"\n{short_desc}")
            # Show current stats
            stats = self.get_total_stats()
            health_bar = self.create_health_bar(self.health, stats["max_health"])
            print(f"\n📊 СТАТИСТИКА:")
            print(f"  ❤️  {health_bar} {self.health}/{stats['max_health']}")
            print(f"  🏅 Уровень: {self.level}, ⚡ Опыт: {self.experience}/{GameConstants.XP_PER_LEVEL}")
            print(f"  💰 Золото: {self.gold}")
            print(f"  🎒 Инвентарь: {len(self.inventory)}/{GameConstants.INVENTORY_CAPACITY}")
            print(f"  📜 Квестов: {len([q for q in self.active_quests if not q.get('completed', False)])}")
            # Show equipped weapon and armor
            weapon = self.armor_slots.get("weapon")
            armor = self.armor_slots.get("chest")
            if weapon and weapon in self.items:
                weapon_name = self.items[weapon]["name"]
                weapon_atk = self.items[weapon].get("attack", 0)
                print(f"  ⚔️  Оружие: {weapon_name} (+{weapon_atk} атаки)")
            if armor and armor in self.items:
                armor_name = self.items[armor]["name"]
                armor_def = self.items[armor].get("defense", 0)
                print(f"  🛡️  Броня: {armor_name} (+{armor_def} защиты)")
            # Show party members
            if self.party_members:
                party_count = len([m for m in self.party_members if m.is_alive()])
                print(f"  👥 Отряд: {party_count}/{GameConstants.PARTY_MAX_SIZE} живых членов")
            # Main menu
            colorful_print("\n" + MENU_BORDER)
            print("1. 🚶 Исследовать текущую локацию")
            print("2. 🛣️  Переместиться в другую локацию")
            print("3. 👤 Поговорить с NPC")
            print("4. ⚔️  Начать сражение")
            print("5. 🎒 Инвентарь")
            print("6. 🛡️  Снаряжение")
            print("7. 📜 Квесты")
            print("8. 👥 Отряд")
            print("9. 🌍 Карта мира")
            print("10. ⛺ Отдохнуть")
            print("11. 📊 Характеристики")
            print("0. 💾 Сохранить и выйти")
            choice = input(f"\nВыбери действие (0-11): ").strip()
            if choice == "1":
                # Explore location
                result = self.explore_location()
                if result:
                    colorful_print(f"\n{result}")
                    pause_game()
            elif choice == "2":
                # Travel to another location
                current_loc = self.locations[self.current_location]
                if "exits" in current_loc and current_loc["exits"]:
                    clear_screen()
                    colorful_print("\n" + BANNER_BORDER)
                    typewriter_effect(f"🛣️  ДОСТУПНЫЕ ПУТИ ИЗ {location_name.upper()}", 0.02)
                    colorful_print(BANNER_BORDER)
                    print(f"\nДоступные направления:")
                    for i, exit_id in enumerate(current_loc["exits"], 1):
                        if exit_id in self.locations:
                            exit_loc = self.locations[exit_id]
                            exit_name = exit_loc.get("display_name", exit_loc["name"])
                            # Check if location is locked
                            locked = exit_loc.get("locked", False)
                            status_icon = f"🔒" if locked else f"✅"
                            print(f"{i}. {status_icon} {exit_name}")
                            # Show requirements if locked
                            if locked:
                                requirements = []
                                if "required_item" in exit_loc:
                                    requirements.append(f"Предмет: {exit_loc['required_item'].replace('_', ' ')}")
                                if "required_reputation" in exit_loc:
                                    for faction, rep in exit_loc["required_reputation"].items():
                                        requirements.append(f"Репутация с {faction}: {rep}")
                                if "required_quest" in exit_loc:
                                    requirements.append(f"Квест: {exit_loc['required_quest']}")
                                if requirements:
                                    print(f"   Требуется: {', '.join(requirements)}")
                    print(f"\n{len(current_loc['exits']) + 1}. Назад")
                    location_choice = input(f"\nВыбери направление (1-{len(current_loc['exits']) + 1}): ").strip()
                    if location_choice.isdigit():
                        choice_num = int(location_choice)
                        if 1 <= choice_num <= len(current_loc["exits"]):
                            new_location = current_loc["exits"][choice_num - 1]
                            travel_result = self.travel_to_location(new_location)
                            colorful_print(f"\n{travel_result}")
                            pause_game()
                        elif choice_num == len(current_loc["exits"]) + 1:
                            continue
                else:
                    colorful_print(f"\n❌ Нет доступных выходов из этой локации!")
                    pause_game()
            elif choice == "3":
                # Talk to NPC
                current_loc = self.locations[self.current_location]
                if "npcs" in current_loc and current_loc["npcs"]:
                    clear_screen()
                    colorful_print("\n" + BANNER_BORDER)
                    typewriter_effect(f"👤 ДОСТУПНЫЕ NPC В {location_name}", 0.02)
                    colorful_print(BANNER_BORDER)
                    available_npcs = []
                    for npc_id in current_loc["npcs"]:
                        if npc_id in self.npcs:
                            npc = self.npcs[npc_id]
                            available_npcs.append((npc_id, npc))
                    for i, (npc_id, npc) in enumerate(available_npcs, 1):
                        npc_name = npc.get("display_name", npc["name"])
                        print(f"{i}. {npc_name}")
                        print(f"   {npc['description']}")
                    print(f"\n{len(available_npcs) + 1}. Назад")
                    npc_choice = input(f"\nВыбери NPC для разговора (1-{len(available_npcs) + 1}): ").strip()
                    if npc_choice.isdigit():
                        choice_num = int(npc_choice)
                        if 1 <= choice_num <= len(available_npcs):
                            npc_id, npc = available_npcs[choice_num - 1]
                            interaction_result = self.interact_with_npc(npc_id)
                            if interaction_result:
                                colorful_print(f"\n{interaction_result}")
                        elif choice_num == len(available_npcs) + 1:
                            continue
                else:
                    colorful_print(f"\n❌ В этой локации нет NPC!")
                    pause_game()
            elif choice == "4":
                # Start battle
                current_loc = self.locations[self.current_location]
                if "monsters" in current_loc and current_loc["monsters"]:
                    clear_screen()
                    colorful_print("\n" + BANNER_BORDER)
                    typewriter_effect(f"⚔️  ВЫБЕРИ ПРОТИВНИКА", 0.02)
                    colorful_print(BANNER_BORDER)
                    # List available monsters
                    for i, monster_id in enumerate(current_loc["monsters"], 1):
                        if monster_id in self.monsters:
                            monster = self.monsters[monster_id]
                            monster_name = monster.get("display_name", monster["name"])
                            print(f"{i}. {monster_name}")
                            print(f"   Уровень: {monster['level']}, Здоровье: {monster['health']}")
                    print(f"\n{len(current_loc['monsters']) + 1}. Случайный противник")
                    print(f"{len(current_loc['monsters']) + 2}. Назад")
                    monster_choice = input(f"\nВыбери противника (1-{len(current_loc['monsters']) + 2}): ").strip()
                    if monster_choice.isdigit():
                        choice_num = int(monster_choice)
                        if 1 <= choice_num <= len(current_loc["monsters"]):
                            monster_id = current_loc["monsters"][choice_num - 1]
                            if monster_id in self.monsters:
                                self.handle_combat(monster_id)
                        elif choice_num == len(current_loc["monsters"]) + 1:
                            # Random monster
                            monster_id = random.choice(current_loc["monsters"])
                            if monster_id in self.monsters:
                                self.handle_combat(monster_id)
                else:
                    colorful_print(f"\n❌ В этой локации нет монстров для сражения!")
                    pause_game()
            elif choice == "5":
                # Inventory management
                self.show_inventory()
                pause_game()
            elif choice == "6":
                # Equipment management
                self.manage_equipment()
            elif choice == "7":
                # Quest log
                self.show_quest_log()
            elif choice == "8":
                # Party management
                self.handle_party_management()
            elif choice == "9":
                # World map
                self.display_world_map()
            elif choice == "10":
                # Rest
                self.rest_at_location()
            elif choice == "11":
                # Character sheet
                self.show_character_sheet()
            elif choice == "0":
                # Save and exit
                self.save_progress()
                colorful_print(f"\n✅ Прогресс сохранен! До новых встреч, {self.name}!")
                game_active = False
            else:
                colorful_print(f"\n❌ Неверный выбор! Попробуй снова.")
                time.sleep(1)

    def show_inventory(self):
        """Display and manage inventory"""
        while True:
            clear_screen()

            colorful_print("\n" + BANNER_BORDER)
            typewriter_effect("🎒 ИНВЕНТАРЬ", 0.02)
            colorful_print(BANNER_BORDER)

            print(f"\n💰 Золото: {self.gold}")
            print(f"📊 Вместимость: {len(self.inventory)}/{GameConstants.INVENTORY_CAPACITY}")

            # Group items by type
            item_groups = {
                "weapon": [],
                "armor": [],
                "shield": [],
                "consumable": [],
                "material": [],
                "quest_item": [],
                "key": [],
                "artifact": [],
                "other": []
            }

            for item_name in self.inventory:
                item = self.items.get(item_name, {})
                item_type = item.get("type", "other")
                if item_type not in item_groups:
                    item_type = "other"
                item_groups[item_type].append((item_name, item))

            # Display grouped items
            type_names = {
                "weapon": f"⚔️  ОРУЖИЕ",
                "armor": f"🛡️  БРОНЯ",
                "shield": f"🛡️  ЩИТЫ",
                "consumable": f"💊 РАСХОДНИКИ",
                "material": f"🔧 МАТЕРИАЛЫ",
                "quest_item": f"📜 КВЕСТОВЫЕ ПРЕДМЕТЫ",
                "key": f"🔑 КЛЮЧИ",
                "artifact": f"🔮 АРТЕФАКТЫ",
                "other": f"📦 ПРОЧЕЕ"
            }

            has_items = False
            for item_type, items in item_groups.items():
                if items:
                    has_items = True
                    print(f"\n{type_names.get(item_type, item_type.upper())}:")
                    for i, (item_name, item) in enumerate(items, 1):
                        item_display = item.get("name", item_name.replace("_", " "))
                        item_value = item.get("value", 0)

                        # Format item info based on type
                        if item_type == "consumable" and item.get("effect") == "health":
                            info = f"(Восстанавливает {item['value']} HP)"
                        elif item_type in ["weapon", "armor", "shield"]:
                            stat_type = "атаки" if item_type == "weapon" else "защиты"
                            stat_value = item.get("attack", 0) if item_type == "weapon" else item.get("defense", 0)
                            info = f"({stat_type.capitalize()}: +{stat_value})"
                        else:
                            info = f"(Цена: {item_value} золота)"

                        print(f"  {i}. {item_display} {info}")

            if not has_items:
                print(f"\nВаш инвентарь пуст!")

            print(f"\nДоступные действия:")
            print("1. Использовать предмет")
            print("2. Выбросить предмет")
            print("3. Назад")

            action = input(f"\nВыбери действие (1-3): ").strip()

            if action == "3":
                break

            elif action == "1" and has_items:
                # Use item
                self.use_item_from_inventory()

            elif action == "2" and has_items:
                # Drop item
                self.drop_item_from_inventory()

            else:
                colorful_print(f"\n❌ Нет предметов для этого действия!")
                time.sleep(1)

    def use_item_from_inventory(self):
        """Use an item from inventory"""
        # Filter usable items
        usable_items = []
        for item_name in self.inventory:
            item = self.items.get(item_name, {})
            if item.get("type") == "consumable" or item.get("type") == "key" or item.get("type") == "artifact":
                usable_items.append((item_name, item))

        if not usable_items:
            colorful_print(f"\n❌ Нет предметов, которые можно использовать!")
            time.sleep(1)
            return

        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("💊 ИСПОЛЬЗОВАНИЕ ПРЕДМЕТА", 0.02)
        colorful_print(BANNER_BORDER)

        print(f"\nДоступные для использования предметы:")
        for i, (item_name, item) in enumerate(usable_items, 1):
            item_display = item.get("name", item_name.replace("_", " "))
            if item.get("type") == "consumable" and item.get("effect") == "health":
                info = f"(Восстанавливает {item['value']} HP)"
            else:
                info = ""
            print(f"{i}. {item_display} {info}")

        print(f"\n{len(usable_items) + 1}. Назад")

        choice = input(
            f"\nВыбери предмет для использования (1-{len(usable_items) + 1}): ").strip()

        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(usable_items):
                item_name, item = usable_items[choice_num - 1]

                if item.get("type") == "consumable":
                    if item.get("effect") == "health":
                        heal_amount = item["value"]
                        old_health = self.health
                        self.health = min(self.get_total_stats()["max_health"], self.health + heal_amount)
                        heal_actual = self.health - old_health
                        self.inventory.remove(item_name)

                        print(
                            f"\n💖 Ты использовал {item['name']} и восстановил {heal_actual} здоровья!")
                        time.sleep(1)

                elif item.get("type") == "key":
                    # Handle key usage (unlock location, chest, etc.)
                    current_loc = self.locations[self.current_location]
                    if "required_item" in current_loc and current_loc["required_item"] == item_name:
                        if current_loc.get("locked", False):
                            current_loc["locked"] = False
                            self.inventory.remove(item_name)
                            print(f"\n🗝️  Ты использовал {item['name']} и открыл путь!")
                        else:
                            print(f"\nЭтот ключ не нужен здесь.")
                    else:
                        print(f"\nЭтот ключ не подходит для текущей локации.")

                elif item.get("type") == "artifact" and "activation" in item and item["activation"] == "active":
                    # Use artifact ability
                    artifact = next((a for a in self.artifacts if a.name == item["name"]), None)
                    if artifact:
                        result = artifact.use_active_ability(self)
                        print(f"\n{result}")

                pause_game()

            elif choice_num == len(usable_items) + 1:
                return

    def drop_item_from_inventory(self):
        """Drop an item from inventory"""
        if not self.inventory:
            colorful_print(f"\n❌ Инвентарь пуст!")
            time.sleep(1)
            return

        clear_screen()

        colorful_print("\n" + BANNER_BORDER)
        typewriter_effect("🗑️  ВЫБРОСИТЬ ПРЕДМЕТ", 0.02)
        colorful_print(BANNER_BORDER)

        print(f"\nПредметы в инвентаре:")
        for i, item_name in enumerate(self.inventory, 1):
            item = self.items.get(item_name, {})
            item_display = item.get("name", item_name.replace("_", " "))
            item_value = item.get("value", 0)
            print(f"{i}. {item_display} (Можно продать за {item_value // 2} золота)")

        print(f"\n{len(self.inventory) + 1}. Назад")

        choice = input(
            f"\nВыбери предмет для выбрасывания (1-{len(self.inventory) + 1}): ").strip()

        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(self.inventory):
                item_name = self.inventory[choice_num - 1]
                item = self.items.get(item_name, {})
                item_display = item.get("name", item_name.replace("_", " "))

                confirm = input(f"Точно выбросить {item_display}? (да/нет): ").lower().strip()
                if confirm.startswith('д'):
                    self.inventory.pop(choice_num - 1)
                    print(f"\n🗑️  {item_display} выброшен!")
                    time.sleep(1)

            elif choice_num == len(self.inventory) + 1:
                return


# Основная функция запуска игры
def main():
    """Основная функция запуска игры"""
    clear_screen()
    print("=" * 60)
    print("🎮 ТЕКСТОВАЯ РПГ 'МИР ВЕЧНЫХ ТЕНЕЙ'")
    print("=" * 60)

    # Запрашиваем ID пользователя
    user_input = input("\nВведите ваш ID для загрузки персонажа (или оставьте пустым для создания нового): ").strip()

    # Определяем ID пользователя
    if user_input:
        try:
            user_id = int(user_input)
            print(f"\n🔍 Поиск персонажа с ID: {user_id}")
            time.sleep(1)
        except ValueError:
            print("\n❌ Неверный формат ID. Будет создан новый персонаж.")
            user_id = random.randint(100000000, 999999999)
            print(f"🆕 Ваш новый ID: {user_id}")
            time.sleep(1)
    else:
        # Генерируем случайный ID для нового персонажа
        user_id = random.randint(100000000, 999999999)
        print(f"\n🆕 Создан новый персонаж с ID: {user_id}")
        time.sleep(1)

    # Инициализация базы данных
    init_database()

    # Создание экземпляра игры
    game = PlayerCharacter(user_id)

    # Запуск игры
    game.start_game()


if __name__ == "__main__":
    main()
