
import pygame
from pygame.locals import *
from pygame.math import Vector2
from pygame import mixer
import time
import random

game_state = 0
score = 0
score_int = 0
max_score = 0
entities_alive = []

class Player:
    position = pygame.Vector2()
    scale = pygame.Vector2()
    velocity_y = 0
    gravity_scale = 3000
    jump_force = 2000
    speed = 400
    is_grounded = False
    player_sprite = 0
    rotation = 0
    rot_speed = 400
    scale_speed = 3
    player_collider = 0

    def __init__(self, desired_scale_x, desired_scale_y, Width, Height):
        self.scale.x = desired_scale_x
        self.scale.y = desired_scale_y
        self.scalar = 50
        self.player_sprite = pygame.sprite.Sprite()
        self.player_sprite.image = pygame.image.load("Data/Textures/Snowball.png").convert_alpha()
        self.player_sprite.rect = self.player_sprite.image.get_rect()
        self.player_sprite.image = pygame.transform.scale(self.player_sprite.image, (int(self.scale.x), int(self.scale.y)))
        self.position.x = Width / 2
        self.position.y = Height / 2 
        self.scalar = self.scale.x

    def move(self, keys, dt):
        global score_int
        global score
        global max_score
        if(keys[0]):
            self.position.x -= 0.01 * dt * self.speed
            self.rotation += 0.01 * dt * self.rot_speed
        if(keys[1]):
            self.position.x += 0.01 * dt * self.speed
            self.rotation -= 0.01 * dt * self.rot_speed
        if(keys[2] and self.is_grounded):
            self.velocity_y -= 0.01 * dt * self.jump_force
        self.velocity_y += 0.00001 * dt * self.gravity_scale
        self.position.y += self.velocity_y * dt
        self.player_sprite.rect.topleft = self.position.x, self.position.y
        if(self.scalar < 12):
            game_state = 0
            if(score > max_score):
                max_score = score
        else:
            self.scalar -= 0.01 * dt * self.scale_speed

    def draw(self, screen, color, dt, colliders):
        img_copy = pygame.transform.scale(self.player_sprite.image, (int(self.scalar), int(self.scalar)))
        img_copy = pygame.transform.rotate(img_copy, self.rotation)
        self.collisions(colliders, img_copy.get_height())
        screen.blit(img_copy, (self.position.x - int(img_copy.get_width() / 2), self.position.y - int(img_copy.get_height() / 2)))

    def collisions(self, colliders, scale):
        self.is_grounded = False
        for i in range(len(colliders)):
            if(self.position.y - int(scale / 2) >= colliders[i].top - scale and colliders[i].typeof == "environment"):
                self.is_grounded = True
                self.position.y = colliders[i].top - int(scale / 2) + 5
                self.velocity_y = 0
            if(self.position.x + int(self.player_sprite.image.get_width() / 2) >= 720):
                self.position.x = 720 - int(self.player_sprite.image.get_width() / 2)
            if(self.position.x - int(self.player_sprite.image.get_width() / 2) <= 0):
                self.position.x = 0 + int(self.player_sprite.image.get_width() / 2)

class Box_Collider:
    position = Vector2()
    scale = Vector2()
    top = 0
    right = 0
    left = 0
    down = 0
    typeof = "default"

    def __init__(self, desired_position_x, desired_position_y, desired_scale_x, desired_scale_y, typeof):
        self.position.x = desired_position_x
        self.position.y = desired_position_y
        self.scale.x = desired_scale_x
        self.scale.y = desired_scale_y
        self.typeof = typeof
        self.top = self.position.y - self.scale.y / 2
        self.right = self.position.x + self.scale.x / 2
        self.left = self.position.x - self.scale.x / 2
        self.down = self.position.y + self.scale.y / 2

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (self.position.x, self.position.y, self.scale.x, self.scale.y))

class Entity:
    tag = "Default"
    bottom = 0
    entity_color = (0, 0, 0)
    sound = 0
    radius = 0
    right = 0
    left = 0

    def move(self, dt):
        self.position.y += dt * self.speed
        self.bottom = self.position.y + (self.radius * 2)
        self.right = self.position.x + (self.radius * 2)
        self.left = self.position.x

    def collisions(self, enemies):
        if(self.position.y > 390):
            enemies.remove(self)
            enemies = enemies[:-1]
            self.sound.play()

    def initialiser(self, color, sfx_path):
        self.entity_color = color
        self.sound = mixer.Sound(sfx_path)

    def draw(self, screen):
        pygame.draw.circle(screen, self.entity_color, (self.position.x, self.position.y), self.radius)

class Enemy(Entity):
    def __init__(self):
        self.speed = random.randrange(1, 5)
        self.position = Vector2()
        self.position.x = random.randrange(0, 720)
        self.position.y = 0
        self.initialiser((102, 107, 102), "Data/Sounds/RockHit.wav")
        self.tag = "enemy"
        self.radius = random.randrange(10, 30)

class Snowball(Entity):
    def __init__(self):
        self.speed = random.randrange(1, 5)
        self.position = Vector2()
        self.position.x = random.randrange(0, 720)
        self.position.y = 0
        self.initialiser((255, 255, 255), "Data/Sounds/SnowballHit.wav")
        self.tag = "snowball"
        self.radius = random.randrange(10, 30)

class Spawner:
    global game_state
    global entities_alive
    total_enemies_spawned = 0
    time_elapsed = 0
    screen = 0
    time_between_spawns = 100
    concurrent_enemys = 0
    sound = 0

    def __init__(self, screen):
        self.screen = screen
        self.sound = mixer.Sound("Data/Sounds/SnowballPowerup.wav")

    def check_for_player(self, player, scalar):
        global game_state
        global score_int
        global score
        global max_score
        for i in range(len(entities_alive)):
            try:
                if(entities_alive[i].bottom > 380 + 50 - scalar):
                    if(entities_alive[i].position.x > player.position.x - player.scale.x and entities_alive[i].position.x < player.position.x + player.scale.x):
                        if(entities_alive[i].tag == "enemy"):
                            game_state = 0
                            if(score > max_score):
                                max_score = score
                        else:
                            score += 5
                            player.scalar = 50
                            self.sound.play()
                            entities_alive.remove(entities_alive[i])
            except:
                pass

    def set_time_between_spawns(self, time_between_spawns):
        self.time_between_spawns = time_between_spawns

    def draw_enemies(self, dt):
        for i in range(len(entities_alive)):
            try:
                entities_alive[i].draw(self.screen)
                entities_alive[i].move(dt)
                entities_alive[i].collisions(entities_alive)
            except:
                pass

    def timer(self, dt):
        self.time_elapsed += dt

    def spawner(self):
        if(self.time_elapsed >= self.time_between_spawns):
            random_int = random.randint(0, 4)
            if(random_int != 0 and self.concurrent_enemys < 3):
                entity = Enemy()
                self.concurrent_enemys += 1
            else:
                entity = Snowball()
                self.concurrent_enemys = 0
            entities_alive.append(entity)
            self.time_elapsed = 0

class Particle:
    def __init__(self):
        self.position = Vector2()
        self.position.x = random.randrange(0, 720)
        self.position.y = 0
        self.size = random.randrange(0, 15)
        self.color = (255, 255, 255)
        self.speed = random.randrange(20, 50)

    def move(self, dt):
        self.position.y += 0.01 * dt * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.position.x, self.position.y, self.size, self.size))

    def collision(self, particles):
        if(self.position.y > 390):
            particles.remove(self)

class Main:
    global game_state
    previous_frame_time = 0
    dt = 0
    elapsed_time = 0
    time_between_spawns = 100

    def calculate_deltatime(self):
        self.dt = time.time() - self.previous_frame_time
        self.dt *= 60
        self.previous_frame_time = time.time()

    def difficulty(self):
        self.elapsed_time += self.dt
        if(self.elapsed_time > 100):
            self.elapsed_time = 0
            self.time_between_spawns -= 1

    def main(self):
        global game_state
        global score_int
        global score
        global max_score
        global entities_alive
        pygame.init()
        screen = pygame.display.set_mode((720, 390))
        icon = pygame.image.load("Data/Textures/Snowball.png").convert_alpha()
        pygame.display.set_icon(icon)
        mixer.init()
        bg_music = mixer.Sound("Data/Sounds/BackgroundMusic.wav")
        bg_music.play(1000)
        spawner = Spawner(screen)
        font = pygame.font.Font('freesansbold.ttf', 32)
        end_font = pygame.font.Font('freesansbold.ttf', 64)
        Width, Height = pygame.display.get_surface().get_size()
        player = Player(50, 50, Width, Height)
        ground = Box_Collider(0, 380, 720, 10, "environment")
        particles = []
        while True:
            keys = [False, False, False]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            key = pygame.key.get_pressed()
            if key[pygame.K_a]:
                keys[0] = True
            if key[pygame.K_d]:
                keys[1] = True
            if key[pygame.K_SPACE]:
                keys[2] = True
            self.calculate_deltatime()
            screen.fill((155, 173, 183))
            if(game_state == 1):
                self.difficulty()
                if(len(particles) < 100):
                    particles.append(Particle())
                player.move(keys, self.dt)
                for i in range(len(particles)):
                    try:
                        particles[i].draw(screen)
                        particles[i].move(self.dt)
                        particles[i].collision(particles)
                    except:
                        pass
                score_int += 1
                score = int(score_int / 10)
                player.draw(screen, (255, 255, 255), self.dt, [ground])
                spawner.spawner()
                spawner.timer(self.dt)
                spawner.draw_enemies(self.dt)
                spawner.check_for_player(player, player.scalar)
                text = font.render(f'Score: {score}', True, (255, 255, 255))
                screen.blit(text, (10, 10))
            else:
                title_text = end_font.render('Snowball Dodge', True, (255, 255, 255))
                score_text = font.render(f'Current Score: {score}', True, (255, 255, 255))
                max_score_text = font.render(f'Max Score: {max_score}', True, (255, 255, 255))
                instr_text = font.render(f'Press SPACE to Start', True, (255, 255, 255))
                screen.blit(title_text, (120, 40))
                screen.blit(score_text, (10, 150))
                screen.blit(max_score_text, (10, 190))
                screen.blit(instr_text, (10, 230))
                entities_alive = []
                player = Player(50, 50, Width, Height)
                spawner = Spawner(screen)
                self.time_between_spawns = 100
                score_int = 0
                score = 0
                if keys[2]:
                    game_state = 1
            pygame.display.flip()
            pygame.display.update()

Main().main()
