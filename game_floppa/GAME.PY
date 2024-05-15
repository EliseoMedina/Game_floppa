import pygame
import sys
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
width, height = 700, 775
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Disparando con sandreke")

# Cargar imágenes y escalarlas
try:
    player_image = pygame.image.load("imgs/walter.jpg")
    player_image = pygame.transform.scale(player_image, (60, 60))

    bullet_image = pygame.image.load("imgs/pescado.png")
    bullet_image = pygame.transform.scale(bullet_image, (50, 50))

    enemy_image = pygame.image.load("imgs/bingus.png")
    enemy_image = pygame.transform.scale(enemy_image, (40, 40))  # Reducido el tamaño del enemigo

    background_image = pygame.image.load("imgs/floppa.jpg")
    background_image = pygame.transform.scale(background_image, (width, height))
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

# Colores
WHITE = (255, 255, 255)

# Fuente para texto
font = pygame.font.SysFont(None, 36)

# Clase para el jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height - 60)
        self.lives = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.move_ip(5, 0)
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.move_ip(0, -5)
        if keys[pygame.K_DOWN] and self.rect.bottom < height:
            self.rect.move_ip(0, 5)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Clase para las balas
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

    def update(self):
        self.rect.move_ip(0, -10)
        if self.rect.bottom < 0:
            self.kill()

# Clase para los enemigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedx = random.choice([-3, -2, -1, 1, 2, 3])  # Movimiento diagonal
        self.speedy = random.randint(2, 5)  # Velocidad más lenta

    def update(self):
        self.rect.move_ip(self.speedx, self.speedy)
        if self.rect.top > height or self.rect.left < 0 or self.rect.right > width:
            self.rect.x = random.randint(0, width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedx = random.choice([-3, -2, -1, 1, 2, 3])
            self.speedy = random.randint(2, 5)

# Inicializar grupos de sprites
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Crear el jugador
player = Player()
all_sprites.add(player)

# Crear enemigos
for i in range(15):  # Mantener el número de enemigos aumentado
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Variables de juego
score = 0
high_score = 0
game_over = False
paused = False
shooting = False
shoot_delay = 250  # milisegundos entre disparos (ajustado para mayor dificultad)
last_shot = pygame.time.get_ticks()

# Bucle principal del juego
clock = pygame.time.Clock()
running = True

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def reset_game():
    global score, game_over, paused, player, enemies, all_sprites, bullets
    score = 0
    game_over = False
    paused = False
    player.lives = 5
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites.add(player)
    for i in range(15):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

while running:
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r and game_over:
                reset_game()
            elif event.key == pygame.K_SPACE:
                player.shoot()  # Disparo con cada pulsación de la barra espaciadora

    if not paused and not game_over:
        # Actualizar
        all_sprites.update()

        # Colisiones entre balas y enemigos
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Colisiones entre jugador y enemigos
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            player.lives -= 1
            if player.lives > 0:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
            else:
                game_over = True
                if score > high_score:
                    high_score = score

        # Dibujar / renderizar
        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)

        # Mostrar puntaje, vidas y puntaje máximo
        draw_text(f"Puntaje: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Vidas: {player.lives}", font, WHITE, screen, 10, 50)
        draw_text(f"Record: {high_score}", font, WHITE, screen, 10, 90)

        pygame.display.flip()
    elif game_over:
        screen.blit(background_image, (0, 0))
        draw_text("Game Over", font, WHITE, screen, width // 2 - 80, height // 2 - 36)
        draw_text("Presiona 'R' para reiniciar", font, WHITE, screen, width // 2 - 160, height // 2 + 10)
        pygame.display.flip()

    # Mantener 60 fps
    clock.tick(60)

pygame.quit()
sys.exit()