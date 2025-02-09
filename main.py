import pygame
import sys
import random
import math

pygame.init()

# Настройки экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Across the Sky")

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def create_gradient(surface):
    for y in range(surface.get_height()):
        color = (0, 0, int(255 * (y / surface.get_height())))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


background = pygame.Surface((screen_width, screen_height))
create_gradient(background)


def game_over():
    font = pygame.font.Font(None, 50)
    while True:
        screen.fill(black)
        draw_text("Игра окончена", font, red, screen_width // 3, 200)
        draw_text("Нажмите ENTER, чтобы заново", font, white, screen_width // 4, 280)
        draw_text("Нажмите ESC, чтобы выйти", font, white, screen_width // 4, 340)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True  # Перезапуск игры
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def game_loop():
    # Параметры игрока
    circle_radius = 20
    circle_x = screen_width // 2
    circle_y = screen_height // 2
    circle_speed = 7
    player_health = 5

    # Параметры пуль
    bullets = []
    bullet_speed = -10
    enemy_bullets = []

    # Враги
    class Enemy:
        def __init__(self, x, y, enemy_type):
            self.rect = pygame.Rect(x, y, 30, 30)
            self.enemy_type = enemy_type
            self.speed = 3 if enemy_type == "kamikaze" else 2
            self.color = white if enemy_type == "kamikaze" else blue
            self.shoot_timer = 0  # Таймер для выстрелов
            self.hit_timer = 0  # Таймер для мигания при атаке
            self.has_collided = False  # Флаг для предотвращения многократных столкновений

        def move(self):
            if self.enemy_type == "kamikaze":
                direction_x = (circle_x - self.rect.x) / max(1, abs(circle_x - self.rect.x))
                direction_y = (circle_y - self.rect.y) / max(1, abs(circle_y - self.rect.y))
                self.rect.x += int(direction_x * self.speed)
                self.rect.y += int(direction_y * self.speed)
            elif self.enemy_type == "shooter":
                self.rect.y += self.speed
                self.shoot_timer += 1
                if self.shoot_timer >= 60:  # Каждые 60 кадров стреляет
                    self.shoot_timer = 0
                    # Вычисляем направление пули к игроку
                    angle = math.atan2(circle_y - self.rect.centery, circle_x - self.rect.centerx)
                    enemy_bullets.append([self.rect.centerx, self.rect.centery, angle])

        def update_hit(self):
            if self.hit_timer > 0:
                self.hit_timer -= 1

        def draw(self, screen, shake_x, shake_y):
            # Если враг был атакован, меняем его цвет на красный
            if self.hit_timer > 0:
                color = red
            else:
                color = self.color
            pygame.draw.rect(screen, color, self.rect.move(shake_x, shake_y))

    enemies = []
    enemy_spawn_rate = 50
    enemy_timer = 0

    # Взрывы
    explosions = []  # Список для хранения взрывов

    def spawn_enemy():
        x = random.randint(0, screen_width - 30)
        enemy_type = random.choice(["kamikaze", "shooter"])
        enemies.append(Enemy(x, 0, enemy_type))

    clock = pygame.time.Clock()
    shake_intensity = 0
    shake_duration = 0  # Длительность тряски

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

        to_remove = []
        for enemy in enemies:
            enemy.move()

            # Проверка столкновения камикадзе с игроком
            if enemy.enemy_type == "kamikaze" and enemy.rect.colliderect(
                    pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)):
                if not enemy.has_collided:  # Проверяем, чтобы столкновение учитывалось только один раз
                    player_health -= 1
                    shake_intensity = 20  # Увеличиваем тряску
                    shake_duration = 10  # Устанавливаем длительность тряски
                    enemy.hit_timer = 10  # Включаем мигание на 10 кадров
                    enemy.has_collided = True  # Устанавливаем флаг, чтобы избежать повторного учета столкновения
                    # Добавляем взрыв
                    explosions.append({"x": enemy.rect.centerx, "y": enemy.rect.centery, "timer": 10})
                    to_remove.append(enemy)  # Удаляем камикадзе после взрыва

            # Проверка попадания пуль
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet):
                    bullets.remove(bullet)
                    to_remove.append(enemy)

        for enemy in to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        # Обновление движения вражеских пуль
        to_remove_bullets = []
        for bullet in enemy_bullets:
            bx, by, angle = bullet

            # Вычисление направления движения пули
            speed = 4
            bx += int(math.cos(angle) * speed)
            by += int(math.sin(angle) * speed)

            if pygame.Rect(bx - 5, by - 5, 10, 10).colliderect(
                    pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)):
                player_health -= 1
                shake_intensity = 20  # Увеличиваем тряску
                shake_duration = 10  # Устанавливаем длительность тряски
                to_remove_bullets.append(bullet)

            if by > screen_height or bx < 0 or bx > screen_width:
                to_remove_bullets.append(bullet)

            bullet[0], bullet[1] = bx, by  # Обновление координат пули

        for bullet in to_remove_bullets:
            enemy_bullets.remove(bullet)

        # Если здоровье закончилось — вызываем Game Over
        if player_health <= 0:
            if game_over():
                return  # Перезапуск игры
            else:
                pygame.quit()
                sys.exit()

        # Эффект тряски экрана
        if shake_duration > 0:
            shake_x = random.randint(-shake_intensity, shake_intensity)
            shake_y = random.randint(-shake_intensity, shake_intensity)
            shake_duration -= 1
        else:
            shake_x, shake_y = 0, 0

        # Отрисовка
        screen.fill(black)
        screen.blit(background, (shake_x, shake_y))

        for enemy in enemies:
            enemy.update_hit()
            enemy.draw(screen, shake_x, shake_y)

        for bullet in bullets:
            pygame.draw.rect(screen, white, bullet.move(shake_x, shake_y))

        for bullet in enemy_bullets:
            pygame.draw.circle(screen, red, (bullet[0] + shake_x, bullet[1] + shake_y), 5)

        # Отрисовка взрывов
        for explosion in explosions[:]:
            pygame.draw.circle(screen, yellow, (explosion["x"] + shake_x, explosion["y"] + shake_y), 20)
            explosion["timer"] -= 1
            if explosion["timer"] <= 0:
                explosions.remove(explosion)

        pygame.draw.circle(screen, red, (circle_x + shake_x, circle_y + shake_y), circle_radius)
        draw_text(f"HP: {player_health}", pygame.font.Font(None, 36), white, 10, 10)

        pygame.display.update()
        clock.tick(60)


# Основной цикл игры
while True:
    game_loop()