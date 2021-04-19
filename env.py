import pygame
import random
import time
from pathlib import Path

class LoadImages:
    def __init__(self, path):
        self.imgs = {filename.stem: pygame.image.load(str(filename)) for filename in path.glob('*.png')}

    def __call__(self, name):
        assert name in list(self.imgs.keys()), f"There's no image with name: {name}"

        return self.imgs[name]


class GObject(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def setX(self, x):
        self.rect.x = x

    def setY(self, y):
        self.rect.y = y
    
    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y


class Bars:
    def __init__(self, display, bars_distance, speed, img, width, height, start=None):
        self.display = display
        
        self.bars_distance = bars_distance
        self.speed = speed

        self.width = width
        self.height = height

        self.pipes = pygame.sprite.Group()
        self.top_pipe = GObject(pygame.transform.flip(img, False, True))
        self.bot_pipe = GObject(img)
        self.pipes.add(self.top_pipe, self.bot_pipe)

        self.top_pad = 0.05
        self.bot_pad = 0.25

        self.pipe_width, self.pipe_height = img.get_size()

        self.bars_height = self.random_height()

        self.start = start
        self.x = self.width if start is None else start

    def random_height(self):
        return random.randint(self.width * self.top_pad + self.bars_distance, self.height * (1 - self.bot_pad) - self.bars_distance)

    def run(self):
        # Upper Bar
        self.display.blit(self.top_pipe.image, (self.top_pipe.x, self.top_pipe.y))
        
        # Lower Bar
        self.display.blit(self.bot_pipe.image, (self.bot_pipe.x, self.bot_pipe.y))

        self.x -= self.speed

        if self.x <= -self.pipe_width:
            self.x = self.width
            self.bars_height = self.random_height()

        self.top_pipe.setX(self.x)
        self.bot_pipe.setX(self.x)
        
        self.top_pipe.setY(self.bars_height - self.pipe_height - (self.bars_distance / 2))
        self.bot_pipe.setY(self.bars_height + (self.bars_distance / 2))

    def collisions(self, bird):
        if pygame.sprite.spritecollide(bird, self.pipes, False, pygame.sprite.collide_mask):
            return True

    def passed(self, bird):   
        return self.x < bird.x < self.x + self.top_pipe.image.get_width()
    
    def reset(self):
        self.bars_height = self.random_height()

        self.x = self.width if self.start is None else self.start


class Animation:
    def __init__(self, *imgs, speed):
        self.imgs = imgs
        self.playing_imgs = imgs

        self.speed = speed

        self.anim_time = time.time()

    def rotate(self, angle):
        self.playing_imgs = [pygame.transform.rotate(img, angle) for img in self.imgs]

    def current_frame(self):
        for i, img in enumerate(self.playing_imgs):
            if (time.time() * self.speed - self.anim_time) % len(self.playing_imgs) >= (len(self.playing_imgs) - 1 - i):
                return img


class Bird:
    def __init__(self, display, x, y, animation):
        self.display = display

        self.initial_x, self.initial_y = x, y
        self.x, self.y = x, y

        self.y_velocity = 0

        self.angle = 0

        self.animation = animation

    def flap(self):
        self.y_velocity = 5
        self.angle = 200

    def update(self):
        self.y_velocity -= .3  
        self.angle -= 5

        self.y -= self.y_velocity

    def position(self):
        return int(self.x), int(self.y)
    
    @property
    def rect(self):
        rect = self.animation.imgs[0].get_rect()
        rect.x = self.x
        rect.y = self.y
        return rect

    @property
    def mask(self):
        return pygame.mask.from_surface(self.animation.imgs[0])

    def draw(self):
        # I know its not beautiful and could be done better but it gets the job done
        if self.angle > 25:
            self.animation.rotate(25)
        else:
            if self.angle < -90:
                self.angle = -90

            self.animation.rotate(self.angle)

        self.display.blit(self.animation.current_frame(), self.position())

    def reset(self):
        self.x, self.y = self.initial_x, self.initial_y

        self.y_velocity = 0

        self.angle = 0


class Footer:
    def __init__(self, display, imgs, xs, width, height, speed=2):
        self.display = display

        self.width = width
        self.height = height

        self.footer = [[x, GObject(img)] for x, img in zip(xs, imgs)]
        self.speed = speed

        self.sprites = pygame.sprite.Group()
        for _, img in self.footer:
            self.sprites.add(img)

    def update(self):
        for i in range(len(self.footer)):
            if self.footer[i][0] <= -self.width:
                self.footer[i][0] = self.width

            self.footer[i][0] = self.footer[i][0] - self.speed

    def draw(self):
        for x, img in self.footer:
            self.display.blit(img.image, (x, self.height - img.image.get_size()[1]))

    def collisions(self, bird):
        # Why all of a sudden spritecollide doesn't work??!! WTF, Quick fix!
        # if pygame.sprite.spritecollide(bird, self.sprites, False, pygame.sprite.collide_mask):
        #     return True       
        return bird.rect.bottom >= self.height-self.footer[0][1].image.get_size()[1]


class FlappyEnv:
    pygame.init()

    WIDTH = 500
    HEIGHT = 900

    pygame.display.set_caption('Flappy Birds')

    FPS = 60

    def __init__(self):

        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.clock = pygame.time.Clock()

        self.resources = LoadImages(Path.cwd() / "imgs")

        speed = 2

        self.bird = Bird(self.display, x=self.WIDTH // 3, y=self.WIDTH // 2, animation=Animation(self.resources("bird1"), self.resources("bird2"), self.resources("bird3"), speed=10))

        self.bar1 = Bars(self.display, 120, speed, img=self.resources("pipe"), width=self.WIDTH, height=self.HEIGHT)
        self.bar2 = Bars(self.display, 120, speed, img=self.resources("pipe"), start=self.WIDTH + ((self.WIDTH + 50) // 2 ), width=self.WIDTH, height=self.HEIGHT)

        self.footer = Footer(self.display, [self.resources("bg_bottom"), self.resources("bg_bottom")], [0, self.WIDTH], width=self.WIDTH, height=self.HEIGHT, speed=speed)

    def step(self, action=1):
        done = False
        reward = -1

        if action == 1:
            self.bird.flap()

        self.display.blit(self.resources("bg"), (0, 0))

        self.bar1.run()
        self.bar2.run()

        self.bird.update()
        self.bird.draw()

        self.footer.update()
        self.footer.draw()

        if self.bar1.collisions(self.bird) or self.bar2.collisions(self.bird) or self.footer.collisions(self.bird) or self.bird.rect.top <= 0:
            done = True

        if self.bar1.passed(self.bird) or self.bar2.passed(self.bird):
            reward = 0

        pygame.display.update()
        self.clock.tick(self.FPS)

        return self.get_current_frame(), reward, done

    def get_current_frame(self):
        frame = pygame.surfarray.array3d(self.display)
        frame = frame.swapaxes(0, 1)
        return frame

    def reset(self):
        self.bird.reset()
        self.bar1.reset()
        self.bar2.reset()
        return self.get_current_frame()


if __name__ == "__main__":
    env = FlappyEnv()

    env.reset()

    action = 0
    while 1:
        action = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Escape key to exit
                    exit()
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    action = 1

        obs, reward, done = env.step(action)
        print(f"Obeservation: {type(obs)}, reward: {reward}, done: {done}")

        if done:
            env.reset()
