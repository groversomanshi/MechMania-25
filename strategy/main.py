from . import *

global teamNum
teamNum = -1

def get_strategy(team: int):
    """This function tells the engine what strategy you want your bot to use"""
    global teamNum

    # team == 0 means I am on the left
    # team == 1 means I am on the right
    
    if team == 0:
        teamNum = 0 
        print("Hello! I am team A (on the left)")
        return Strategy(goalee_formation, ball_chase)
    else:
        teamNum = 1
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

def gotoPos(game, playerNum, pos): 
    return pos - game.players[playerNum].pos

def getBallOwner(game: GameState):
    if game._ball_possession.type == 0:  # BallPossessionType.Possessed
        num = game._ball_possession.data.possessed.owner
        if num > 9:
            num = -1
        return num
    else:
        return -1  # Ball not possessed

def getBallPossessionTeam(game: GameState) -> int:
    # Returns 0 for Self, 1 for Other, or -1 if no team possesses the ball
    if game._ball_possession.type == 0:  # BallPossessionType.Possessed
        return game._ball_possession.data.possessed.team
    else:
        return -1  # Ball not possessed by any team

def getNearestOp(game: GameState, playerNum):
    global teamNum
    curPos = game.players[playerNum].pos 
    minDist = float('inf')
    minPlayer = -1 
    for i in game.team(teamNum): 
        dist = curPos.dist(game.players[i.id].pos)
        if dist < minDist: 
            minDist = dist
            minPlayer = i.id
    return minPlayer

def getBallPos(game: GameState) -> Vec2:
    return(game.ball.pos)

def getNearestTeammate( game: GameState, player: PlayerState.id):
    global teamNum
    nearestpos = Vec2(-1, -1)
    teamplayers = game.team(teamNum)
    for teammate in teamplayers:
        if teammate.id != player:
            if nearestpos == Vec2(-1, -1):
                nearestpos = teammate.pos
                nearestid = teammate.id
            elif teamplayers[player].pos.dist(teammate.pos) < teamplayers[player].pos.dist(nearestpos):
                nearestpos = teammate.pos
                nearestid = teammate.id
    return nearestid

def getNearestTeammatePos(game: GameState, player: PlayerState.id):
    return game.players[game.getNearestTeammate(player, game)].pos

def getAllTeammates(game: GameState):
    global teamNum
    return game.team(teamNum)

def getAllOps(game: GameState):
    global teamNum
    return game.team(not teamNum)

def checkMove(game: GameState, playerNum): 
    config = get_config()
    endX = 750 
    endY = 500
    # print("ball owned by: ", getBallOwner(game))
    # print("nearest OP player: ", getNearestOp(game, 2))

    if (game.players[playerNum].pos.x >= endX-1): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    if (game.players[playerNum].pos.x >= 499): 
        return PlayerAction(gotoPos(game, 2, Vec2(endX, endY)), None)
    if (game.players[playerNum].pos.x < 500): 
        return PlayerAction(gotoPos(game, 2,  config.field.center()), None)
    else: 
        return PlayerAction(Vec2(0,0), None)
    
def kickTo(game, pos, playerNum): 
    return pos - game.players[playerNum].pos

def getBetweenObjects(closer: Vec2, farther: Vec2, fraction: float) -> Vec2:
    # """Returns a point that is `fraction` of the way from obj1 to obj2"""
    return closer + (farther - closer) * fraction

def isBetweenObjects(middle: Vec2, closer: Vec2, farther: Vec2) -> bool:
    # Project middle onto the line segment and check if it lies between closer and farther
    ab = farther - closer
    am = middle - closer
    ab_dot_ab = ab.dot(ab)
    if ab_dot_ab == 0:
        return False
    t = am.dot(ab) / ab_dot_ab
    return 0 <= t <= 1

def goalieOffense(game: GameState, playerNum: int) -> PlayerAction: 
    config = get_config()
    if (getBallOwner(game) == playerNum): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    else: 
        return PlayerAction(gotoPos(game, playerNum, getBetweenObjects(config.field.goal_self(), getBallPos(game), 0.15)), None)
    
#MIDFIELD PLANS: 
# --> if opposing is between main and goal, pass to support

def runAndKick(game: GameState, playerNum: int, endX, endY) -> PlayerAction:
    config = get_config()
    # print("ball owned by: ", getBallOwner(game))
    # print("nearest OP player: ", getNearestOp(game, 2))
    if (game.players[playerNum].pos.x >= endX-1): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    if (game.players[playerNum].pos.x < endX): 
        return PlayerAction(gotoPos(game, playerNum, Vec2(endX, endY)), None)
    else: 
        return PlayerAction(Vec2(0,0), None)


def anyOpBetween(game: GameState, playerNum: int, startPoint: Vec2, endPoint: Vec2, threshold: float = 30.0) -> bool:
    # Check if any opposing player is close enough to block the line between startPoint and endPoint
    def point_line_dist(p: Vec2, a: Vec2, b: Vec2) -> float:
        # Distance from point p to line segment ab
        ap = p - a
        ab = b - a
        ab_norm_sq = ab.norm_sq()
        if ab_norm_sq == 0:
            return ap.norm()
        t = max(0, min(1, ap.dot(ab) / ab_norm_sq))
        closest = a + ab * t
        return (p - closest).norm()
    for op in getAllOps(game):
        if isBetweenObjects(op.pos, startPoint, endPoint):
            if point_line_dist(op.pos, startPoint, endPoint) < threshold:
                return True
    return False

def bestTeammatePass(game: GameState, playerNum: int) -> Vec2:
    teammates = [p for p in getAllTeammates(game) if p.id != playerNum and p.id != 0]  # exclude self and goalie
    cur_pos = game.players[playerNum].pos
    open_teammates = []
    for mate in teammates:
        if not anyOpBetween(game, playerNum, cur_pos, mate.pos):
            open_teammates.append(mate)
    if open_teammates:
        # Pass to the nearest open teammate
        nearest_open = min(open_teammates, key=lambda t: cur_pos.dist(t.pos))
        return nearest_open.pos
    # fallback: pass to nearest teammate (even if blocked)
    nearest = min(teammates, key=lambda t: cur_pos.dist(t.pos))
    return nearest.pos

# assume you have the ball or can easily get it 
def midfieldOffenseMain(game: GameState, playerNum: int) -> PlayerAction:
    config = get_config()
    if (getBallOwner(game) == playerNum): 
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, game.players[3].pos)) and game.players[3].speed == 0):
           return PlayerAction(Vec2(0,0), kickTo(game, game.players[3].pos, playerNum))
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, config.field.goal_other()))): 
           return PlayerAction(Vec2(0,0), kickTo(game, bestTeammatePass(game, playerNum), playerNum))
        return runAndKick(game, playerNum, 800, 250)
    elif (getBallPossessionTeam(game) == 1): 
        return PlayerAction(gotoPos(game, playerNum, getBallPos(game)), None)
    else:
        return PlayerAction(gotoPos(game, playerNum, Vec2(800, 250)), None)

def midfieldOffenseSupport(game: GameState, playerNum: int) -> PlayerAction: 
    config = get_config()
    if (getBallOwner(game) == playerNum): 
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, game.players[3].pos)) and game.players[3].speed == 0): 
           return PlayerAction(Vec2(0,0), kickTo(game, game.players[3].pos, playerNum))
        if (not anyOpBetween(game, playerNum, game.players[playerNum].pos, Vec2(900, 250))): 
            return PlayerAction(Vec2(0,0), kickTo(game, bestTeammatePass(game, playerNum), playerNum))
        return runAndKick(game, playerNum, 900, 150)
    else: 
        return PlayerAction(gotoPos(game, playerNum, Vec2(900, 150)), None)


def strikerOffense(game: GameState, playerNum: int) -> PlayerAction: 
    config = get_config()
    if (getBallOwner(game) == playerNum): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    else: 
        return PlayerAction(gotoPos(game, playerNum, Vec2(900, 500)), None)


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

    actions.append(goalieOffense(game, 0))
    actions.append(midfieldOffenseSupport(game, 1))
    actions.append(midfieldOffenseMain(game, 2))
    actions.append(strikerOffense(game, 3))


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


