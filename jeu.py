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
boss_spawned = False
boss = None

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
            "ASSASSIN": {"vie": 100, "distance_attaque": 150, "vitesse_recup": 1, "vitesse_deplacement": 2, "degats": 25, "sprite_folder": "sprites/assassin/"},
            "TANK": {"vie": 280, "distance_attaque": 100, "vitesse_recup": 0.8, "vitesse_deplacement": 0.6, "degats": 50, "sprite_folder": "sprites/tank/"},
            "COMBATTANT": {"vie": 150, "distance_attaque":125 , "vitesse_recup": 0.7, "vitesse_deplacement": 1.5, "degats": 75, "sprite_folder": "sprites/combattant/"},
            "SNIPER": {"vie": 120, "distance_attaque": 200 , "vitesse_recup": 0.5, "vitesse_deplacement": 1, "degats": 100, "sprite_folder": "sprites/sniper/"}
        }

        if classe not in stats:
            raise ValueError("Classe inconnue")

        # Assignation des valeurs selon la classe
        self.vie = stats[classe]["vie"]
        self.distance_attaque = stats[classe]["distance_attaque"]
        self.vitesse_recup = stats[classe]["vitesse_recup"]
        self.vitesse_deplacement = stats[classe]["vitesse_deplacement"]
        self.degats = stats[classe]["degats"]
        self.xp = 0
        self.vie_max = stats[classe]["vie"]
        self.gold = 0
        self.niveau = 1
        self.dot = 0
        self.vol_vie = 0
        self.xp_prochain_niveau = 100
        self.sprite_folder = stats[classe]["sprite_folder"]
        #self.sprite_folder = 'sprites/player/'

        # Initialisation du parent avec les stats définies
        super().__init__(classe, self.vie, self.distance_attaque, self.vitesse_recup, self.vitesse_deplacement, pos_x, pos_y, argent, xp)
        pygame.sprite.Sprite.__init__(self)

        # Chargement des sprites spécifiques à la classe
        self.spritesheet_course = pygame.image.load(self.sprite_folder + 'run.png')
        self.spritesheet_marche = pygame.image.load(self.sprite_folder + 'walk.png')
        self.spritesheet_attaque = pygame.image.load(self.sprite_folder + 'attaque.png')
        self.spritesheet_mort = pygame.image.load(self.sprite_folder + 'hurt.png')
        self.spritesheet_attente = pygame.image.load(self.sprite_folder + 'hurt.png')

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
        self.cooldown_max = int(60 / self.vitesse_recup)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Chargement  effets sonores
        self.son_attaque = pygame.mixer.Sound("sons/attaque.mp3")
        self.son_degats = pygame.mixer.Sound("sons/degats.mp3")
        self.son_level_up = pygame.mixer.Sound("sons/level_up.mp3")
        self.son_attaque.set_volume(0.7)
        self.son_degats.set_volume(0.7)
        self.son_level_up.set_volume(1.0)



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
                return None
        else:
            spritesheet = self.spritesheet_course if en_course else self.spritesheet_marche

        # Vérification si la spritesheet a bien été assignée
        if spritesheet is None:
            print("Erreur : spritesheet non chargée ou non définie !")
            return None

        # Extraction de la frame et redimensionnement
        frame_image = spritesheet.subsurface(pygame.Rect(x, y, self.largeur_frame, self.hauteur_frame))
        return pygame.transform.scale(frame_image, (self.largeur_frame * self.facteur_echelle, self.hauteur_frame * self.facteur_echelle))

    def obtenir_frames_attaque(self):
        """Nombre de frames pour l'attaque"""
        if self.type_attaque == 3:
            return 8
        return 8

    def commencer_mouvement(self, direction, en_course):
        """Début du mouvement"""
        if not self.en_attaque:
            self.en_mouvement = True
            self.en_course = en_course
            self.direction = direction

    def arreter_mouvement(self):
        """Arrêt du mouvement"""
        if not self.en_attaque:
            self.en_mouvement = False
            self.sprite_actuel = 0

    def commencer_attaque(self, type_attaque, ennemis):
        """attaque du joueur"""
        if self.timer_attaque <= 0:
            self.en_attaque = True
            self.son_attaque.play()
            self.type_attaque = type_attaque
            self.sprite_actuel = 0
            self.timer_attaque = self.cooldown_max
            range_attaque = max( 50, self.distance_attaque)
            centre_x = self.rect.centerx
            centre_y = self.rect.centery

            self.zone_attaque = (centre_x, centre_y, range_attaque)
            for ennemi in ennemis:
                distance = ((ennemi.rect.centerx - centre_x) ** 2 + (ennemi.rect.centery - centre_y) ** 2) ** 0.5
                if distance <= range_attaque:
                    ennemi.vie -= self.degats
                    self.degats_affiches.append([ennemi.rect.x, ennemi.rect.y, str(self.degats), 60])
            if boss and boss_spawned:
                distance_boss = ((boss.rect.centerx - centre_x) ** 2 + (boss.rect.centery - centre_y) ** 2) ** 0.5
                if distance_boss <= range_attaque:
                    boss.subir_degats(self.degats)
                    # Appliquer le vol de vie
                    soin = self.degats * (self.vol_vie / 100)
                    self.vie = min(self.vie + soin, 200)
                    # # Appliquer les dégâts sur la durée (DoT)
                    # ennemi.dot_damage = self.degats_dot
                    # ennemi.dot_timer = 300  # 5 secondes à 60 FPS
                    # if ennemi not in ennemis_dot:
                    #     ennemis_dot.append(ennemi)

                    if ennemi.vie <= 0:
                        ennemis.remove(ennemi)
                        self.ajouter_xp(10)



    def afficher_zone_attaque(self, surface, decalage_camera_x, decalage_camera_y):
        """affiche zone degats"""
        if self.timer_attaque >= int(60 / self.vitesse_recup /1.5) and self.zone_attaque:
            centre_x = self.rect.x + self.rect.width // 2 - decalage_camera_x
            centre_y = self.rect.y + self.rect.height // 2 - decalage_camera_y
            pygame.draw.circle(surface, (255, 0, 0), (centre_x, centre_y), self.distance_attaque, 2)
            self.timer_attaque -= 1

    def ajouter_xp(self, xp_gagne):
        """ajoute xp"""
        self.xp += xp_gagne
        if self.xp >= self.xp_prochain_niveau:
            self.niveau += 1
            self.xp -= self.xp_prochain_niveau
            self.xp_prochain_niveau *= 2
            self.son_level_up.play()  # 🎵 Joue le son de level-up !
            print(f"Niveau augmenté ! Niveau actuel : {self.niveau}")
            afficher_choix_niveau(fenetre, self)


    def afficher_xp(self, surface):
        """affiche xp"""
        font = pygame.font.Font(None, 36)
        texte_xp = font.render(f"XP: {self.xp} / {self.xp_prochain_niveau}", True, (255, 255, 255))
        texte_niveau = font.render(f"Niveau: {self.niveau}", True, (255, 255, 255))
        texte_or = font.render(f"Or: {self.gold}", True, (255, 255, 255))
        surface.blit(texte_xp, (20, 50))
        surface.blit(texte_niveau, (20, 80))
        surface.blit(texte_or, (20, 110))

        if self.en_attaque:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= self.obtenir_frames_attaque():
                self.en_attaque = False
                self.sprite_actuel = 0
        elif self.en_mouvement:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= 8:
                self.sprite_actuel = 0

        nouvelle_image = self.obtenir_frame(int(self.sprite_actuel), self.direction, self.en_course, self.en_attaque)
        if nouvelle_image:
            self.image = nouvelle_image
            self.rect.width = self.image.get_width()
            self.rect.height = self.image.get_height()
        else:
            self.image = self.obtenir_frame(0, self.direction, False)

    def mettre_a_jour(self,):
        """Mise à jour de l'animation"""
        if self.en_attaque:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= self.obtenir_frames_attaque():
                self.en_attaque = False
                self.sprite_actuel = 0
        elif self.en_mouvement:
            self.sprite_actuel += 0.2
            if self.sprite_actuel >= 8:
                self.sprite_actuel = 0

        nouvelle_image = self.obtenir_frame(int(self.sprite_actuel), self.direction, self.en_course, self.en_attaque)
        if nouvelle_image:
            self.image = nouvelle_image
            self.rect.width = self.image.get_width()
            self.rect.height = self.image.get_height()
        else:
            self.image = self.obtenir_frame(0, self.direction, False)

        if self.timer_attaque > 0:
            self.timer_attaque -= 1

        # ennemis_dot[:] = [ennemi for ennemi in ennemis_dot if ennemi.dot_timer > 0]
        # for ennemi in ennemis_dot:
        #     if ennemi.dot_timer % 60 == 0:  # Appliquer les dégâts chaque seconde
        #         ennemi.vie -= ennemi.dot_damage
        #     ennemi.dot_timer -= 1


class Orc(Ennemi, pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        Ennemi.__init__(self, type_ennemi="Orc", vie=100, degats=1, distance_attaque=1, vitesse_deplacement=VITESSE_MARCHE, x=pos_x, y=pos_y)
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet_course = pygame.image.load('sprites/orc/orc_run.png')
        self.largeur_frame = self.spritesheet_course.get_width() // 8
        self.hauteur_frame = self.spritesheet_course.get_height() // 4
        self.sprite_actuel = 0
        self.direction = "bas"
        self.image = self.obtenir_frame(0, self.direction, True)
        self.rect = pygame.Rect(pos_x, pos_y, self.largeur_frame, self.hauteur_frame)
        self.derniere_attaque = 0

    def obtenir_frame(self, frame, direction, en_course):
        """image selon déplacement"""
        directions = {"haut": 0, "gauche": 1, "bas": 2, "droite": 3}
        ligne = directions.get(direction, 2)
        x = int(frame) * self.largeur_frame
        y = ligne * self.hauteur_frame

        frame_image = self.spritesheet_course.subsurface(pygame.Rect(x, y, self.largeur_frame, self.hauteur_frame))
        return pygame.transform.scale(frame_image, (self.largeur_frame, self.hauteur_frame))

    def attaquer_joueur(self, joueur):
        """Inflige des dégâts au joueur s'il est touché"""
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - self.derniere_attaque > 1000:
            joueur.vie -= self.degats
            joueur.son_degats.play()
            self.derniere_attaque = temps_actuel

    def mettre_a_jour(self, joueur):
        """met a jour"""
        diff_x = joueur.rect.centerx - self.rect.centerx
        diff_y = joueur.rect.centery - self.rect.centery

        if abs(diff_x) > abs(diff_y):
            self.direction = "droite" if diff_x > 0 else "gauche"
        else:
            self.direction = "bas" if diff_y > 0 else "haut"
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

        if self.rect.colliderect(joueur.rect):
            self.attaquer_joueur(joueur)

class BossOrc(Ennemi, pygame.sprite.Sprite):
    def __init__(self, x, y):
        Ennemi.__init__(self, type_ennemi="BossOrc", vie=1000, degats=10, distance_attaque=3, vitesse_deplacement=VITESSE_MARCHE * 0.8, x=x, y=y)
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet_course = pygame.image.load('sprites/orc/orc_run.png')
        self.largeur_frame = (self.spritesheet_course.get_width() // 8) * 2
        self.hauteur_frame = (self.spritesheet_course.get_height() // 4) * 2
        self.sprite_actuel = 0
        self.direction = "bas"
        self.image = self.obtenir_frame(0, self.direction, True)
        self.rect = pygame.Rect(x, y, self.largeur_frame, self.hauteur_frame)
        self.derniere_attaque = 0

    def subir_degats(self, degats):
        """Le boss subit des dégâts lorsqu'il est attaqué"""
        self.vie -= degats
        if self.vie <= 0:
            print("Le boss est vaincu !")
            return True
        return False

    def obtenir_frame(self, frame, direction, en_course):
        """image selon déplacement"""

        directions = {"haut": 0, "gauche": 1, "bas": 2, "droite": 3}
        ligne = directions.get(direction, 2)
        x = int(frame) * self.largeur_frame // 2
        y = ligne * self.hauteur_frame // 2

        frame_image = self.spritesheet_course.subsurface(pygame.Rect(x, y, self.largeur_frame // 2, self.hauteur_frame // 2))
        return pygame.transform.scale(frame_image, (self.largeur_frame, self.hauteur_frame))
    def attaquer_joueur(self, joueur):
        """Inflige des dégâts au joueur s'il est touché"""
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - self.derniere_attaque > 1000:
            joueur.vie -= self.degats
            self.derniere_attaque = temps_actuel

    def mettre_a_jour(self, joueur):
        """met a jour"""
        diff_x = joueur.rect.centerx - self.rect.centerx
        diff_y = joueur.rect.centery - self.rect.centery

        if abs(diff_x) > abs(diff_y):
            self.direction = "droite" if diff_x > 0 else "gauche"
        else:
            self.direction = "bas" if diff_y > 0 else "haut"

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
        nouvelle_ligne = int(centre_y // TAILLE_TUILE)
        nouvelle_colonne = int(centre_x // TAILLE_TUILE)

        if 0 <= nouvelle_ligne < lignes and carte[nouvelle_ligne][self.rect.x // TAILLE_TUILE] in map(str, range(25, 39)):
            self.rect.y += deplacement_y
        if 0 <= nouvelle_colonne < colonnes and carte[self.rect.y // TAILLE_TUILE][nouvelle_colonne] in map(str, range(25, 39)):
            self.rect.x += deplacement_x

        self.sprite_actuel += 0.2
        if self.sprite_actuel >= 8:
            self.sprite_actuel = 0

        self.image = self.obtenir_frame(int(self.sprite_actuel), self.direction, en_course=True)

        if self.rect.colliderect(joueur.rect):
            self.attaquer_joueur(joueur)

class ObjetCle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("sprites/cle.png")
        self.rect = self.image.get_rect(topleft=(x, y))

    def ramasser(self, joueur):
        return self.rect.colliderect(joueur.rect)

#==================================================
#--------------------FONCTIONS---------------------
#==================================================
def fondu_entree(surface, duree=60):
    """ Effet de fondu à l'entrée sur la surface de jeu """
    surface_fondu = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    surface_fondu.fill((0, 0, 0))

    for alpha in range(255, -1, -5):
        surface_fondu.set_alpha(alpha)
        surface.fill((0, 0, 0))
        surface.blit(surface_fondu, (0, 0))
        pygame.display.flip()
        pygame.time.delay(duree // 30)

def charger_et_redimensionner_image(chemin):
    """Chargement et redimensionnement des images importées"""
    try:
        return pygame.transform.scale(pygame.image.load(chemin).convert(), (TAILLE_TUILE, TAILLE_TUILE))
    except pygame.error as e:
        print(f"Erreur lors du chargement de l'image {chemin}: {e}")
        return None

# Liste des chemins pour une modification facilitée
chemin = "images/cornes_tiles_x80/Tileset/Exports"
corners = ["Exterior_Corners", "Exterior_Corners_v2", "Interior_Corners", "Interior_Corners_v2"]
walls = ["Walls", "Walls_v2"]
paths = ["path_walls", "path_interior_corners", "path_exteriors_corners"]
diagonals = ["diagonals"]
backgrounds = ["Backgrounds"]
# Dictionnaire pour associer chaque caractère à son image
dictionnaire_images = {
    0 : charger_et_redimensionner_image(f'{chemin}/{corners[0]}/top_left_exterior_corner.png'),
    1 : charger_et_redimensionner_image(f'{chemin}/{corners[0]}/top_right_exterior_corner.png'),
    2 : charger_et_redimensionner_image(f'{chemin}/{corners[2]}/top_left_interior_corner.png'),
    3 : charger_et_redimensionner_image(f'{chemin}/{corners[2]}/top_right_interior_corner.png'),
    4 : charger_et_redimensionner_image(f'{chemin}/{walls[0]}/right.png'),
    5 : charger_et_redimensionner_image(f'{chemin}/{walls[0]}/bottom.png'),
    6 : charger_et_redimensionner_image(f'{chemin}/{corners[0]}/bottom_left_exterior_corner.png'),
    7 : charger_et_redimensionner_image(f'{chemin}/{corners[0]}/bottom_right_exterior_corner.png'),
    8 : charger_et_redimensionner_image(f'{chemin}/{corners[2]}/bottom_left_interior_corner.png'),
    9 : charger_et_redimensionner_image(f'{chemin}/{corners[2]}/bottom_right_interior_corner.png'),
    10: charger_et_redimensionner_image(f'{chemin}/{walls[0]}/top.png'),
    11: charger_et_redimensionner_image(f'{chemin}/{walls[0]}/left.png'),
    12: charger_et_redimensionner_image(f'{chemin}/{corners[1]}/top_left_exterior_corner.png'),
    13: charger_et_redimensionner_image(f'{chemin}/{corners[1]}/top_right_exterior_corner.png'),
    14: charger_et_redimensionner_image(f'{chemin}/{corners[3]}/top_left_interior_corner.png'),
    15: charger_et_redimensionner_image(f'{chemin}/{corners[3]}/top_right_interior_corner.png'),
    16: charger_et_redimensionner_image(f'{chemin}/{walls[1]}/right.png'),
    17: charger_et_redimensionner_image(f'{chemin}/{walls[1]}/bottom.png'),
    18: charger_et_redimensionner_image(f'{chemin}/{corners[1]}/bottom_left_exterior_corner.png'),
    19: charger_et_redimensionner_image(f'{chemin}/{corners[1]}/bottom_right_exterior_corner.png'),
    20: charger_et_redimensionner_image(f'{chemin}/{corners[3]}/bottom_left_interior_corner.png'),
    21: charger_et_redimensionner_image(f'{chemin}/{corners[3]}/bottom_right_interior_corner.png'),
    22: charger_et_redimensionner_image(f'{chemin}/{walls[1]}/top.png'),
    23: charger_et_redimensionner_image(f'{chemin}/{walls[1]}/left.png'),
    24: charger_et_redimensionner_image(f'{chemin}/{paths[0]}/path_left_wall.png'),
    25: charger_et_redimensionner_image(f'{chemin}/{paths[0]}/path_top_wall.png'),
    26: charger_et_redimensionner_image(f'{chemin}/{paths[1]}/path_top_left_corner.png'),
    27: charger_et_redimensionner_image(f'{chemin}/{paths[1]}/path_top_right_corner.png'),
    28: charger_et_redimensionner_image(f'{chemin}/{paths[2]}/path_top_left_corner.png'),
    29: charger_et_redimensionner_image(f'{chemin}/{paths[2]}/path_top_right_corner.png'),
    30: charger_et_redimensionner_image(f'{chemin}/{paths[0]}/path_bottom_wall.png'),
    31: charger_et_redimensionner_image(f'{chemin}/{paths[0]}/path_right_wall.png'),
    32: charger_et_redimensionner_image(f'{chemin}/{paths[1]}/path_bottom_left_corner.png'),
    33: charger_et_redimensionner_image(f'{chemin}/{paths[1]}/path_bottom_right_corner.png'),
    34: charger_et_redimensionner_image(f'{chemin}/{paths[2]}/path_bottom_left_corner.png'),
    35: charger_et_redimensionner_image(f'{chemin}/{paths[2]}/path_bottom_right_corner.png'),
    36: charger_et_redimensionner_image(f'{chemin}/{backgrounds[0]}/path_bg_color.png'),
    37: charger_et_redimensionner_image(f'{chemin}/{backgrounds[0]}/exterior_background.png'),
    38: charger_et_redimensionner_image(f'{chemin}/{backgrounds[0]}/interior_background.png'),
    40: charger_et_redimensionner_image(f'{chemin}/{diagonals[0]}/diagonal_top-left_bottom-right.png'),
    41: charger_et_redimensionner_image(f'{chemin}/{diagonals[0]}/diagonal_bottom-left_top-right.png'),

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

fichier_matrice = 'map1.csv'
carte = charger_matrice_depuis_csv(fichier_matrice)

# Dimensions de la carte
lignes = len(carte)
colonnes = len(carte[0])
largeur_matrice = colonnes * TAILLE_TUILE
hauteur_matrice = lignes * TAILLE_TUILE

def generer_orcs(nombre_orcs, joueur, vie_orc=100):
    """Génère des orcs uniquement sur les cases 36 et 38 de la carte."""
    orcs = []
    for _ in range(nombre_orcs):
        while True:
            spawn_x = random.randint(0, colonnes - 1) * TAILLE_TUILE
            spawn_y = random.randint(0, lignes - 1) * TAILLE_TUILE

            ligne = spawn_y // TAILLE_TUILE
            colonne = spawn_x // TAILLE_TUILE

            if carte[ligne][colonne] in ["36", "38"]:
                orc = Orc(spawn_x, spawn_y)
                orc.vie = vie_orc
                orcs.append(orc)
                #print(f"Orc généré à ({spawn_x}, {spawn_y}) avec {vie_orc} HP")
                break

    return orcs

def afficher_barre_vie(surface, x, y, largeur, hauteur, vie_actuelle, vie_max, couleur_fond, couleur_barre):
    """crée barre vie"""

    pygame.draw.rect(surface, couleur_fond, (x, y, largeur, hauteur))
    largeur_barre = int((vie_actuelle / vie_max) * largeur)
    pygame.draw.rect(surface, couleur_barre, (x, y, largeur_barre, hauteur))

position_joueur_x = LARGEUR_FENETRE // 2
position_joueur_y = HAUTEUR_FENETRE // 2

def afficher_barre_cooldown(surface, x, y, largeur, hauteur, cooldown_actuel, cooldown_max):
    """affiche attente avec attaque"""
    pygame.draw.rect(surface, (100, 100, 100), (x, y, largeur, hauteur))  # Fond gris
    largeur_barre = int((cooldown_max - cooldown_actuel) / cooldown_max * largeur)
    pygame.draw.rect(surface, (200, 200, 200), (x, y, largeur_barre, hauteur))

objets_cles = []

def generer_objets_cles():
    """genere les clés"""
    global objets_cles
    objets_cles = []
    for _ in range(3):
        while True:
            x = random.randint(0, colonnes - 1) * TAILLE_TUILE
            y = random.randint(0, lignes - 1) * TAILLE_TUILE
            ligne = y // TAILLE_TUILE
            colonne = x // TAILLE_TUILE
            if carte[ligne][colonne] in ["36","38"]:
                objets_cles.append(ObjetCle(x, y))
                break

generer_objets_cles()

def afficher_game_over(fenetre):
    """aaffiche ecran de fin + relance"""
    pygame.mixer.music.stop()
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

def afficher_choix_niveau(fenetre, joueur):
    """ Affiche trois choix d'amélioration lors d'une montée de niveau avec interface graphique """
    choix_possibles = [
        ("Augmentation de vie", "+50 points de vie", lambda: setattr(joueur, 'vie', joueur.vie + 50)),
        ("Régénération de vie", "régenère 30HP", lambda: setattr(joueur, 'vie', min(joueur.vie + 30, 200))),
        ("Dégâts augmentés", "+5 points de dégâts", lambda: setattr(joueur, 'degats', joueur.degats + 5)),
        ("Or supplémentaire", "+100 pièces d'or", lambda: setattr(joueur, 'gold', joueur.gold + 100)),
        ("vitesse supplémentaire", "+5  vitesse augmentée ", lambda: setattr(joueur, 'vitesse_deplacement', joueur.vitesse_deplacement + 5)),
        ("Surprise", "Effet bonus x2 aléatoire", lambda: random.choice([
            setattr(joueur, 'vie', joueur.vie + 100),
            setattr(joueur, 'degats', joueur.degats + 10),
            setattr(joueur, 'gold', joueur.gold + 200)
        ]))
    ]

    choix = random.sample(choix_possibles, 3)

    # Fond semi-transparent
    surface_transparente = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.SRCALPHA)
    surface_transparente.fill((0, 0, 0, 180))
    fenetre.blit(surface_transparente, (0, 0))

    # Cadre principal plus grand
    cadre = pygame.Rect(LARGEUR_FENETRE // 2 - 500, HAUTEUR_FENETRE // 2 - 250, 1000, 500)
    pygame.draw.rect(fenetre, (0, 0, 0), cadre)
    pygame.draw.rect(fenetre, (255, 255, 255), cadre, 5)

    # Dessiner chaque choix en colonne
    boutons = []
    font = pygame.font.Font(None, 25)
    for i, (titre, description, _) in enumerate(choix):
        x = LARGEUR_FENETRE // 2 - 450 + (i * 350)
        y = HAUTEUR_FENETRE // 2 - 100
        bouton = pygame.Rect(x, y, 200, 100)

        pygame.draw.rect(fenetre, (100, 100, 100), bouton)
        pygame.draw.rect(fenetre, (255, 255, 255), bouton, 3)

        texte_titre = font.render(titre, True, (255, 255, 255))
        texte_desc = font.render(description, True, (200, 200, 200))

        fenetre.blit(texte_titre, (x + 10, y + 10))
        fenetre.blit(texte_desc, (x + 20, y + 80))

        boutons.append((bouton, choix[i][2]))

    pygame.display.flip()

    choix_effectue = False
    while not choix_effectue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for bouton, action in boutons:
                    if bouton.collidepoint(event.pos):
                        action()
                        choix_effectue = True
                        break

boss_a_eu_lieu=0

def verifier_ramassage(joueur):
    """verifie ramassage des clés"""
    global boss_a_eu_lieu
    global boss_spawned, boss
    for objet in objets_cles[:]:
        if objet.ramasser(joueur):
            objets_cles.remove(objet)

    if not objets_cles and not boss_spawned and boss_a_eu_lieu==0:
        boss_a_eu_lieu +=1
        spawn_boss()

def spawn_boss():
    """fait spawn le boss"""
    global boss_spawned, boss
    boss_spawned = True
    boss = BossOrc(largeur_matrice // 2, hauteur_matrice // 2)
    print("Le boss est apparu !")

def afficher_menu_achat(fenetre, joueur):
    """ Affiche le menu d'achat pour acheter des bonus """
    choix_bonus = [
        ("Amélioration de l'épée", "+10 dégâts", 50, lambda: setattr(joueur, 'degats', joueur.degats + 10)),
        ("Vitesse d'attaque", "Attaque + rapide", 75, lambda: setattr(joueur, 'vitesse_recup', joueur.vitesse_recup * 0.9)),
        ("Vol de vie", "+10% soin par attaque", 100, lambda: setattr(joueur, 'vol_vie', joueur.vol_vie + 2 )),
        ("Range d'attaque", "+20% portée", 80, lambda: setattr(joueur, 'distance_attaque', joueur.distance_attaque * 1.2)),
        ("Dégâts sur la durée", "Brûlure 5s", 120, lambda: setattr(joueur, 'degats_dot',joueur.dot + 5)),
    ]

    surface_transparente = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.SRCALPHA)
    surface_transparente.fill((0, 0, 0, 180))
    fenetre.blit(surface_transparente, (0, 0))

    cadre = pygame.Rect(600, 300, 700, 400)
    pygame.draw.rect(fenetre, (0, 0, 0), cadre)
    pygame.draw.rect(fenetre, (255, 255, 255), cadre, 5)

    font = pygame.font.Font(None, 35)
    boutons = []
    message_erreur = ""
    message_timer = 0

    for i, (nom, desc, prix, effet) in enumerate(choix_bonus):
        bouton = pygame.Rect(650, 350 + i * 60, 600, 50)
        pygame.draw.rect(fenetre, (100, 100, 100), bouton)
        pygame.draw.rect(fenetre, (255, 255, 255), bouton, 2)

        texte = font.render(f"{nom} ({prix} or)  {desc}", True, (255, 255, 255))
        fenetre.blit(texte, (660, 360 + i * 60))

        boutons.append((bouton, prix, effet))

    pygame.display.flip()

    menu_ouvert = True
    while menu_ouvert:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for bouton, prix, effet in boutons:
                    if bouton.collidepoint(event.pos):
                        if joueur.gold >= prix:
                            joueur.gold -= prix
                            effet()
                            menu_ouvert = False
                        else:
                            message_erreur = "Pas assez d'or !"
                            message_timer = pygame.time.get_ticks()
                        break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu_ouvert = False

        if message_erreur and pygame.time.get_ticks() - message_timer < 3000:
            texte_erreur = font.render(message_erreur, True, (255, 0, 0))
            fenetre.blit(texte_erreur, (850, 660))
            pygame.display.flip()

def lancer_jeu(classe):
    """lance le jeu + verif continue"""
    global boss_spawned,boss
    en_cours = True
    horloge = pygame.time.Clock()
    fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.RESIZABLE)

    pygame.mixer.init()
    pygame.mixer.music.load("aventure.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


    surface_fondu = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    surface_fondu.fill((0, 0, 0))
    alpha_fondu = 255

    joueur = Joueur(classe, largeur_matrice // 2, hauteur_matrice // 2)

    list_orcs = generer_orcs(15, joueur)


    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_2:
                    afficher_menu_achat(fenetre, joueur)
            elif evenement.type == pygame.KEYUP:
                if evenement.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_d, pygame.K_q, pygame.K_z, pygame.K_s]:
                    joueur.arreter_mouvement()
            elif evenement.type == pygame.MOUSEBUTTONDOWN:
                        if evenement.button == 1:
                            joueur.commencer_attaque(3, list_orcs)
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


        vie_orc = 100
        list_orcs = [orc for orc in list_orcs if orc.vie > 0]

        if len(list_orcs) < 15:
            nouveaux_orcs = generer_orcs(15 - len(list_orcs), joueur, vie_orc)
            list_orcs.extend(nouveaux_orcs)
            vie_orc += 10
        for orc in list_orcs:
            orc.mettre_a_jour(joueur)
            x = orc.rect.x - decalage_camera_x
            y = orc.rect.y - decalage_camera_y
            if 0 <= x < LARGEUR_FENETRE and 0 <= y < HAUTEUR_FENETRE:
                fenetre.blit(orc.image, (x, y))
                afficher_barre_vie(fenetre, x, y - 10, 40, 5, orc.vie, 100, (255, 0, 0), (0, 255, 0))

        for objet in objets_cles:
            x = objet.rect.x - decalage_camera_x
            y = objet.rect.y - decalage_camera_y
            if 0 <= x < LARGEUR_FENETRE and 0 <= y < HAUTEUR_FENETRE:
                fenetre.blit(objet.image, (x, y))
        verifier_ramassage(joueur)
        if boss_spawned and boss:
            boss.mettre_a_jour(joueur)
            x = boss.rect.x - decalage_camera_x
            y = boss.rect.y - decalage_camera_y
            if 0 <= x < LARGEUR_FENETRE and 0 <= y < HAUTEUR_FENETRE:
                fenetre.blit(boss.image, (x, y))
                afficher_barre_vie(fenetre, x, y - 20, 100, 10, boss.vie, 1000, (255, 0, 0), (0, 255, 0))
        #affiche les dégats de l'attaque
        joueur.afficher_zone_attaque(fenetre, decalage_camera_x, decalage_camera_y)
        # Affichage de la barre de vie du joueur
        afficher_barre_vie(fenetre, 20, 20, 200, 20, joueur.vie, joueur.vie_max, (255, 0, 0), (0, 255, 0))
        joueur.afficher_xp(fenetre)
        afficher_barre_cooldown(fenetre, 850, HAUTEUR_FENETRE - 40, 200, 10, joueur.timer_attaque, joueur.cooldown_max)
        if boss_spawned == True and boss.vie <= 0:
                boss_spawned = False
                boss = None
                #changement de niveau ici
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
    lancer_jeu("TANK")#changer dirrectement ici avec les différentes classes pour test