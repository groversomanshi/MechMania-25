from . import *

#global teamNum

def get_strategy(team: int):
    """This function tells the engine what strategy you want your bot to use"""
    global teamNum

    # team == 0 means I am on the left
    # team == 1 means I am on the right
    teamNum = Team #########EDIT teamNum to be a placeholder for which team we belong to
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

def gotoPos(game: GameState, playerNum: PlayerState.id, pos: Vec2):
    teamplayers, opplayers = game.team(Team.Self), game.team(Team.Other)
    allplayers = teamplayers + opplayers
    return Vec2(pos.x - allplayers[playerNum].pos.x, pos.y - allplayers[playerNum].pos.y)

def getBallOwner(game: GameState):
    if game._ball_possession.type == 0:  # BallPossessionType.Possessed
        num = game._ball_possession.data.possessed.owner
        if num > 9:
            num = -1
        return num
    else:
        return -1  # Ball not possessed

def getNearestOp(player: PlayerState.id, game: GameState):
    #global teamNum
    nearestpos = Vec2(-1, -1)
    # if teamNum == Team.Self:
    #     teamplayers = game.team(teamNum)
    #     opplayers = game.team(not teamNum)
    # else:
    #     teamplayers = game.team(not teamNum)
    #     opplayers = game.team(teamNum)
    teamplayers = game.team(Team.Self)
    opplayers = game.team(Team.Other)
    for op in opplayers:
        if nearestpos == Vec2(-1, -1):
            nearestpos = op.pos
            nearestid = op.id
        elif teamplayers[player].pos.dist(op.pos) < teamplayers[player].pos.dist(nearestpos):
            nearestpos = op.pos
            nearestid = op.id
    return nearestid

def getBallPos(game: GameState) -> Vec2:
    return(game.ball.pos)

def getNearestTeammate(player: PlayerState.id, game: GameState):
    #global teamNum
    nearestpos = Vec2(-1, -1)
    # if teamNum == Team.Self:
    #     teamplayers = game.team(teamNum)
    # else:
    #     teamplayers = game.team(not teamNum)
    teamplayers = game.team(Team.Self)
    for teammate in teamplayers:
        if teammate.id != player:
            if nearestpos == Vec2(-1, -1):
                nearestpos = teammate.pos
                nearestid = teammate.id
            elif teamplayers[player].pos.dist(teammate.pos) < teamplayers[player].pos.dist(nearestpos):
                nearestpos = teammate.pos
                nearestid = teammate.id
    return nearestid

def getAllTeammates(game: GameState):
    global teamNum
    return game.team(teamNum)

def getAllOps(game: GameState):
    global teamNum
    return game.team(not teamNum)

def checkMove(game: GameState, playerNum): 

    # print("Nearest Teammate", getNearestTeammate(playerNum, game))
    # print("Nearest Opponent", getNearestOp(playerNum, game))
    # print("All Teammates", getAllTeammates(game))
    # print("All Opponents", getAllOps(game))

    config = get_config()

    endX = 750 
    endY = 500


    #print("ball owned by: ", getBallOwner(game))
    #print("nearest OP player: ", getNearestOp(game, 2))

    if (game.players[playerNum].pos.x >= endX-1): 
        return PlayerAction(Vec2(0,0), config.field.goal_other() - game.players[playerNum].pos)
    if (game.players[playerNum].pos.x >= 499): 
        return PlayerAction(gotoPos(game, 2, Vec2(endX, endY)), None)
    if (game.players[playerNum].pos.x < 500): 
        return PlayerAction(gotoPos(game, 2,  config.field.center()), None)

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

    do_something = checkMove(game, 2)

    actions.append(do_nothing)
    actions.append(do_nothing)
    actions.append(do_something)
    actions.append(do_nothing)


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


