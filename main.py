import pygame
import numpy

WIDTH, HEIGHT = 1280, 720
FPS = 60
BG_COLOR = (15, 15, 25)
RED = (255,0,0)
BLACK = (0,0,0)

ALIGNMENT_WEIGHT = 2
COHESION_WEIGHT = 2
SEPARATION_WEIGHT = 3

SEPARATION_RADIUS = 50

NUM_BOIDS = 100

class Boid:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH*numpy.random.random(), HEIGHT*numpy.random.random())
        self.direction = pygame.Vector2(numpy.random.uniform(-1,1),numpy.random.uniform(-1,1)).normalize()
        self.speed = 100
        self.base_color = pygame.Vector3(numpy.random.uniform(0,255),numpy.random.uniform(0,255),numpy.random.uniform(0,255))
        self.color = self.base_color
        self.size = pygame.Vector2(10,10)
        self.detection_radius = pygame.Vector2(200, 200)
        self.neighbours = []
        self.flock_pos = pygame.Vector2()
        self.crowding_list = []
        self.steering = pygame.Vector2()
        

    def draw(self,screen):
        side = pygame.Vector2(-self.direction.y, self.direction.x)
        nose = self.pos + self.direction * 10
        back = self.pos - self.direction * 5
        left = back + side * 5
        right = back - side * 5
        pygame.draw.polygon(screen, self.color, [nose, left, right])

    def move(self,dt):
        self.pos.x += self.speed*self.direction.x*dt
        self.pos.y += self.speed*self.direction.y*dt

        self.direction += self.steering * dt
        self.direction = self.direction.normalize()

        if self.pos.x < 0:
            self.pos.x = 0
            self.direction.x *= -1
        elif self.pos.x > WIDTH - self.size.x:
            self.pos.x = WIDTH - self.size.x
            self.direction.x *= -1
        if self.pos.y < 0:
            self.pos.y = 0
            self.direction.y *= -1
        elif self.pos.y > HEIGHT - self.size.y:
            self.pos.y = HEIGHT - self.size.y
            self.direction.y *= -1

    def check_neighbours(self, boids):
        for boid in boids:
            if self.pos.distance_to(boid.pos) <= self.detection_radius.x:
                if boid not in self.neighbours and boid is not self:
                    self.neighbours.append(boid)
                if self.pos.distance_to(boid.pos) <= SEPARATION_RADIUS:
                    if boid not in self.crowding_list and boid is not self:
                        self.crowding_list.append(boid)
                else:
                    if boid in self.crowding_list:
                        self.crowding_list.remove(boid)
            else:
                if boid in self.neighbours:
                    self.neighbours.remove(boid)

        self.flock_heading = pygame.Vector2() 
        self.flock_pos = pygame.Vector2()
        self.flock_crowd = pygame.Vector2()
        self.steering = pygame.Vector2()

        alignment = pygame.Vector2()
        cohesion = pygame.Vector2()
        seperation = pygame.Vector2()

        for n in self.neighbours:
            self.flock_heading += n.direction
            self.flock_pos += n.pos

        for c in self.crowding_list:
            away = self.pos - c.pos
            if away:
                away = away.normalize() / self.pos.distance_to(c.pos)
                self.flock_crowd += away
        if self.flock_crowd:
            self.flock_crowd = self.flock_crowd.normalize()
            seperation += (self.flock_crowd - self.direction) * SEPARATION_WEIGHT

        if len(self.neighbours) != 0:
            self.flock_heading = self.flock_heading / len(self.neighbours)
            self.flock_pos = self.flock_pos / len(self.neighbours)

            to_center = self.flock_pos - self.pos
            if to_center:
                to_center = to_center.normalize()
                cohesion += (to_center - self.direction) * COHESION_WEIGHT

            alignment += (self.flock_heading - self.direction ) * ALIGNMENT_WEIGHT
            self.steering = (alignment + cohesion + seperation)

    def debug(self,screen):
        self.color = RED
        pygame.draw.circle(screen, RED, self.pos, self.detection_radius.x, 1)
        pygame.draw.circle(screen, RED, self.flock_pos, 10)
        for n in self.neighbours:
            n.color = RED

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boids")
    clock = pygame.time.Clock()
    boids = [Boid() for _ in range(NUM_BOIDS)]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(BG_COLOR)
        for boid in boids:
            boid.check_neighbours(boids)

        for boid in boids:
            boid.draw(screen)
            boid.move(dt)
            boid.color = boid.base_color
        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
