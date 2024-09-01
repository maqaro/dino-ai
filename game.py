import pygame
import os
import neat

class Robot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/character-1.png").convert_alpha()
        original_width, original_height = self.image.get_size()
        new_width = int(original_width * 2.5)
        new_height = int(original_height * 2.5)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = (240, 600)
        self.jumping = False
        self.jump_height = 0
        self.score = 0

    def jump(self):
        if self.rect.bottom >= 600:
            self.jumping = True

    def gravity(self):
        if self.jumping:
            self.rect.y -= 8
            self.jump_height += 8
        if self.jump_height >= 160:
            self.jumping = False
            self.jump_height = 0
        if not self.jumping:
            self.rect.y += 8
        if self.rect.bottom >= 600:
            self.rect.bottom = 600

    def increase_score(self):
        self.score += 1

    def update(self):
        self.gravity()

class Ground(pygame.sprite.Sprite):
    def __init__(self, x: int):
        super().__init__()
        self.image = pygame.image.load("assets/ground-1.png")
        original_width, original_height = self.image.get_size()
        new_width = int(original_width * 2)
        new_height = int(original_height * 2)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, 600)

    def move(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.rect.x = 1280

    def update(self):
        self.move()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/obstacle-1.png")
        original_width, original_height = self.image.get_size()
        new_width = int(original_width * 2.5)
        new_height = int(original_height * 2.5)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = (1280, 560)
        self.speed = 5
        self.scored = False

    def move(self):
        self.rect.x -= self.speed

    def boundaries(self):
        if self.rect.right < 0:
            self.despawn()

    def despawn(self):
        self.kill()

    def update(self):
        self.move()
        self.boundaries()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_generation = 0

        self.players = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group(Obstacle())
        self.ground = pygame.sprite.Group()

        pygame.display.set_icon(pygame.image.load("assets/character-1.png"))
        pygame.display.set_caption("AI Runner")

    def run(self, genomes, config):
        nets = []
        ge = []
        self.players = pygame.sprite.Group()
        self.current_generation += 1

        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            player = Robot()
            self.players.add(player)
            genome.fitness = 0
            ge.append(genome)

        while self.running and len(self.players) > 0:
            self.clock.tick(60)
            self.handle_events()
            self.update(nets, ge)
            self.draw()

        self.obstacles.empty()

    def handle_collision(self, ge):
        for i, player in enumerate(self.players):
            if pygame.sprite.spritecollideany(player, self.obstacles):
                ge[i].fitness -= 1
                self.players.remove(player)

    def handle_score(self, ge):
        for obstacle in self.obstacles:
            for i, player in enumerate(self.players):
                if not obstacle.scored and player.rect.left > obstacle.rect.right:
                    ge[i].fitness += 1
                    player.increase_score()
                    obstacle.scored = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, nets, ge):
        if len(self.obstacles) == 0:
            self.obstacles.add(Obstacle())

        if len(self.ground) <= 2:
            self.ground.add(Ground(0))
            self.ground.add(Ground(640))
            self.ground.add(Ground(1280))

        for i, player in enumerate(self.players):
            distance_to_obstacle = self.get_nearest_obstacle_distance(player)
            output = nets[i].activate((player.rect.y, abs(player.rect.y - 600), distance_to_obstacle))
            if output[0] > 0.5:
                player.jump()
                if distance_to_obstacle > 200:
                    ge[i].fitness -= 0.1

        self.players.update()
        self.obstacles.update()
        self.ground.update()
        self.handle_score(ge)
        self.handle_collision(ge)

    def get_nearest_obstacle_distance(self, player):
        nearest_obstacle = None
        min_distance = float('inf')
        for obstacle in self.obstacles:
            distance = obstacle.rect.x - player.rect.x
            if 0 < distance < min_distance:
                min_distance = distance
                nearest_obstacle = obstacle
        return min_distance if nearest_obstacle else 1280  #

    def draw(self):
        self.screen.fill(('white'))
        if len(self.players) > 0:
            self.ground.draw(self.screen)
            self.players.draw(self.screen)
            self.obstacles.draw(self.screen)
            font = pygame.font.Font(None, 74)
            score = self.players.sprites()[0].score
            text = font.render(str(score), True, (0, 0, 0))
            text_rect = text.get_rect(center=(640, 50))
            self.screen.blit(text, text_rect)

            current_generation_text = font.render(f"Generation: {self.current_generation}", True, (0, 0, 0))
            alive_count_text = font.render(f"Alive: {len(self.players)}", True, (0, 0, 0))

            generation_rect = current_generation_text.get_rect(center=(640, 100))
            alive_rect = alive_count_text.get_rect(center=(640, 150))

            self.screen.blit(current_generation_text, generation_rect)
            self.screen.blit(alive_count_text, alive_rect)
        pygame.display.flip()

def run_AI(config_path: str):
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction, 
        neat.DefaultSpeciesSet, neat.DefaultStagnation, 
        config_path
    )
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    game_instance = Game()
    winner = population.run(game_instance.run, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_AI(config_path)