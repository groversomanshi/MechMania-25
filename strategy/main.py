from . import *

def get_strategy(team: int):
    """This function tells the engine what strategy you want your bot to use"""
    
    # team == 0 means I am on the left
    # team == 1 means I am on the right
    
    if team == 0:
        print("Hello! I am team A (on the left)")
        return Strategy(goalee_formation, ball_chase)
    else:
        print("Hello! I am team B (on the right)")
        return Strategy(goalee_formation, do_nothing)
    
    # NOTE when actually submitting your bot, you probably want to have the SAME strategy for both
    # sides.

def goalee_formation(score: Score) -> List[Vec2]:
    """The engine will call this function every time the field is reset:
    either after a goal, if the ball has not moved for too long, or right before endgame"""
    
    config = get_config()
    field = config.field.bottom_right()
    
    return [
        Vec2(field.x * 0.1, field.y * 0.5),
        Vec2(field.x * 0.4, field.y * 0.4),
        Vec2(field.x * 0.4, field.y * 0.5),
        Vec2(field.x * 0.4, field.y * 0.6),
    ]

def checkMove(game: GameState): 

    config = get_config()

    # print(game.players[3].pos.x)
    if (game.players[3].pos.x >= 799): 
        return PlayerAction(Vec2(0,0), config.field.goal_other() - game.players[3].pos)

    if (game.players[3].pos.x < 500): 
        return PlayerAction(Vec2(500, 300) - game.players[3].pos, None) #movement 
    if (game.players[3].pos.x >= 499): 
        return PlayerAction(Vec2(800, 350) - game.players[3].pos, None)
    else: 
        return PlayerAction(Vec2(0,0), None)


def ball_chase(game: GameState) -> List[PlayerAction]:
    """Very simple strategy to chase the ball and shoot on goal"""
    
    config = get_config()
    
    # NOTE Do not worry about what side your bot is on! 
    # The engine mirrors the world for you if you are on the right, 
    # so to you, you always appear on the left.

    actions = []

    # # goalee
    
    do_nothing = PlayerAction(
        Vec2(0, 0), None
    )

    do_something = checkMove(game)

    

    actions.append(do_nothing)
    actions.append(do_nothing)
    actions.append(do_nothing)
    actions.append(do_something)


    return actions
    
    # return [
    #     PlayerAction(
    #         game.ball.pos - game.players[i].pos,
    #         config.field.goal_other() - game.players[i].pos
    #     ) 
    #     for i in range(NUM_PLAYERS)
    # ]

def do_nothing(game: GameState) -> List[PlayerAction]:
    """This strategy will do nothing :("""
    
    return [
        PlayerAction(Vec2(0, 0), None) 
        for _ in range(NUM_PLAYERS)
    ]


