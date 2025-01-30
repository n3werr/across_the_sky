import pygame
import sys
import random

pygame.init()

# Настройки экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Across the sky")

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)


# генерация фона
def create_gradient(surface):
    for y in range(surface.get_height()):
        color = (0, 0, int(255 * (y / surface.get_height())))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


background = pygame.Surface((screen_width, screen_height))
create_gradient(background)

# Параметры звёзд
num_stars = 100
stars = []

for _ in range(num_stars):
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    stars.append([x, y])

star_speed = 5

# Параметры персонажа
circle_radius = 20
circle_x = screen_width // 2
circle_y = screen_height // 2
circle_speed = 7

# Параметры пуль
bullets = []
bullet_speed = -10

# Параметры врагов
enemies = []
enemy_size = 30
enemy_spawn_rate = 30  # каждые 30 кадров
enemy_speed = 3
enemy_timer = 0


# Параметры врагов и их здоровье
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.health = 5  # Здоровье врага


# Цикл игры
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Управление персонажем
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and circle_x - circle_radius > 0:
        circle_x -= circle_speed
    if keys[pygame.K_RIGHT] and circle_x + circle_radius < screen_width:
        circle_x += circle_speed
    if keys[pygame.K_UP] and circle_y - circle_radius > 0:
        circle_y -= circle_speed
    if keys[pygame.K_DOWN] and circle_y + circle_radius < screen_height:
        circle_y += circle_speed

    # Стрельба
    if keys[pygame.K_SPACE]:
        bullets.append([circle_x, circle_y])  # Добавление пули в список

    # Обновление положения пуль
    for bullet in bullets[:]:
        bullet[1] += bullet_speed
        if bullet[1] < 0:  # Удаление ненужных пуль
            bullets.remove(bullet)

    # Обновление положения врагов
    enemy_timer += 1
    if enemy_timer >= enemy_spawn_rate:
        enemy_x = random.randint(0, screen_width - enemy_size)
        enemies.append(Enemy(enemy_x, 0))
        enemy_timer = 0

    for enemy in enemies[:]:
        enemy.rect.y += enemy_speed
        if enemy.rect.y > screen_height:
            enemies.remove(enemy)

        # Система пуль
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10)
            if enemy.rect.colliderect(bullet_rect):
                enemy.health -= 1
                bullets.remove(bullet)
                if enemy.health <= 0:
                    enemies.remove(enemy)
                break

    # Обновление положения звёзд
    for star in stars:
        star[1] += star_speed
        if star[1] > screen_height:
            star[1] = random.randint(-20, 0)  # Сброс звезды на верх экрана
            star[0] = random.randint(0, screen_width)


    screen.blit(background, (0, 0))

    for star in stars:
        pygame.draw.circle(screen, white, (star[0], star[1]), 2)  # Рисуем звезды

    # Генерация врагов
    for enemy in enemies:
        pygame.draw.rect(screen, green, enemy.rect)

    # Персонаж (для теста в виде круга)

    pygame.draw.circle(screen, red, (circle_x, circle_y), circle_radius)

    # Генерация пуль
    for bullet in bullets:
        pygame.draw.circle(screen, white, (bullet[0], bullet[1]), 5)  # Рисуем пули

    # Эффект движения фона
    background.scroll(0, star_speed)
    if background.get_height() < screen_height:
        create_gradient(background)

    pygame.display.update()
    clock.tick(60)
