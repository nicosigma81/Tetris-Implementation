import pygame
from random import randint

grid_h = 25
grid_w = 10
win_x, win_y = (800, 600)

# Assume grid_h is smaller than grid_w
sq_len = 20
w_len = sq_len * grid_w
h_len = sq_len * grid_h

offset_x = (win_x - w_len) // 2
offset_y = (win_y - h_len) // 2

pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((win_x, win_y))
pygame.display.set_caption('Tetris')

font = pygame.font.Font('freesansbold.ttf', 18)

BACKGROUND1 = (100, 100, 100)
BACKGROUND2 = (120, 120, 120)


def pos_to_grid(pos):
    x, y = pos
    return (x - offset_x) // sq_len, (y - offset_y) // sq_len


def grid_to_pos(grid_pos):
    x, y = grid_pos
    return sq_len * x + offset_x, sq_len * y + offset_y


def read_high_score():
    file = open('file.txt', 'r')
    score = file.read()
    file.close()

    print(score)

    text = score.replace('highscore ', '')
    if text:
        return int(text)
    else:
        return 0


class Block:

    # Shape defaults in grid coordinates
    # T is 1, L is 2, flipped L is 3, line is 4, square is 5, S is 6, flipped S is 7.
    shapes = {1: [(-1, 0), (0, 0), (0, 1), (1, 0)],
              2: [(0, -1), (0, 0), (0, 1), (1, 1)],
              3: [(0, -1), (0, 0), (0, 1), (-1, 1)],
              4: [(-1, 0), (0, 0), (1, 0), (2, 0)],
              5: [(0, 0), (0, 1), (1, 1), (1, 0)],
              6: [(-1, 0), (0, 0), (0, 1), (1, 1)],
              7: [(-1, 1), (0, 1), (0, 0), (1, 0)]}

    colours = {1: (194, 242, 80),
               2: (56, 167, 171),
               3: (76, 18, 148),
               4: (207, 43, 68),
               5: (240, 149, 53),
               6: (25, 42, 227),
               7: (230, 80, 217)}

    def __init__(self, pos, shape_num):
        # Rotation in degrees
        self.orientation = 0
        self.pos = pos # Grid position
        self.colour = self.colours[shape_num]
        self.shape = self.shapes[shape_num]
        self.shape_num = shape_num

    def move(self, disp):
        self.pos = (self.pos[0] + disp[0], self.pos[1] + disp[1])

    def set_pos(self, pos):
        self.pos = pos

    def rotate(self, dir):
        self.orientation = (self.orientation + 90) % 360
        # Dir = 1 -> CW rotation, dir = -1 -> CCW rotation

        # Doesn't rotate square
        if self.shape_num == 5:
            return

        new_shape = []
        for shape in self.shape:
            # Rotates the shape by 90 degrees

            x = -dir * shape[1]
            y = dir * shape[0]

            new_shape.append((x, y))

        self.shape = new_shape

    def draw(self, surf):
        for vert in self.shape:
            # In relative grid coordinates
            x, y = grid_to_pos((vert[0] + self.pos[0], vert[1] + self.pos[1]))

            rect = pygame.Rect(x, y, sq_len, sq_len)

            pygame.draw.rect(surf, self.colour, rect)


class Square:
    def __init__(self, pos, colour):
        self.pos = pos
        self.colour = colour

    def move(self, disp):
        self.pos = (self.pos[0] + disp[0], self.pos[1] + disp[1])


def fix_block(block):

    # Returns a set of fixed squares in place of block object, deletes block object
    set_ = []
    for vert in block.shape:
        x, y = vert[0] + block.pos[0], vert[1] + block.pos[1]
        set_.append(Square((x, y), block.colour))

    del block
    return set_


def get_blocks_list():
    def get_blocks(arr):
        q = randint(1, 7)
        counter = 0
        for i in arr:
            if q == i: counter += 1
        if counter < 3:
            arr.append(q)
        else:
            get_blocks(arr)

    next_blocks = []
    for i in range(1, 7):
        get_blocks(next_blocks)

    return next_blocks


blocks = get_blocks_list()

num = randint(1, 5)
current_block = Block((grid_w // 2, 1), num)
squares = []

for i in range(grid_w):
    squares.append(Square((i, grid_h), (0, 0, 0)))

display_block = Block((grid_w + 2, 7), blocks[1])

speed = 0.005
fast = False
displacement = 0

# In grid coordinates
loss_level = 5
clear_counter = 0
level = 0

points = 0
tetris_counter = 0
highscore = read_high_score()

pygame.mixer.music.load("Tetris1.mp3")
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.3)
paused = False
music_textRect = pygame.Rect(0, 0, 0, 0)


player_loses = False
running = True
while running:

    current_block.vel = (0, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:

            file = open('file.txt', 'w')
            file.write(f'highscore {highscore}')
            file.close()

            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not player_loses:
            if event.button == 1:
                if music_textRect.collidepoint(event.pos):
                    if paused:
                        paused = False
                        pygame.mixer.music.play(loops=-1)
                    else:
                        paused = True
                        pygame.mixer.music.stop()

        if event.type == pygame.KEYDOWN and not player_loses:
            if event.key == pygame.K_m:
                if paused:
                    paused = False
                    pygame.mixer.music.play(loops=-1)
                else:
                    paused = True
                    pygame.mixer.music.stop()

            if event.key == pygame.K_UP:
                current_block.rotate(1)

                hit = False
                for vert in current_block.shape:
                    vert_pos = (vert[0] + current_block.pos[0], vert[1] + current_block.pos[1])
                    for sq in squares:
                        hit += vert_pos == sq.pos
                if hit:
                    current_block.rotate(-1)

            if event.key == pygame.K_DOWN:
                speed = 0.005

            flag1 = 0
            flag2 = 0
            for vert in current_block.shape:
                vert_pos = (vert[0] + current_block.pos[0], vert[1] + current_block.pos[1])
                for sq in squares:
                    flag1 += (sq.pos[0] + 1, sq.pos[1]) == vert_pos
                    flag2 += (sq.pos[0] - 1, sq.pos[1]) == vert_pos

            if event.key == pygame.K_LEFT and not flag1:
                current_block.move((-1, 0))
            elif event.key == pygame.K_RIGHT and not flag2:
                current_block.move((1, 0))

            if event.key == pygame.K_DOWN:
                fast = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                fast = False

    # Update blocks list
    if len(blocks) <= 1:
        blocks = get_blocks_list()

    # Collide with walls
    for vert in current_block.shape:
        vert_pos = (vert[0] + current_block.pos[0], vert[1] + current_block.pos[1])
        if vert_pos[0] >= grid_w:
            current_block.move((-1, 0))
        if vert_pos[0] < 0:
            current_block.move((1, 0))

    level = clear_counter // 10
    if fast: speed = 0.03 + level / 300
    else: speed = 0.002 + level / 300

    # Updates block position
    displacement += speed
    if int(displacement) == 1 and not player_loses:
        # Collision detection
        for vert in current_block.shape:
            vert_pos = (vert[0] + current_block.pos[0], vert[1] + current_block.pos[1])
            for sq in squares:
                if (sq.pos[0], sq.pos[1] - 1) == vert_pos:
                    for sq in fix_block(current_block):
                        squares.append(sq)

                    # Generate a new block to fall
                    num = blocks[0]
                    del blocks[0]
                    current_block = Block((grid_w // 2, 1), num)

        current_block.move((0, 1))
        displacement = 0

    # Check for clear
    counter_increment = 0
    for i in range(grid_h):
        row = []
        upper = []
        for sq in squares:
            if sq.pos[1] == i:
                row.append(sq)
            elif sq.pos[1] < i:
                upper.append(sq)
        if len(row) == grid_w:
            squares = [s for s in squares if s not in row]
            for s in row:
                del s
            for s in upper:
                s.move((0, 1))
            counter_increment += 1

    # Update Points
    clear_counter += counter_increment
    if 0 < counter_increment < 4:
        points += 100 * counter_increment
    elif counter_increment == 4:
        tetris_counter += 1
        if tetris_counter == 1:
            points += 800
        elif tetris_counter > 1:
            points += 1200

    if points > highscore:
        highscore = points

    # Check for loss
    for sq in squares:
        if sq.pos[1] <= loss_level:
            player_loses = True

    # ---------------------
    # Draw Frame
    # ---------------------

    # Draw background
    screen.fill((0, 0, 0))
    for i in range(grid_w):
        for j in range(grid_h):
            if i % 2 == 0: colour = BACKGROUND1
            else: colour = BACKGROUND2

            pygame.draw.rect(screen, colour,
                             pygame.Rect(i * sq_len + offset_x, j * sq_len + offset_y, sq_len, sq_len))

    # Display Score
    text = font.render(f"High score: {highscore}", True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.update(offset_x + w_len + 5, offset_y, 200, 20)
    screen.blit(text, textRect)

    text = font.render(f"Score: {points}", True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.update(offset_x + w_len + 5, offset_y + 30, 200, 20)
    screen.blit(text, textRect)

    text = font.render(f"Level: {level + 1}", True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.update(offset_x + w_len + 5, offset_y + 60, 200, 20)
    screen.blit(text, textRect)

    # Draw next block delay
    text = font.render(f"Next Block:", True, (255, 255, 255), (0, 0, 0))
    textRect = text.get_rect()
    textRect.update(offset_x + w_len + 5, offset_y + 90, 200, 20)
    screen.blit(text, textRect)

    display_block.shape = display_block.shapes[blocks[0]]
    display_block.colour = display_block.colours[blocks[0]]
    display_block.draw(screen)

    # Settings
    music_state = 'On'
    if paused:
        music_state = 'Off'
    text = font.render(f"Music: {music_state}", True, (255, 255, 255), (0, 0, 0))
    music_textRect = text.get_rect()
    music_textRect.update(offset_x - 100, offset_y, 200, 20)
    if music_textRect.collidepoint(pygame.mouse.get_pos()):
        text = font.render(f"Music: {music_state}", True, (200, 200, 200), (0, 0, 0))
    screen.blit(text, music_textRect)

    # Draw squares
    for sq in squares:
        x, y = grid_to_pos(sq.pos)
        pygame.draw.rect(screen, sq.colour, pygame.Rect(x, y, sq_len, sq_len))

    # Draw current block
    current_block.draw(screen)

    pygame.display.update()
