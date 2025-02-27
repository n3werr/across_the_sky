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

best_score_file = "best_score.txt"


def load_best_score():
    try:
        with open(best_score_file, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0


def save_best_score(score):
    with open(best_score_file, "w") as file:
        file.write(str(score))


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def create_gradient(surface):
    for y in range(surface.get_height()):
        color = (0, 0, int(255 * (y / surface.get_height())))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


background = pygame.Surface((screen_width, screen_height))
create_gradient(background)


def start_screen():
    font = pygame.font.Font('KenVector Future.ttf', 40)
    small_font = pygame.font.Font('KenVector Future.ttf', 30)
    while True:
        screen.fill(black)
        draw_text("Across the Sky", font, white, screen_width // 4, 250)
        draw_text("Press ENTER to start.",
        small_font, white, screen_width // 5, 300)
        draw_text("Press ESC to exit.",
        small_font, white, screen_width // 5, 350)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Старт игры
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def reset_game_state():
    global bullets, enemy_bullets, enemies, explosions, player_health, circle_x, circle_y, enemy_timer

    # Параметры игрока
    circle_x = screen_width // 2
    circle_y = screen_height // 1.25
    player_health = 5

    # Очищаем списки
    bullets = []
    enemy_bullets = []
    enemies = []
    explosions = []
    enemy_timer = 0


def game_loop(best_score):
    global circle_x, circle_y, player_health, bullets, enemy_bullets, enemies, explosions, enemy_timer
    circle_radius = 20
    circle_speed = 7

    # Загрузка текстуры игрока
    player_image = pygame.image.load("img/player.png")
    player_rect = player_image.get_rect(center=(circle_x, circle_y))

    # Загрузка текстуры пули игрока
    bullet_image = pygame.image.load("img/fire.png")
    bullet_rect = bullet_image.get_rect()

    # Загрузка текстур врагов
    enemy_kamikaze_image = pygame.image.load("img/enemy1.png")
    enemy_shooter_image = pygame.image.load("img/enemy2.png")

    # Загрузка текстуры пуль врагов
    enemy_bullet_image = pygame.image.load("img/fire2.png")

    # Параметры пуль
    bullet_speed = -10
    player_shoot_delay = 6
    player_shoot_timer = 0

    # Враги
    class Enemy:
        def __init__(self, x, y, enemy_type):
            self.rect = pygame.Rect(x, y, 30, 30)
            self.enemy_type = enemy_type
            self.speed = 3 if enemy_type == "kamikaze" else 2
            self.image = enemy_kamikaze_image if enemy_type == "kamikaze" else enemy_shooter_image
            self.shoot_timer = 0
            self.hit_timer = 0
            self.has_collided = False

        def move(self):
            if self.enemy_type == "kamikaze":
                direction_x = (circle_x - self.rect.x) / max(1, abs(circle_x - self.rect.x))
                direction_y = (circle_y - self.rect.y) / max(1, abs(circle_y - self.rect.y))
                self.rect.x += int(direction_x * self.speed)
                self.rect.y += int(direction_y * self.speed)
            elif self.enemy_type == "shooter":
                self.rect.y += self.speed
                self.shoot_timer += 1
                if self.shoot_timer >= 120:
                    self.shoot_timer = 0
                    angle = math.atan2(circle_y - self.rect.centery, circle_x - self.rect.centerx)
                    enemy_bullets.append([self.rect.centerx, self.rect.centery, angle])

        def update_hit(self):
            if self.hit_timer > 0:
                self.hit_timer -= 1

        def draw(self, screen, shake_x, shake_y):
            if self.hit_timer > 0:
                pass
            screen.blit(self.image, self.rect.move(shake_x, shake_y))

    enemy_spawn_rate = 50

    def spawn_enemy():
        x = random.randint(0, screen_width - 30)
        enemy_type = random.choice(["kamikaze", "shooter"])
        enemies.append(Enemy(x, 0, enemy_type))

    clock = pygame.time.Clock()
    shake_intensity = 0
    shake_duration = 0

    score = 0  # Результат игрока

    while True:  # Цикл игры
        score = 0  # Сброс счёта при каждом новом запуске игры
        reset_game_state()  # Сброс состояния игры
        player_health = 5  # Восстановление здоровья игрока

        while player_health > 0:
            # Основной игровой цикл
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

            player_shoot_timer += 1
            if keys[pygame.K_SPACE] and player_shoot_timer >= player_shoot_delay:
                bullets.append(pygame.Rect(circle_x - 5, circle_y - 10, 10, 10))
                player_shoot_timer = 0

            bullets = [b.move(0, bullet_speed) for b in bullets if b.y > 0]

            enemy_timer += 1
            if enemy_timer >= enemy_spawn_rate:
                spawn_enemy()
                enemy_timer = 0

            to_remove = []
            for enemy in enemies:
                enemy.move()

                if enemy.enemy_type == "kamikaze" and enemy.rect.colliderect(
                        pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)):
                    if not enemy.has_collided:
                        player_health -= 1
                        score -= 1
                        shake_intensity = 20
                        shake_duration = 10
                        enemy.hit_timer = 10
                        enemy.has_collided = True
                        explosions.append({"x": enemy.rect.centerx, "y": enemy.rect.centery, "timer": 10})
                        to_remove.append(enemy)

                for bullet in bullets[:]:
                    if enemy.rect.colliderect(bullet):
                        bullets.remove(bullet)
                        score += 1
                        to_remove.append(enemy)

            for enemy in to_remove:
                if enemy in enemies:
                    enemies.remove(enemy)

            to_remove_bullets = []
            for bullet in enemy_bullets:
                bx, by, angle = bullet

                speed = 4
                bx += int(math.cos(angle) * speed)
                by += int(math.sin(angle) * speed)

                if pygame.Rect(bx - 5, by - 5, 10, 10).colliderect(
                        pygame.Rect(circle_x - 20, circle_y - 20, 40, 40)):
                    player_health -= 1
                    shake_intensity = 20
                    shake_duration = 10
                    to_remove_bullets.append(bullet)

                if by > screen_height or bx < 0 or bx > screen_width:
                    to_remove_bullets.append(bullet)

                bullet[0], bullet[1] = bx, by

            for bullet in to_remove_bullets:
                enemy_bullets.remove(bullet)

            if player_health <= 0:  # Смерть и обновление рекорда
                if score > best_score:
                    best_score = score
                    save_best_score(best_score)
                if not game_over():
                    return best_score
                break

            if shake_duration > 0:
                shake_x = random.randint(-shake_intensity, shake_intensity)
                shake_y = random.randint(-shake_intensity, shake_intensity)
                shake_duration -= 1
            else:
                shake_x, shake_y = 0, 0

            screen.fill(black)
            screen.blit(background, (shake_x, shake_y))

            for enemy in enemies:
                enemy.update_hit()
                enemy.draw(screen, shake_x, shake_y)

            for bullet in bullets:
                screen.blit(bullet_image, bullet.move(shake_x, shake_y))

            for bullet in enemy_bullets:
                screen.blit(enemy_bullet_image, (bullet[0] + shake_x - 10, bullet[1] + shake_y - 10))

            for explosion in explosions[:]:
                pygame.draw.circle(screen, yellow, (explosion["x"] + shake_x, explosion["y"] + shake_y), 20)
                explosion["timer"] -= 1
                if explosion["timer"] <= 0:
                    explosions.remove(explosion)

            player_rect.center = (circle_x + shake_x, circle_y + shake_y)
            screen.blit(player_image, player_rect)

            draw_text(f"HP: {player_health}", pygame.font.Font('KenVector Future.ttf', 36), white, 10, 10)
            draw_text(f"Score: {score}", pygame.font.Font('KenVector Future.ttf', 36), white, 10, 50)
            draw_text(f"Best Score: {best_score}", pygame.font.Font('KenVector Future.ttf', 36), white, 10, 90)

            pygame.display.update()
            clock.tick(60)


def game_over():
    font = pygame.font.Font('KenVector Future.ttf', 40)
    small_font = pygame.font.Font('KenVector Future.ttf', 30)
    while True:
        screen.fill(black)
        draw_text("Game Over", font, red, screen_width // 4, 250)
        draw_text("Press ENTER to start over.", small_font, white, screen_width // 5, 300)
        draw_text("Press ESC to exit.", small_font, white, screen_width // 5, 350)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


best_score = load_best_score()

start_screen()
reset_game_state()
best_score = game_loop(best_score)
