import pgzrun
import random
import math
from pygame import Rect

# --- Constantes ---
WIDTH, HEIGHT = 800, 600
PLAYER_SPEED = 200.0
ENEMY_BASE_SPEED = 80.0 
BULLET_SPEED = 450.0
ANIMATION_SPEED = 6 
BULLET_LIFETIME = 2.0
PLAYER_INITIAL_LIVES = 10
PLAYER_INVINCIBILITY_DURATION = 1.5
ENEMY_CORPSE_DURATION = 2.0
PLAYER_SHOOT_DELAY = 0.25
FLYING_EYE_ATTACK_RANGE = 40 
ENEMY_STOP_RADIUS = 30 
BG_WIDTH, BG_HEIGHT = 4690, 4690
DIFFICULTY_INCREASE_INTERVAL = 5.0
SPAWN_INTERVAL_BASE = 3.5
SPAWN_INTERVAL_MIN = 0.4
DIFFICULTY_MULTIPLIER_START = 1.2

# --- Nomes dos Arquivos de Música ---
MENU_MUSIC = '2021-08-17_-_8_bit_nostalgia_-_www.fesliyanstudios.com'
GAME_MUSIC = '2019-12-11_-_retro_platforming_-_david_fesliyan'

# --- Configuração dos Assets ---
PLAYER_FOLDER = 'diego/'
PLAYER_ANIMATIONS = {
    'idle':  {'subfolder': 'processed_idle/', 'prefix': 'idle', 'num_frames': 4, 'loop': True},
    'run':   {'subfolder': 'processed_running/', 'prefix': 'running',  'num_frames': 6, 'loop': True},
    'shooting_while_standing': {'subfolder': 'processed_shooting_while_standing/', 'prefix': 'shooting_while_standing', 'num_frames': 2, 'loop': True},
    'shooting_while_running': {'subfolder': 'processed_shooting_while_running/', 'prefix': 'shooting_while_running', 'num_frames': 6, 'loop': True},
    'hurt':      {'subfolder': '', 'prefix': 'hurt', 'num_frames': 1, 'loop': False, 'is_single_file': True},
}
PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT = 32, 48 
BULLET_IMAGE_PATH = f'{PLAYER_FOLDER}bullet.png'

FLYING_EYE_FOLDER = 'flying_eye/'
FLYING_EYE_ANIMATIONS = {
    'fly':    {'prefix': 'fly', 'num_frames': 8, 'loop': True},
    'attack': {'prefix': 'attack', 'num_frames': 8, 'loop': True, 'impact_frame': 4},
    'death':  {'prefix': 'death', 'num_frames': 4, 'loop': False},
}
FLYING_EYE_FRAME_WIDTH, FLYING_EYE_FRAME_HEIGHT = 48, 48 
FLYING_EYE_HEALTH = 3

# --- Estado Global ---
game_state = 'menu'  # Começa no menu
music_on = True      # Música começa ligada
world_x, world_y = 0.0, 0.0; player_lives = 0; player_is_invincible, player_invincible_timer = False, 0.0
player_state, player_anim_frame, player_anim_timer = 'idle', 0, 0; player_is_moving, player_is_shooting = False, False
player_last_dx, player_last_dy = 1.0, 0.0; player_shoot_cooldown = 0.0; enemies, bullets = [], []
horde_timer = 0.0; difficulty_level = 1.0; difficulty_timer = 0.0; player = None # Jogador começa como None

# --- Background ---
try: background = Actor('background.jpg'); background.width = BG_WIDTH; background.height = BG_HEIGHT
except Exception: background = Actor('color:#202030', (WIDTH, HEIGHT)); background.pos = WIDTH / 2, HEIGHT / 2

# --- Botões do Menu ---
buttons = []
button_w, button_h = 300, 50; button_x = WIDTH // 2 - button_w // 2
button_start_y = HEIGHT // 2 - 70; button_spacing = 75
start_button_rect = Rect(button_x, button_start_y, button_w, button_h)
buttons.append({'text': "Começar o jogo", 'rect': start_button_rect, 'action': 'start'})
music_button_rect = Rect(button_x, button_start_y + button_spacing, button_w, button_h)
buttons.append({'text': "Música e sons: ON", 'rect': music_button_rect, 'action': 'toggle_music'}) # O texto será atualizado no draw
exit_button_rect = Rect(button_x, button_start_y + 2 * button_spacing, button_w, button_h)
buttons.append({'text': "Saída", 'rect': exit_button_rect, 'action': 'exit'})

# --- Inimigo ---
class FlyingEye:
    def __init__(self, world_pos):
        self.folder, self.animations = FLYING_EYE_FOLDER, FLYING_EYE_ANIMATIONS; self.state = 'fly'; self.anim_frame, self.anim_timer = 0, 0
        self.current_anim_info = self.animations[self.state]; self.is_alive, self.death_anim_finished = True, False; self.health = FLYING_EYE_HEALTH
        self.world_x, self.world_y = world_pos[0], world_pos[1]; self.corpse_timer = 0.0
        try: initial_image = f"{self.folder}{self.current_anim_info['prefix']}_0.png"; self.actor = Actor(initial_image, (-100,-100)); self.actor.width, self.actor.height = FLYING_EYE_FRAME_WIDTH, FLYING_EYE_FRAME_HEIGHT
        except Exception as e: print(f"ERRO FlyingEye img: {e}"); self.is_alive = False; self.actor=Actor('color:red',(0,0))

    def set_state(self, new_state):
        if self.state != new_state and new_state in self.animations: self.state = new_state; self.anim_frame = 0; self.anim_timer = 0; self.current_anim_info = self.animations[self.state]; self._update_actor_image()

    def _update_actor_image(self):
        if self.death_anim_finished and self.corpse_timer >= ENEMY_CORPSE_DURATION: return
        img_path = None
        try:
            anim_info = self.current_anim_info
            num_frames = anim_info['num_frames']
            frame_idx = min(self.anim_frame, num_frames - 1)
            img_path = f"{self.folder}{anim_info['prefix']}_{frame_idx}.png"
            if self.actor.image != img_path: self.actor.image = img_path
        except KeyError: print(f"Erro _update_actor_image: Estado '{self.state}' inválido.")
        except Exception as e: error_img_path = img_path if img_path is not None else "(caminho não definido)"; print(f"Erro definir img FlyingEye (Estado: {self.state}, Frame Idx: {self.anim_frame}): {e}")

    def update_animation(self):
        if self.death_anim_finished: return
        try: self.current_anim_info = self.animations[self.state]
        except KeyError: return
        num_f, loops = self.current_anim_info.get('num_frames', 1), self.current_anim_info.get('loop', False)
        if num_f <= 1: self._update_actor_image(); return
        self.anim_timer += 1
        if self.anim_timer >= ANIMATION_SPEED:
            self.anim_timer = 0; next_f = self.anim_frame + 1
            if next_f >= num_f: self.anim_frame = 0 if loops else num_f - 1; self.death_anim_finished = (self.state == 'death' and not loops)
            else: self.anim_frame = next_f
            self._update_actor_image()
# --- Movimentação ---
    def move(self, dt):
        if not self.is_alive or self.state != 'fly':
             return

        p_wx, p_wy = player.x + world_x, player.y + world_y

        dist_sq = (self.world_x - p_wx)**2 + (self.world_y - p_wy)**2
        stop_radius_sq = ENEMY_STOP_RADIUS**2 # Calcula o raio ao quadrado uma vez

        if dist_sq > stop_radius_sq:
            angle = math.atan2(p_wy - self.world_y, p_wx - self.world_x)
            current_speed = ENEMY_BASE_SPEED * difficulty_level
            dist_to_move = current_speed * dt

            self.world_x += math.cos(angle) * dist_to_move
            self.world_y += math.sin(angle) * dist_to_move

            self.world_x=max(0, min(BG_WIDTH, self.world_x))
            self.world_y=max(0, min(BG_HEIGHT, self.world_y))
    def decide_action(self):
         if not self.is_alive: self.set_state('death'); return
         p_wx, p_wy = player.x + world_x, player.y + world_y; dist_sq = (self.world_x - p_wx)**2 + (self.world_y - p_wy)**2
         range_sq = FLYING_EYE_ATTACK_RANGE**2; state = self.state
         if dist_sq < range_sq and state != 'attack': self.set_state('attack')
         elif dist_sq >= range_sq and state == 'attack': self.set_state('fly')
    def take_damage(self, amount=1):
        if not self.is_alive: return
        self.health -= amount;
        if self.health <= 0: self.set_state('death')
    def update(self, dt):
        if self.is_alive: self.decide_action(); self.move(dt);
        self.update_animation();
        if self.death_anim_finished: self.corpse_timer += dt

# --- Lógica das Balas ---
def spawn_bullet():
    global player_last_dx, player_last_dy; target_enemy, min_dist_sq = None, float('inf')
    p_wcx, p_wcy = player.centerx + world_x, player.centery + world_y
    for e in enemies:
        if e.is_alive and e.state != 'death': # Mira Corrigida
            dist_sq = (e.world_x - p_wcx)**2 + (e.world_y - p_wcy)**2;
            if dist_sq < min_dist_sq: min_dist_sq = dist_sq; target_enemy = e
    if target_enemy: angle_rad = math.atan2(target_enemy.world_y - p_wcy, target_enemy.world_x - p_wcx)
    else: dist=math.hypot(player_last_dx, player_last_dy); dx, dy = (player_last_dx/dist, player_last_dy/dist) if dist>0 else (1.0, 0.0); angle_rad = math.atan2(dy, dx)
    try: b_actor=Actor(BULLET_IMAGE_PATH,(-100,-100)); bullets.append({'x':p_wcx, 'y':p_wcy, 'angle':angle_rad, 'actor':b_actor, 'timer':0.0})
    except Exception as e: print(f"Erro Actor bala: {e}")

def update_bullets(dt):
    speed = BULLET_SPEED * dt
    for b in bullets[:]:
        b['x'] += math.cos(b['angle'])*speed; b['y'] += math.sin(b['angle'])*speed; b['timer'] += dt
        if b['timer'] > BULLET_LIFETIME or not (0<b['x']<BG_WIDTH) or not (0<b['y']<BG_HEIGHT): bullets.remove(b); continue
        b['actor'].pos = (b['x']-world_x, b['y']-world_y)
        for e in enemies:
            if e.is_alive: e.actor.pos = (e.world_x - world_x, e.world_y - world_y);
            if e.is_alive and b['actor'].colliderect(e.actor): e.take_damage(1); bullets.remove(b); break

# --- Funções do Jogo ---
def spawn_enemy():
    side=random.randint(0,3); dist_out=50; wx,wy=0,0
    if side==0: wx,wy=world_x+random.randint(0,WIDTH), world_y-dist_out
    elif side==1: wx,wy=world_x+random.randint(0,WIDTH), world_y+HEIGHT+dist_out
    elif side==2: wx,wy=world_x-dist_out, world_y+random.randint(0,HEIGHT)
    else: wx,wy=world_x+WIDTH+dist_out, world_y+random.randint(0,HEIGHT)
    wx=max(FLYING_EYE_FRAME_WIDTH/2, min(BG_WIDTH-FLYING_EYE_FRAME_WIDTH/2, wx)); wy=max(FLYING_EYE_FRAME_HEIGHT/2, min(BG_HEIGHT-FLYING_EYE_FRAME_HEIGHT/2, wy))
    enemies.append(FlyingEye((wx, wy)))

def update_player_and_world(dt):
    global world_x, world_y, player_state, player_anim_frame, player_anim_timer, player_shoot_cooldown
    global player_is_moving, player_is_shooting, player_last_dx, player_last_dy, player_is_invincible, player_invincible_timer, player
    if player is None: return
    # --- Controle de Invencibilidade ---
    if player_is_invincible:
        player_invincible_timer -= dt
        image_path = None 
        if 'hurt' in PLAYER_ANIMATIONS:
            anim_info = PLAYER_ANIMATIONS['hurt']
            image_path = f"{PLAYER_FOLDER}{anim_info['prefix']}.png" 
            if player_state != 'hurt':
                player_state='hurt'; player.state='hurt'; player_anim_frame=0; player_anim_timer=0;
                if player.image != image_path: player.image = image_path
            elif player.image != image_path:
                 player.image = image_path
        if player_invincible_timer <= 0:
            player_is_invincible = False;
            if player_state == 'hurt': 
                player_state='idle'; player.state='idle'; player_anim_frame=0; player_anim_timer=0

    dx, dy = 0.0, 0.0;
    if keyboard.w: dy-=1.0
    if keyboard.s: dy+=1.0
    if keyboard.a: dx-=1.0
    if keyboard.d: dx+=1.0
    player_is_moving = (dx != 0 or dy != 0)
    if player_is_moving:
        player_last_dx, player_last_dy = dx, dy
        dist=math.hypot(dx, dy); scroll=PLAYER_SPEED*dt; world_x+=(dx/dist)*scroll; world_y+=(dy/dist)*scroll
        world_x=max(0.0, min(BG_WIDTH-WIDTH, world_x)); world_y=max(0.0, min(BG_HEIGHT-HEIGHT, world_y))

    # --- Definição do Estado do Jogador ---
    if player_is_invincible: new_state = 'hurt' if 'hurt' in PLAYER_ANIMATIONS else player_state
    elif player_is_shooting: new_state = 'shooting_while_running' if player_is_moving else 'shooting_while_standing'
    else: new_state = 'run' if player_is_moving else 'idle'
    if new_state not in PLAYER_ANIMATIONS: new_state = 'run' if player_is_moving else 'idle' # Fallback
    if new_state != player_state: player_state = new_state; player.state = new_state; player_anim_frame = 0; player_anim_timer = 0

    # --- Animação do Jogador ---
    img_path = None
    if player_state in PLAYER_ANIMATIONS:
        info, n_frames = PLAYER_ANIMATIONS[player_state], PLAYER_ANIMATIONS[player_state]['num_frames']
        if n_frames <= 1 or info.get('is_single_file', False): img_path = f"{PLAYER_FOLDER}{info['prefix']}.png"; player_anim_timer=0; player_anim_frame=0 # Estático
        else: 
            player_anim_timer += 1;
            if player_anim_timer >= ANIMATION_SPEED: player_anim_timer = 0; player_anim_frame = (player_anim_frame + 1) % n_frames
            folder, prefix = info['subfolder'], info['prefix']; img_path = f"{PLAYER_FOLDER}{folder}{prefix}_{player_anim_frame}.png"
        if img_path is not None and player.image != img_path:
            try: player.image = img_path
            except Exception as e: print(f"Erro set img jogador: {img_path} - {e}")
    player_shoot_cooldown -= dt
    if player_is_shooting and player_shoot_cooldown <= 0 and not player_is_invincible: spawn_bullet(); player_shoot_cooldown = PLAYER_SHOOT_DELAY

def reset_game_state():
    """Reinicia as variáveis para um novo jogo."""
    global world_x, world_y, player_lives, player_is_invincible, player_invincible_timer
    global player_state, player_anim_frame, player_anim_timer, player_is_moving, player_is_shooting
    global player_last_dx, player_last_dy, player_shoot_cooldown, enemies, bullets
    global horde_timer, difficulty_level, difficulty_timer, player

    print("Reiniciando estado do jogo...")
    world_x, world_y = (BG_WIDTH - WIDTH) / 2.0, (BG_HEIGHT - HEIGHT) / 2.0
    player_lives = PLAYER_INITIAL_LIVES
    player_is_invincible, player_invincible_timer = False, 0.0
    player_state, player_anim_frame, player_anim_timer = 'idle', 0, 0
    player_is_moving, player_is_shooting = False, False
    player_last_dx, player_last_dy = 1.0, 0.0
    player_shoot_cooldown = 0.0
    enemies, bullets = [], []
    horde_timer = 0.0
    difficulty_level = DIFFICULTY_MULTIPLIER_START
    difficulty_timer = 0.0

    player_screen_pos = (WIDTH // 2, HEIGHT // 2)
    try:
        player_anim_info = PLAYER_ANIMATIONS[player_state]
        player_initial_image = f"{PLAYER_FOLDER}{player_anim_info['subfolder']}{player_anim_info['prefix']}_0.png"
        player = Actor(player_initial_image, player_screen_pos)
        player.width = PLAYER_FRAME_WIDTH; player.height = PLAYER_FRAME_HEIGHT
        player.state = player_state
        print("Jogador recriado.")
    except Exception as e: print(f"ERRO JOGADOR no reset: {e}"); player = None

    spawn_enemy() 
# --- Loop Principal 
def update(dt):
    global game_state, horde_timer, player_lives, player_is_invincible, player_invincible_timer, player_state, player_anim_frame, player_anim_timer
    global difficulty_level, difficulty_timer
    try:
        if not music_on and music.is_playing():
            music.stop()
    except: 
        pass
    if game_state == 'playing':
        if player is None: print("Erro: Jogador não existe."); game_state = 'menu'; return
        # Atualizações
        update_player_and_world(dt); update_bullets(dt)
        for e in enemies[:]: e.update(dt)
        for e in enemies[:]:
            if e.death_anim_finished and e.corpse_timer >= ENEMY_CORPSE_DURATION: enemies.remove(e)
        # Dificuldade
        difficulty_timer += dt
        if difficulty_timer >= DIFFICULTY_INCREASE_INTERVAL: difficulty_level += 0.15; difficulty_timer = 0.0; 
        # Spawner
        horde_timer += dt; spawn_interval = max(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_BASE / difficulty_level)
        if horde_timer > spawn_interval: spawn_enemy(); horde_timer = 0
        # Colisão Jogador-Inimigo
        player_rect_world = Rect(player.left + world_x, player.top + world_y, player.width, player.height)
        for e in enemies:
             if e.is_alive:
                enemy_rect_world = Rect(e.world_x - e.actor.width/2, e.world_y - e.actor.height/2, e.actor.width, e.actor.height)
                if (not player_is_invincible) and player_rect_world.colliderect(enemy_rect_world):
                    impact_frame = e.animations.get(e.state, {}).get('impact_frame', None)
                    if e.state == 'attack' and (impact_frame is None or e.anim_frame == impact_frame):
                        # --- Lógica de Dano ---
                        player_lives -= 1; print(f"Player hit! Lives left: {player_lives}")
                        if player_lives <= 0:
                            print("GAME OVER")
                            game_state = 'menu' 
                            music.stop()        
                            if music_on:
                                try:
                                    music.play(MENU_MUSIC)
                                    music.set_volume(0.5)
                                except Exception as err:
                                    print(f"Erro tocar menu pós-GO: {err}")
                        else: 
                            player_is_invincible = True; player_invincible_timer = PLAYER_INVINCIBILITY_DURATION
                            if 'hurt' in PLAYER_ANIMATIONS:
                                 player_state = 'hurt'; player.state = 'hurt'; player_anim_frame = 0; player_anim_timer = 0
                                 anim_info = PLAYER_ANIMATIONS['hurt']; image_path = f"{PLAYER_FOLDER}{anim_info['prefix']}.png"; player.image = image_path
                        break 
def draw():
    global music_on 
    screen.clear()
    if game_state == 'menu':
        # --- Desenho do Menu ---
        screen.fill((30, 30, 50)) 
        for i, button in enumerate(buttons):
            if button['action'] == 'toggle_music': button['text'] = f"Música e sons: {'ON' if music_on else 'OFF'}"
            screen.draw.filled_rect(button['rect'], (60, 60, 90)); screen.draw.rect(button['rect'], "white")
            screen.draw.textbox(button['text'], button['rect'], color="white", align="center")

    elif game_state == 'playing':
        # --- Desenho do Jogo ---
        if player is None: screen.draw.text("ERRO", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="red"); return
        background.topleft = (-world_x, -world_y); background.draw()
        for item_list in [enemies, bullets]:
            for item in item_list:
                actor = item.actor if isinstance(item, FlyingEye) else item['actor']; world_pos_x = item.world_x if isinstance(item, FlyingEye) else item['x']; world_pos_y = item.world_y if isinstance(item, FlyingEye) else item['y']
                should_draw = not (isinstance(item, FlyingEye) and item.death_anim_finished and item.corpse_timer >= ENEMY_CORPSE_DURATION)
                if should_draw: actor.pos = (world_pos_x - world_x, world_pos_y - world_y);
                if should_draw and actor.colliderect(screen.surface.get_rect()): actor.draw() 
        # Jogador e UI
        if player_is_invincible and int(player_invincible_timer * 10) % 2 != 0: pass 
        else: player.draw()
        screen.draw.text(f"LIFE: {player_lives}", topleft=(10, 10), color="white", fontsize=32, owidth=1, ocolor="black")
        difficulty_display = max(1, 1 + math.floor((difficulty_level - DIFFICULTY_MULTIPLIER_START) / 0.30))
        screen.draw.text(f"DIFICULDADE: {difficulty_display}", topright=(WIDTH - 10, 10), color="white", fontsize=32, owidth=1, ocolor="black")

def on_key_down(key):
    global player_is_shooting
    if game_state == 'playing' and player is not None: 
        if key == keys.SPACE: player_is_shooting = True

def on_key_up(key):
    global player_is_shooting
    if game_state == 'playing':
        if key == keys.SPACE: player_is_shooting = False

def on_mouse_down(pos):
    global game_state, music_on, player 
    if game_state == 'menu':
        for i, button in enumerate(buttons):
            if button['rect'].collidepoint(pos):
                action = button['action']
                print(f"Button clicked: {action}") 
                if action == 'start':
                    reset_game_state() 
                    if player is not None: 
                        game_state = 'playing' 
                        music.stop() 
                        if music_on: 
                            try: music.play(GAME_MUSIC); music.set_volume(0.5)
                            except Exception as e: print(f"Erro tocar música jogo: {e}")
                    else: print("Falha ao iniciar: Jogador não criado.") 
                elif action == 'toggle_music':
                    music_on = not music_on 
                    if music_on:
                        if game_state == 'menu':
                             try: music.play(MENU_MUSIC); music.set_volume(0.5)
                             except Exception as e: print(f"Erro tocar música menu: {e}")
                    else: music.stop()
                elif action == 'exit':
                    exit() 
                break 
# --- Início ---
if music_on:
     try: music.play(MENU_MUSIC); music.set_volume(0.5)
     except Exception as e: print(f"Erro ao tocar música inicial: {e}")

pgzrun.go()