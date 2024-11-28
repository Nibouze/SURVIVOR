class Personnage:
    #caca
    def __init__(self, nom, vie, armure, distance_attaque, vitesse_recup, vitesse_deplacement, x, y, argent=0, xp=0):
        self.nom = nom
        self.vie = vie
        self.armure = armure
        self.distance_attaque = distance_attaque
        self.vitesse_recup = vitesse_recup
        self.vitesse_deplacement = vitesse_deplacement
        self.argent = argent
        self.xp = xp
        self.niveau = 1
        self.arme = None
        self.x = x  # Coordonnée x
        self.y = y  # Coordonnée y

    def deplacer(self, dx, dy):
        """Déplace le personnage sur la carte."""
        self.x += dx * self.vitesse_deplacement
        self.y += dy * self.vitesse_deplacement
        print(f"{self.nom} est maintenant à ({self.x}, {self.y}).")

    def monter_de_niveau(self):
        self.niveau += 1
        self.xp = 0
        print(f"{self.nom} est passé au niveau {self.niveau} !")

    def equiper_arme(self, arme):
        self.arme = arme
        print(f"{self.nom} a équipé {arme.nom}.")

class Ennemi:
    def __init__(self, type_ennemi, vie, armure, degats, distance_attaque, vitesse_deplacement, x, y):
        self.type_ennemi = type_ennemi
        self.vie = vie
        self.armure = armure
        self.degats = degats
        self.distance_attaque = distance_attaque
        self.vitesse_deplacement = vitesse_deplacement
        self.x = x  # Coordonnée x
        self.y = y  # Coordonnée y

    def deplacer(self, dx, dy):
        """Déplace l'ennemi sur la carte."""
        self.x += dx * self.vitesse_deplacement
        self.y += dy * self.vitesse_deplacement
        print(f"L'ennemi {self.type_ennemi} est maintenant à ({self.x}, {self.y}).")

# Sous-classes spécifiques
class TankEnnemi(Ennemi):
    def __init__(self, x, y):
        super().__init__(type_ennemi="Tank", vie=300, armure=200, degats=20, distance_attaque=1, vitesse_deplacement=0.5, x=x, y=y)

class CombattantEnnemi(Ennemi):
    def __init__(self, x, y):
        super().__init__(type_ennemi="Combattant simple", vie=150*coef, armure=100, degats=40, distance_attaque=1.5, vitesse_deplacement=1, x=x, y=y)

class RangeEnnemi(Ennemi):
    def __init__(self, x, y):
        super().__init__(type_ennemi="Range", vie=100, armure=50, degats=60, distance_attaque=5, vitesse_deplacement=1.2, x=x, y=y)

# Sous-classes spécifiques
class Assassin(Personnage):
    def __init__(self, nom, x, y):
        super().__init__(nom, vie=100, armure=50, distance_attaque=2, vitesse_recup=1.5, vitesse_deplacement=2, x=x, y=y)

class Tank(Personnage):
    def __init__(self, nom, x, y):
        super().__init__(nom, vie=200, armure=150, distance_attaque=1, vitesse_recup=1, vitesse_deplacement=0.8, x=x, y=y)

class Combattant(Personnage):
    def __init__(self, nom, x, y):
        super().__init__(nom, vie=150, armure=100, distance_attaque=1.5, vitesse_recup=1.2, vitesse_deplacement=1.5, x=x, y=y)

class Sniper(Personnage):
    def __init__(self, nom, x, y):
        super().__init__(nom, vie=120, armure=60, distance_attaque=5, vitesse_recup=1.8, vitesse_deplacement=1, x=x, y=y)

# Sous-classes spécifiques
class Assassin(Personnage):
    def __init__(self, nom):
        super().__init__(nom, vie=100, armure=50, distance_attaque=2, vitesse_recup=1.5, vitesse_deplacement=2)

class Tank(Personnage):
    def __init__(self, nom):
        super().__init__(nom, vie=200, armure=150, distance_attaque=1, vitesse_recup=1, vitesse_deplacement=0.8)

class Combattant(Personnage):
    def __init__(self, nom):
        super().__init__(nom, vie=150, armure=100, distance_attaque=1.5, vitesse_recup=1.2, vitesse_deplacement=1.5)

class Sniper(Personnage):
    def __init__(self, nom):
        super().__init__(nom, vie=120, armure=60, distance_attaque=5, vitesse_recup=1.8, vitesse_deplacement=1)

class Arme:
    def __init__(self, nom, degats, niveau, portee, vitesse_attaque, type_degats, chance_critique, degats_critiques):
        self.nom = nom
        self.degats = degats
        self.niveau = niveau
        self.portee = portee
        self.vitesse_attaque = vitesse_attaque
        self.type_degats = type_degats
        self.chance_critique = chance_critique
        self.degats_critiques = degats_critiques

    def ameliorer(self):
        self.niveau += 1
        self.degats += 5  # Par exemple
        print(f"L'arme {self.nom} a été améliorée au niveau {self.niveau} !")

# Sous-classes d'armes
class Dague(Arme):
    def __init__(self):
        super().__init__("Dague", degats=20, niveau=1, portee=1, vitesse_attaque=2, type_degats="unique", chance_critique=0.3, degats_critiques=50)

class Sniper(Arme):
    def __init__(self):
        super().__init__("Sniper", degats=50, niveau=1, portee=10, vitesse_attaque=0.8, type_degats="unique", chance_critique=0.4, degats_critiques=100)

class Epee(Arme):
    def __init__(self):
        super().__init__("Épée", degats=30, niveau=1, portee=2, vitesse_attaque=1.2, type_degats="unique", chance_critique=0.2, degats_critiques=60)

class Bouclier(Arme):
    def __init__(self):
        super().__init__("Bouclier", degats=10, niveau=1, portee=1, vitesse_attaque=1, type_degats="zone", chance_critique=0.1, degats_critiques=20)
