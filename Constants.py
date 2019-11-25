# Repository of most of the colors and dimensions used in the game
SCALE = 1.3

PEACH = (255, 204, 153)
BLACK = (0, 0, 0)
HEALTH_COLOR = (0, 102, 255)
BANDAGE_COLOR = (0, 204, 255)
ADREN_COLOR = (0, 102, 255)
FOOD_COLOR = (255, 153, 102)
BUSH_GREEN = (0, 102, 0, 220)
TREE_BROWN = (102, 51, 0)
LIGHT_GRAY = (230, 230, 230)

AMMO_COLORS = {'9mm'  :  (255, 204, 0),
               '7.62' :  (102, 102, 255),
               '5.56' :  (0, 255, 170),
               '12g'  :  (255, 51, 153)}

ITEM_COLORS = {'9mm'  :  (255, 204, 0),
               '7.62' :  (102, 102, 255),
               '5.56' :  (0, 255, 170),
               '12g'  :  (255, 51, 153),
               'health' : HEALTH_COLOR,
               'adrenaline' : ADREN_COLOR}


PLAYER_RADIUS = int(40 // SCALE)
ZOMBIE_RADIUS = int(30 // SCALE)
TREE_RADIUS = int(40 // SCALE)
BUSH_RADIUS = int(50 // SCALE)
ITEM_RADIUS = int(25 // SCALE)
AMMO_RADIUS = int(20 // SCALE)
BULLET_RADIUS = int(6 // SCALE)
