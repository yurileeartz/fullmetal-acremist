from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import random

app = Ursina()

# --- CONFIGURAÇÕES DA JANELA ---
window.title = 'The Fullmetal Acremist'
window.fps_counter.enabled = False
window.exit_button.visible = False

# --- MAQUINA DE ESTADOS E PROGRESSO ---
estado_atual = 'INTRO' 
puzzle_id_ativo = None 
video_tocando = False 

# Variáveis globais dos minigames do quarto
angulos_atuais = [0, 0, 180, 270] 
angulos_de_vitoria = [180, 90, 0, 0] 

# Containers de Cenário
game_container = Entity(enabled=False)
abc_container = Entity(enabled=False) 

# Containers de UI
menu_container = Entity(parent=camera.ui, enabled=False) 
minigame_painel = Entity(parent=camera.ui, enabled=False, model='quad', scale=(1, 0.7), z=-20, color=color.rgba(0,0,0,0.9))
game_over_container = Entity(parent=camera.ui, enabled=False)
elementos_puzzle_container = Entity(parent=camera.ui, scale=(1, 1), enabled=False)

# Container Seguro da UI do A.B.C.
ui_abc_container = Entity(parent=camera.ui, enabled=False)


# ==========================================================
# 0. INICIALIZAÇÃO DOS ÁUDIOS E CONTROLE DE MÍDIA
# ==========================================================
musica_menu = Audio('fullmetalacremistmusicaabertura.mp3', loop=True, autoplay=False, volume=0.7)
musica_gameplay = Audio('fullmetalacremistmusicagame.mp3', loop=True, autoplay=False, volume=0.6)
som_passos = Audio('passos.wav', loop=True, autoplay=False, volume=0.5)
som_puzzle_resolvido = Audio('puzzlesolving.wav', loop=False, autoplay=False, volume=0.8)
som_porta_aberta = Audio('somportaaberta.wav', loop=False, autoplay=False, volume=0.9)
som_zeramento = Audio('fullmetalacremistzeramento1.wav', loop=False, autoplay=False, volume=1.0)

# Áudios do A.B.C.
musica_abc = Audio('musica_abc.mp3', loop=True, autoplay=False, volume=0.6) 
som_coleta_livro = Audio('puzzlesolving.wav', loop=False, autoplay=False, volume=0.7) 
som_vitoria_abc = Audio('fullmetalacremistzeramento2.wav', loop=False, autoplay=False, volume=1.0) 

# Tela preta estática inicial de espera
# --- INTRODUÇÃO COM IMAGEM ESTÁTICA E TEXTO SUBINDO VAGAROSAMENTE ---
# Carrega a imagem da sua pasta
tela_intro_estatica = Entity(parent=camera.ui, model='quad', texture='fullmetalacremistintroducao.png', scale=(1.78, 1), z=-55, enabled=True)

# Cria o texto numa posição mais baixa (invisível ou fora de foco) e anima sua subida
texto_historia = Text(
    parent=camera.ui, 
    text="""...Bostil Games apresenta\n\n \
    \nO Enigma do Fullmetal Acremist. \
    \n\nAs paredes do quarto guardam segredos \
    \n\nque desafiam a \
    \n\nprópria lógica do tempo e do espaço. \
    \n\nO jovem alquimista, conhecido  \
    \n\npelas lendas como o  \
    \n\nMenino do Acre, desapareceu sem \
    \n\ndeixar vestígios. \
    \n\nDeixou para trás apenas um  \
    \n\nrastro de manuscritos,  \
    \n\ncifras indecifráveis e uma  \
    \n\nréplica exata de sua jornada. \
    \n\nDizem que ele viajou para \
    \n\nmuito além do óbvio,  \
    \n\nbuscando o conhecimento absoluto \
    \n\nnas vastidões inóspitas. \
    \n\nPara encontrá-lo, o jogador  \
    \n\ndeve mergulhar na \
    \n\nmente brilhante e reclusa \
    \n\ndesse andarilho. \
    \n\nO quarto transformou-se em \
    \n\num labirinto alquímico \
    \n\nonde cada parede esconde uma \
    \n\ncharada críptica. \
    \n\nÉ preciso decifrar códigos \
    \n\nnuméricos antigos, \
    \n\nalinhar frequências cósmicas e  \
    \n\nseguir a trilha dos tomos sagrados. \
    \n\nA Cifra de César na penumbra  \
    \n\nrevela pistas sobre o  \
    \n\ndestino improvável que ele \
    \n\nescolheu seguir... \
 
                                                               """,

    scale=0.9, 
    position=(0.0, -0.4),  # Começa embaixo
    color=color.white, 
    z=-56,
    origin=(0, 0.6)
)

texto_historia.animate_position((0,2.8), duration=48.0, curve=curve.linear)

video_zeramento = Entity(parent=camera.ui, model='quad', scale=(1.78, 1), z=-50, enabled=False)
video_zeramento2 = Entity(parent=camera.ui, model='quad', scale=(1.78, 1), z=-50, enabled=False)


# ==========================================================
# 1. INTERFACES DE UI E VARIÁVEIS DO A.B.C.
# ==========================================================
selos = {
    'frontal':  {'resolvido': False, 'nome': 'Cifra do Manifesto'},
    'esquerda': {'resolvido': False, 'nome': 'Alinhamento dos Astros'},
    'direita':  {'resolvido': False, 'nome': 'Seqüência do Fluxo'},
    'traseira': {'resolvido': False, 'nome': 'O Livro de Giordano'}
}
selos_coletados = 0

livros_abc_coletados = 0
livros_abc_lista = []
tempo_abc_segundos = 120 
ultimo_segundo_checado = -1

# Textos puros na tela sem retângulos pretos ou caixas de fundo sólidas
timer_abc_texto = Text(parent=camera.ui, text='Tempo: 2:00', position=(-0.85, 0.45), scale=1.5, color=color.red, z=-100, background=False, enabled=False)
contador_abc_texto = Text(parent=camera.ui, text='Livros: 0/11', position=(-0.85, 0.38), scale=1.5, color=color.white, z=-100, background=False, enabled=False)


# ==========================================================
# 2. SISTEMA DE TRANSIÇÃO DE ESTADOS E MAPAS
# ==========================================================
def finalizar_intro():
    global estado_atual
    if estado_atual == 'INTRO':
        estado_atual = 'MENU'
        video_intro.disable() if 'video_intro' in globals() else None
        tela_intro_estatica.disable()    
        destroy(tela_intro_estatica)
        destroy(texto_historia)      # <--- ADICIONE ESTA LINHA PARA DELETAR O TEXTO DA INTRO
        menu_container.enable()  
        musica_menu.play()     

def iniciar_jogo():
    global estado_atual, selos_coletados, video_tocando, angulos_atuais, tempo_abc_segundos, livros_abc_coletados
    
    # --- RESET TOTAL DE VARIÁVEIS E ESTADOS ---
    estado_atual = 'GAMEPLAY'
    selos_coletados = 0
    livros_abc_coletados = 0
    tempo_abc_segundos = 240
    video_tocando = False
    angulos_atuais = [0, 0, 180, 270] 
    
    for chave in selos: 
        selos[chave]['resolvido'] = False
        
    p_frontal_esquerda.color = color.white
    p_traseira.color = color.white
    p_esquerda.color = color.white
    p_direita.color = color.white
    
    p_corredor_fundo.color = color.white
    p_corredor_fundo.collider = 'box'
    
    # Desativa todas as telas de menu, game over, vídeos e minigames
    menu_container.disable()
    game_over_container.disable()
    minigame_painel.disable()
    elementos_puzzle_container.disable()
    video_zeramento.disable() 
    video_zeramento2.disable()
    abc_container.disable()
    ui_abc_container.disable()
    
    # Interrompe todos os áudios e músicas
    musica_menu.stop()
    som_zeramento.stop()
    som_vitoria_abc.stop() 
    musica_abc.stop()
    som_passos.stop()
    
    # Oculta os textos da HUD do Cerrado
    timer_abc_texto.disable()
    contador_abc_texto.disable()
    
    # Reativa o cenário principal
    game_container.enable()
    
    # Reposiciona o jogador no início do quarto e libera o controle
    player.position = (0, 2.0, 0)
    player.rotation_y = 0
    player.enabled = True
    
    # Restaura a estátua do Menino do Acre para a posição inicial
    menino_acre.texture = 'statue'
    menino_acre.position = (6.5, 1.9, 39)
    menino_acre.rotation = (0,0,0)
    menino_acre.enabled = True
    
    # Trava o mouse no centro da tela para o modo 1ª pessoa
    mouse.locked = True
    
    # Toca a música tema do gameplay
    musica_gameplay.play()     
    
    vignette_lanterna.enabled = False  
    tela_preta_breu.enabled = True

def iniciar_busca_abc():
    global estado_atual, livros_abc_coletados, tempo_abc_segundos, video_tocando
    print("🌅 Transmutação concluída. Bem-vindo ao Cerrado. Apenas Busque Conhecimento!")
    estado_atual = 'GAMEPLAY_ABC'
    video_tocando = False
    video_zeramento.disable() 

    game_container.disable()
    vignette_lanterna.enabled = False
    tela_preta_breu.enabled = True 
    som_passos.stop()
    musica_gameplay.stop()

    abc_container.enable()
    ceu_noturno.enable()
    lua_abc.enable() 
    musica_abc.play()

    player.position = (0, 2, 0) 
    player.speed = 6.0 
    mouse.locked = True
    player.enabled = True
    
    livros_abc_coletados = 0
    tempo_abc_segundos = 120 
    spawn_livros_abc()
    
    # Exibe a HUD de textos puros de forma segura
    ui_abc_container.enable()
    timer_abc_texto.enable()
    contador_abc_texto.enable()
    
    timer_abc_texto.text = 'Tempo: 2:00'
    contador_abc_texto.text = 'Livros: 0/11'
    timer_abc_texto.color = color.red
    contador_abc_texto.color = color.white

    menino_acre.texture = 'meninodoacre.png'
    menino_acre.position = (random.uniform(-40, 40), 2.2, random.uniform(20, 40)) 
    menino_acre.rotation = (0,0,0)

def ativar_game_over(causa):
    global estado_atual, tempo_abc_segundos
    estado_atual = 'GAME_OVER'  # <--- MUDA O ESTADO PARA PARAR O LOOP DE UPDATE
    
    player.enabled = False
    
    # Liberação total do mouse para o retry funcionar garantido
    mouse.locked = False
    mouse.visible = True 
    
    game_container.disable()
    minigame_painel.disable()
    elementos_puzzle_container.disable()
    abc_container.disable()
    ui_abc_container.disable()
    game_over_container.enable()  
    
    vignette_lanterna.enabled = False
    tela_preta_breu.enabled = False
    
    # --- ZERA TUDO PARA MATAR O PROCESSAMENTO EM SEGUNDO PLANO ---
    tempo_abc_segundos = 0
    if 'livros_abc_lista' in globals():
        livros_abc_lista.clear()
        
    som_passos.stop()
    musica_gameplay.stop()
    musica_abc.stop()
    musica_menu.play()
    
    # Limpa contadores da tela
    timer_abc_texto.disable()
    contador_abc_texto.disable()

def voltar_para_o_menu():
    global estado_atual, video_tocando
    estado_atual = 'MENU'
    video_tocando = False
    
    game_container.disable()
    abc_container.disable() 
    ui_abc_container.disable()
    player.enabled = False
    mouse.locked = False
    
    minigame_painel.disable()
    elementos_puzzle_container.disable()
    game_over_container.disable()
    video_zeramento.disable()
    video_zeramento2.disable() 
    
    vignette_lanterna.enabled = False
    tela_preta_breu.enabled = False
    
    som_zeramento.stop()
    som_vitoria_abc.stop() 
    musica_gameplay.stop()
    musica_abc.stop()
    som_passos.stop()
    musica_menu.play()
    
    menu_container.enable()
    
    # Limpa contadores da tela
    timer_abc_texto.disable()
    contador_abc_texto.disable()

# Menu Principal
start_button = Button(parent=menu_container, text='INICIAR TRANSMUTAÇÃO', scale=(0.35, 0.1), y=-0.28, color=color.black, highlight_color=color.red, on_click=iniciar_jogo)
Entity(parent=menu_container, model='quad', texture='fullmetalacremistcapa', scale=(1.78, 1), z=1)

# Tela de Game Over
bg_game_over = Entity(parent=game_over_container, model='quad', color=color.black, scale=(9, 1), z=2)
text_game_over = Text(parent=game_over_container, text='GAME OVER', position=(-0.28, 0.2), scale=4, color=color.red, z=1)
text_frase_derrota = Text(parent=game_over_container, text='A busca falhou...Você foi sod0mizado.', position=(-0.3, -0.0), scale=1.4, color=color.light_gray, z=1)
retry_button = Button(parent=game_over_container, text='TENTAR NOVAMENTE', scale=(0.3, 0.08), y=-0.22, color=color.rgba(20, 20, 20, 0.9), highlight_color=color.red, text_color=color.white, on_click=iniciar_jogo, z=1)


# ==========================================================
# 3. GEOMETRIA DO CERRADO (A.B.C.) - LUA E GRAMA ALTA 4
# ==========================================================
ceu_noturno = Entity(parent=abc_container, model='sky_dome', texture='ceu_noturno.png', scale=200, enabled=False)
lua_abc = Entity(parent=abc_container, model='quad', texture='lua.png', scale=(18, 18), position=(25, 65, 80), billboard=True, enabled=False)
chao_abc = Entity(parent=abc_container, model='plane', texture='grama_chao.png', scale=150, collider='box', texture_scale=(10,10))

def spawn_livros_abc():
    global livros_abc_lista
    for child in abc_container.children:
        if hasattr(child, 'tipo_abc') and child.tipo_abc == 'livro':
            destroy(child)
    livros_abc_lista.clear()

    for i in range(11):
        x = random.uniform(-45, 45)
        z = random.uniform(-45, 45)
        livro = Entity(parent=abc_container, model='plane', texture='livros_abc_coletados', scale=(0.8, 0.8, 0.8), position=(x, 0.5, z))
        livro.collider = 'box'
        livro.tipo_abc = 'livro'
        livros_abc_lista.append(livro)

def gerar_cerrado():
    texturas_arvores = ['arvore_cerrado1.png', 'arvore_cerrado2.png', 'arvore_cerrado3.png', 'arvore_cerrado4.png']
    texturas_gramas = ['grama_alta1.png', 'grama_alta2.png', 'grama_alta3.png', 'grama_alta4.png']

    for i in range(120):
        arvore = Entity(parent=abc_container, model='quad', texture=random.choice(texturas_arvores), scale=(random.uniform(6, 12), random.uniform(8, 16)), position=(random.uniform(-75, 70), random.uniform(2.5, 4.5), random.uniform(-75, 70)), billboard=True, collider='box')
        arvore.collider = BoxCollider(arvore, size=(0.5, 2, 0.5))

    for i in range(200):
        Entity(parent=abc_container, model='quad', texture=random.choice(texturas_gramas), scale=(random.uniform(2, 4), random.uniform(2, 4)), position=(random.uniform(-75, 70), random.uniform(1.2, 1.8), random.uniform(-75, 70)), billboard=True)

gerar_cerrado()


# ==========================================================
# 4. GEOMETRIA DO MAPA E ARQUITETURA EM "L" (Fullmetal)
# ==========================================================
chao_quarto = Entity(parent=game_container, model='cube', texture='quarto10', scale=(16, 1, 16), position=(0, -0.5, 0), collider='box')
teto_quarto = Entity(parent=game_container, model='plane', texture='quarto3', scale=16, y=6, rotation_x=180, collider='box')

p_traseira = Entity(parent=game_container, model='quad', texture='quarto8', scale=(16, 6), position=(0, 3, -8), rotation_y=180, collider='box')
p_esquerda = Entity(parent=game_container, model='quad', texture='quarto9', scale=(16, 6), position=(-8, 3, 0), rotation_y=-90, collider='box')
p_direita = Entity(parent=game_container, model='quad', texture='quarto6', scale=(16, 6), position=(8, 3, 0), rotation_y=90, collider='box')
p_frontal_esquerda = Entity(parent=game_container, model='quad', texture='quarto2', scale=(13, 6), position=(-1.5, 3, 8), collider='box')

chao_corredor = Entity(parent=game_container, model='cube', texture='corredor_chao', scale=(3, 1, 32), position=(6.5, -0.5, 24), collider='box')
teto_corredor = Entity(parent=game_container, model='cube', texture='corredor_teto', scale=(3, 0.1, 32), position=(6.5, 6, 24), texture_scale=(1, 8), collider='box')
p_corredor_esquerda = Entity(parent=game_container, model='quad', texture='corredor_parede_esquerda', scale=(32, 6), position=(5, 3, 24), rotation_y=-90, collider='box')
p_corredor_direita = Entity(parent=game_container, model='quad', texture='corredor_parede_direita', scale=(32, 6), position=(8, 3, 24), rotation_y=90, collider='box')
p_corredor_fundo = Entity(parent=game_container, model='quad', texture='corredor_porta', scale=(3, 6), position=(6.5, 3, 40), collider='box')

menino_acre = Entity(model='quad', texture='statue', scale=(3.4, 6.0), position=(6.5, 1.9, 39), billboard=True)
menino_acre.collider = BoxCollider(menino_acre, size=(2.5, 4, 2.5))


# ==========================================================
# 5. CONTROLLER DO JOGADOR E ILUMINAÇÃO (Lanterna)
# ==========================================================
player = FirstPersonController(enabled=False, y=1.5, origin_y=-0.5)
player.speed = 4.8

tela_preta_breu = Entity(parent=camera.ui, model='quad', color=color.black, scale=(1.78, 1), z=-48, enabled=False)
vignette_lanterna = Entity(parent=camera.ui, model='quad', texture='vignette_slender', scale=(1.78, 1), z=-49, enabled=False)


# ==========================================================
# 6. SISTEMA DE RESOLUÇÃO DOS DESAFIOS ALQUÍMICOS
# ==========================================================
def fechar_minigame():
    global estado_atual, puzzle_id_ativo
    estado_atual = 'GAMEPLAY'
    puzzle_id_ativo = None
    minigame_painel.disable()
    elementos_puzzle_container.disable()
    menino_acre.enabled = True 
    mouse.locked = True 
    musica_gameplay.volume = 0.6
    for child in elementos_puzzle_container.children: destroy(child)

def resolver_puzzle_correto(parede_id):
    global selos_coletados, estado_atual
    if selos[parede_id]['resolvido']: return

    selos[parede_id]['resolvido'] = True
    selos_coletados += 1
    som_puzzle_resolvido.play()
    
    mapa_paredes = {'frontal': p_frontal_esquerda, 'esquerda': p_esquerda, 'direita': p_direita, 'traseira': p_traseira}
    mapa_paredes[parede_id].color = color.cyan
    fechar_minigame()

    if selos_coletados == 4:
        som_porta_aberta.play()
        p_corredor_fundo.collider = None
        p_corredor_fundo.color = color.green 
        print("🔓 Conhecimento Alcançado! Corra pela porta!")

def abrir_minigame_painel(puzzle_id):
    global estado_atual, puzzle_id_ativo
    if selos[puzzle_id]['resolvido']: return
    if tela_preta_breu.enabled: return

    estado_atual = 'MINIGAME'
    puzzle_id_ativo = puzzle_id
    mouse.locked = False 
    menino_acre.enabled = False 
    minigame_painel.enable()
    elementos_puzzle_container.enable()
    
    som_passos.stop()
    musica_gameplay.volume = 0.25
    
    Text(parent=elementos_puzzle_container, text=selos[puzzle_id]['nome'], position=(-0.45, 0.45), scale=2, color=color.white, z=-21)
    Button(parent=elementos_puzzle_container, text='VOLTAR', scale=(0.15, 0.06), position=(0.35, 0.42), color=color.black, highlight_color=color.red, on_click=fechar_minigame, z=-21)

    if puzzle_id == 'frontal': setup_minigame_frontal()
    elif puzzle_id == 'esquerda': setup_minigame_esquerda()
    elif puzzle_id == 'direita': setup_minigame_direita()
    elif puzzle_id == 'traseira': setup_minigame_traseira()


# ==========================================================
# 7. INTERFACES DE PUZZLES (Blindadas sem flicker)
# ==========================================================
def setup_minigame_frontal():
    Text(parent=elementos_puzzle_container, text='Use a Cifra de César da parede para decifrar:', position=(-0.4, 0.25), scale=1.3, color=color.cyan, z=-21)
    Text(parent=elementos_puzzle_container, text='"P-V-Z-E-M"', position=(-0.25, 0.1), scale=2.5, color=color.white, z=-21)
    input_field = InputField(parent=elementos_puzzle_container, position=(0, -0.1), scale=(0.4, 0.08), character_limit=12, text_color=color.black, z=-21)
    def confirmar_cifra():
        if input_field.text.upper() == 'ACRE': resolver_puzzle_correto('frontal')
        else: input_field.text = ""; input_field.color = color.rgba(255,0,0,0.5)
    Button(parent=elementos_puzzle_container, text='Confirmar', scale=(0.2, 0.08), position=(0.3, -0.1), color=color.cyan, highlight_color=color.red, on_click=confirmar_cifra, z=-21)

def setup_minigame_esquerda():
    global angulos_atuais, angulos_de_vitoria
    Text(parent=elementos_puzzle_container, text='Ajuste a frequência oculta dos diagramas para liberar o fluxo:', position=(-0.43, 0.25), scale=1.3, color=color.cyan, z=-21)
    posicoes_x = [-0.34, -0.11, 0.11, 0.34]
    
    for i in range(4):
        astro_quad = Entity(
            parent=elementos_puzzle_container, 
            model='quad', 
            texture='quarto9', 
            scale=(0.15, 0.15), 
            position=(posicoes_x[i], -0.1), 
            rotation_z=angulos_atuais[i], 
            z=-22
        )
        
        btn_giro = Button(
            parent=elementos_puzzle_container,
            scale=(0.15, 0.15),
            position=(posicoes_x[i], -0.1),
            color=color.rgba(0,0,0,0),      
            highlight_color=color.rgba(0,0,0,0.1),
            z=-23
        )
        
        def girar_anel(idx=i, entity=astro_quad):
            global angulos_atuais, angulos_de_vitoria
            angulos_atuais[idx] = (angulos_atuais[idx] + 90) % 360
            entity.animate_rotation_z(angulos_atuais[idx], duration=0.15)
            
            venceu = all((angulos_atuais[j] % 360 == angulos_de_vitoria[j] % 360) for j in range(4))
            if venceu: 
                resolver_puzzle_correto('esquerda')
                
        btn_giro.on_click = girar_anel

def setup_minigame_direita():
    Text(parent=elementos_puzzle_container, text='Repita a seqüência de glifos que piscará:', position=(-0.4, 0.25), scale=1.3, color=color.cyan, z=-21)
    grade_botoes = []
    sequencia_alvo = [0, 4, 8, 2, 6]
    sequencia_jogador = []
    for i in range(9):
        btn = Button(parent=elementos_puzzle_container, scale=0.1, position=(-0.2 + (i%3)*0.2, 0.1 - (i//3)*0.2), color=color.gray, z=-21)
        def clique_genius(idx=i, b=btn):
            if idx == sequencia_alvo[len(sequencia_jogador)]:
                sequencia_jogador.append(idx)
                b.animate_color(color.cyan, duration=0.2)
                if len(sequencia_jogador) == len(sequencia_alvo): resolver_puzzle_correto('direita')
            else:
                for b_all in grade_botoes: b_all.animate_color(color.red, duration=0.25)
                sequencia_jogador.clear()
        btn.on_click = clique_genius
        grade_botoes.append(btn)
    for idx, glifo_idx in enumerate(sequencia_alvo):
        grade_botoes[glifo_idx].animate_color(color.white, duration=0.2, delay=1.0 + idx*0.8)

# --- SEQUÊNCIA FIXA EXATA PEDIDA: 4, 1, 5, 2, 3 ---
def setup_minigame_traseira():
    Text(parent=elementos_puzzle_container, text='Decifre o código de Giordano clicando nos tomos na ordem secreta:', position=(-0.43, 0.32), scale=1.1, color=color.cyan, z=-21)
    charada_texto = (
        "Manuscrito Oculto:\n"
        "O conhecimento não segue a linha do tempo... ele exige uma ordem de sacrifício.\n"
        "Descubra a combinação correta de 5 cliques entre as runas dos manuscritos.\n\n"
    
    )
    Text(parent=elementos_puzzle_container, text=charada_texto, position=(-0.43, 0.22), scale=0.9, color=color.white, z=-21)
    livros_config = [{'id_tomo': 'Tomo-1', 'ordem_esperada': 1}, {'id_tomo': 'Tomo-2', 'ordem_esperada': 3}, {'id_tomo': 'Tomo-3', 'ordem_esperada': 4}, {'id_tomo': 'Tomo-4', 'ordem_esperada': 0}, {'id_tomo': 'Tomo-5', 'ordem_esperada': 2}]
    grade_livros = []
    sequencia_jogador = []
    for i, config in enumerate(livros_config):
        livro_btn = Button(parent=elementos_puzzle_container, model='quad', texture='quarto8', scale=(0.11, 0.25), position=(-0.34 + i * 0.17, -0.2), color=color.brown, highlight_color=color.dark_gray, z=-21)
        Text(parent=livro_btn, text=f"[{config['id_tomo']}]", position=(-0.35, 0.05), scale=1.2, color=color.gold, z=-1)
        def interagir_com_livro(config_atual=config, botao_atual=livro_btn):
            passo_atual = len(sequencia_jogador)
            if config_atual['ordem_esperada'] == passo_atual:
                sequencia_jogador.append(config_atual['ordem_esperada'])
                botao_atual.animate_color(color.cyan, duration=0.2)
                if len(sequencia_jogador) == 5: resolver_puzzle_correto('traseira')
            else:
                for btn_all in grade_livros:
                    btn_all.animate_color(color.red, duration=0.25)
                    btn_all.animate_color(color.brown, duration=0.25, delay=0.3)
                sequencia_jogador.clear()
        livro_btn.on_click = interagir_com_livro
        grade_livros.append(livro_btn)


# ==========================================================
# 8. INPUT (Seletor Universal por Tecla E / ESC / Lanterna)
# ==========================================================
def input(key):
    global estado_atual, puzzle_id_ativo
    
    if estado_atual == 'INTRO' and key == 'left mouse down':
        finalizar_intro()
        return

    if estado_atual == 'MENU' or estado_atual == 'GAME_OVER':
        return

    # Sair do modo puzzle / minigame apertando ESC
    if key == 'escape':
        if estado_atual == 'MINIGAME':
            fechar_minigame()
            return

    # Alternar lanterna
    if key == 'left mouse down':
        if estado_atual in ['GAMEPLAY', 'GAMEPLAY_ABC']:
            vignette_lanterna.enabled = not vignette_lanterna.enabled
            tela_preta_breu.enabled = not vignette_lanterna.enabled

    # Interação via tecla 'E' nos Puzzles
    if key == 'e' and estado_atual == 'GAMEPLAY':
        dist_frontal = distance(player.position, (-1.5, 1.5, 8))
        dist_esquerda = distance(player.position, (-8, 1.5, 0))
        dist_direita = distance(player.position, (8, 1.5, 0))
        dist_traseira = distance(player.position, (0, 1.5, -8))

        if dist_frontal < 2.5: abrir_minigame_painel('frontal')
        elif dist_esquerda < 2.5: abrir_minigame_painel('esquerda')
        elif dist_direita < 2.5: abrir_minigame_painel('direita')
        elif dist_traseira < 2.5: abrir_minigame_painel('traseira')


# ==========================================================
# 9. LOOP RECORRENTE (UPDATE)
# ==========================================================
def update():
    global estado_atual, selos_coletados, video_tocando, tempo_abc_segundos, ultimo_segundo_checado, livros_abc_coletados

    if video_tocando:
        if som_passos.playing: som_passos.stop()
        return

    if estado_atual == 'MENU' or estado_atual == 'INTRO':
        if som_passos.playing: som_passos.stop()
        return

    if estado_atual == 'GAMEPLAY' or estado_atual == 'GAMEPLAY_ABC':
        esta_movendo = held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']
        if esta_movendo and not som_passos.playing: som_passos.play()
        elif not esta_movendo and som_passos.playing: som_passos.stop()

    # --- UPDATE: MUNDO CERRADO (A.B.C.) ---
    if estado_atual == 'GAMEPLAY_ABC':
        if tempo_abc_segundos > 0:
            tempo_abc_segundos -= time.dt
            
            # Atualiza o cronômetro na tela a cada segundo inteiro, sem fundo preto
            segundo_inteiro_atual = int(tempo_abc_segundos)
            if segundo_inteiro_atual != ultimo_segundo_checado:
                ultimo_segundo_checado = segundo_inteiro_atual
                minutos = segundo_inteiro_atual // 60
                segundos = segundo_inteiro_atual % 60
                timer_abc_texto.text = f'Tempo: {minutos}:{segundos:02d}'
            
            if tempo_abc_segundos <= 0:
                ativar_game_over("O tempo acabou!")
                return

        # Coleta de livros 3D físicos espalhados
        for livro in list(livros_abc_lista):
            if livro in abc_container.children and distance(player.position, livro.position) < 3.0:
                destroy(livro)
                livros_abc_lista.remove(livro)
                livros_abc_coletados += 1
                som_coleta_livro.play()
                contador_abc_texto.text = f'Livros: {livros_abc_coletados}/11'
                
                if livros_abc_coletados == 11:
                    timer_abc_texto.color = color.green
                    timer_abc_texto.text = "Busca Concluída!"
                    print("👑 Os 11 tomos foram coletados. O Menino do Acre cessou a fuga. Encontre-o!")

        distancia_player_acre = distance(player.position, menino_acre.position)

        if livros_abc_coletados < 11:
            # Ativa textos puros na tela
            timer_abc_texto.enable()
            contador_abc_texto.enable()
            
            if distancia_player_acre < 6.0:
                direcao_fuga = (menino_acre.position - player.position).normalized()
                direcao_fuga.y = 0 
                menino_acre.position += direcao_fuga * 11 * time.dt
        else:
            if distancia_player_acre < 3.0:
                estado_atual = 'FIM_ABC'
                abc_container.disable()
                
                # Desabilita textos puros da tela ao terminar
                timer_abc_texto.disable()
                contador_abc_texto.disable()
                
                player.enabled = False
                mouse.locked = False
                som_passos.stop()
                musica_abc.stop()
                
                video_zeramento2.texture = 'fullmetalacremistzeramento2.mp4'
                video_zeramento2.enable() 
                som_vitoria_abc.play() 
                
                print("👑 Você o encontrou! Transmutação Finalizada.")
                invoke(voltar_para_o_menu, delay=7.0)
                return
        return 

    # --- UPDATE: MUNDO QUARTO (Fullmetal) ---
    if estado_atual == 'GAMEM' or estado_atual == 'MINIGAME' or estado_atual == 'GAMEPLAY':
        # Oculta textos puros da fase do cerrado ao voltar pro quarto
        timer_abc_texto.disable()
        contador_abc_texto.disable()

        if player.z > 39.8 and selos_coletados == 4:
            video_tocando = True
            estado_atual = 'VIDEO_FINAL' 
            
            player.enabled = False
            mouse.locked = False
            
            som_passos.stop()
            musica_gameplay.stop()
            
            video_zeramento.texture = 'fullmetalacremistzeramento1.mp4'
            video_zeramento.enable()
            som_zeramento.play()
            
            invoke(iniciar_busca_abc, delay=7.0) 
            return

        distancia_acre_quarto = distance(player.position, menino_acre.position)
        if distancia_acre_quarto > 1.5:
            velocidade_busca = 0.8 if (vignette_lanterna.enabled or estado_atual == 'MINIGAME') else 2.2
            if menino_acre.z > 8.0:
                menino_acre.z -= velocidade_busca * time.dt
                menino_acre.x = 6.5
            else:
                direcao_busca = (player.position - menino_acre.position).normalized()
                direcao_busca.y = 0 
                menino_acre.position += direcao_busca * velocidade_busca * time.dt
            
        if distancia_acre_quarto < 2.5:
            ativar_game_over("Capturado!")


invoke(finalizar_intro, delay=38.0)
app.run()