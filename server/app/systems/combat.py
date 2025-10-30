"""
Combat System - Inspired by Shattered Pixel Dungeon
Handles damage calculation, surprise attacks, critical hits
"""
import random
from typing import Dict, Any, Optional

class CombatSystem:
    """Combat system with mark-based modifications"""

    def __init__(self, config):
        self.config = config
        self.base_crit_chance = config.BASE_CRIT_CHANCE
        self.surprise_multiplier = config.SURPRISE_DAMAGE_MULTIPLIER
        self.critical_multiplier = config.CRITICAL_DAMAGE_MULTIPLIER

    def calculate_damage(self, attacker, defender, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calculate damage from attacker to defender
        Based on Shattered Pixel Dungeon's damage roll system
        """
        context = context or {}

        # Get weapon stats
        weapon = attacker.equipped.get('weapon')
        if weapon:
            min_dmg = weapon.get('min_damage', 1)
            max_dmg = weapon.get('max_damage', 3)
            tier = weapon.get('tier', 1)
        else:
            # Unarmed
            min_dmg, max_dmg, tier = 1, 3, 0

        # Level scaling (SPD formula)
        level_bonus = attacker.level * tier * 0.3

        # Base damage roll
        base_damage = random.randint(
            int(min_dmg + level_bonus),
            int(max_dmg + level_bonus * 1.5)
        )

        # Strength modifier
        strength_bonus = (attacker.stats['strength'] - 10) * 0.2
        base_damage = int(base_damage * (1 + strength_bonus))

        # Mark modifiers
        damage_mult = 1.0
        crit_chance = self.base_crit_chance

        if hasattr(attacker, 'marks'):
            # VIOLENCIA increases raw damage
            violencia = attacker.marks.get('VIOLENCIA', 0)
            if violencia > 50:
                violencia_bonus = (violencia - 50) / 200  # Max +25% at 100
                damage_mult += violencia_bonus
                crit_chance += 0.10  # +10% crit chance

            # CONTROLE affects consistency
            controle = attacker.marks.get('CONTROLE', 0)
            if controle > 50:
                # High control = consistent damage (low variance)
                variance = 0.05
            elif controle < -50:
                # Low control = chaotic damage (high variance)
                variance = 0.40
            else:
                variance = 0.20

            base_damage = int(base_damage * random.uniform(1 - variance, 1 + variance))

        # Critical hit check
        luck_bonus = (attacker.stats.get('luck', 10) - 10) * 0.01
        final_crit_chance = crit_chance + luck_bonus

        is_critical = random.random() < final_crit_chance
        if is_critical:
            damage_mult *= self.critical_multiplier

        # Surprise attack (inspired by SPD backstab)
        is_surprise = context.get('is_surprise', False)
        if is_surprise:
            damage_mult *= self.surprise_multiplier

            # Extra bonus for violent attackers
            if hasattr(attacker, 'marks') and attacker.marks.get('VIOLENCIA', 0) > 70:
                damage_mult *= 1.2

        # Apply multipliers
        final_damage = int(base_damage * damage_mult)

        # Defense roll (SPD-style)
        armor = defender.armor
        evasion = defender.evasion
        defense_roll = random.randint(0, armor + evasion)

        # Agility-based evasion chance
        if hasattr(defender, 'stats'):
            agility_bonus = (defender.stats.get('agility', 10) - 10) * 0.02
            if random.random() < agility_bonus:
                defense_roll = int(defense_roll * 1.5)

        # Mark defensive modifiers
        if hasattr(defender, 'marks'):
            # Pacifists have better defense
            if defender.marks.get('VIOLENCIA', 0) < -50:
                defense_roll = int(defense_roll * 1.3)

        # Final damage
        final_damage = max(1, final_damage - defense_roll)

        return {
            'damage': final_damage,
            'is_critical': is_critical,
            'is_surprise': is_surprise,
            'hit_type': 'critical' if is_critical else 'surprise' if is_surprise else 'normal',
            'defense_roll': defense_roll,
            'base_damage': base_damage,
            'damage_mult': damage_mult
        }

    def check_surprise(self, attacker_pos: tuple, defender, fov_set: set) -> bool:
        """
        Check if attack is a surprise (defender can't see attacker)
        Based on SPD's surprise mechanic
        """
        return attacker_pos not in fov_set

    def apply_damage(self, target, damage: int, source: str = 'attack') -> Dict[str, Any]:
        """Apply damage to target entity"""
        result = target.take_damage(damage, source)

        # Award XP if killed
        if result['is_dead']:
            result['xp_reward'] = getattr(target, 'xp_reward', 0)

        return result

    def process_attack(self, attacker, defender, fov_data: Optional[set] = None) -> Dict[str, Any]:
        """
        Process complete attack sequence
        Returns comprehensive attack result
        """
        # Check surprise
        context = {}
        if fov_data:
            attacker_pos = (attacker.x, attacker.y)
            context['is_surprise'] = self.check_surprise(attacker_pos, defender, fov_data)

        # Calculate damage
        damage_result = self.calculate_damage(attacker, defender, context)

        # Apply damage
        apply_result = self.apply_damage(defender, damage_result['damage'], 'attack')

        # Combine results
        full_result = {
            **damage_result,
            'target_id': defender.id,
            'target_hp': defender.hp,
            'target_died': apply_result['is_dead'],
            'attacker_id': attacker.id
        }

        if apply_result['is_dead']:
            full_result['death_event'] = apply_result.get('death_event')
            full_result['xp_reward'] = apply_result.get('xp_reward', 0)

        return full_result

    def apply_knockback(self, target, direction: tuple, distance: int = 1):
        """Apply knockback effect"""
        dx, dy = direction
        new_x = target.x + dx * distance
        new_y = target.y + dy * distance

        # Validate position
        # (world validation would happen at game_server level)
        return {
            'target_id': target.id,
            'from': (target.x, target.y),
            'to': (new_x, new_y),
            'distance': distance
        }

    def calculate_hit_chance(self, attacker, defender) -> float:
        """Calculate hit chance percentage"""
        base_chance = 0.85  # 85% base

        # Attacker accuracy from perception
        accuracy_bonus = (attacker.stats.get('perception', 10) - 10) * 0.02

        # Defender evasion from agility
        evasion_penalty = (defender.stats.get('agility', 10) - 10) * 0.02

        final_chance = base_chance + accuracy_bonus - evasion_penalty

        return max(0.1, min(0.99, final_chance))  # Clamp between 10% and 99%
