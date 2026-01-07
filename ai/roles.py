# ai/roles.py
class Role:
    CARRY = "carry"
    SUPPORT = "support"
    OFFLANE = "offlane"
    MID = "mid"

ROLE_BEHAVIOR = {
    Role.CARRY: {"farm_priority": 1.0, "fight": 0.3},
    Role.SUPPORT: {"farm_priority": 0.2, "fight": 0.8},
    Role.MID: {"farm_priority": 0.6, "fight": 0.6},
}
