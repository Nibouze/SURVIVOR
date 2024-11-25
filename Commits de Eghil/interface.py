import pygame
import sys

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
LARGEUR = 800
HAUTEUR = 600

img = pygame.image.load('donjon.jpg')

class Menu:
    def __init__(self, screen, options, font, font_color, couleur):
        self.screen = screen
        self.options = options
        self.font = font
        self.font_color = font_color
        self.couleur = couleur
        self.selected_index = 0

    def draw(self):
        souris_pos = pygame.mouse.get_pos()
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, self.font_color)
            text_rect = text.get_rect(center=(LARGEUR // 2, 200 + i * 60))
            if text_rect.collidepoint(souris_pos):
                zoomed_font = pygame.font.Font("dungeon.ttf", 60)
                text = zoomed_font.render(option, True, self.couleur)
                text_rect = text.get_rect(center=(LARGEUR // 2, 200 + i * 60))
            else:
                text = self.font.render(option, True, self.font_color)
                text_rect = text.get_rect(center=(LARGEUR // 2, 200 + i * 60))

            self.screen.blit(text, text_rect)


    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        if event.type == pygame.MOUSEBUTTONDOWN:
            souris_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                text_rect = pygame.Rect(LARGEUR // 2 - 150, 200 + i * 60 - 25, 300, 50)
                if text_rect.collidepoint(souris_pos):
                    return option
        return None


def photo(screen, img):
    scaled_img = pygame.transform.scale(img, (LARGEUR, HAUTEUR))
    screen.blit(scaled_img, (0, 0))


def options_menu(screen, img, volume_actuel):
    options = ["Retour"]
    font = pygame.font.Font("dungeon.ttf", 50)
    menu = Menu(screen, options, font, BLANC, NOIR)

    running = True
    while running:
        photo(screen, img)
        bar_volume(screen, volume_actuel)
        menu.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            selected = menu.event(event)
            if selected == "Retour":
                return volume_actuel

            """Réglage du volume"""
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    volume_actuel = changement_volume(event.pos, volume_actuel)
                    pygame.mixer.music.set_volume(volume_actuel)
        pygame.display.flip()


def bar_volume(screen, volume_actuel):
    """Affiche la barre de volume et le curseur."""
    largeur_bar = 400
    hauteur_bar = 20
    bar_x = (LARGEUR - largeur_bar) // 2
    bar_y = 100
    """dessin de la bar volume"""
    pygame.draw.rect(screen, NOIR, (bar_x, bar_y, largeur_bar, hauteur_bar))
    largeur_rempli = int(largeur_bar * volume_actuel)
    pygame.draw.rect(screen, ROUGE, (bar_x, bar_y, largeur_rempli, hauteur_bar))

    curseur_x = bar_x + largeur_rempli
    curseur_y = bar_y + hauteur_bar // 2
    pygame.draw.circle(screen, BLANC, (curseur_x, curseur_y), 10)
    """pourcentage"""
    font = pygame.font.Font("dungeon.ttf", 40)
    volume_text = f"{int(volume_actuel * 100)}%"
    text = font.render(volume_text, True, BLANC)
    text_rect = text.get_rect(center=(LARGEUR // 2, bar_y - 30))
    screen.blit(text, text_rect)


def changement_volume(souris_pos, volume_actuel):
    """Modifie le volume en fonction de la position de la souris."""
    largeur_bar = 400
    bar_x = (LARGEUR - largeur_bar) // 2
    bar_y = 100

    if bar_x <= souris_pos[0] <= bar_x + largeur_bar:
        nouveau_volume = (souris_pos[0] - bar_x) / largeur_bar
        return min(max(nouveau_volume, 0.0), 1.0)
    return volume_actuel


def play_music():
    pygame.mixer.music.load('musique_donjon.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0)


def main():
    pygame.init()
    pygame.mixer.init()
    play_music()

    screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Menu Principal")

    font = pygame.font.Font("dungeon.ttf", 50)
    options = ["Jouer", "Options", "Quitter"]
    menu = Menu(screen, options, font, BLANC, NOIR)

    current_menu = "main"
    volume_actuel = 0.5

    while True:
        if current_menu == "main":
            photo(screen, img)
            menu.draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_menu == "main":
                selected = menu.event(event)
                if selected:
                    if selected == "Jouer":
                        print("Lancement du jeu...")
                    elif selected == "Options":
                        current_menu = "options"
                        volume_actuel = options_menu(screen, img, volume_actuel)
                        current_menu = "main"
                    elif selected == "Quitter":
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()
