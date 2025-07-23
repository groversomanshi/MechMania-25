from . import *

def standard_formation(_: Score) -> List[Vec2]:
    config = get_config()
    w = float(config.field.width)
    h = float(config.field.height)
    return [
        Vec2(w * 0.5, h * 0.5),
        Vec2(w * 0.3, h * 0.7),
        Vec2(w * 0.15, h * 0.3),
        Vec2(w * 0.15, h * 0.7)
    ]


def ball_chase(game: GameState) -> List[PlayerAction]:
    return list(PlayerAction((game.ball.pos - p.pos).normalize(), None) for p in game.players[:NUM_PLAYERS])

def get_strategy():
    return Strategy(standard_formation, ball_chase)
