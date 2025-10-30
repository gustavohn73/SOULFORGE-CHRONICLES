"""
Marks System - Soul mark tracking and effects
"""
from typing import Dict, Optional

class MarksSystem:
    """Manages player soul marks and their effects"""

    def __init__(self, config):
        self.config = config
        self.mark_min = config.MARK_MIN
        self.mark_max = config.MARK_MAX
        self.skill_threshold = config.SKILL_UNLOCK_THRESHOLD

    def register_action(self, player, action_type: str, context: Optional[Dict] = None) -> Dict:
        """
        Register player action and update marks
        Returns changes made
        """
        context = context or {}
        changes = {}

        if action_type == 'kill':
            change = 5
            if context.get('target_type') == 'innocent':
                change = 10  # Killing innocents is more violent
            elif context.get('target_type') == 'player':
                change = 15  # PvP is very violent

            result = player.change_mark('VIOLENCIA', change)
            if result:
                changes['VIOLENCIA'] = result

        elif action_type == 'spare':
            # Sparing enemies reduces violence
            result = player.change_mark('VIOLENCIA', -3)
            if result:
                changes['VIOLENCIA'] = result

        elif action_type == 'explore_new_area':
            result = player.change_mark('CURIOSIDADE', 2)
            if result:
                changes['CURIOSIDADE'] = result

        elif action_type == 'open_chest':
            result = player.change_mark('CURIOSIDADE', 1)
            if result:
                changes['CURIOSIDADE'] = result

        elif action_type == 'craft':
            result = player.change_mark('CONTROLE', 1)
            if result:
                changes['CONTROLE'] = result

        elif action_type == 'complete_loop':
            result = player.change_mark('MEMORIA', 10)
            if result:
                changes['MEMORIA'] = result

        elif action_type == 'read_book':
            changes['CURIOSIDADE'] = player.change_mark('CURIOSIDADE', 1)
            changes['MEMORIA'] = player.change_mark('MEMORIA', 1)

        elif action_type == 'destroy_object':
            result = player.change_mark('VIOLENCIA', 1)
            result2 = player.change_mark('CONTROLE', -1)
            if result:
                changes['VIOLENCIA'] = result
            if result2:
                changes['CONTROLE'] = result2

        # Check for skill unlocks
        for mark_name, mark_data in changes.items():
            if mark_data.get('threshold_crossed') == self.skill_threshold:
                skill_id = mark_data.get('unlocked_skill')
                if skill_id and player.unlock_skill(skill_id):
                    changes[mark_name]['skill_unlocked'] = skill_id

        return changes

    def get_mark_effects(self, player) -> Dict:
        """Get active effects from player's marks"""
        effects = {
            'damage_multiplier': 1.0,
            'defense_multiplier': 1.0,
            'vision_bonus': 0,
            'loot_multiplier': 1.0,
            'social_modifiers': {}
        }

        marks = player.marks

        # VIOLENCIA effects
        violencia = marks.get('VIOLENCIA', 0)
        if violencia > 50:
            effects['damage_multiplier'] += (violencia - 50) / 200  # Up to +25%
        if violencia > 80:
            effects['social_modifiers']['merchants_hostile'] = True
            effects['social_modifiers']['guards_hostile'] = True

        # CONTROLE effects
        controle = marks.get('CONTROLE', 0)
        if controle > 50:
            effects['defense_multiplier'] += (controle - 50) / 200
        if controle > 80:
            effects['loot_multiplier'] *= 0.7  # Less loot (too selective)

        # CURIOSIDADE effects
        curiosidade = marks.get('CURIOSIDADE', 0)
        if curiosidade > 50:
            effects['vision_bonus'] += (curiosidade - 50) // 20  # +1 per 20 points
        if curiosidade > 80:
            effects['trap_chance_multiplier'] = 1.5  # More traps triggered

        # MEMORIA effects
        memoria = marks.get('MEMORIA', 0)
        if memoria > 80:
            effects['sanity_drain'] = True  # Remembering too much hurts

        return effects

    def get_skill_for_mark(self, mark_name: str) -> Optional[str]:
        """Get skill ID associated with mark"""
        skill_map = {
            'VIOLENCIA': 'furia_berserker',
            'CONTROLE': 'tempo_congelado',
            'CURIOSIDADE': 'sexto_sentido',
            'MEMORIA': 'deja_vu'
        }
        return skill_map.get(mark_name)
