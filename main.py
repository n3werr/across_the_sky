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
blue = (0, 0, 255)


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def create_gradient(surface):
    for y in range(surface.get_height()):
        color = (0, 0, int(255 * (y / surface.get_height())))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


background = pygame.Surface((screen_width, screen_height))
create_gradient(background)


def main_menu():
    menu_font = pygame.font.Font(None, 50)
    running = True
    while running:
        screen.fill(black)
        draw_text("Across the Sky", menu_font, white, screen_width // 3, 100)
        draw_text("Нажмите ENTER, чтобы начать", menu_font, white, screen_width // 4, 250)
        draw_text("Нажмите ESC, чтобы выйти", menu_font, white, screen_width // 4, 300)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Запуск игры
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


main_menu()

# Параметры персонажа
circle_radius = 20
circle_x = screen_width // 2
circle_y = screen_height // 2
circle_speed = 7
player_health = 10

# Параметры пуль
bullets = []
bullet_speed = -10


# Параметры врагов
class Enemy:
    def __init__(self, x, y, health, speed, color, attack_type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.health = health
        self.speed = speed
        self.color = color
        self.attack_type = attack_type

    def move(self):
        if self.attack_type == "kamikaze":
            direction_x = (circle_x - self.rect.x) / max(1, abs(circle_x - self.rect.x))
            direction_y = (circle_y - self.rect.y) / max(1, abs(circle_y - self.rect.y))
            self.rect.x += int(direction_x * self.speed)
            self.rect.y += int(direction_y * self.speed)
        elif self.attack_type == "homing":
            self.rect.y += self.speed
            if self.rect.x < circle_x:
                self.rect.x += 1
            elif self.rect.x > circle_x:
                self.rect.x -= 1

    def attack(self):
        if self.attack_type == "homing":
            enemy_bullets.append([self.rect.centerx, self.rect.bottom])


enemies = []
enemy_bullets = []
enemy_spawn_rate = 30
enemy_timer = 0


def spawn_enemy():
    enemy_type = random.choice(["kamikaze", "homing"])
    x = random.randint(0, screen_width - 30)
    if enemy_type == "kamikaze":
        enemies.append(Enemy(x, 0, 1, 5, white, "kamikaze"))
    elif enemy_type == "homing":
        enemies.append(Enemy(x, 0, 2, 2, blue, "homing"))


clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and circle_x - circle_radius > 0:
        circle_x -= circle_speed
    if keys[pygame.K_RIGHT] and circle_x + circle_radius < screen_width:
        circle_x += circle_speed
    if keys[pygame.K_UP] and circle_y - circle_radius > 0:
        circle_y -= circle_speed
    if keys[pygame.K_DOWN] and circle_y + circle_radius < screen_height:
        circle_y += circle_speed
    if keys[pygame.K_SPACE]:
        bullets.append(pygame.Rect(circle_x - 5, circle_y - 10, 10, 10))

    bullets = [b.move(0, bullet_speed) for b in bullets if b.y > 0]

    enemy_timer += 1
    if enemy_timer >= enemy_spawn_rate:
        spawn_enemy()
        enemy_timer = 0

    for enemy in enemies[:]:
        enemy.move()
        to_remove = []  # Список для удаления врагов
        for enemy in enemies[:]:
            enemy.move()

            # Проверка столкновения камикадзе с игроком
            if enemy.rect.colliderect(
                    pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)) and enemy.attack_type == "kamikaze":
                player_health -= 2
                to_remove.append(enemy)

            # Проверка попадания пуль
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet):
                    enemy.health -= 1
                    bullets.remove(bullet)
                    if enemy.health <= 0:
                        to_remove.append(enemy)  # Добавляем в список на удаление

        # Удаляем всех врагов после прохода по списку
        for enemy in to_remove:
            if enemy in enemies:  # Проверяем, есть ли враг в списке перед удалением
                enemies.remove(enemy)

    for bullet in enemy_bullets[:]:
        bullet[1] += 5
        if pygame.Rect(bullet[0] - 5, bullet[1] - 5, 10, 10).colliderect(
                pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)):
            player_health -= 1
            enemy_bullets.remove(bullet)
        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)

    screen.blit(background, (0, 0))
    for enemy in enemies:
        pygame.draw.rect(screen, enemy.color, enemy.rect)
    for bullet in bullets:
        pygame.draw.rect(screen, white, bullet)
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, red, (bullet[0], bullet[1]), 5)
    pygame.draw.circle(screen, red, (circle_x, circle_y), circle_radius)
    draw_text(f"HP: {player_health}", pygame.font.Font(None, 36), white, 10, 10)

    pygame.display.update()
    clock.tick(60)
