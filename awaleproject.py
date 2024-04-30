import pygame

pygame.init()
screen = pygame.display.set_mode((1400, 800))
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((211, 211, 211))
    
    rectangle = pygame.Rect(100, 100, 1200, 600)
    pygame.draw.rect(screen, (161, 91, 0), rectangle)
    
    pygame.draw.circle(screen, (0, 0, 0), (200, 250), 75)
    pygame.draw.circle(screen, (0, 0, 0), (400, 250), 75)
    pygame.draw.circle(screen, (0, 0, 0), (600, 250), 75)
    pygame.draw.circle(screen, (0, 0, 0), (800, 250), 75)
    pygame.draw.circle(screen, (0, 0, 0), (1000, 250), 75)
    pygame.draw.circle(screen, (0, 0, 0), (1200, 250), 75)  
    pygame.draw.circle(screen, (0, 0, 0), (200, 550), 75)
    pygame.draw.circle(screen, (0, 0, 0), (400, 550), 75)
    pygame.draw.circle(screen, (0, 0, 0), (600, 550), 75)
    pygame.draw.circle(screen, (0, 0, 0), (800, 550), 75)
    pygame.draw.circle(screen, (0, 0, 0), (1000, 550), 75)
    pygame.draw.circle(screen, (0, 0, 0), (1200, 550), 75)
    
    
    pygame.display.flip()

pygame.quit()

