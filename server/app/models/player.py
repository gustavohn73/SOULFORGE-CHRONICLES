"""
Player model - Represents a player entity
"""
import time
import uuid
from typing import Dict, List, Optional, Tuple

class Player:
    """Player entity with stats, marks, inventory, and position"""

    def __init__(self, username: str, player_id: Optional[str] = None):
        self.id = player_id or str(uuid.uuid4())
        self.username = username
        self.entity_type = 'player'

        # Position
        self.x = 0
        self.y = 0
        self.spawn_x = 0
        self.spawn_y = 0

        # Core Stats
        self.level = 1
        self.xp = 0
        self.hp = 100
        self.max_hp = 100

        # Attributes
        self.stats = {
            'strength': 10,
            'agility': 10,
            'endurance': 10,
            'perception': 10,
            'luck': 10
        }

        # Soul Marks (-100 to 100)
        self.marks = {
            'VIOLENCIA': 0,
            'CONTROLE': 0,
            'CURIOSIDADE': 0,
            'MEMORIA': 0
        }

        # Combat
        self.armor = 0
        self.evasion = 0
        self.vision_range = 8

        # Inventory
        self.inventory = []  # List of {item_id, quantity}
        self.max_inventory_size = 20
        self.equipped = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }

        # Skills
        self.unlocked_skills = []
        self.skill_cooldowns = {}  # {skill_id: remaining_turns}

        # Status effects
        self.status_effects = []  # List of {effect_type, duration, intensity}

        # Progression
        self.loops_completed = 0
        self.total_kills = 0
        self.total_deaths = 0

        # Session
        self.socket_id = None
        self.last_action_time = time.time()
        self.action_count_this_second = 0

        # FOV cache
        self.fov_cache = None
        self.fov_dirty = True

    # ========================================================================
    # Core Methods
    # ========================================================================

    def set_position(self, x: int, y: int):
        """Set player position and mark FOV as dirty"""
        self.x = x
        self.y = y
        self.fov_dirty = True

    def set_spawn_point(self, x: int, y: int):
        """Set spawn point"""
        self.spawn_x = x
        self.spawn_y = y
        self.set_position(x, y)

    def respawn(self):
        """Respawn player at spawn point"""
        self.set_position(self.spawn_x, self.spawn_y)
        self.hp = self.max_hp
        self.status_effects = []

    # ========================================================================
    # Stats and Combat
    # ========================================================================

    def take_damage(self, damage: int, source: str = 'unknown') -> Dict:
        """Apply damage to player"""
        self.hp -= damage
        result = {
            'damage': damage,
            'remaining_hp': self.hp,
            'is_dead': self.hp <= 0,
            'source': source
        }

        if self.hp <= 0:
            self.hp = 0
            result['death_event'] = self.on_death(source)

        return result

    def heal(self, amount: int) -> int:
        """Heal player, return actual amount healed"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def on_death(self, cause: str) -> Dict:
        """Handle player death"""
        self.total_deaths += 1

        # Drop some items (not all)
        drops = []
        if len(self.inventory) > 3:
            # Drop half of inventory
            drop_count = len(self.inventory) // 2
            for _ in range(drop_count):
                if self.inventory:
                    item = self.inventory.pop(0)
                    drops.append(item)

        return {
            'type': 'player_death',
            'player_id': self.id,
            'cause': cause,
            'drops': drops,
            'xp_lost': int(self.xp * 0.1)  # Lose 10% XP
        }

    def gain_xp(self, amount: int) -> Optional[Dict]:
        """Gain XP, returns level up info if leveled up"""
        self.xp += amount
        xp_needed = self.xp_for_next_level()

        if self.xp >= xp_needed:
            return self.level_up()

        return None

    def xp_for_next_level(self) -> int:
        """Calculate XP needed for next level"""
        return int(100 * (1.5 ** (self.level - 1)))

    def level_up(self) -> Dict:
        """Level up player"""
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp

        return {
            'new_level': self.level,
            'hp_increase': 10,
            'attribute_point': 1
        }

    def allocate_stat_point(self, stat_name: str) -> bool:
        """Allocate attribute point"""
        if stat_name in self.stats:
            self.stats[stat_name] += 1
            self._recalculate_derived_stats()
            return True
        return False

    def _recalculate_derived_stats(self):
        """Recalculate derived stats from attributes"""
        # Max HP from endurance
        base_hp = 100
        endurance_bonus = (self.stats['endurance'] - 10) * 15
        self.max_hp = base_hp + endurance_bonus

        # Vision from perception
        base_vision = 8
        perception_bonus = (self.stats['perception'] - 10) // 3
        self.vision_range = base_vision + perception_bonus

        # Evasion from agility
        self.evasion = max(0, (self.stats['agility'] - 10) * 2)

    # ========================================================================
    # Soul Marks
    # ========================================================================

    def change_mark(self, mark_name: str, amount: int) -> Dict:
        """Change a soul mark, returns notification if threshold crossed"""
        if mark_name not in self.marks:
            return {}

        old_value = self.marks[mark_name]
        new_value = max(-100, min(100, old_value + amount))
        self.marks[mark_name] = new_value

        result = {
            'mark': mark_name,
            'old_value': old_value,
            'new_value': new_value,
            'change': amount
        }

        # Check if crossed skill unlock threshold
        if old_value < 80 and new_value >= 80:
            result['threshold_crossed'] = 80
            result['unlocked_skill'] = self._get_skill_for_mark(mark_name)

        return result

    def _get_skill_for_mark(self, mark_name: str) -> Optional[str]:
        """Get skill ID for a mark threshold"""
        skill_map = {
            'VIOLENCIA': 'furia_berserker',
            'CONTROLE': 'tempo_congelado',
            'CURIOSIDADE': 'sexto_sentido',
            'MEMORIA': 'deja_vu'
        }
        return skill_map.get(mark_name)

    # ========================================================================
    # Inventory
    # ========================================================================

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory"""
        # Check if item already exists (stack)
        for item in self.inventory:
            if item['item_id'] == item_id:
                item['quantity'] += quantity
                return True

        # Add new item
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append({
                'item_id': item_id,
                'quantity': quantity
            })
            return True

        return False  # Inventory full

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        for item in self.inventory:
            if item['item_id'] == item_id:
                if item['quantity'] >= quantity:
                    item['quantity'] -= quantity
                    if item['quantity'] == 0:
                        self.inventory.remove(item)
                    return True
        return False

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if player has item"""
        for item in self.inventory:
            if item['item_id'] == item_id and item['quantity'] >= quantity:
                return True
        return False

    def equip_item(self, item_id: str, slot: str) -> bool:
        """Equip item to slot"""
        if slot not in self.equipped:
            return False

        # Unequip current item
        if self.equipped[slot]:
            self.add_item(self.equipped[slot]['item_id'], 1)

        # Equip new item
        if self.remove_item(item_id, 1):
            self.equipped[slot] = {'item_id': item_id}
            return True

        return False

    # ========================================================================
    # Skills
    # ========================================================================

    def unlock_skill(self, skill_id: str) -> bool:
        """Unlock a skill"""
        if skill_id not in self.unlocked_skills:
            self.unlocked_skills.append(skill_id)
            return True
        return False

    def can_use_skill(self, skill_id: str) -> Tuple[bool, str]:
        """Check if skill can be used"""
        if skill_id not in self.unlocked_skills:
            return False, "Skill not unlocked"

        if skill_id in self.skill_cooldowns and self.skill_cooldowns[skill_id] > 0:
            return False, f"On cooldown ({self.skill_cooldowns[skill_id]} turns)"

        return True, "OK"

    def use_skill(self, skill_id: str, cooldown: int):
        """Use skill and start cooldown"""
        self.skill_cooldowns[skill_id] = cooldown

    def update_cooldowns(self):
        """Decrement all skill cooldowns (call each turn)"""
        for skill_id in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill_id] -= 1
            if self.skill_cooldowns[skill_id] <= 0:
                del self.skill_cooldowns[skill_id]

    # ========================================================================
    # Status Effects
    # ========================================================================

    def add_status_effect(self, effect_type: str, duration: int, intensity: float = 1.0):
        """Add status effect"""
        self.status_effects.append({
            'type': effect_type,
            'duration': duration,
            'intensity': intensity,
            'applied_at': time.time()
        })

    def remove_status_effect(self, effect_type: str):
        """Remove status effect"""
        self.status_effects = [e for e in self.status_effects if e['type'] != effect_type]

    def has_status_effect(self, effect_type: str) -> bool:
        """Check if has status effect"""
        return any(e['type'] == effect_type for e in self.status_effects)

    def update_status_effects(self) -> List[Dict]:
        """Update status effects, return events"""
        events = []

        for effect in list(self.status_effects):
            effect['duration'] -= 1

            # Apply effect
            if effect['type'] == 'poison':
                damage = int(2 * effect['intensity'])
                events.append({
                    'type': 'poison_damage',
                    'damage': damage
                })
                self.take_damage(damage, 'poison')

            elif effect['type'] == 'burning':
                damage = int(3 * effect['intensity'])
                events.append({
                    'type': 'burn_damage',
                    'damage': damage
                })
                self.take_damage(damage, 'fire')

            # Remove if expired
            if effect['duration'] <= 0:
                self.status_effects.remove(effect)
                events.append({
                    'type': 'effect_expired',
                    'effect': effect['type']
                })

        return events

    # ========================================================================
    # Rate Limiting
    # ========================================================================

    def can_perform_action(self, max_per_second: int = 10) -> bool:
        """Check if player can perform action (rate limiting)"""
        current_time = time.time()

        # Reset counter if new second
        if current_time - self.last_action_time >= 1.0:
            self.action_count_this_second = 0
            self.last_action_time = current_time

        # Check limit
        if self.action_count_this_second >= max_per_second:
            return False

        self.action_count_this_second += 1
        return True

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self, include_private: bool = False) -> Dict:
        """Convert to dictionary for network transmission"""
        data = {
            'id': self.id,
            'username': self.username,
            'x': self.x,
            'y': self.y,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'level': self.level,
            'marks': self.marks.copy(),
            'stats': self.stats.copy()
        }

        if include_private:
            data.update({
                'xp': self.xp,
                'inventory': self.inventory.copy(),
                'equipped': self.equipped.copy(),
                'unlocked_skills': self.unlocked_skills.copy(),
                'skill_cooldowns': self.skill_cooldowns.copy(),
                'status_effects': self.status_effects.copy(),
                'loops_completed': self.loops_completed,
                'total_kills': self.total_kills,
                'total_deaths': self.total_deaths
            })

        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from dictionary"""
        player = cls(data['username'], data.get('id'))

        # Restore all fields
        player.x = data.get('x', 0)
        player.y = data.get('y', 0)
        player.spawn_x = data.get('spawn_x', 0)
        player.spawn_y = data.get('spawn_y', 0)
        player.level = data.get('level', 1)
        player.xp = data.get('xp', 0)
        player.hp = data.get('hp', 100)
        player.max_hp = data.get('max_hp', 100)
        player.stats = data.get('stats', player.stats)
        player.marks = data.get('marks', player.marks)
        player.inventory = data.get('inventory', [])
        player.equipped = data.get('equipped', player.equipped)
        player.unlocked_skills = data.get('unlocked_skills', [])
        player.loops_completed = data.get('loops_completed', 0)
        player.total_kills = data.get('total_kills', 0)
        player.total_deaths = data.get('total_deaths', 0)

        player._recalculate_derived_stats()

        return player

    def __repr__(self):
        return f"<Player {self.username} (Lv{self.level}) at ({self.x},{self.y})>"
