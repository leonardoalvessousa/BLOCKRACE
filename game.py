import random
from pgzero.actor import Actor
from pgzero.keyboard import keys, keyboard
import math
from pgzero import music
from typing import TYPE_CHECKING

# Este bloco e para ferramentas de verificacao de tipo como o Pylance.
# Ajuda com sugestoes de codigo e deteccao de erros.
if TYPE_CHECKING:
    import pgzero.loaders
    sounds: pgzero.loaders._SoundLoader  # Apenas para o Pylance nao reclamar

# Tenta importar o objeto screen. Se falhar, significa que nao estamos num ambiente Pygame Zero.
try:
    from pgzero.screen import screen
except ImportError:
    pass

# Dimensoes e titulo da janela do jogo.
WIDTH = 400
HEIGHT = 600
TITLE = "Vertical Platformer estilo Pou"

# Define cores usando tuplas RGB.
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)

# Constantes de fisica do jogo.
GRAVITY = 0.4
JUMP_VELOCITY = -10
PLAYER_SPEED = 4
ROTATION_SPEED = 5
MAX_ROTATION = 20

# Propriedades da plataforma.
BRICK_IMAGES = ['brick1', 'brick2', 'brick3', 'brick4']
BRICK_WIDTH = 60
BRICK_HEIGHT = 20

# Configuracao do personagem do jogador.
player = Actor("player_block", (WIDTH // 2, HEIGHT - 100))
player_y_velocity = 0
player_highest_y = player.y # Rastreia o ponto mais alto que o jogador alcancou.

# Configuracao do personagem do bot.
bot = Actor("bot", (WIDTH // 3, HEIGHT - 100))
bot_y_velocity = 0
bot_direction = 1 # 1 para direita, -1 para esquerda.
bot_active = True # O bot esta atualmente no jogo?
bot_triggered = True # O bot iniciou sua logica de movimento?
next_bot_spawn_height = -600 # Coordenada Y para o proximo spawn do bot.

# Variaveis de animacao de spawn do bot.
bot_spawning = False
bot_spawn_alpha = 0.0
bot_spawn_pos = (0, 0)

# Elementos do jogo.
platforms = []
camera_y = 0 # Deslocamento vertical da camera.

# Variaveis de animacao de salto do jogador.
bounce_anim_timer = 0.0
BOUNCE_ANIM_DURATION = 0.5
is_bouncing = False

# Variaveis de animacao de salto do bot.
bot_bounce_timer = 0.0
bot_is_bouncing = False

# Variaveis de efeito de particulas.
particles = []
PARTICLE_LIFETIME = 0.5
PARTICLE_GRAVITY = 300
PARTICLE_SIZE = 6
PARTICLE_SPEED = 80
PARTICLE_COLORS = [
    (255, 200, 200, 120),
    (255, 255, 200, 120),
    (200, 255, 255, 120),
    (200, 200, 255, 120),
    (230, 255, 230, 120),
]

# Estado do jogo.
game_state = 'start'

# Ajusta volumes individuais dos sons de pulo.
sounds.jump_player.set_volume(0.3) # Volume do som de pulo do jogador.
sounds.jump_bot.set_volume(0.1)    # Volume do som de pulo do bot.

# Volume e reproducao da musica.
music.set_volume(0.2)
music.play("music")

# Variavel para rastrear se a tecla espaco foi pressionada no ultimo quadro.
space_pressed_last_frame = False

# Atores das telas do jogo.
start_screen = Actor("start", (WIDTH // 2, HEIGHT // 2))
load_screen = Actor("load", (WIDTH // 2, HEIGHT // 2))
gameover_screen = Actor("gameover", (WIDTH // 2, HEIGHT // 2))

# Funcao para reiniciar o jogo para o estado inicial.
def reset_game():
    global platforms, player, player_y_velocity, player_highest_y, camera_y, is_bouncing, bounce_anim_timer
    global bot, bot_y_velocity, bot_direction, bot_is_bouncing, bot_bounce_timer, bot_active, bot_triggered, next_bot_spawn_height
    global particles, bot_spawning, bot_spawn_alpha, bot_spawn_pos

    # Limpa e redefine os elementos do jogo.
    platforms = []
    player.pos = (WIDTH // 2, HEIGHT - 100)
    player.angle = 0
    player_y_velocity = 0
    player_highest_y = player.y

    bot.pos = (WIDTH // 3, HEIGHT - 100)
    bot.angle = 0
    bot_y_velocity = 0
    bot_direction = 1
    bot_is_bouncing = False
    bot_bounce_timer = 0.0
    bot_active = True
    bot_triggered = True
    next_bot_spawn_height = -600

    bot_spawning = False
    bot_spawn_alpha = 0.0
    bot_spawn_pos = (0, 0)

    camera_y = 0
    is_bouncing = False
    bounce_anim_timer = 0.0

    particles.clear()

    # Cria as plataformas iniciais do chao.
    for i in range(0, WIDTH, BRICK_WIDTH):
        brick_img = random.choice(BRICK_IMAGES)
        tile = Actor(brick_img, (i + BRICK_WIDTH // 2, HEIGHT - BRICK_HEIGHT // 2))
        platforms.append(tile)

    # Cria as plataformas flutuantes iniciais.
    y = HEIGHT - 120
    for _ in range(6):
        x = random.randint(50, WIDTH - 50)
        platforms.append(Actor(random.choice(BRICK_IMAGES), (x, y)))
        y -= 100

# Funcao para criar efeitos de particulas.
def spawn_particles(x, y, count=10):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0, PARTICLE_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed * 0.5 - 50
        color = random.choice(PARTICLE_COLORS)
        particles.append({
            'pos': [x, y],
            'vel': [vx, vy],
            'lifetime': PARTICLE_LIFETIME,
            'size': PARTICLE_SIZE,
            'color': color
        })

# Inicializa o jogo chamando reset_game.
reset_game()

# Funcao principal de atualizacao do jogo, chamada repetidamente pelo Pygame Zero.
def update(dt):
    global player_y_velocity, camera_y, player_highest_y, is_bouncing, bounce_anim_timer, particles
    global bot_y_velocity, bot_direction, bot_is_bouncing, bot_bounce_timer, bot_active, bot_triggered, next_bot_spawn_height
    global bot_spawning, bot_spawn_alpha, bot_spawn_pos, game_state, space_pressed_last_frame

    # Verifica se a tecla espaco esta atualmente pressionada.
    space_pressed = keyboard.space

    # Logica do estado do jogo.
    if game_state == 'start':
        # Transicao da tela de inicio para a tela de carregamento.
        if space_pressed and not space_pressed_last_frame:
            game_state = 'loading'

    elif game_state == 'loading':
        # Transicao da tela de carregamento para o jogo.
        if space_pressed and not space_pressed_last_frame:
            game_state = 'playing'
            reset_game() # Reinicia os elementos do jogo para uma nova sessao.

    elif game_state == 'playing':
        # Movimento e rotacao do jogador com base na entrada do teclado.
        if keyboard.left:
            player.x -= PLAYER_SPEED
            player.angle = max(player.angle + ROTATION_SPEED, -MAX_ROTATION)
            if player.x < 0:
                player.x = WIDTH # Volta o jogador para o outro lado da tela.
        elif keyboard.right:
            player.x += PLAYER_SPEED
            player.angle = min(player.angle - ROTATION_SPEED, MAX_ROTATION)
            if player.x > WIDTH:
                player.x = 0 # Volta o jogador para o outro lado da tela.

        # Aplica gravidade ao jogador.
        player_y_velocity += GRAVITY
        player.y += player_y_velocity

        # Verifica colisao do jogador com plataformas ao cair.
        if player_y_velocity > 0:
            for plat in platforms:
                if player.colliderect(plat) and player.bottom <= plat.top + 10:
                    player_y_velocity = JUMP_VELOCITY # Jogador pula.
                    is_bouncing = True # Inicia animacao de salto.
                    bounce_anim_timer = 0.0
                    spawn_particles(player.x, player.bottom) # Gera particulas.
                    sounds.jump_player.set_volume(1.0) # Ajusta volume do som de pulo do jogador.
                    sounds.jump_player.play() # Toca som de pulo do jogador.
                    break

        # Atualizacao da animacao de salto do jogador.
        if is_bouncing:
            bounce_anim_timer += dt
            progress = bounce_anim_timer / BOUNCE_ANIM_DURATION
            if progress > 1.0:
                is_bouncing = False
            factor = math.sin(min(progress, 1.0) * math.pi)
            player.scale_y = 1.0 - 0.6 * factor
            player.scale_x = 1.0 + 0.6 * factor
        else:
            player.scale_x = 1.0
            player.scale_y = 1.0

        # Logica de spawn do bot.
        if bot_spawning:
            spawn_particles(bot_spawn_pos[0], bot_spawn_pos[1], count=5) # Particulas durante o spawn.
            bot_spawn_alpha += dt / 1.0 # Aumenta gradualmente a visibilidade do bot.
            if bot_spawn_alpha >= 1.0:
                bot_spawn_alpha = 1.0
                bot_spawning = False
                bot_active = True
                bot_triggered = True
                bot_y_velocity = 0
                bot_is_bouncing = False
                bot.pos = bot_spawn_pos # Posiciona o bot na posicao de spawn.
        else:
            # Movimento e interacao do bot quando ativo.
            if bot_active:
                # Aciona o movimento do bot se o jogador estiver perto o suficiente.
                if not bot_triggered:
                    if abs(bot.y - player.y) < 150:
                        bot_triggered = True

                if bot_triggered:
                    bot.x += bot_direction * (PLAYER_SPEED / 2) # Movimento horizontal do bot.

                    # Rotacao do bot com base na direcao.
                    if bot_direction == 1:
                        bot.angle = max(bot.angle - ROTATION_SPEED, -MAX_ROTATION)
                    else:
                        bot.angle = min(bot.angle + ROTATION_SPEED, MAX_ROTATION)

                    # Inverte a direcao do bot se ele atingir as bordas da tela.
                    if bot.x < 30:
                        bot_direction = 1
                    elif bot.x > WIDTH - 30:
                        bot_direction = -1

                # Aplica gravidade ao bot.
                bot_y_velocity += GRAVITY
                bot.y += bot_y_velocity

                # Verifica colisao do bot com plataformas.
                if bot_y_velocity > 0:
                    for plat in platforms:
                        if bot.colliderect(plat) and bot.bottom <= plat.top + 10:
                            bot_y_velocity = JUMP_VELOCITY # Bot pula.
                            bot_is_bouncing = True # Inicia animacao de salto do bot.
                            bot_bounce_timer = 0.0
                            spawn_particles(bot.x, bot.bottom) # Gera particulas.
                            sounds.jump_bot.set_volume(0.1) # Ajusta volume do som de pulo do bot.
                            sounds.jump_bot.play() # Toca som de pulo do bot.
                            break

                # Atualizacao da animacao de salto do bot.
                if bot_is_bouncing:
                    bot_bounce_timer += dt
                    progress = bot_bounce_timer / BOUNCE_ANIM_DURATION
                    if progress > 1.0:
                        bot_is_bouncing = False
                    factor = math.sin(min(progress, 1.0) * math.pi)
                    bot.scale_y = 1.0 - 0.6 * factor
                    bot.scale_x = 1.0 + 0.6 * factor
                else:
                    bot.scale_x = 1.0
                    bot.scale_y = 1.0

                # Se o bot cair da tela, desativa e prepara para o respawn.
                if bot.y > HEIGHT + 100:
                    bot_active = False
                    bot_spawning = True
                    bot_spawn_alpha = 0.0
                    bot_spawn_pos = (random.randint(50, WIDTH - 50), player.y - 150) # Posicao de spawn aleatoria.

        # Lida com a colisao entre jogador e bot (efeito de empurrao simples).
        if bot_active and player.colliderect(bot):
            overlap_x = min(player.right - bot.left, bot.right - player.left)
            if player.x < bot.x:
                player.x -= overlap_x / 4
                bot.x += overlap_x / 4
            else:
                player.x += overlap_x / 4
                bot.x -= overlap_x / 4

        # Atualiza e remove particulas.
        new_particles = []
        for p in particles:
            p['lifetime'] -= dt
            if p['lifetime'] > 0:
                p['vel'][1] += PARTICLE_GRAVITY * dt
                p['pos'][0] += p['vel'][0] * dt
                p['pos'][1] += p['vel'][1] * dt
                new_particles.append(p)
        particles[:] = new_particles

        # Movimento da camera.
        screen_center_y = HEIGHT // 2
        if player.y < screen_center_y:
            offset = screen_center_y - player.y
            player.y = screen_center_y
            camera_y += offset # Move a camera para cima.
            for plat in platforms:
                plat.y += offset # Move as plataformas com a camera.
            if bot_active or bot_spawning:
                if bot_spawning:
                    bot_spawn_pos = (bot_spawn_pos[0], bot_spawn_pos[1] + offset) # Move a posicao de spawn do bot.
                else:
                    bot.y += offset # Move o bot com a camera.

        # Remove plataformas fora da tela e gera novas.
        platforms[:] = [p for p in platforms if p.y < HEIGHT + BRICK_HEIGHT]
        while len(platforms) < 10: # Mantem um numero minimo de plataformas.
            highest_platform_y = min(p.y for p in platforms) if platforms else HEIGHT
            new_x = random.randint(50, WIDTH - 50)
            new_y = highest_platform_y - 100
            platforms.append(Actor(random.choice(BRICK_IMAGES), (new_x, new_y)))

        # Verifica a condicao de fim de jogo (jogador cai da tela).
        if player.y > HEIGHT + 50:
            game_state = 'gameover'

    elif game_state == 'gameover':
        # Transicao da tela de fim de jogo para a tela de inicio.
        if space_pressed and not space_pressed_last_frame:
            game_state = 'start'

    # Atualiza space_pressed_last_frame para a verificacao de entrada do proximo quadro.
    space_pressed_last_frame = space_pressed

# Funcao principal de desenho do jogo, chamada repetidamente pelo Pygame Zero.
def draw():
    screen.fill(CYAN) # Preenche o fundo com a cor CIANO.

    # Desenha elementos com base no estado atual do jogo.
    if game_state == 'start':
        start_screen.draw()
        screen.draw.text("PRESS START", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=40, color=WHITE)
    elif game_state == 'loading':
        load_screen.draw()
        screen.draw.text("PRESS START", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=40, color=WHITE)
    elif game_state == 'playing':
        for plat in platforms:
            plat.draw() # Desenha todas as plataformas.
        player.draw() # Desenha o jogador.
        if bot_active or bot_spawning:
            if bot_spawning:
                # Desenha o bot com alfa para a animacao de spawn.
                bot.draw()
                screen.surface.set_alpha(int(bot_spawn_alpha * 255))
            else:
                bot.draw() # Desenha o bot quando ativo.

        # Desenha todas as particulas ativas.
        for p in particles:
            color = p['color']
            screen.draw.filled_circle((p['pos'][0], p['pos'][1]), p['size'], color)

    elif game_state == 'gameover':
        gameover_screen.draw()
        screen.draw.text("PRESS START", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=40, color=WHITE)