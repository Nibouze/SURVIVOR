#==================================================
#--------------------IMPORTATIONS------------------
#==================================================
import pygame
import csv
import os
import random
import time
import subprocess
from classes import Personnage, Ennemi, TankEnnemi, CombattantEnnemi, RangeEnnemi, Assassin, Tank, Combattant, Sniper

#==================================================
#--------------------CONSTANTES--------------------
#==================================================
# Définition des constantes pour la fenêtre, les tuiles, le joueur, etc.
LARGEUR_FENETRE = 1920
HAUTEUR_FENETRE = 1080
TAILLE_TUILE = 80
ECHELLE_JOUEUR = 2
VITESSE_MARCHE = 5
VITESSE_COURSE = 10
NOIR = (0, 0, 0)
DEGATS_JOUEUR = 20  # Définition des dégâts du joueur
ATTAQUE_RANGE = 100  # Portée de l'attaque du joueur
DUREE_ANIMATION_ATTAQUE = 25
#==================================================
#----------------PYGAME INITIALISATION-------------
#==================================================

# Initialisation de Pygame
if not pygame.get_init():
    pygame.init()
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Survivor")

#==================================================
#----------------CLASS DU JEU----------------------
#==================================================

class Joueur(Personnage, pygame.sprite.Sprite):
    def __init__(self, classe, pos_x, pos_y, argent=0, xp=0):
        self.classe = classe  # Stocker la classe choisie

        # Définition des stats et du dossier des sprites selon la classe
        stats = {
            "ASSASSIN": {"vie": 100, "armure": 50, "distance_attaque": 2, "vitesse_recup": 1.5, "vitesse_deplacement": 2, "degats": 25, "sprite_folder": "sprites/assassin/"},
            "TANK": {"vie": 200, "armure": 150, "distance_attaque": 1, "vitesse_recup": 1, "vitesse_deplacement": 0.8, "degats": 15, "sprite_folder": "sprites/tank/"},
            "COMBATTANT": {"vie": 150, "armure": 100, "distance_attaque": 1.5, "vitesse_recup": 1.2, "vitesse_deplacement": 1.5, "degats": 20, "sprite_folder": "sprites/combattant/"},
            "SNIPER": {"vie": 120, "armure": 60, "distance_attaque": 5, "vitesse_recup": 1.8, "vitesse_deplacement": 1, "degats": 30, "sprite_folder": "sprites/sniper/"}
        }

        if classe not in stats:
            raise ValueError("Classe inconnue")

        # Assignation des valeurs selon la classe
        self.vie = stats[classe]["vie"]
        self.armure = stats[classe]["armure"]
        self.distance_attaque = stats[classe]["distance_attaque"]
        self.vitesse_recup = stats[classe]["vitesse_recup"]
        self.vitesse_deplacement = stats[classe]["vitesse_deplacement"]
        self.degats = stats[classe]["degats"]
        # self.sprite_folder = stats[classe]["sprite_folder"] a decommenter quand sprite rajoutée au fichier et enlevr ligne du dessous.
        self.sprite_folder = 'sprites/player/'

        # Initialisation du parent avec les stats définies
        super().__init__(classe, self.vie, self.armure, self.distance_attaque, self.vitesse_recup, self.vitesse_deplacement, pos_x, pos_y, argent, xp)
        pygame.sprite.Sprite.__init__(self)

        # Chargement des sprites spécifiques à la classe
        self.spritesheet_course = pygame.image.load(self.sprite_folder + 'run.png')
        self.spritesheet_marche = pygame.image.load(self.sprite_folder + 'walk.png')
        self.spritesheet_attaque = pygame.image.load(self.sprite_folder + 'attack.png')
        self.spritesheet_mort = pygame.image.load(self.sprite_folder + 'hurt.png')
        self.spritesheet_attente = pygame.image.load(self.sprite_folder + 'waiting.png')

        # Définition des dimensions et autres attributs
        self.largeur_frame = self.spritesheet_course.get_width() // 8
        self.hauteur_frame = self.spritesheet_course.get_height() // 4
        self.facteur_echelle = ECHELLE_JOUEUR
        self.sprite_actuel = 0
        self.en_mouvement = False
        self.en_course = False
        self.en_attaque = False
        self.type_attaque = None
        self.direction = "bas"
        self.rect = pygame.Rect(pos_x, pos_y, self.largeur_frame * self.facteur_echelle, self.hauteur_frame * self.facteur_echelle)
        self.degats_affiches = []
        self.zone_attaque = None
        self.timer_attaque = 0


    def obtenir_frame(self, frame, direction, en_course, en_attaque=False):
        # Définition des directions pour les animations
        directions = {"haut": 0, "gauche": 1, "bas": 2, "droite": 3}
        ligne = directions.get(direction, 2)
        x = int(frame) * self.largeur_frame
        y = ligne * self.hauteur_frame

        # Choix de la spritesheet en fonction de l'action
        spritesheet = None
        if en_attaque:
            if self.type_attaque == 3:
                spritesheet = self.spritesheet_attaque
            else:
                return None  # Si une autre attaque est ajoutée plus tard, éviter une erreur
        else:
            spritesheet = self.spritesheet_course if en_course else self.spritesheet_marche

        # Vérification si la spritesheet a bien été assignée
        if spritesheet is None:
            print("Erreur : spritesheet non chargée ou non définie !")
            return None  # Évite de planter le jeu

        # Extraction de la frame et redimensionnement
        frame_image = spritesheet.subsurface(pygame.Rect(x, y, self.largeur_frame, self.hauteur_frame))
        return pygame.transform.scale(frame_image, (self.largeur_frame * self.facteur_echelle, self.hauteur_frame * self.facteur_echelle))

    def obtenir_frames_attaque(self):
        # Nombre de frames pour l'attaque
        if self.type_attaque == 3:
            return 8
        return 8  # Par défaut

    def commencer_mouvement(self, direction, en_course):
        # Début du mouvement
        if not self.en_attaque:
            self.en_mouvement = True
            self.en_course = en_course
            self.direction = direction

    def arreter_mouvement(self):
        # Arrêt du mouvement
        if not self.en_attaque:
            self.en_mouvement = False
            self.sprite_actuel = 0

    def commencer_attaque(self, type_attaque, ennemis):
        # Début de l'attaque
        self.en_attaque = True
        self.type_attaque = type_attaque
        self.sprite_actuel = 0
        self.timer_attaque = DUREE_ANIMATION_ATTAQUE

        # Définir une attaque en cercle autour du joueur en utilisant la position correcte
        centre_x = self.rect.x + self.rect.width // 2
        centre_y = self.rect.y + self.rect.height // 2
        self.zone_attaque = (centre_x, centre_y, ATTAQUE_RANGE)  # Représentation circulaire

        # Vérifier si l'attaque touche un ennemi
        for ennemi in ennemis:
            distance = ((ennemi.rect.x + ennemi.rect.width // 2 - centre_x) ** 2 + (ennemi.rect.y + ennemi.rect.height // 2 - centre_y) ** 2) ** 0.5
            if distance <= ATTAQUE_RANGE:
                ennemi.vie -= DEGATS_JOUEUR
                print(f"{ennemi.type_ennemi} touché ! Vie restante : {ennemi.vie}")
                self.degats_affiches.append([ennemi.rect.x, ennemi.rect.y, str(DEGATS_JOUEUR), 60])
                if ennemi.vie <= 0:
                    ennemis.remove(ennemi)
                    print(f"{ennemi.type_ennemi} éliminé !")



    def afficher_zone_attaque(self, surface, decalage_camera_x, decalage_camera_y):
        if self.timer_attaque > 0 and self.zone_attaque:
            centre_x = self.rect.x + self.rect.width // 2 - decalage_camera_x
            centre_y = self.rect.y + self.rect.height // 2 - decalage_camera_y
            pygame.draw.circle(surface, (255, 0, 0), (centre_x, centre_y), ATTAQUE_RANGE, 2)
            self.timer_attaque -= 1


    def mettre_a_jour(self):
        # Mise à jour de l'animation
        if self.en_attaque:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= self.obtenir_frames_attaque():
                self.en_attaque = False
                self.sprite_actuel = 0
        elif self.en_mouvement:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= 8:
                self.sprite_actuel = 0

        # Mise à jour de l'image du joueur
        nouvelle_image = self.obtenir_frame(int(self.sprite_actuel), self.direction, self.en_course, self.en_attaque)
        if nouvelle_image:
            self.image = nouvelle_image
            self.rect.width = self.image.get_width()  # Utiliser width au lieu de largeur
            self.rect.height = self.image.get_height()  # Utiliser height au lieu de hauteur
        else:
            self.image = self.obtenir_frame(0, self.direction, False)


class Orc(Ennemi, pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        Ennemi.__init__(self, type_ennemi="Orc", vie=100, armure=50, degats=20, distance_attaque=1, vitesse_deplacement=VITESSE_MARCHE, x=pos_x, y=pos_y)
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet_course = pygame.image.load('sprites/player/orc_run.png')
        self.largeur_frame = self.spritesheet_course.get_width() // 8
        self.hauteur_frame = self.spritesheet_course.get_height() // 4
        self.sprite_actuel = 0
        self.direction = random.choice(["haut", "bas", "gauche", "droite"])
        self.temps_mouvement = random.randint(30, 90)
        self.image = self.obtenir_frame(0, self.direction, True)
        self.rect = pygame.Rect(pos_x, pos_y, self.largeur_frame, self.hauteur_frame)

    def obtenir_frame(self, frame, direction, en_course):
        directions = {"haut": 0, "gauche": 1, "bas": 2, "droite": 3}
        ligne = directions.get(direction, 2)
        x = int(frame) * self.largeur_frame
        y = ligne * self.hauteur_frame

        frame_image = self.spritesheet_course.subsurface(pygame.Rect(x, y, self.largeur_frame, self.hauteur_frame))
        return pygame.transform.scale(frame_image, (self.largeur_frame, self.hauteur_frame))

    def mettre_a_jour(self, joueur):
        self.temps_mouvement -= 1
        if self.temps_mouvement <= 0:
            diff_x = joueur.rect.x - self.rect.x
            diff_y = joueur.rect.y - self.rect.y
            if abs(diff_x) > abs(diff_y):
                if diff_x > 0:
                    nouvelle_direction = "droite"
                else:
                    nouvelle_direction = "gauche"
            else:
                if diff_y > 0:
                    nouvelle_direction = "bas"
                else:
                    nouvelle_direction = "haut"

            centre_x = self.rect.centerx + (self.vitesse_deplacement if nouvelle_direction == "droite" else -self.vitesse_deplacement if nouvelle_direction == "gauche" else 0)
            centre_y = self.rect.centery + (self.vitesse_deplacement if nouvelle_direction == "bas" else -self.vitesse_deplacement if nouvelle_direction == "haut" else 0)
            nouvelle_ligne = centre_y // TAILLE_TUILE
            nouvelle_colonne = centre_x // TAILLE_TUILE
            if 0 <= nouvelle_ligne < lignes and 0 <= nouvelle_colonne < colonnes and carte[nouvelle_ligne][nouvelle_colonne] == '38':
                self.direction = nouvelle_direction
            self.temps_mouvement = random.randint(30, 90)

        deplacement_x, deplacement_y = 0, 0
        if self.direction == "haut":
            deplacement_y = -self.vitesse_deplacement
        elif self.direction == "bas":
            deplacement_y = self.vitesse_deplacement
        elif self.direction == "gauche":
            deplacement_x = -self.vitesse_deplacement
        elif self.direction == "droite":
            deplacement_x = self.vitesse_deplacement

        centre_x = self.rect.centerx + deplacement_x
        centre_y = self.rect.centery + deplacement_y
        nouvelle_ligne = centre_y // TAILLE_TUILE
        nouvelle_colonne = centre_x // TAILLE_TUILE

        if 0 <= nouvelle_ligne < lignes and carte[nouvelle_ligne][self.rect.x // TAILLE_TUILE] in map(str, range(25, 39)):
            self.rect.y += deplacement_y
        if 0 <= nouvelle_colonne < colonnes and carte[self.rect.y // TAILLE_TUILE][nouvelle_colonne] in map(str, range(25, 39)):
            self.rect.x += deplacement_x
        self.sprite_actuel += 0.2
        if self.sprite_actuel >= 8:
            self.sprite_actuel = 0
        self.image = self.obtenir_frame(int(self.sprite_actuel), self.direction, en_course=True)


#==================================================
#--------------------FONCTIONS---------------------
#==================================================
def fondu_entree(surface, duree=60):
    """ Effet de fondu à l'entrée sur la surface de jeu """
    surface_fondu = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    surface_fondu.fill((0, 0, 0))

    for alpha in range(255, -1, -5):  # Diminue l'opacité progressivement
        surface_fondu.set_alpha(alpha)
        surface.fill((0, 0, 0))  # Assurer un fond noir avant de dessiner le jeu
        surface.blit(surface_fondu, (0, 0))
        pygame.display.flip()
        pygame.time.delay(duree // 30)  # Ajuste la vitesse du fondu

def charger_et_redimensionner_image(chemin):
    """Chargement et redimensionnement des images importées"""
    try:
        return pygame.transform.scale(pygame.image.load(chemin).convert(), (TAILLE_TUILE, TAILLE_TUILE))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image {chemin}: {e}")
        return None

# Dictionnaire pour associer chaque caractère à son image
dictionnaire_images = {
    0 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners/top_left_exterior_corner.png'),
    1 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners/top_right_exterior_corner.png'),
    2 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners/top_left_interior_corner.png'),
    3 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners/top_right_interior_corner.png'),
    4 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls/right.png'),
    5 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls/bottom.png'),
    6 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners/bottom_left_exterior_corner.png'),
    7 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners/bottom_right_exterior_corner.png'),
    8 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners/bottom_left_interior_corner.png'),
    9 : charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners/bottom_right_interior_corner.png'),
    10: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls/top.png'),
    11: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls/left.png'),
    12: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/top_left_exterior_corner.png'),
    13: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/top_right_exterior_corner.png'),
    14: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/top_left_interior_corner.png'),
    15: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/top_right_interior_corner.png'),
    16: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/right.png'),
    17: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/bottom.png'),
    18: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/bottom_left_exterior_corner.png'),
    19: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Exterior_Corners_v2/bottom_right_exterior_corner.png'),
    20: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/bottom_left_interior_corner.png'),
    21: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Interior_Corners_v2/bottom_right_interior_corner.png'),
    22: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/top.png'),
    23: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Walls_v2/left.png'),
    24: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_left_wall.png'),
    25: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_top_wall.png'),
    26: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_top_left_corner.png'),
    27: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_top_right_corner.png'),
    28: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_exteriors_corners/path_top_left_corner.png'),
    29: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_exteriors_corners/path_top_right_corner.png'),
    30: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_bottom_wall.png'),
    31: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_walls/path_right_wall.png'),
    32: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_bottom_left_corner.png'),
    33: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_interior_corners/path_bottom_right_corner.png'),
    34: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_exteriors_corners/path_bottom_left_corner.png'),
    35: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/path_exteriors_corners/path_bottom_right_corner.png'),
    36: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/path_bg_color.png'),
    37: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/exterior_background.png'),
    38: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/Backgrounds/interior_background.png'),
    40: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/diagonals/diagonal_top-left_bottom-right.png'),
    41: charger_et_redimensionner_image('images/cornes_tiles_x80/Tileset/Exports/diagonals/diagonal_bottom-left_top-right.png'),

}

# Chargement de la carte CSV
def charger_matrice_depuis_csv(chemin_fichier):
    """Chargement et importation des différentes cartes du jeu à partir de fichiers CSV"""
    if not os.path.exists(chemin_fichier):
        print(f"Erreur : Fichier '{chemin_fichier}' introuvable.")
        return []
    try:
        with open(chemin_fichier, newline='', encoding='utf-8') as fichier_csv:
            lecteur = csv.reader(fichier_csv)
            return [list(ligne) for ligne in lecteur]
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
        return []

fichier_matrice = 'nul.csv'
carte = charger_matrice_depuis_csv(fichier_matrice)

# Dimensions de la carte
lignes = len(carte)
colonnes = len(carte[0])
largeur_matrice = colonnes * TAILLE_TUILE
hauteur_matrice = lignes * TAILLE_TUILE

def generer_orcs(nombre_orcs, joueur):
    """Génère des orcs sur des positions valides de la carte."""
    orcs = []
    for _ in range(nombre_orcs):
        while True:
            spawn_x = random.randint(0, colonnes - 1) * TAILLE_TUILE
            spawn_y = random.randint(0, lignes - 1) * TAILLE_TUILE

            # Vérifier si la tuile est une zone de déplacement valide
            ligne = spawn_y // TAILLE_TUILE
            colonne = spawn_x // TAILLE_TUILE
            if peut_se_deplacer_vers(carte[ligne][colonne]):
                orc = Orc(spawn_x, spawn_y)
                orcs.append(orc)
                print(f"Orc généré à ({spawn_x}, {spawn_y})")
                break  # Sortir de la boucle une fois qu'un emplacement valide est trouvé
    return orcs

# Fonction d'affichage des barres de vie
def afficher_barre_vie(surface, x, y, largeur, hauteur, vie_actuelle, vie_max, couleur_fond, couleur_barre):
    pygame.draw.rect(surface, couleur_fond, (x, y, largeur, hauteur))
    largeur_barre = int((vie_actuelle / vie_max) * largeur)
    pygame.draw.rect(surface, couleur_barre, (x, y, largeur_barre, hauteur))

position_joueur_x = LARGEUR_FENETRE // 2
position_joueur_y = HAUTEUR_FENETRE // 2

def afficher_game_over(fenetre):
    fenetre.fill((0, 0, 0))
    font = pygame.font.Font(None, 100)
    texte = font.render("GAME OVER", True, (255, 0, 0))
    fenetre.blit(texte, ((LARGEUR_FENETRE - texte.get_width()) // 2, (HAUTEUR_FENETRE - texte.get_height()) // 2))
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    subprocess.run(["python", "interface.py"])

def peut_se_deplacer_vers(caractere_tuile):
    """ Vérifie si le mouvement est possible """
    return caractere_tuile == '38' or caractere_tuile.isalpha() or (caractere_tuile.isdigit() and 25 <= int(caractere_tuile) <= 38)


def lancer_jeu(classe):
    en_cours = True
    horloge = pygame.time.Clock()
    fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.RESIZABLE)

    surface_fondu = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    surface_fondu.fill((0, 0, 0))
    alpha_fondu = 255

    joueur = Joueur(classe, largeur_matrice // 2, hauteur_matrice // 2)


    orcs = generer_orcs(10, joueur)

    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYUP:
                if evenement.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_d, pygame.K_q, pygame.K_z, pygame.K_s]:
                    joueur.arreter_mouvement()
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_1:
                    joueur.commencer_attaque(3,orcs)

        touches = pygame.key.get_pressed()

        deplacement_x, deplacement_y = 0, 0
        vitesse = VITESSE_COURSE if touches[pygame.K_z] or touches[pygame.K_q] or touches[pygame.K_s] or touches[pygame.K_d] else VITESSE_MARCHE

        if not joueur.en_attaque:
            if touches[pygame.K_z]:
                joueur.commencer_mouvement("haut", en_course=True)
                deplacement_y = -vitesse
            elif touches[pygame.K_UP]:
                joueur.commencer_mouvement("haut", en_course=False)
                deplacement_y = -vitesse

            if touches[pygame.K_s]:
                joueur.commencer_mouvement("bas", en_course=True)
                deplacement_y = vitesse
            elif touches[pygame.K_DOWN]:
                joueur.commencer_mouvement("bas", en_course=False)
                deplacement_y = vitesse

            if touches[pygame.K_q]:
                joueur.commencer_mouvement("gauche", en_course=True)
                deplacement_x = -vitesse
            elif touches[pygame.K_LEFT]:
                joueur.commencer_mouvement("gauche", en_course=False)
                deplacement_x = -vitesse

            if touches[pygame.K_d]:
                joueur.commencer_mouvement("droite", en_course=True)
                deplacement_x = vitesse
            elif touches[pygame.K_RIGHT]:
                joueur.commencer_mouvement("droite", en_course=False)
                deplacement_x = vitesse

        nouvelle_ligne = (joueur.rect.y + deplacement_y + 10) // TAILLE_TUILE
        nouvelle_colonne = (joueur.rect.x + deplacement_x) // TAILLE_TUILE

        if 0 <= nouvelle_ligne < lignes and peut_se_deplacer_vers(carte[nouvelle_ligne][joueur.rect.x // TAILLE_TUILE]):
            joueur.rect.y += deplacement_y
        if 0 <= nouvelle_colonne < colonnes and peut_se_deplacer_vers(carte[joueur.rect.y // TAILLE_TUILE][nouvelle_colonne]):
            joueur.rect.x += deplacement_x

        decalage_camera_x = joueur.rect.x - position_joueur_x + 60
        decalage_camera_y = joueur.rect.y - position_joueur_y +60

        fenetre.fill(NOIR)

        for index_ligne, ligne in enumerate(carte):
            for index_colonne, caractere in enumerate(ligne):
                caractere = int(caractere) if caractere.isdigit() else caractere
                image = dictionnaire_images.get(caractere)
                if image:
                    x = index_colonne * TAILLE_TUILE - decalage_camera_x
                    y = index_ligne * TAILLE_TUILE - decalage_camera_y
                    if 0 <= x < LARGEUR_FENETRE and 0 <= y < HAUTEUR_FENETRE:
                        fenetre.blit(image, (x, y))
        joueur.mettre_a_jour()
        fenetre.blit(joueur.image, (position_joueur_x - joueur.rect.width // 2, position_joueur_y - joueur.rect.height // 2))

        # Correction de l'affichage dans la boucle du jeu
        for orc in orcs:
            orc.mettre_a_jour(joueur)
            x = orc.rect.x - decalage_camera_x
            y = orc.rect.y - decalage_camera_y
            if 0 <= x < LARGEUR_FENETRE and 0 <= y < HAUTEUR_FENETRE:
                fenetre.blit(orc.image, (x, y))
                afficher_barre_vie(fenetre, x, y - 10, 40, 5, orc.vie, 100, (255, 0, 0), (0, 255, 0))

                # Gestion des collisions
                if joueur.rect.colliderect(orc.rect):
                    joueur.vie -= 0.1  # Réduction de la vie du joueur en cas de collision

        #affiche les dégats de l'attaque
        joueur.afficher_zone_attaque(fenetre, decalage_camera_x, decalage_camera_y)
        # Affichage de la barre de vie du joueur
        afficher_barre_vie(fenetre, 20, 20, 200, 20, joueur.vie, 100, (255, 0, 0), (0, 255, 0))

        if joueur.vie <= 0:
            afficher_game_over(fenetre)
            return
        if alpha_fondu > 0:
            surface_fondu.set_alpha(alpha_fondu)
            fenetre.blit(surface_fondu, (0, 0))
            alpha_fondu -= 5

        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()

if __name__ == "__main__":
    lancer_jeu("ASSASSIN")