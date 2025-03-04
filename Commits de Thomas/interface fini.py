import pygame
import sys
import jeu
import classes

# Définition des couleurs et dimensions
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
LARGEUR, HAUTEUR = 1920, 1080

# Chargement des ressources
def charger_image():
    return pygame.image.load('menu.png')

def effet_zoom_fondu(ecran, image, cible):
    clock = pygame.time.Clock()
    zoom = 1
    fade_alpha = 0
    surface_fade = pygame.Surface((LARGEUR, HAUTEUR))
    surface_fade.fill(NOIR)
    volume = pygame.mixer.music.get_volume()

    while zoom < 5.5:
        clock.tick(30)
        ecran.fill(NOIR)
        taille = (int(LARGEUR * zoom), int(HAUTEUR * zoom))
        image_zoom = pygame.transform.scale(image, taille)
        x = -((cible[0] + 420) * (zoom - 1))
        y = -((cible[1] - 50) * (zoom - 1))
        ecran.blit(image_zoom, (x, y))
        pygame.display.flip()
        zoom += 0.15
        volume = max(0, volume - 0.03)
        pygame.mixer.music.set_volume(volume)

    while fade_alpha < 255:
        clock.tick(30)
        surface_fade.set_alpha(fade_alpha)
        ecran.blit(surface_fade, (0, 0))
        pygame.display.flip()
        fade_alpha += 5
        volume = max(0, volume - 0.03)
        pygame.mixer.music.set_volume(volume)

    pygame.mixer.music.stop()

# Classe du menu principal
class Menu:
    def __init__(self, ecran, options, positions):
        self.ecran = ecran
        self.options = options
        self.police = pygame.font.Font("VINERITC.ttf", 60)
        self.positions = positions

    def afficher(self):
        souris_x, souris_y = pygame.mouse.get_pos()
        for option, position in self.positions.items():
            texte = self.police.render(option, True, BLANC)
            rect_texte = texte.get_rect(center=position)
            if rect_texte.collidepoint(souris_x, souris_y):
                texte = pygame.font.Font("VINERITC.ttf", 80).render(option, True, ROUGE)
                rect_texte = texte.get_rect(center=position)
            self.ecran.blit(texte, rect_texte)

    def gerer_evenement(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            souris_x, souris_y = pygame.mouse.get_pos()
            for option, position in self.positions.items():
                rect_option = pygame.Rect(position[0] - 100, position[1] - 50, 200, 100)
                if rect_option.collidepoint(souris_x, souris_y):
                    return option
        return None

def choisir_classe(ecran, image_fond):
    """ Affiche le menu de sélection de classe et renvoie la classe choisie. """
    options = ["ASSASSIN", "TANK", "COMBATTANT", "SNIPER"]
    positions = {
        "ASSASSIN": (LARGEUR // 4, HAUTEUR // 2),
        "TANK": (LARGEUR // 2, HAUTEUR // 2),
        "COMBATTANT": (3 * LARGEUR // 4, HAUTEUR // 2),
        "SNIPER": (LARGEUR // 2, HAUTEUR // 1.5)
    }
    menu = Menu(ecran, options, positions)

    while True:
        ecran.blit(pygame.transform.scale(image_fond, (LARGEUR, HAUTEUR)), (0, 0))
        menu.afficher()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            choix = menu.gerer_evenement(event)
            if choix:
                effet_zoom_fondu(ecran, image_fond, positions[choix])
                return choix

def lancer_musique():
    pygame.mixer.music.stop()
    pygame.mixer.music.load('menu.mp3')
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1, 0.0)

def bar_volume(ecran, volume_actuel):
    """Affiche la barre de volume et le curseur."""
    largeur_bar = 400
    hauteur_bar = 20
    bar_x = (LARGEUR - largeur_bar) // 2
    bar_y = 300

    pygame.draw.rect(ecran, NOIR, (bar_x, bar_y, largeur_bar, hauteur_bar))
    largeur_rempli = int(largeur_bar * volume_actuel)
    pygame.draw.rect(ecran, ROUGE, (bar_x, bar_y, largeur_rempli, hauteur_bar))

    curseur_x = bar_x + largeur_rempli
    curseur_y = bar_y + hauteur_bar // 2
    pygame.draw.circle(ecran, BLANC, (curseur_x, curseur_y), 10)

    font = pygame.font.Font("VINERITC.ttf", 40)
    volume_text = f"{int(volume_actuel * 100)}%"
    text = font.render(volume_text, True, BLANC)
    text_rect = text.get_rect(center=(LARGEUR // 2, bar_y - 30))
    ecran.blit(text, text_rect)

def options_menu(ecran, image_fond, volume_actuel):
    """ Affiche le menu des options et permet d'ajuster le volume. """
    while True:
        ecran.blit(pygame.transform.scale(image_fond, (LARGEUR, HAUTEUR)), (0, 0))

        font = pygame.font.Font("VINERITC.ttf", 50)
        texte = font.render("OPTIONS", True, BLANC)
        ecran.blit(texte, (LARGEUR // 2 - 100, 100))

        bar_volume(ecran, volume_actuel)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return volume_actuel
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    souris_x, _ = pygame.mouse.get_pos()
                    largeur_bar = 400
                    bar_x = (LARGEUR - largeur_bar) // 2
                    if bar_x <= souris_x <= bar_x + largeur_bar:
                        volume_actuel = (souris_x - bar_x) / largeur_bar
                        pygame.mixer.music.set_volume(volume_actuel)



def changement_volume(souris_pos, volume_actuel):
    """Modifie le volume en fonction de la position de la souris."""
    largeur_bar = 400
    bar_x = (LARGEUR - largeur_bar) // 2
    bar_y = 100

    if bar_x <= souris_pos[0] <= bar_x + largeur_bar:
        nouveau_volume = (souris_pos[0] - bar_x) / largeur_bar
        return min(max(nouveau_volume, 0.0), 1.0)
    return volume_actuel

def main():
    pygame.init()
    pygame.mixer.init()

    lancer_musique()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Menu Principal")
    image_fond = charger_image()
    menu = Menu(ecran, ["JOUER", "OPTIONS", "EXIT"], {
        "JOUER": (350, 180),
        "EXIT": (LARGEUR - 300, 180),
        "OPTIONS": (370, HAUTEUR - 200)
    })
    volume = 0.5

    while True:
        ecran.blit(pygame.transform.scale(image_fond, (LARGEUR, HAUTEUR)), (0, 0))
        menu.afficher()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            choix = menu.gerer_evenement(event)
            if choix:
                if choix == "JOUER":
                    classe = choisir_classe(ecran, image_fond)
                    jeu.lancer_jeu(classe)
                elif choix == "OPTIONS":
                    volume = options_menu(ecran, image_fond, volume)
                elif choix == "EXIT":
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main()
