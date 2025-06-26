import pygame
from constants import * 

def main():
    pygame.init()
    print('Starting Asteroids!')
    print(f"Screen width: {SCREEN_WIDTH} \nScreen height: {SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill("black")
    pygame.display.flip()

    pygame.time.Clock()
    dt = 0


    for event in pygame.event.get():
        dt = pygame.time.Clock().tick(60) / 1000
        if event.type == pygame.QUIT:
            pygame.quit()
            return

if __name__ == "__main__":
    main()