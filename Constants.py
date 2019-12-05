# Stores most of the colors and dimensions used in the game
SCALE = 1.3
MAPSIZE = 3000

PEACH = (255, 204, 153)
TAN = (255, 153, 51)
BLACK = (0, 0, 0)
MEDKIT_COLOR = (0, 102, 255)
HEALTH_RED = (255, 80, 80)
BANDAGE_COLOR = (0, 204, 255)
ADREN_COLOR = (0, 102, 255)
FOOD_COLOR = (255, 153, 102)
BUSH_GREEN = (0, 102, 0, 250)
TREE_BROWN = (102, 51, 0)
ROCK_GRAY = (204, 204, 204)
LIGHT_GRAY = (230, 230, 230)
LIGHT_GRAY_TRANSP = (230, 230, 230, 128)

AMMO_COLORS = {'9mm'  :  (255, 204, 0),
               '7.62' :  (102, 102, 255),
               '5.56' :  (0, 255, 170),
               '12g'  :  (255, 51, 153)}

ITEM_COLORS = {'9mm'  :  (255, 204, 0),
               '7.62' :  (102, 102, 255),
               '5.56' :  (0, 255, 170),
               '12g'  :  (255, 51, 153),
               'medkit' : MEDKIT_COLOR,
               'adrenaline' : ADREN_COLOR}


PLAYER_RADIUS = int(40 // SCALE)
ZOMBIE_RADIUS = int(30 // SCALE)
TREE_RADIUS = int(40 // SCALE)
TREETOP_RADIUS = int(160 // SCALE)
BUSH_RADIUS = int(100 // SCALE)
ROCK_RADIUS = int(60 // SCALE)
ITEM_RADIUS = int(25 // SCALE)
AMMO_RADIUS = int(20 // SCALE)
BULLET_RADIUS = int(6 // SCALE)

windowWidth = 800
windowHeight = 800
mode = None
