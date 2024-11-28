import pygame

# Constantes
WIN_WIDTH = 1920
WIN_HEIGHT = 1080
TILE_SIZE = 80  # Taille des tuiles
PLAYER_SIZE = 40  # Taille du joueur
PLAYER_COLOR = (0, 255, 0)  # Vert
PLAYER_SPEED = 5  # Vitesse de déplacement du joueur
BLACK = (0, 0, 0)  # Couleur de fond

# Initialisation de Pygame
pygame.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Survivor")

# Importation et redimensionnement des images pour chaque caractère
corner_up_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/top_left_exterior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
corner_up_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/top_right_exterior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
corner_down_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/bottom_left_exterior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
corner_down_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/bottom_right_exterior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
border_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/left.png').convert(), (TILE_SIZE, TILE_SIZE))
border_up = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/top.png').convert(), (TILE_SIZE, TILE_SIZE))
border_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/right.png').convert(), (TILE_SIZE, TILE_SIZE))
border_down = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/bottom.png').convert(), (TILE_SIZE, TILE_SIZE))
interieur_corner_up_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/top_left_interior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
interieur_corner_up_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/top_right_interior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
interieur_corner_bottom_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/bottom_right_interior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
interieur_corner_bottom_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/bottom_left_interior_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
exterior_background = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/interior_background.png').convert(), (TILE_SIZE, TILE_SIZE))
interior_background = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/exterior_background.png').convert(), (TILE_SIZE, TILE_SIZE))
interior_wall_bg = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/path_bg_color.png').convert(), (TILE_SIZE, TILE_SIZE))
path_interieur_corner_bottom_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_interior_bottom_right_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_interieur_corner_bottom_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_interior_bottom_left_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_interieur_corner_top_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_interior_top_right_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_interieur_corner_top_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_interior_top_left_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_exterior_corner_bottom_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_exterior_corners/path_bottom_right_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_exterior_corner_bottom_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_exterior_corners/path_bottom_left_corner.png').convert(), (TILE_SIZE, TILE_SIZE)) 
path_exterior_corner_top_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_exterior_corners/path_top_left_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_exterior_corner_top_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_exterior_corners/path_top_right_corner.png').convert(), (TILE_SIZE, TILE_SIZE))
path_wall_top = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_top_wall.png').convert(), (TILE_SIZE, TILE_SIZE))
path_wall_left = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_left_wall.png').convert(), (TILE_SIZE, TILE_SIZE))
path_wall_bottom = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_bottom_wall.png').convert(), (TILE_SIZE, TILE_SIZE))
path_wall_right = pygame.transform.scale(pygame.image.load('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_right_wall.png').convert(), (TILE_SIZE, TILE_SIZE))

# Dictionnaire pour associer chaque caractère à son image
image_map = {
    '0': corner_up_left,
    '1': corner_up_right,
    '2': corner_down_left,
    '3': corner_down_right,
    '4': border_up, 
    '5': border_left,
    '6': border_down,
    '7': border_right,
    '8': exterior_background,
    '.': interior_background,
    '+': interieur_corner_up_left,
    '-': interieur_corner_up_right,
    '/': interieur_corner_bottom_right,
    '*': interieur_corner_bottom_left,
    '!': interior_wall_bg,
    'A': path_interieur_corner_top_left,
    'B': path_interieur_corner_top_right,
    'C': path_interieur_corner_bottom_right,
    'D': path_interieur_corner_bottom_left,
    'a': path_exterior_corner_top_left,
    'b': path_exterior_corner_top_right,
    'c': path_exterior_corner_bottom_right,
    'd': path_exterior_corner_bottom_left,
    'E': path_wall_top,
    'F': path_wall_left,
    'G': path_wall_bottom,
    'H': path_wall_right
}

# Lecture du fichier de la matrice
with open('matrix_pattern.txt', 'r') as file:
    lines = file.readlines()

# Dimensions de la matrice
rows = len(lines)
cols = len(lines[0].strip())

# Dimensions de la matrice en pixels
matrix_width = cols * TILE_SIZE
matrix_height = rows * TILE_SIZE

# Position initiale du joueur dans le monde
player_world_x = matrix_width // 2
player_world_y = matrix_height // 2

# Position fixe du joueur au centre de la fenêtre
player_screen_x = WIN_WIDTH // 2
player_screen_y = WIN_HEIGHT // 2

# Fonction pour vérifier si une case est traversable
def can_move_to(tile_char):
    if tile_char == '8' or tile_char == '!':  # Le chiffre 8 est traversable
        return True
    elif tile_char.isalpha():  # Les lettres sont traversables
        return True
    elif tile_char.isdigit() and tile_char != '8':  # Les chiffres autres que 8 ne sont pas traversables
        return False
    else:  # Les caractères spéciaux ne sont pas traversables
        return False

# Boucle principale
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gérer les touches pour le déplacement
    keys = pygame.key.get_pressed()
    move_x = 0
    move_y = 0

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move_y = -PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move_y = PLAYER_SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move_x = -PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move_x = PLAYER_SPEED

    # Calculer les nouvelles positions de la matrice en fonction du mouvement
    new_player_row = (player_world_y + move_y) // TILE_SIZE
    new_player_col = (player_world_x + move_x) // TILE_SIZE

    # Vérification des collisions
    if 0 <= new_player_row < rows and can_move_to(lines[new_player_row][player_world_x // TILE_SIZE]):
        player_world_y += move_y  # Mouvement vertical autorisé si la case est traversable
    if 0 <= new_player_col < cols and can_move_to(lines[player_world_y //  TILE_SIZE][new_player_col]):
        player_world_x += move_x  # Mouvement horizontal autorisé si la case est traversable

    # Calculer les décalages de la caméra
    camera_offset_x = player_world_x - player_screen_x
    camera_offset_y = player_world_y - player_screen_y

    # Remplir l'écran de noir pour le rafraîchissement
    win.fill((0, 0, 0))

    # Afficher les images selon la matrice en fonction du décalage de la caméra
    for row_index, line in enumerate(lines):
        for col_index, char in enumerate(line.strip()):
            image = image_map.get(char)
            if image:
                x = col_index * TILE_SIZE - camera_offset_x
                y = row_index * TILE_SIZE - camera_offset_y
                if 0 <= x < WIN_WIDTH and 0 <= y < WIN_HEIGHT :
                    win.blit(image, (x, y))

    # Dessiner le joueur au centre de l'écran
    pygame.draw.rect(win, PLAYER_COLOR, (player_screen_x - PLAYER_SIZE // 2, player_screen_y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE))

    # Mettre à jour l'affichage
    pygame.display.flip()
    clock.tick(60)

# Quitter Pygame
pygame.quit()
