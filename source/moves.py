import random

def dodged(defender):
    roll = random.randint(1, 100)
    return roll <= defender.evasion

def perform_move(move_name, attacker, defender):
    match move_name:
        case "ATTACK":
            if dodged(defender):
                return f"{defender.name} dodges the attack"
            damage = max(1, attacker.attack - defender.defense)
            defender -= damage
            return f"{attacker.name} attacks for {damage} damage"

        case "DEFEND":
            attacker.defense += 10
            return f"{attacker.name} raises his defense"

        case "WEAKEN":
            if dodged(defender):
                return f"{defender.name} evades the weakening spell"
            defender /= 1.2
            return f"{defender.name} weakens"

        case "STRENGTH":
            attacker *= 1.1
            return f"{attacker.name} adopts a fighting stance"

        case "POISON":
            if dodged(defender):
                return f"{defender.name} evades the poison"
            defender.status_effects.append({"type": "POISON", "damage": 30, "turns_left": 3})
            return f"{attacker.name} poisons {defender.name}"

        case "REGEN":
            attacker.status_effects.append({"type": "REGEN", "damage": 10, "turns_left": 5})
            return f"{attacker.name} casts regeneration"

        case "SCARE":
            if dodged(defender):
                return f"{defender.name} is not scared"
            defender.attack = max(1, defender.attack - 8)
            return f"{attacker.name} scares {defender.name}"

        case "DRAIN":
            damage = max(1,int(attacker.attack * 0.2))
            defender -= damage
            attacker += damage
            if attacker.hp > attacker.max_hp: attacker.hp = attacker.max_hp
            return f"{attacker.name} drains {damage} HP from {defender.name}"

        case "CURSE":
            if dodged(defender):
                return f"{defender.name} avoided the curse"
            defender.defense -= 10
            return f"{defender.name} is now cursed"

        case _:
            return "default case"