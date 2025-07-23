import ctypes

NUM_PLAYERS = 4

class BallConfig(ctypes.Structure):
    _fields_ = [
        ("friction", ctypes.c_float),
        ("radius", ctypes.c_float),
        ("capture_ticks", ctypes.c_uint32),
        ("stagnation_radius", ctypes.c_float),
        ("stagnation_ticks", ctypes.c_uint32),
    ]

class PlayerConfig(ctypes.Structure):
    _fields_ = [
        ("radius", ctypes.c_float),
        ("pickup_radius", ctypes.c_float),
        ("speed", ctypes.c_float),
        ("pass_speed", ctypes.c_float),
        ("pass_error", ctypes.c_float),
        ("possession_slowdown", ctypes.c_float),
    ]

class FieldConfig(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
    ]

class GoalConfig(ctypes.Structure):
    _fields_ = [
        ("height", ctypes.c_uint32),
        ("thickness", ctypes.c_uint32),
        ("penalty_radius", ctypes.c_uint32),
    ]

class GameConfig(ctypes.Structure):
    _fields_ = [
        ("max_ticks", ctypes.c_uint32),
        ("spawn_ball_dist", ctypes.c_float),
        ("ball", BallConfig),
        ("player", PlayerConfig),
        ("field", FieldConfig),
        ("goal", GoalConfig),
    ]
