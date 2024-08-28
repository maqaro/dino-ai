import pygame
import math
import random

class Robot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/character-1.png").convert_alpha()

        original_width, original_height = self.image.get_size()
        new_width = int(original_width * 2.5)
        new_height = int(original_height * 2.5)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = (480, 360)

        self.jumping = False
        self.jump_height = 0

        self.score = 0

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 720:
            self.jumping = True 

    def gravity(self):
        if self.jumping:
            self.rect.y -= 8
            self.jump_height += 8

        if self.jump_height >= 180:
            self.jumping = False
            self.jump_height = 0

        if not self.jumping:
            self.rect.y += 8 

        if self.rect.bottom >= 720:
            self.rect.bottom = 720

    def increase_score(self):
        self.score += 1

    def update(self):
        self.jump()
        self.gravity()


class obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/obstacle-1.png")

        original_width, original_height = self.image.get_size()
        new_width = int(original_width * 2.5)
        new_height = int(original_height * 2.5)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = (1000, 680)

        self.speed = 5
        self.scored = False

    def move(self):
        self.rect.x -= self.speed

    def boundries(self):
        if self.rect.right < 0:
            self.despawn()

    def despawn(self):
        self.kill()

    def update(self):
        self.move()
        self.boundries()

class game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((960, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.alive = True
        self.player_group = pygame.sprite.GroupSingle(Robot())
        self.obstacles = pygame.sprite.Group(obstacle())
        self.score = 0

        pygame.display.set_icon(pygame.image.load("assets/character-1.png"))
        pygame.display.set_caption("AI Runner")

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_collision(self):
        if self.player_group and pygame.sprite.spritecollide(self.player_group.sprite, self.obstacles, False):
            self.player_group.empty()
            self.obstacles.empty()
            return False
        else:
            return True
        
    def handle_score(self):
        for obstacle in self.obstacles:
            if not obstacle.scored and self.player_group.sprite.rect.left > obstacle.rect.right:
                self.player_group.sprite.increase_score()
                obstacle.scored = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if not self.alive and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.alive = True
                    self.player_group.add(Robot())

    def update(self):
        if self.alive:
            if len(self.obstacles) == 0:
                self.obstacles.add(obstacle())

            if len(self.player_group) < 1:
                self.player_group.add(Robot())

            self.player_group.update()
            self.obstacles.update()
            self.handle_score()
            self.alive = self.handle_collision()

    def draw(self):
        self.screen.fill(('white'))
        if self.alive:
            self.player_group.draw(self.screen)
            self.obstacles.draw(self.screen)

            font = pygame.font.Font(None, 74)
            text = font.render(str(self.player_group.sprite.score), True, (0, 0, 0))
            text_rect = text.get_rect(center=(480, 50))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

        else:
            font = pygame.font.Font(None, 74)
            text = font.render("You Died", True, (0, 0, 0))
            text_rect = text.get_rect(center=(480, 360))
            self.screen.blit(text, text_rect)

            font = pygame.font.Font(None, 74)
            text = font.render("Press S to start", True, (0, 0, 0))
            text_rect = text.get_rect(center=(480, 420))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

game = game()
game.run()