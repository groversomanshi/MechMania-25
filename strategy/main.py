from . import *
import math
import random

global teamNum
teamNum = -1
global chosen
chosen = False

def get_strategy(team: int):
    """This function tells the engine what strategy you want your bot to use"""
    
    # team == 0 means I am on the left
    # team == 1 means I am on the right
    teamNum = Team #########EDIT teamNum to be a placeholder for which team we belong to
    if team == 0:
        print("Hello! I am team A (on the left)")
        return Strategy(goalee_formation, ball_chase)
    else:   
        print("Hello! I am team B (on the right)")
        return Strategy(goalee_formation, ball_chase) #MAKE SURE THIS IS BALL_CHASE (options: do_nothing, did_something)
    
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

def getNearestTeammatePos(game: GameState, player: PlayerState.id):
    return game.players[game.getNearestTeammate(player, game)].pos

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
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    if (game.players[playerNum].pos.x >= 499): 
        return PlayerAction(gotoPos(game, 2, Vec2(endX, endY)), None)
    if (game.players[playerNum].pos.x < 500): 
        return PlayerAction(gotoPos(game, 2,  config.field.center()), None)
    else: 
        return PlayerAction(Vec2(0,0), None)
    
def kickTo(game, pos, playerNum): 
    return pos - game.players[playerNum].pos


def getBetweenObjects(closer: Vec2, farther: Vec2, fraction: float, max_dist: float = None) -> Vec2:
    # Returns a point that is `fraction` of the way from closer to farther,
    # but never more than max_dist pixels away from closer.
    direction = farther - closer
    distance = direction.norm()
    if max_dist is not None and distance > 0:
        max_fraction = min(1.0, max_dist / distance)
        fraction = min(fraction, max_fraction)
    return closer + direction * fraction

def getBetweenObjectsRadius(center: Vec2, pos: Vec2, R: float) -> Vec2:
    """
    Returns a point on a circle of radius R around center, in the direction of pos.
    """
    direction = pos - center
    norm = direction.norm()
    if norm == 0:
        # If pos == center, return a default point on the circle
        return center + Vec2(R, 0)
    unit_dir = direction * (1.0 / norm)
    return center + unit_dir * R


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
        if (game.tick > 7200): 
            return PlayerAction(Vec2(0,0), kickTo(game, getNearestWall(game, playerNum), playerNum)) 
        return PlayerAction(Vec2(0,0), kickTo(game, bestTeammatePass(game, playerNum), playerNum))
    return PlayerAction(gotoPos(game, playerNum, getBetweenObjectsRadius(config.field.goal_self(), getBallPos(game), 120)), None)

#MIDFIELD PLANS: 
# --> if opposing is between main and goal, pass to support

def runAndKick(game: GameState, playerNum: int, endX, endY) -> PlayerAction:
    config = get_config()
    # print("ball owned by: ", getBallOwner(game))
    # print("nearest OP player: ", getNearestOp(game, 2))
    if (game.players[playerNum].pos.x < endX): 
        return PlayerAction(gotoPos(game, playerNum, Vec2(endX, endY)), None)
    if (game.players[playerNum].pos.x >= endX-1): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    else: 
        return PlayerAction(gotoPos(game, playerNum, Vec2(850, 300)), None)


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

def getNearestWall(game: GameState, playerNum: int) -> Vec2:
    config = get_config()
    field = config.field.bottom_right()
    cur_pos = game.players[playerNum].pos

    # Clamp x and y to the field boundaries
    wall_x = min(max(cur_pos.x, 0), field.x)
    wall_y = min(max(cur_pos.y, 0), field.y)

    # Find the closest wall point
    candidates = [
        Vec2(0, wall_y),           # Left wall
        Vec2(field.x, wall_y),     # Right wall
        Vec2(wall_x, 0),           # Top wall
        Vec2(wall_x, field.y)      # Bottom wall
    ]
    nearest = min(candidates, key=lambda p: cur_pos.dist(p))
    return nearest

def getNearestTeammateBest(player: PlayerState.id, game: GameState, openMatesOnly):
    #global teamNum
    nearestpos = Vec2(-1, -1)
    # if teamNum == Team.Self:
    #     teamplayers = game.team(teamNum)
    # else:
    #     teamplayers = game.team(not teamNum)
    for teammate in openMatesOnly:
        if teammate.id != player:
            if nearestpos == Vec2(-1, -1):
                nearestpos = teammate.pos
                nearestid = teammate.id
            elif openMatesOnly[player].pos.dist(teammate.pos) < openMatesOnly[player].pos.dist(nearestpos):
                nearestpos = teammate.pos
                nearestid = teammate.id
    return nearestid

def bestTeammatePass(game: GameState, playerNum: int) -> Vec2:
    teammates = [p for p in getAllTeammates(game) if p.id != playerNum and p.id != 0]  # exclude self and goalie
    cur_pos = game.players[playerNum].pos
    open_teammates = []
    for mate in teammates:
        if not anyOpBetween(game, playerNum, cur_pos, mate.pos):
            open_teammates.append(mate)
    if open_teammates:
        # Pass to the nearest open teammate
        return game.players[getNearestTeammateBest(playerNum, game, open_teammates)].pos
    # fallback: pass to nearest teammate (even if blocked)
    return game.players[getNearestTeammateBest(playerNum, game, teammates)].pos


# assume you have the ball or can easily get it 
def midfieldOffenseMain(game: GameState, playerNum: int) -> PlayerAction:
    config = get_config()

    if (getBallOwner(game) == playerNum): 
        if (game.tick > 7200): 
            return PlayerAction(Vec2(0,0), kickTo(game, getNearestWall(game, playerNum), playerNum))  
        if (not anyOpBetween(game, playerNum, game.players[playerNum].pos, config.field.goal_other())): 
           return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, game.players[3].pos)) and game.players[3].speed == 0):
           return PlayerAction(Vec2(0,0), kickTo(game, game.players[3].pos, playerNum))
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, config.field.goal_other()))): 
           return PlayerAction(Vec2(0,0), kickTo(game, bestTeammatePass(game, playerNum), playerNum))
        return PlayerAction(Vec2(800,250), kickTo(game, config.field.goal_other(), playerNum))
    elif (getBallPossessionTeam(game) != 0): 
        return corner(game, playerNum)
    else:
        return PlayerAction(gotoPos(game, playerNum, Vec2(800, 250)), None)

def midfieldOffenseSupport(game: GameState, playerNum: int) -> PlayerAction: 
    config = get_config()
    if (getBallOwner(game) == playerNum): 
        if (game.tick > 7200): 
            return PlayerAction(Vec2(0,0), kickTo(game, getNearestWall(game, playerNum), playerNum)) 
        if (not anyOpBetween(game, playerNum, game.players[playerNum].pos, config.field.goal_other())): 
           return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
        if ((not anyOpBetween(game, playerNum, game.players[playerNum].pos, game.players[3].pos)) and game.players[3].speed == 0): 
           return PlayerAction(Vec2(0,0), kickTo(game, game.players[3].pos, playerNum))
        if (not anyOpBetween(game, playerNum, game.players[playerNum].pos, Vec2(900, 250))): 
            return PlayerAction(Vec2(0,0), kickTo(game, bestTeammatePass(game, playerNum), playerNum))
        else: 
            return runAndKick(game, playerNum, 900, 150)
    elif (getBallPossessionTeam(game) != 0): 

        return corner(game, playerNum)
    else: 
        return PlayerAction(gotoPos(game, playerNum, Vec2(900, 150)), None)


def strikerOffense(game: GameState, playerNum: int) -> PlayerAction: 
    config = get_config()
    if (game.tick > 7200): 
            return PlayerAction(Vec2(0,0), kickTo(game, getNearestWall(game, playerNum), playerNum)) 
    if (getBallOwner(game) == playerNum): 
        return PlayerAction(Vec2(0,0), kickTo(game, config.field.goal_other(), playerNum))
    elif (getBallPossessionTeam(game) != 0): 
        return corner(game, playerNum)
    else: 
        return PlayerAction(gotoPos(game, playerNum, Vec2(900, 500)), None)


def did_something(game: GameState) -> List[PlayerAction]:
    actions = []

    do_something = checkMove(game, 2)

    actions.append(do_something)
    actions.append(do_something)
    actions.append(do_something)
    actions.append(do_something)


    return actions



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


def corner(game: GameState, playerNum: int) -> PlayerAction:
    global chosen
    opNum = getBallOwner(game)
    corners = [Vec2(0, 600), Vec2(0, 0), Vec2(1000, 600), Vec2(1000, 0)]
    corner = Vec2(0, 0)
    if (not chosen):
        corner = random.choice(corners)
        chosen = True
    if (getBallPossessionTeam(game) == -1): 
        return PlayerAction(gotoPos(game, playerNum, game.players[getNearestOpToBall(game)].pos), None)
    elif (((game.players[playerNum].pos.x - game.players[opNum].pos.x) > 5)) or (((game.players[playerNum].pos.y - game.players[opNum].pos.y) > 5)):
        chosen = False
        return PlayerAction(gotoPos(game, playerNum, game.players[opNum].pos), None)
    else:
        return PlayerAction(gotoPos(game, playerNum, corner), None)



def getNearestOpToBall(game: GameState):
    global teamNum
    curPos = getBallPos(game) 
    minDist = float('inf')
    minPlayer = -1 
    for i in game.team(teamNum): 
        dist = curPos.dist(game.players[i.id].pos)
        if dist < minDist: 
            minDist = dist
            minPlayer = i.id
    return minPlayer

def evil_chase(game: GameState) -> List[PlayerAction]:
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

   