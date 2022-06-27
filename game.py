from pygame.locals import *
import pygame
import sys
import random

clock = pygame.time.Clock()

pygame.init()  # inicializa pygame

#Inicializando el sonido
pygame.mixer.pre_init(44100, -16, 2, 512)
# Caales para reproducir más sonidos a la vez
pygame.mixer.set_num_channels(64)
pygame.display.set_caption('Pygame Window')  # Le da un nombre a la pantalla

WINDOW_SIZE = (800, 640)  # Establece el tamaño de la pantalla

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # Inicializa la pantalla

display = pygame.Surface((400, 320))
# Se puede proyectar una imagen en una superficie y escalar
# esa superficie independientemente del resto de elemtnos


#Objetos de fondo para el efect Parallax
background_objects = [[0.25,[120,10,70,400]],
                        [0.25,[50,120,550,400]],
                        [0.5,[30,70,50,400]],
                        [0.5,[130,50,80,300]],
                        [0.75,[130,50,80,150]],
                        [0.75,[800,50,80,400]]]

# ColorKey es el color clave para definir la transparencia del sprite
#player_image.set_colorkey((255,255,255))

grass_image = pygame.image.load('data/images/grass.png')
TILE_SIZE = grass_image.get_width()
dirt_image = pygame.image.load('data/images/dirt.png')

forest_bg = pygame.image.load('data/images/forest.png')

flag_image1 = pygame.image.load( 'data/images/flag1.png' )
flag_image2 = pygame.image.load( 'data/images/flag2.png' )

plant = pygame.image.load( 'data/images/plant.png' )
flower = pygame.image.load( 'data/images/flower.png' )

perdiste_image = pygame.image.load( 'data/images/perdiste.png' )
ganaste_image = pygame.image.load( 'data/images/ganaste.png' )

jump_sound = pygame.mixer.Sound('data/sounds/jump.wav')
jump_sound.set_volume(0.3)
grass_sounds = [pygame.mixer.Sound('data/sounds/grass_0.wav'), pygame.mixer.Sound('data/sounds/grass_1.wav')]
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)

damage_sound = pygame.mixer.Sound('data/sounds/present.wav')
damage_sound.set_volume(0.3)

pygame.mixer.music.load('data/sounds/Noise.wav')
pygame.mixer.music.play(-1) #how many times it plays after the first play; -1 to play in loop, 0 just once


moving_right = False
moving_left = False
air_timer = 0
player_y_momentum = 0

true_scroll = [0,0]

def load_map(path):
    f = open(path + '.txt','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


game_map = load_map('data/maps/map')

rows = len(game_map)
columns = len(game_map[0]) 

global animation_frames
animation_frames = {}

def load_animation(path, frame_durations): #[7,7]
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0,0,0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

# Función para cambiar la direccion del sprite
def change_action(action_var, frame, new_var):
    if action_var != new_var:
        action_var = new_var
        frame = 0
    return action_var, frame

animation_database = {}

animation_database['idle'] = load_animation('data/images/idle',[60,15,20])
animation_database['run'] = load_animation('data/images/run',[8,8,8])
animation_database['jump'] = load_animation('data/images/jump',[20,20,20,20])

player_action = 'idle'
player_frame = 0
player_flip = False

# Fisicas, colisiones con los tiles
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)

    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    #Actualizar la 
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right']=True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left']=True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom']=True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top']=True
    return rect, collision_types

player_rect = pygame.Rect(30,30, 20, 23)

test_rect = pygame.Rect(100, 100, 100, 50)

last_move = [0,0]
grass_sound_timer = 0
death_count = 0

GAME_ON = True
while GAME_ON:  # Loop del Juego
    display.fill((255, 255, 255))
    
    display.blit( forest_bg, (0,0) )

    # play the grass sound only when
    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player_rect.x-true_scroll[0]-140)/20
    true_scroll[1] += (player_rect.y-true_scroll[1]-200)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    
    #pygame.draw.rect(display,(0,0,0), pygame.Rect(0,120,300,80))
    # Efecto Parallax
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],
                                background_object[1][1]-scroll[1]*background_object[0], 
                                50, 400)
        if background_object[0] == 0.25:
            pygame.draw.rect(display,(255, 0, 0), obj_rect)
        if background_object[0] == 0.5:
            pygame.draw.rect(display,(0, 255, 0), obj_rect)
        if background_object[0] == 0.75:
            pygame.draw.rect(display,(0, 0, 255 ), obj_rect)

    # Bucle para generar los tiles en la pantalla
    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt_image, (x*TILE_SIZE-scroll[0],y*TILE_SIZE-scroll[1]))
            if tile == '2':
                display.blit(grass_image, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '3':
                display.blit(flag_image1, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '4':
                flag_pos = x*TILE_SIZE
                #print( x*TILE_SIZE-scroll[0] )
                display.blit(flag_image2, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '5':
                display.blit( plant, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]) )
            if tile == '6':
                display.blit( flower, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]) )
            if tile != '0' and tile != '4' and tile != '3' and tile != '5' and tile != '6':
                tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    #print( player_rect.x )
    #print(flag_pos)

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
        last_move[0] = player_movement[0]
                
    if moving_left:
        player_movement[0] -= 2
        last_move[0] = player_movement[0]
                    
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    last_move[1] = player_y_momentum
    if player_y_momentum > 3:
        player_y_momentum = 3


    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
        position_fall = []
        position_fall = player_rect.x, player_rect.y

        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer - 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1

    if collisions['top']:
        player_y_momentum = 0

    # Banderas para las animaciones, orientación y caida segura
    if player_movement[0] > 0:
        player_action,player_frame = change_action(player_action,player_frame,'run')
        player_flip = False
    if player_movement[0] == 0 and last_move[0] >= 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
        player_flip = False
    if player_movement[0] == 0 and last_move[0] < 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')
        player_flip = True
    if player_movement[0] < 0:
        player_action,player_frame = change_action(player_action,player_frame,'run')
        player_flip = True
    if last_move[0] > 0 and air_timer > 5:
        player_action, player_frame = change_action(player_action, player_frame,'jump')
        player_flip = False
    if last_move[0] < 0 and air_timer > 5:
        player_action, player_frame = change_action(player_action, player_frame,'jump')
        player_flip = True
        
        

    if  player_rect.y >= 200:
        damage_sound.play()
        removeTiles(100)
        player_rect.x = position_fall[0]
        player_rect.y = position_fall[1]-30
        air_timer = 0
        death_count += 1
        
    def removeTiles(n):
        while(n != 0):
            a = random.randint(1, rows-2)
            b = random.randint(1, columns-2)
            #print(a, b)
            game_map[a][b] = '0'
            n -= 1

    # Loop para repetir el frame inicial
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]

    display.blit(pygame.transform.flip(player_img,player_flip,False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    #if last_move[0] >= 0 and air_timer > 5:
    #   display.blit(player_image_jump, (player_rect.x-scroll[0], player_rect.y-scroll[1])) 
    #elif last_move[0] >= 0:
    #   display.blit(player_image, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
    #if last_move[0] < 0 and air_timer > 5:
    #   display.blit(player_image_jump_mirror, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
    #elif last_move[0] < 0:
    #    display.blit(player_image_mirror, (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    for event in pygame.event.get():  # Evento Loop
        if event.type == QUIT:  # Revisa si se cerró la pantalla
            pygame.quit()  # Detiene pygame
            sys.exit()  # Detiene el script
        if event.type == KEYDOWN:
            if event.key == K_z:
                removeTiles( 100 )
            if event.key == K_w:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_e:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
                #print('right')
            if event.key == K_LEFT:
                #print('left')
                moving_left = True
            if event.key == K_UP:
                # Solo permite saltar cuando el tiempo en el aire sea menor que 20
                if air_timer < 20:              
                    player_y_momentum = -5
                    #The sounds must be initialize - check the first lines of code
                    jump_sound.play()
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
        
        #print(death_count)

        if death_count >= 3:
            print( "Perdiste" )
            lose = True
            while( lose ):
                for event in pygame.event.get():  # Evento Loop
                        if event.type == QUIT:  # Revisa si se cerró la pantalla
                            pygame.quit()  # Detiene pygame
                            sys.exit()  # Detiene el script
                        if event.type == KEYDOWN:
                            if event.key == K_k:
                                lose = False
                display.blit( perdiste_image, (0,0) )
                pygame.display.update()
                surf = pygame.transform.scale(display,WINDOW_SIZE)
                screen.blit(surf,(0,0))
                clock.tick(60)
            pygame.quit()
            sys.exit()

        if player_rect.x >= flag_pos - 15 and player_rect.x <= flag_pos + 15:
            print( "Ganaste" )
            win = True
            while( win ):
                for event in pygame.event.get():  # Evento Loop
                        if event.type == QUIT:  # Revisa si se cerró la pantalla
                            pygame.quit()  # Detiene pygame
                            sys.exit()  # Detiene el script
                        if event.type == KEYDOWN:
                            if event.key == K_k:
                                win = False 
                display.blit( ganaste_image, (0,0) )
                pygame.display.update()
                surf = pygame.transform.scale(display,WINDOW_SIZE)
                screen.blit(surf,(0,0))
                clock.tick(60)
            pygame.quit()
            sys.exit()


        #print( "Ubicación x: " + str( player_rect.x ) )
        #print( "Ubicación y: " + str( player_rect.y ) )
    
    surf = pygame.transform.scale(display,WINDOW_SIZE)
    screen.blit(surf,(0,0))
    pygame.display.update()
    clock.tick(60)
