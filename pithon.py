import pygame
import random
from itertools import product
from operator import itemgetter



# ['left', 'up', 'right', 'down']
DIRECTIONS = ['left', 'up', 'right', 'down']
# {1073741904: 'left', 1073741906: 'up', 1073741903: 'right', 1073741905: 'down'}
KEYS_DIRS = dict(zip((pygame.K_LEFT, pygame.K_UP, pygame.K_RIGHT,
                     pygame.K_DOWN), DIRECTIONS))
# {'left': 1073741904, 'up': 1073741906, 'right': 1073741903, 'down': 1073741905}
DIRS_KEYS = dict(zip(KEYS_DIRS.values(), KEYS_DIRS.keys()))
# {'left': 'right', 'up': 'down', 'right': 'left', 'down': 'up'}
OPPO_DIRS = dict(zip(DIRECTIONS, itemgetter(2, 3, 0, 1)(DIRECTIONS)))
# {1073741904: 1073741903, 1073741906: 1073741905, 1073741903: 1073741904, 1073741905: 1073741906}
OPPO_KEYS = {DIRS_KEYS[d]: DIRS_KEYS[op_d] for d, op_d in OPPO_DIRS.items()}
# {'strait': {'left': (0, -1), 'right': (0, 1), 'up': (1, -1), 'down': (1, 1)},
# 'back': {'left': (0, 1), 'right': (0, -1), 'up': (1, 1), 'down': (1, -1)}}
PLUS_MINUS = {'strait': dict(zip(('left', 'right', 'up', 'down'),
                                 product((0, 1), (-1, 1)))),
              'back': dict(zip(('left', 'right', 'up', 'down'),
                               product((0, 1), (1, -1))))}


def coords_plus_minus(coords, value, direction, strait_or_back):
    coords = list(coords)
    idx, sign = PLUS_MINUS[strait_or_back][direction]
    coords[idx] += value * sign
    return tuple(coords)


class Game:
    def __init__(self):
        self.square_size = 16
        # Кол-во ячеек по-вертик. и по-горит.
        self.field_size = size[0] // self.square_size, size[1] // \
                          self.square_size

        # Создать объект Змеи
        self.snake = Snake(self, self.square_size * 8)
        # Создать группу спрайтов Яблок
        # self.apples = pygame.sprite.Group()

    def next_move(self):
        self.snake.update()
##        self.apples.update()

    def gen_apple(self):
        pass


class Snake(pygame.sprite.Group):
    def __init__(self, game, length):
        super().__init__()
        self.game = game
        self.color = 'black'
        self.head_color = 'red'

        self.dir = random.choice(DIRECTIONS)
        
        # Добавить первую часть - и хвост, и голова
        ## Создать головную ячейку
        head_coords = (self.game.field_size[0] // 2 * self.game.square_size,
                       self.game.field_size[1] // 2 * self.game.square_size)
        head_cells = [Snake_cell(coords_plus_minus(head_coords, 1, self.dir,
                                                   'back'), visual_head=True)
                      for i in range(self.game.square_size)]
        ## Создать головную часть с головной ячейкой
        snake_head = Snake_part(groups=[self], snake=self, length=length,
                                dir=self.dir, cells=head_cells)
        for i in range(len(head_cells), length):
            coords = coords_plus_minus(head_cells[-1].coords, i,
                                       snake_head.dir, 'back')
            snake_head.insert(Snake_cell(coords))
        snake_head.renew_image_rect()

    def get_head(self, item='part'):
        head_part = self.sprites()[-1]
        head_cell = head_part.cells[-1]
        head_coords = head_cell.coords
        head_items = {'part': head_part,
                      'cell': head_cell,
                      'coords': head_coords}
        return head_items[item]
    
    def update(self):
        parts = self.sprites()
        last_cells = [part.pop() for part in parts]  # Выделить последние ячейки из всех частей
        head_cell = last_cells.pop(-1)  # Выделить головную ячейку в отдельную переменную
        if last_cells:  # Переставить передние ячейки в следующие части
            [parts[i + 1].insert(last_cells[i]) for i in range(len(last_cells))]
        if not parts[0].cells:  # Если хвостовая часть не содержит ячеек - удалить ее из группы
            parts[0].remove(self)
        # Создать новую головную часть
        if self.get_head('part').dir != self.dir:
            new_head_part = Snake_part(groups=[self], snake=self, length=1,
                                       dir=self.dir, cells=[head_cell])
        else:
            self.get_head('part').insert(head_cell, -1)
        # Вызвать методы update у каждого спрайта (части)
        parts = self.sprites()
        for part in parts:
            part.update()

    def change_dir(self, direction):
        self.dir = direction
        

class Snake_part(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        # kwargs:
        # groups: []
        # snake: Snake
        # length: int
        # dir: str
        # cells: [Snake_cells]
        super().__init__(*kwargs['groups'])
        self.length = kwargs['length'] if 'length' in kwargs else 1
        self.snake = kwargs['snake']
        self.dir = kwargs['dir'] if 'dir' in kwargs else self.snake.dir
        # Добавляем все ячейки в новую часть (головную)
        self.cells = [cell for cell in kwargs['cells']]
        [cell.update(part=self) for cell in self.cells]


    def index(self):
        return self.snake.sprites().index(self)

    def is_head(self): return self.index() == len(self.snake) - 1

    def is_tail(self): return not self.index()

    def renew_image_rect(self):
        self.length = self.get_length()
        self.image = self.get_image()
        self.rect = self.get_rect()

    def get_image(self):
        x1, y1, x2, y2 = self.get_sprite_coords()
        return pygame.Surface((x2 - x1, y2 - y1))

    # Используется метод 'coords_plus_minus'
    def get_rect(self):
        x1, y1, x2, y2 = self.get_sprite_coords()
        return pygame.Rect(x1, y1, x2 - x1, y2 - y1)

    def get_sprite_coords(self):
        hor, ver = self.cells[0].get_sizes()
        print(hor, ver)
        hor_coords = tuple(map(lambda cell: cell.coords[0], self.cells))
        left = min(hor_coords)
        right = max(hor_coords)
        ver_coords = tuple(map(lambda cell: cell.coords[1], self.cells))
        up = min(ver_coords)
        down = max(ver_coords)
        x1 = left - hor
        y1 = up - ver
        x2 = right
        y2 = down
        return (x1, y1, x2, y2)

    def update(self):
        for cell in self.cells:  # передвинуть вперед каждую ячейку в части
            cell.update(coords=coords_plus_minus(cell.coords, 1,
                                                 self.dir, 'strait'))
        self.renew_image_rect()

    def insert(self, cell, idx=0):
        cell.update(part=self)
        if idx == -1:
            self.cells.append(cell)
        else:
            self.cells.insert(idx, cell)

    def get_length(self):
        return len(self.cells)

    def pop(self, index=-1):
        return self.cells.pop(index)



class Snake_cell:
    def __init__(self, coords, part=False, visual_head=False):
        self.coords = coords
        self.part = part
        self.visual_head = visual_head

    def update(self, **kwargs):
        if 'coords' in kwargs:
            self.coords = kwargs['coords']
        if 'part' in kwargs:
            self.part = kwargs['part']
        if 'visual_head' in kwargs:
            self.visual_head = kwargs['visual_head']

    def get_sizes(self):
        if self.part.dir in ('up', 'down'):
            hor = self.part.snake.game.square_size
            ver = 1
        elif self.part.dir in ('left', 'right'):
            hor = 1
            ver = self.part.snake.game.square_size
        return (hor, ver)

        
class Apple(pygame.sprite.Sprite):
    def __init__(self, square, apples, game):
        super().__init__(*apples)
        self.game = game
        self.color = 'green'
        self.square = square
        self.rect = pygame.Rect(self.square[0] * self.game.square_size,
                                self.square[1] * self.game.square_size,
                                self.square[0] * self.game.square_size +
                                self.game.square_size,
                                self.square[1] * self.game.square_size +
                                self.game.square_size)
        self.image = pygame.Surface((self.game.square_size,
                                     self.game.square_size))
        self.rect = pygame.Rect(self.x, self.y, self.game.square_size,
                                self.game.square_size)


if __name__ == '__main__':
    pygame.init()
    size = 1280, 1024
    screen = pygame.display.set_mode(size)
    screen.fill('white')
    fps = 50
    clock = pygame.time.Clock()

    game = Game()


    test = 0
    new_snake_dir = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                print(event.key, KEYS_DIRS[event.key])
                if (event.key in KEYS_DIRS) and (game.snake.dir not in \
                        (KEYS_DIRS[event.key], KEYS_DIRS[OPPO_KEYS
                        [event.key]])):
                    new_snake_dir = KEYS_DIRS[event.key]
        if all(map(lambda coord: not coord % game.square_size,
                   game.snake.get_head('coords'))) and new_snake_dir:
            game.snake.change_dir(new_snake_dir)
            new_snake_dir = False
            
        screen.fill('white')
        game.snake.draw(screen)

        game.next_move()

        
        clock.tick(fps)
        pygame.display.flip()
        

    pygame.quit()
