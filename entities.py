import pygame
import os

pygame.font.init()
pygame.mixer.init()


# Crea dinamicamente un'istanza dell'oggetto in base al nome della classe passato
# Es. get_class("Worker", 100, Color.BLACK) -> crea un oggetto di tipo Worker in posizione 100 di colore nero
def get_class(name: str, *args):
    klass = globals()[name]
    return klass(*args)


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)


# Contiene le variabili relative al gioco (Environment)
class Env:
    WIDTH = 900
    HEIGHT = 500
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    FPS = 60
    DEFAULT_DISTANCE = 20
    FONT = pygame.font.SysFont('calibri', 10)
    PAUSE_FONT = pygame.font.SysFont('calibri', 50)


# Definisce gli eventi
class Event:
    WORKER_EXTRACT = pygame.USEREVENT + 1
    WORKER_RESTORE = pygame.USEREVENT + 2

    TROOP_ATTACK_HIT = pygame.USEREVENT + 3
    TROOP_ATTACK_TOWER = pygame.USEREVENT + 4
    TOWER_ATTACK_TROOP = pygame.USEREVENT + 5

    BULLET_HIT = pygame.USEREVENT + 6
    BULLET_HIT_TOWER = pygame.USEREVENT + 7

    def __init__(self, event: int, obj):
        self.event = event
        self.obj = obj

    def as_list(self):
        return [self.WORKER_EXTRACT, self.WORKER_RESTORE, self.TROOP_ATTACK_HIT, self.TROOP_ATTACK_TOWER,
                self.TOWER_ATTACK_TROOP, self.BULLET_HIT, self.BULLET_HIT_TOWER]


# Definisce lo sfondo
class Background:
    COLOR = Color.WHITE
    IMAGE = Color.WHITE

    def __init__(self):
        self.background = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'background.jpg')),
                                                 (Env.WIDTH, Env.HEIGHT))

    def draw(self):
        Env.WIN.blit(self.background, (0, 0))


# Definisce una entità generica di gioco (hitbox)
class Box:
    def __init__(self, x, y, width, height, color=Color.BLACK, image=None):
        self.color = color
        self.hitbox = pygame.Rect(x, y, width, height)
        self.image = image

    def draw(self):
        if self.image is not None:
            Env.WIN.blit(self.image, (self.hitbox.x, self.hitbox.y))

    def rect(self):
        return self.hitbox

    def collide(self, obj):
        return self.hitbox.colliderect(obj.hitbox)


# Definisce il terreno di gioco
class Ground:
    HEIGHT = 20
    X = 0
    Y = Env.HEIGHT - HEIGHT
    COLOR = Color.GREEN

    def __init__(self):
        self.hitbox = pygame.Rect(self.X, self.Y, Env.WIDTH, self.HEIGHT)

    def draw(self):
        #Env.WIN.blit(IMAGE, HITBOX.x, HITBOX.y)
        #pygame.draw.rect(Env.WIN, self.hitbox)
        #pygame.draw.rect(Env.WIN, [255, 0, 0], [50, 50, 90, 180], 1)
        pass

    def collide(self, obj):
        return self.hitbox.colliderect(obj.hitbox)


# Definisce la miniera
class Mine(Box):
    WIDTH = 25
    HEIGHT = 25
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'mine.png')), (WIDTH*1.5, HEIGHT*1.5))

    def __init__(self, x: int, color: tuple):
        super().__init__(x, get_y(self.HEIGHT), self.WIDTH, self.HEIGHT, color, self.IMAGE)


# Definisce la caserma
class Barrack(Box):
    WIDTH = 35
    HEIGHT = 35
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'barrack.png')), (WIDTH*1.3, HEIGHT*1.3))

    def __init__(self, x: int, color: tuple):
        super().__init__(x, get_y(self.HEIGHT), self.WIDTH, self.HEIGHT, color, self.IMAGE)


# Definisce la torre
class Tower(Box):
    RANGE = 350
    WIDTH = 50
    HEIGHT = 150
    MAX_HP = 100
    DAMAGE = 5
    ACTION_TURNS = 75
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'tower.png')), (WIDTH*1.1, HEIGHT*1.1))

    def __init__(self, x: int, color: tuple):
        super().__init__(x, get_y(self.HEIGHT), self.WIDTH, self.HEIGHT, color, self.IMAGE)
        self.hp = 100
        self.bullets = []
        self.action_turn = self.ACTION_TURNS

    def collide(self, obj):
        return self.hitbox.x < obj.hitbox.x < self.hitbox.x + Tower.RANGE or obj.hitbox.x > (760 - Tower.RANGE)

    def attack(self, direction):
        if self.action_turn == self.ACTION_TURNS:
            self.bullets.append(Bullet(self.hitbox.x, self.hitbox.y, self.DAMAGE, Bullet.DEFAULT_SPEED,
                                       direction, self.color))
            self.action_turn = 0
            return True
        else:
            self.action_turn += 1
            return False

    def draw(self):
        super(Tower, self).draw()
        for bullet in self.bullets:
            bullet.draw()


# Restituisce la coordinata Y relativa all'altezza dell'entità passata
def get_y(height):
    return Ground.Y - height


# Restituisce la coordinata X relativa al tipo di unità e al team di appartenenza
def get_x(unit: str, team: int):
    if team == Team.BLACK:
        if unit == Mine.__name__:
            return Env.DEFAULT_DISTANCE
        if unit == Barrack.__name__ or unit in Team.Unit.as_list():
            return Env.DEFAULT_DISTANCE * 2 + Mine.WIDTH
        if unit == Tower.__name__:
            return Env.DEFAULT_DISTANCE * 3 + Mine.WIDTH + Barrack.WIDTH
    else:
        if unit == Mine.__name__:
            return Env.WIDTH - (Mine.WIDTH + Env.DEFAULT_DISTANCE)
        if unit == Barrack.__name__ or unit in Team.Unit.as_list():
            return Env.WIDTH - (Mine.WIDTH + Barrack.WIDTH + Env.DEFAULT_DISTANCE * 2)
        if unit == Tower.__name__:
            return Env.WIDTH - (Mine.WIDTH + Barrack.WIDTH + Tower.WIDTH + Env.DEFAULT_DISTANCE * 3)


# Definisce una truppa generica
class Troop(Box):
    WIDTH = 30
    HEIGHT = 30
    SPEED = 0
    TURNS = 0
    ACTION_TURNS = 0

    RIGHT = 1
    LEFT = 2

    class Status:
        TO_TRAIN = 0
        MOVE = 1
        ATTACK = 2
        RESTORE = 3
        EXTRACT = 4

    def __init__(self, x: int, color: tuple, image, direction: int = RIGHT):
        self.moving_turn = 0
        self.action_turn = 0
        self.direction = direction
        self.status = Troop.Status.TO_TRAIN
        super().__init__(x, get_y(self.HEIGHT), self.WIDTH, self.HEIGHT, color, image)

    def move(self):
        if self.moving_turn == self.TURNS:
            if self.direction == self.RIGHT:
                self.hitbox.x += self.SPEED
            else:
                self.hitbox.x -= self.SPEED
            return True
        else:
            self.moving_turn += 1
            return False


class Worker(Troop):
    COST = 50
    SPEED = 1
    TURNS = 100
    ACTION_TURNS = 300  #400
    MAX_EXTRACTIONS = 3
    GOLD_EXTRACTED = 100
    RESTORE_POINTS = 20
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'worker-dx.png')), (Troop.WIDTH, Troop.HEIGHT))

    def __init__(self, x, color):
        if color == Color.RED:
            self.IMAGE = pygame.transform.scale(pygame.image.load(
                os.path.join('Assets', 'worker-sx.png')), (Troop.WIDTH, Troop.HEIGHT))
        super().__init__(x, color, self.IMAGE)
        self.extractions = 0

    def extract(self, team):
        if self.extractions != self.MAX_EXTRACTIONS:
            if self.action_turn == self.ACTION_TURNS:
                team.gold += Worker.GOLD_EXTRACTED
                self.extractions += 1
                self.action_turn = 0
                return True
            else:
                self.action_turn += 1
                return False

    def restore(self, tower: Tower):
        if self.action_turn == self.ACTION_TURNS:
            tower.hp += Worker.RESTORE_POINTS
            self.action_turn = 0
            return True
        else:
            self.action_turn += 1
            return False


class Swordsman(Troop):
    COST = 30
    SPEED = 2
    TURNS = 150
    ACTION_TURNS = 45
    DAMAGE = 5
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'swordsman-dx.png')), (Troop.WIDTH, Troop.HEIGHT))

    def __init__(self, x, color):
        if color == Color.RED:
            self.IMAGE = pygame.transform.scale(pygame.image.load(
                os.path.join('Assets', 'swordsman-sx.png')), (Troop.WIDTH, Troop.HEIGHT))
        super().__init__(x, color, self.IMAGE)
        self.hp = 35

    def attack(self, enemy):
        if self.action_turn == self.ACTION_TURNS:
            enemy.hp -= self.DAMAGE
            self.action_turn = 0
            return True
        else:
            self.action_turn += 1
            return False


class Archer(Troop):
    COST = 40
    SPEED = 2
    TURNS = 250
    ACTION_TURNS = 45
    RANGE = 100
    DAMAGE = 20
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'archer-dx.png')), (Troop.WIDTH, Troop.HEIGHT))

    def __init__(self, x, color):
        if color == Color.RED:
            self.IMAGE = pygame.transform.scale(pygame.image.load(
                os.path.join('Assets', 'archer-sx.png')), (Troop.WIDTH, Troop.HEIGHT))
        super().__init__(x, color, self.IMAGE)
        self.hp = 15
        self.bullets = []
        self.action_turn = self.ACTION_TURNS - 5

    def collide(self, obj: Box):
        x = obj.hitbox.x
        hit_range = list(range(x - Troop.WIDTH, x + Troop.WIDTH))
        return self.hitbox.x + self.RANGE in hit_range or self.hitbox.x - self.RANGE in hit_range

    def attack(self):
        if self.action_turn == self.ACTION_TURNS:
            self.bullets.append(Bullet(self.hitbox.x, self.hitbox.y, self.DAMAGE, Bullet.DEFAULT_SPEED,
                                       self.direction, self.color))
            self.action_turn = 0
            return True
        else:
            self.action_turn += 1
            return False

    def draw(self):
        super(Archer, self).draw()
        for bullet in self.bullets:
            bullet.draw()


# Definisce un proiettile
class Bullet(Box):
    HEIGHT = 10
    WIDTH = 10
    DEFAULT_DAMAGE = 5
    DEFAULT_SPEED = 2
    IMAGE = pygame.transform.scale(pygame.image.load(
        os.path.join('Assets', 'bullet-dx.png')), (WIDTH, HEIGHT))

    def __init__(self, x, y, damage, speed, direction, color):
        if color == Color.RED:
            self.IMAGE = pygame.transform.scale(pygame.image.load(
                os.path.join('Assets', 'bullet-sx.png')), (Troop.WIDTH*0.75, Troop.HEIGHT*0.75))
        super().__init__(x, y, self.WIDTH, self.HEIGHT, color, self.IMAGE)
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.color = color

    def attack(self, enemy):
        enemy.hp -= self.damage

    def move(self):
        if self.direction == Troop.RIGHT:
            self.hitbox.x += self.speed
        else:
            self.hitbox.x -= self.speed
        return True

    def move_diagonal(self):
        if self.direction == Troop.RIGHT:
            self.hitbox.x += self.speed
            self.hitbox.y += self.speed
        else:
            self.hitbox.x -= self.speed
            self.hitbox.y += self.speed
        return True


# Definisce un team/giocatore e gestisce tutti gli stati dei propri oggetti
class Team:
    BLACK = 1
    RED = 2

    BLACK_KEYSET = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f, pygame.K_z]
    RED_KEYSET = [pygame.K_i, pygame.K_o, pygame.K_p, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m]

    # Classe di utilità che contiene i nomi degli edifici
    class Building:
        MINE = Mine.__name__
        BARRACK = Barrack.__name__
        TOWER = Tower.__name__

        @staticmethod
        def as_list():
            return [Team.Building.MINE, Team.Building.BARRACK, Team.Building.TOWER]

        @staticmethod
        def as_dict():
            return dict(zip(range(4), Team.Building.as_list()))

    # Classe di utilità che contiene i nomi delle truppe
    class Unit:
        WORKER = Worker.__name__
        SWORDSMAN = Swordsman.__name__
        ARCHER = Archer.__name__

        @staticmethod
        def as_list():
            return [Team.Unit.WORKER, Team.Unit.SWORDSMAN, Team.Unit.ARCHER]

        @staticmethod
        def as_dict():
            return dict(zip(range(4), Team.Unit.as_list()))

    # Costruttore principale per le dinamiche del gioco, contiene tutte le variabili relativi a un giocatore
    def __init__(self, team: int = 1):
        self.gold = 100
        self.team = team
        self.color = Color.BLACK
        self.buildings = []
        self.workers = []
        self.swordsman = []
        self.archers = []
        self.troops = dict(zip(Team.Unit.as_list(), [self.workers, self.swordsman, self.archers]))
        self.dispatched = []
        self.to_mine = []
        self.logs = []
        self.errors = []
        self.winner = False

        if self.team == Team.BLACK:
            self.keyset = Team.BLACK_KEYSET
            self.color = Color.BLACK
        else:
            self.keyset = Team.RED_KEYSET
            self.color = Color.RED

        mine = self.instantiate(Team.Building.MINE)
        barrack = self.instantiate(Team.Building.BARRACK)
        tower = self.instantiate(Team.Building.TOWER)
        self.buildings = [mine, barrack, tower]

    def log(self, string: str):
        self.logs.append(f"Player {self.team} - " + string)

    def error(self, string: str):
        self.errors.append(f"Player {self.team} - " + string)

    def pop(self, troop: str):
        troops = self.troops[troop]
        if len(troops) != 0:
            popped = troops.pop()
            return popped
        else:
            return False

    # Manda in campo una truppa
    def dispatch(self, unit_name: str, extractor: bool = False):
        popped = self.pop(unit_name)
        if popped:
            if extractor:
                popped.direction = Troop.RIGHT if popped.direction == Troop.LEFT else Troop.LEFT
            popped.status = Troop.Status.MOVE
            self.dispatched.append(popped)
            return popped
        else:
            self.error("No " + unit_name + "available!")

    def instantiate(self, unit: str):
        return get_class(unit, get_x(unit, self.team), self.color)

    # Addestra una truppa
    def train(self, unit_name):
        troop = self.instantiate(unit_name)
        troop.direction = Troop.RIGHT if self.team == Team.BLACK else Troop.LEFT
        if self.gold >= troop.COST:
            self.gold -= troop.COST
            self.troops[unit_name].append(troop)
            self.log(f"Training {troop.__class__.__name__}")
            return troop
        else:
            self.error(f"No resources available for {troop.__class__.__name__}!")

    # Gestisce le azioni dell'utente relative all'addestramento e rilascio di una truppa
    def handle_key(self, key):
        if key in self.keyset:
            # Training
            if key == self.keyset[0]:
                return self.train(Team.Unit.WORKER)
            if key == self.keyset[1]:
                return self.train(Team.Unit.SWORDSMAN)
            if key == self.keyset[2]:
                return self.train(Team.Unit.ARCHER)

            # Troop actions
            if key == self.keyset[3]:   # Worker to mine
                self.dispatch(Team.Unit.WORKER, extractor=True)
            if key == self.keyset[4]:   # Worker to wall
                self.dispatch(Team.Unit.WORKER)
            if key == self.keyset[5]:   # Unleash swordsman
                self.dispatch(Team.Unit.SWORDSMAN)
            if key == self.keyset[6]:   # Unleash archer
                self.dispatch(Team.Unit.ARCHER)
            if key == self.keyset[7]:   # Unleash all
                troops = self.swordsman + self.archers
                if len(troops) != 0:
                    offset_spawn = 0
                    for troop in troops:
                        troop.moving_turn = troop.TURNS - offset_spawn
                        troop.status = Troop.Status.MOVE
                        self.dispatched.append(troop)
                        offset_spawn += 35
                    self.swordsman = []
                    self.archers = []

                else:
                    self.error("No troop available!")

    # Controlla gli stati delle entità di gioco e li modifica in base al tipo di evento
    def handle_events(self, event):
        if hasattr(event, "team"):
            team = event.team
            source = event.source
            target = event.target
            if event.team.team == self.team:
                if event.type == Event.WORKER_EXTRACT:
                    if source.extractions == Worker.MAX_EXTRACTIONS:
                        team.dispatched.remove(source)
                        del source
                elif event.type == Event.WORKER_RESTORE:
                    if target.hp > Tower.MAX_HP:
                        target.hp = Tower.MAX_HP
                        team.dispatched.remove(source)
                        del source
                elif event.type == Event.TROOP_ATTACK_TOWER:
                    if target.hp <= 0:
                        team.winner = True
                elif event.type == Event.BULLET_HIT_TOWER:
                    if target.hp <= 0:
                        team.winner = True
                    if event.bullet in source.bullets:
                        source.bullets.remove(event.bullet)

            else:
                if event.type == Event.TROOP_ATTACK_HIT:
                    if not isinstance(source, Archer):
                        if target.hp <= 0 and target in self.dispatched:
                            self.dispatched.remove(target)
                            del target
                            source.status = Troop.Status.MOVE
                elif event.type == Event.BULLET_HIT:
                    if target.hp <= 0 and target in self.dispatched:
                        self.dispatched.remove(target)
                        del target
                        source.status = Troop.Status.MOVE
                        if event.bullet in source.bullets:
                            source.bullets.remove(event.bullet)

    # Contiene l'effettiva dinamica del gioco
    # Qui vengono lanciati gli eventi di gioco che verranno poi gestiti in futuro
    def play(self, enemy_unit: [Box], enemy_buildings: [Box]):
        tower = self.buildings[2]
        for unit in enemy_unit:
            cond = 120 < unit.hitbox.x < 120 + Tower.RANGE
            if self.team == Team.RED:
                cond = unit.hitbox.x > (760 - Tower.RANGE)
            if cond:
                tower.attack(self.team)
                self.post_event(Event.TOWER_ATTACK_TROOP,
                                {"team": self, "source": tower, "target": unit})

        for bullet in tower.bullets:
            for unit in enemy_unit:
                if bullet.collide(unit):
                    bullet.attack(unit)
                    self.post_event(Event.BULLET_HIT, {"team": self, "source": tower, "target": unit,
                                                       "bullet": bullet})
                    if bullet in tower.bullets:
                        tower.bullets.remove(bullet)
            if bullet.hitbox.y == Env.HEIGHT - Ground.HEIGHT:
                tower.bullets.remove(bullet)
            bullet.move_diagonal()

        for troop in self.dispatched:
            mine = self.buildings[0]
            if isinstance(troop, Worker):
                if troop.collide(mine):
                    troop.status = Troop.Status.EXTRACT
                    if troop.extract(self):
                        self.log(f"Worker extraction: +{Worker.GOLD_EXTRACTED}")
                    self.post_event(Event.WORKER_EXTRACT, {"team": self, "source": troop, "target": None})
                if troop.collide(tower):
                    troop.status = Troop.Status.RESTORE
                    if troop.restore(tower):
                        self.log("Worker restore completed")
                    self.post_event(Event.WORKER_RESTORE, {"team": self, "source": troop, "target": tower})

            for unit in enemy_unit + enemy_buildings:
                if troop.collide(unit):
                    troop.status = Troop.Status.ATTACK
                    if isinstance(troop, Swordsman):
                        troop.attack(unit)
                        if isinstance(unit, Tower):
                            self.post_event(Event.TROOP_ATTACK_TOWER, {"team": self, "source": troop, "target": unit})
                        else:
                            self.post_event(Event.TROOP_ATTACK_HIT, {"team": self, "source": troop, "target": unit})
                    elif isinstance(troop, Archer):
                        troop.attack()
                        self.post_event(Event.TROOP_ATTACK_HIT, {"team": self, "source": troop, "target": unit})

            # Bullets
            if isinstance(troop, Archer):
                bullets = troop.bullets
                for bullet in bullets:
                    for unit in enemy_unit + enemy_buildings:
                        if bullet.collide(unit):
                            bullet.attack(unit)
                            if isinstance(unit, Tower):
                                self.post_event(Event.BULLET_HIT_TOWER,
                                                {"team": self, "source": troop, "target": unit, "bullet": bullet})
                            else:
                                self.post_event(Event.BULLET_HIT, {"team": self, "source": troop, "target": unit,
                                                                   "bullet": bullet})
                            if bullet in bullets:
                                bullets.remove(bullet)

                    bullet.move()

            if troop.status == Troop.Status.MOVE:
                troop.move()


            troop.status = Troop.Status.MOVE

            # Secure garbage collector
            if hasattr(troop, "hp") and troop.hp <= 0:
                self.dispatched.remove(troop)
                del troop

        # Pulisce i messaggi di errore e i log
        if len(self.errors) > 5:
            self.errors = []

        if len(self.logs) > 5:
            self.logs = []

    def save(self):
        pass

    @staticmethod
    def collide(obj: Box, obj2: Box):
        return obj.hitbox.colliderect(obj2.hitbox)

    @staticmethod
    def post_event(event_type: int, args: dict):
        pygame.event.post(pygame.event.Event(event_type, args))

    def get_troops(self):
        return self.swordsman + self.archers

    def get_all(self):
        return self.workers + self.get_troops()

    def get_hp(self):
        return self.buildings[2].hp
