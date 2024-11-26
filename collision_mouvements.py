import pygame

# Initialisation de pygame
pygame.init()

# Constantes de la fenêtre
SCREEN_WIDTH = 800  # Largeur de la fenêtre
SCREEN_HEIGHT = 600  # Hauteur de la fenêtre
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
PASSABLE_COLOR = (0, 0, 255)  # Couleur de l'obstacle passable
HIDEABLE_COLOR = (255, 0, 0)  # Couleur de l'obstacle où le joueur peut se cacher

# Classe Joueur (un carré)
class Player:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def draw(self, surface, obstacles):
        hidden = False
        for obstacle in obstacles:
            if obstacle.is_hideable and self.rect.colliderect(obstacle.rect):
                hidden = True
        if not hidden:
            pygame.draw.rect(surface, PLAYER_COLOR, self.rect)

# Classe pour les obstacles
class Obstacle:
    def __init__(self, x, y, width, height, is_solid=True, is_hideable=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_solid = is_solid  # Cet obstacle bloque-t-il le joueur ?
        self.is_hideable = is_hideable  # Cet obstacle peut-il cacher le joueur ?

    def draw(self, surface, color):
        pygame.draw.rect(surface, color, self.rect)

# Classe principale du jeu
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jeu de collision avec des obstacles")
        self.clock = pygame.time.Clock()
        self.player = Player(50, 50, 50, 5)
        # Création des obstacles : solide, passable, et cachable
        self.obstacles = [
            Obstacle(300, 200, 200, 200, is_solid=True),  # Obstacle solide (noir)
            Obstacle(550, 100, 150, 50, is_solid=False),  # Obstacle passable (bleu)
            Obstacle(150, 400, 200, 100, is_solid=False, is_hideable=True)  # Obstacle cachable (rouge)
        ]
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        old_position = self.player.rect.copy()  # Sauvegarder l'ancienne position avant de bouger

        self.player.move(keys)

        # Détection de collision avec obstacles solides
        for obstacle in self.obstacles:
            if obstacle.is_solid and self.player.rect.colliderect(obstacle.rect):
                self.player.rect = old_position  # Rétablir la position si collision avec un obstacle solide

    def draw(self):
        self.screen.fill(WHITE)
        
        # Dessiner les obstacles
        for obstacle in self.obstacles:
            if obstacle.is_solid:
                obstacle.draw(self.screen, BLACK)  # Obstacles solides (noirs)
            elif obstacle.is_hideable:
                obstacle.draw(self.screen, HIDEABLE_COLOR)  # Obstacles cachables (rouges)
            else:
                obstacle.draw(self.screen, PASSABLE_COLOR)  # Obstacles passables (bleus)

        # Dessiner le joueur
        self.player.draw(self.screen, self.obstacles)

        pygame.display.flip()

# Lancer le jeu
if __name__ == "__main__":
    game = Game()
    game.run()

    pygame.quit()
