import pygame
import random
import sys
import time
import math
import numpy as np

# تهيئة pygame
pygame.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("لعبة النيران المحسنة")

# ألوان
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 102, 204)
DARK_BLUE = (0, 51, 102)
DARK_RED = (100, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# خطوط
font_large = pygame.font.SysFont("arial", 60, bold=True)
font_medium = pygame.font.SysFont("arial", 40)
font_small = pygame.font.SysFont("arial", 28)

# نظام الأصوات المضمن
class SoundSystem:
    def __init__(self):
        self.sample_rate = 44100
        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            self.initialized = True
        except:
            self.initialized = False
            print("ملاحظة: النظام الصوتي غير فعال - اللعبة ستشتغل بدون صوت")
    
    def generate_tone(self, freq, duration, wave_type='sine', volume=0.5):
        if not self.initialized:
            return None
            
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * freq - np.floor(t * freq + 0.5))
        elif wave_type == 'noise':
            wave = np.random.uniform(-1, 1, len(t))
        
        wave = np.clip(wave * 32767 * volume, -32768, 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=wave)

# إنشاء الأصوات
sound = SoundSystem()
shoot_sound = sound.generate_tone(880, 0.1, 'square', 0.3)
explosion_sound = sound.generate_tone(110, 0.3, 'noise', 0.5)
victory_sound = sound.generate_tone(784, 1.0, 'sine', 0.7)
defeat_sound = sound.generate_tone(196, 1.5, 'sawtooth', 0.7)
boss_sound = sound.generate_tone(220, 0.4, 'square', 0.6)

# إعدادات اللعبة
class Settings:
    def __init__(self):
        self.volume = 0.5
        self.difficulty = 1
        self.language = "ar"
        self.levels = 3
        self.current_level = 1
        self.player_speed = 5
        self.enemy_speed = 2
        self.boss_health = 10

settings = Settings()

# ترجمات
translations = {
    "ar": {
        "start_game": "ابدأ اللعبة",
        "settings": "الإعدادات",
        "exit": "خروج",
        "volume": "الصوت",
        "difficulty": "الصعوبة",
        "language": "اللغة",
        "back": "الرجوع",
        "settings_title": "الإعدادات",
        "arabic": "العربية",
        "english": "الإنجليزية",
        "victory": "!لقد فزت",
        "defeat": "!لقد خسرت",
        "time": "الوقت: ",
        "level": "المستوى: ",
        "health": "الصحة: ",
        "score": "النقاط: ",
        "pause": "توقف",
        "continue": "استمرار",
        "next_level": "المستوى التالي",
        "boss_coming": "!الزعيم قادم",
        "game_over": "انتهت اللعبة",
        "restart": "إعادة التشغيل",
        "use_arrows": "استخدم الأسهم للتحرك",
        "enter_to_select": "اضغط Enter للتحديد",
        "get_ready": "استعد!"
    },
    "en": {
        "start_game": "Start Game",
        "settings": "Settings",
        "exit": "Exit",
        "volume": "Volume",
        "difficulty": "Difficulty",
        "language": "Language",
        "back": "Back",
        "settings_title": "Settings",
        "arabic": "Arabic",
        "english": "English",
        "victory": "You Win!",
        "defeat": "You Lose!",
        "time": "Time: ",
        "level": "Level: ",
        "health": "Health: ",
        "score": "Score: ",
        "pause": "Pause",
        "continue": "Continue",
        "next_level": "Next Level",
        "boss_coming": "Boss Coming!",
        "game_over": "Game Over",
        "restart": "Restart",
        "use_arrows": "Use arrows to navigate",
        "enter_to_select": "Press Enter to select",
        "get_ready": "Get Ready!"
    }
}

def T(key):
    return translations[settings.language].get(key, key)

# فئات اللعبة
class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.width = 80
        self.height = 60
        self.speed = settings.player_speed
        self.health = 100
        self.score = 0
        self.fire_power = 1
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 300
        self.image = None
        self.create_image()
    
    def create_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, BLUE, (0, 10, self.width, self.height-20))
        pygame.draw.polygon(self.image, DARK_BLUE, [(0, self.height//2), (-20, self.height//2+15), (0, self.height//2+10)])
        pygame.draw.polygon(self.image, DARK_BLUE, [(self.width, self.height//2), (self.width+20, self.height//2+15), (self.width, self.height//2+10)])
        pygame.draw.circle(self.image, WHITE, (20, self.height//2), 5)
        pygame.draw.circle(self.image, WHITE, (40, self.height//2), 5)
        pygame.draw.rect(self.image, YELLOW, (self.width-20, self.height//2-5, 20, 10))
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 20, self.width, 10))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 20, self.width * (self.health / 100), 10))
    
    def move(self, keys):
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.bullets.append(Bullet(self.x + self.width, self.y + self.height//2 - 5))
            if shoot_sound:
                shoot_sound.play()
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x > WIDTH:
                self.bullets.remove(bullet)
    
    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.speed = settings.enemy_speed + random.random() * settings.difficulty
        self.health = 1
        self.image = None
        self.create_image()
    
    def create_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, self.width, self.height))
        pygame.draw.circle(self.image, BROWN, (self.width//2, -10), 20)
        pygame.draw.circle(self.image, WHITE, (self.width//2 - 10, -15), 5)
        pygame.draw.circle(self.image, WHITE, (self.width//2 + 10, -15), 5)
        pygame.draw.rect(self.image, DARK_RED, (-15, self.height//3, 15, 10))
        pygame.draw.rect(self.image, DARK_RED, (self.width, self.height//3, 15, 10))
        pygame.draw.rect(self.image, ORANGE, (self.width//2 - 15, self.height - 10, 30, 10))
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def move(self):
        self.x -= self.speed
    
    def hit(self):
        self.health -= 1
        if self.health <= 0:
            if explosion_sound:
                explosion_sound.play()
            return True
        return False

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 120
        self.height = 150
        self.health = settings.boss_health * settings.difficulty
        self.speed = settings.enemy_speed * 0.7
        self.special_attack_cooldown = 0
        self.bullets = []
        self.create_image()
    
    def create_image(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PURPLE, (0, 0, self.width, self.height))
        pygame.draw.circle(self.image, BLACK, (self.width//2, -30), 30)
        pygame.draw.circle(self.image, WHITE, (self.width//2 - 15, -35), 6)
        pygame.draw.circle(self.image, WHITE, (self.width//2 + 15, -35), 6)
        pygame.draw.rect(self.image, RED, (self.width//2 - 30, self.height//2, 60, 15))
        pygame.draw.circle(self.image, ORANGE, (20, self.height - 20), 10)
        pygame.draw.circle(self.image, ORANGE, (self.width - 20, self.height - 20), 10)
    
    def move(self):
        self.x -= self.speed * 0.5
        self.y += math.sin(pygame.time.get_ticks() * 0.001) * 2
    
    def special_attack(self):
        now = pygame.time.get_ticks()
        if now - self.special_attack_cooldown > 3000:
            self.special_attack_cooldown = now
            self.bullets.append(Bullet(self.x, self.y + self.height//2 - 5, -1, ORANGE))
            self.bullets.append(Bullet(self.x, self.y + self.height//4 - 5, -1, ORANGE))
            self.bullets.append(Bullet(self.x, self.y + 3*self.height//4 - 5, -1, ORANGE))
            if boss_sound:
                boss_sound.play()
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x < 0:
                self.bullets.remove(bullet)
    
    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)

class Bullet:
    def __init__(self, x, y, direction=1, color=YELLOW):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 5
        self.speed = 10 * direction
        self.color = color
    
    def move(self):
        self.x += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.growing = True
    
    def update(self):
        if self.growing:
            self.radius += 2
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 2
        return self.radius <= 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius - 5)
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius - 10)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = random.choice([RED, ORANGE, YELLOW])
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        return self.lifetime <= 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# وظائف العرض
def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    if center:
        rect = surface.get_rect(center=(x, y))
        screen.blit(surface, rect)
    else:
        screen.blit(surface, (x, y))

def show_menu():
    selected = 0
    options = ["start_game", "settings", "exit"]
    
    while True:
        screen.fill(BLACK)
        for i in range(0, WIDTH, 50):
            for j in range(0, HEIGHT, 50):
                pygame.draw.rect(screen, (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)), 
                               (i, j, 50, 50), 1)
        
        draw_text("🔥 " + T("start_game") + " 🔥", font_large, RED, WIDTH//2, 100, True)
        
        for i, opt in enumerate(options):
            color = GREEN if i == selected else WHITE
            draw_text(T(opt), font_medium, color, WIDTH//2, 250 + i * 60, True)
        
        draw_text("الإصدار 2.0 | لعبة النيران المحسنة", font_small, GRAY, 10, HEIGHT - 30)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    opt = options[selected]
                    if opt == "start_game":
                        return
                    elif opt == "settings":
                        show_settings()
                    elif opt == "exit":
                        pygame.quit()
                        sys.exit()

def show_settings():
    selected = 0
    options = ["volume", "difficulty", "language", "back"]
    
    while True:
        screen.fill(BLACK)
        draw_text(T("settings_title"), font_large, WHITE, WIDTH//2, 80, True)
        
        for i, opt in enumerate(options):
            color = GREEN if i == selected else WHITE
            value = ""
            if opt == "volume":
                value = f": {int(settings.volume * 100)}%"
            elif opt == "difficulty":
                value = f": {settings.difficulty}"
            elif opt == "language":
                lang_names = {"ar": T("arabic"), "en": T("english")}
                value = f": {lang_names[settings.language]}"
            
            draw_text(T(opt) + value, font_medium, color, WIDTH//2, 200 + i * 60, True)
        
        draw_text(T("use_arrows"), font_small, GRAY, WIDTH//2, HEIGHT - 100, True)
        draw_text(T("enter_to_select"), font_small, GRAY, WIDTH//2, HEIGHT - 60, True)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    opt = options[selected]
                    if opt == "back":
                        return
                elif event.key == pygame.K_LEFT:
                    opt = options[selected]
                    if opt == "volume" and settings.volume > 0:
                        settings.volume = round(settings.volume - 0.1, 1)
                        if sound.initialized:
                            pygame.mixer.music.set_volume(settings.volume)
                    elif opt == "difficulty" and settings.difficulty > 1:
                        settings.difficulty -= 1
                elif event.key == pygame.K_RIGHT:
                    opt = options[selected]
                    if opt == "volume" and settings.volume < 1:
                        settings.volume = round(settings.volume + 0.1, 1)
                        if sound.initialized:
                            pygame.mixer.music.set_volume(settings.volume)
                    elif opt == "difficulty" and settings.difficulty < 5:
                        settings.difficulty += 1
                    elif opt == "language":
                        settings.language = "en" if settings.language == "ar" else "ar"

def show_level_intro(level):
    screen.fill(BLACK)
    if level == settings.levels:
        draw_text(T("boss_coming"), font_large, RED, WIDTH//2, HEIGHT//2 - 50, True)
    else:
        draw_text(f"{T('level')} {level}", font_large, GREEN, WIDTH//2, HEIGHT//2 - 50, True)
    
    draw_text(T("get_ready"), font_medium, WHITE, WIDTH//2, HEIGHT//2 + 50, True)
    pygame.display.flip()
    time.sleep(3)

def show_victory_screen(total_time, score):
    screen.fill(BLACK)
    if victory_sound:
        victory_sound.play()
    
    draw_text(T("victory"), font_large, GREEN, WIDTH//2, HEIGHT//2 - 100, True)
    draw_text(f"{T('time')}{int(total_time)}s", font_medium, WHITE, WIDTH//2, HEIGHT//2, True)
    draw_text(f"{T('score')}{score}", font_medium, YELLOW, WIDTH//2, HEIGHT//2 + 50, True)
    
    pygame.display.flip()
    time.sleep(5)

def show_defeat_screen():
    screen.fill(BLACK)
    if defeat_sound:
        defeat_sound.play()
    
    draw_text(T("defeat"), font_large, RED, WIDTH//2, HEIGHT//2 - 50, True)
    draw_text(T("restart"), font_medium, WHITE, WIDTH//2, HEIGHT//2 + 50, True)
    
    pygame.display.flip()
    time.sleep(3)

def show_pause_screen():
    draw_text(T("pause"), font_large, WHITE, WIDTH//2, HEIGHT//2 - 50, True)
    draw_text(T("continue"), font_medium, GREEN, WIDTH//2, HEIGHT//2 + 50, True)
    pygame.display.flip()
    
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_RETURN:
                    paused = False
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
    return "continue"

def game_loop():
    player = Player()
    enemies = []
    explosions = []
    particles = []
    boss = None
    level_complete = False
    game_over = False
    victory = False
    start_time = time.time()
    last_enemy_spawn = 0
    enemy_spawn_delay = 2000 - (settings.difficulty * 200)
    
    show_level_intro(settings.current_level)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_p:
                    pause_start = time.time()
                    result = show_pause_screen()
                    if result == "menu":
                        return "menu"
                    start_time += time.time() - pause_start
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update_bullets()
        
        now = pygame.time.get_ticks()
        if now - last_enemy_spawn > enemy_spawn_delay and len(enemies) < 5 + settings.difficulty and boss is None:
            last_enemy_spawn = now
            enemies.append(Enemy(WIDTH, random.randint(50, HEIGHT - 100)))
        
        for enemy in enemies[:]:
            enemy.move()
            
            for bullet in player.bullets[:]:
                if (bullet.x < enemy.x + enemy.width and bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and bullet.y + bullet.height > enemy.y):
                    player.bullets.remove(bullet)
                    if enemy.hit():
                        enemies.remove(enemy)
                        explosions.append(Explosion(enemy.x + enemy.width//2, enemy.y + enemy.height//2))
                        player.score += 10 * settings.difficulty
                        for _ in range(20):
                            particles.append(Particle(enemy.x + enemy.width//2, enemy.y + enemy.height//2))
                    break
            
            if (player.x < enemy.x + enemy.width and player.x + player.width > enemy.x and
                player.y < enemy.y + enemy.height and player.y + player.height > enemy.y):
                player.health -= 10
                enemies.remove(enemy)
                explosions.append(Explosion(enemy.x + enemy.width//2, enemy.y + enemy.height//2))
                if player.health <= 0:
                    game_over = True
        
        if settings.current_level == settings.levels and len(enemies) == 0 and boss is None:
            boss = Boss(WIDTH, HEIGHT//2 - 75)
        
        if boss:
            boss.move()
            boss.special_attack()
            boss.update_bullets()
            
            for bullet in player.bullets[:]:
                if (bullet.x < boss.x + boss.width and bullet.x + bullet.width > boss.x and
                    bullet.y < boss.y + boss.height and bullet.y + bullet.height > boss.y):
                    player.bullets.remove(bullet)
                    if boss.hit():
                        explosions.append(Explosion(boss.x + boss.width//2, boss.y + boss.height//2))
                        player.score += 100 * settings.difficulty
                        victory = True
                        for _ in range(50):
                            particles.append(Particle(boss.x + boss.width//2, boss.y + boss.height//2))
                    break
            
            for bullet in boss.bullets[:]:
                if (bullet.x + bullet.width > player.x and bullet.x < player.x + player.width and
                    bullet.y + bullet.height > player.y and bullet.y < player.y + player.height):
                    boss.bullets.remove(bullet)
                    player.health -= 15
                    if player.health <= 0:
                        game_over = True
            
            if (player.x < boss.x + boss.width and player.x + player.width > boss.x and
                player.y < boss.y + boss.height and player.y + player.height > boss.y):
                player.health -= 20
                if player.health <= 0:
                    game_over = True
        
        for explosion in explosions[:]:
            if explosion.update():
                explosions.remove(explosion)
        
        for particle in particles[:]:
            if particle.update():
                particles.remove(particle)
        
        if settings.current_level < settings.levels and len(enemies) == 0 and not level_complete:
            level_complete = True
            level_end_time = time.time()
        
        if level_complete and time.time() - level_end_time > 2:
            settings.current_level += 1
            return "next_level"
        
        if game_over:
            show_defeat_screen()
            return "game_over"
        
        if victory:
            total_time = time.time() - start_time
            show_victory_screen(total_time, player.score)
            return "victory"
        
        screen.fill(BLACK)
        
        for _ in range(5):
            pygame.draw.circle(screen, WHITE, 
                             (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 
                             random.randint(1, 2))
        
        player.draw(screen)
        player.draw_bullets(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        if boss:
            boss.draw(screen)
            boss.draw_bullets(screen)
        
        for explosion in explosions:
            explosion.draw(screen)
        
        for particle in particles:
            particle.draw(screen)
        
        draw_text(f"{T('level')}{settings.current_level}", font_small, WHITE, 10, 10)
        draw_text(f"{T('health')}{player.health}", font_small, WHITE, 10, 40)
        draw_text(f"{T('score')}{player.score}", font_small, WHITE, 10, 70)
        draw_text(f"{T('time')}{int(time.time() - start_time)}s", font_small, WHITE, WIDTH - 150, 10)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "menu"

def main():
    global settings
    
    while True:
        show_menu()
        settings.current_level = 1
        
        while True:
            result = game_loop()
            
            if result == "menu":
                break
            elif result == "next_level":
                show_level_intro(settings.current_level)
            elif result == "game_over":
                break
            elif result == "victory":
                settings.current_level = 1
                break

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
