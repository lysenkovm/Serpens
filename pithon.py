import pygame
import random
from itertools import product



DIRECTIONS = ['left', 'up', 'right', 'down']
DIR_KEYS = dict(zip((pygame.K_LEFT, pygame.K_UP, pygame.K_RIGHT,
                     pygame.K_DOWN), DIRECTIONS))
# {'strait': {'left': (0, -1), 'right': (0, 1), 'up': (1, -1), 'down': (1, 1)},
# 'back': {'left': (0, 1), 'right': (0, -1), 'up': (1, 1), 'down': (1, -1)}}
PLUS_MINUS = {'strait': dict(zip(('left', 'right', 'up', 'down'),
                                 product((0, 1), (-1, 1)))),
              'back': dict(zip(('left', 'right', 'up', 'down'),
                               product((0, 1), (1, -1))))}


def square_plus_minus(square, value, direction, strait_or_back):
    square = list(square)
    idx, sign = PLUS_MINUS[strait_or_back][direction]
    square[idx] += value * sign
    return tuple(square)


class Game:
    def __init__(self):
        self.square_size = 16
        self.field_size = size[0] // self.square_size, size[1] // \
                          self.square_size

        # Создать объект Змеи
        self.snake = Snake(self, 15)
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
        
        # Добавить первую часть: и хвост, и голова
        ## Создать головную ячейку
        head_square = (self.game.field_size[0] // 2,
                       self.game.field_size[1] // 2)
        head_cell = Snake_cell(head_square)
        ## Создать головную часть с головной ячейкой
        snake_head = Snake_part(groups=[self], snake=self, length=length, dir=self.dir, cells=[head_cell])
        for i in range(1, length):
            square = square_plus_minus(head_square, i, snake_head.dir, 'back')
            snake_head.cells.insert(0, Snake_cell(square))
        snake_head.renew_image_rect()

    def get_head(self, item='part'):
        head_part = self.sprites()[-1]
        head_cell = head_part.cells[-1]
        head_square = head_cell.square
        head_items = {'part': head_part,
                      'cell': head_cell,
                      'square': head_square}
        return head_items[item]
    
    def update(self):
        parts = self.sprites()
        last_cells = [part.get_last_cell() for part in parts]  # Выделить последние ячейки из всех частей
        head_cell = last_cells.pop(-1)  # Выделить головную ячейку в отдельную переменную
        if last_cells:  # Переставить передние ячейки в следующие части
            [parts[i + 1].insert_cell(last_cells[i]) for i in range(len(last_cells))]
        if not parts[0].cells:  # Если хвостовая часть не содержит ячеек - удалить ее из группы
            parts[0].remove(self)
        # Создать новую головную часть
        if self.get_head('part').dir != self.dir:
            new_head_part = Snake_part(groups=[self], snake=self, length=1,
                                       dir=self.dir, cells=[head_cell])
        else:
            self.get_head('part').insert_cell(head_cell, -1)
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
        # cells: [Snake_cell]
        super().__init__(*kwargs['groups'])
        self.length = kwargs['length'] if 'length' in kwargs else 1
        self.snake = kwargs['snake']
        self.dir = kwargs['dir'] if 'dir' in kwargs else self.snake.dir
        # Добавляем все ячейки в новую часть (головную)
        self.cells = kwargs['cells'] if 'cells' in kwargs else []


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

    # Используется метод 'square_plus_minus'
    def get_rect(self):
        x1, y1, x2, y2 = self.get_sprite_coords()
        return pygame.Rect(x1, y1, x2 - x1, y2 - y1)

    def get_sprite_coords(self):
        hor_coords = tuple(map(lambda cell: cell.square[0], self.cells))
        left = min(hor_coords)
        right = max(hor_coords)
        ver_coords = tuple(map(lambda cell: cell.square[1], self.cells))
        up = min(ver_coords)
        down = max(ver_coords)
        x1 = (left - 1) * self.snake.game.square_size
        y1 = (up - 1) * self.snake.game.square_size
        x2 = (right) * self.snake.game.square_size
        y2 = (down) * self.snake.game.square_size
        return (x1, y1, x2, y2)

    def update(self):
        for cell in self.cells:  # передвинуть вперед каждую ячейку в части
            cell.update(square_plus_minus(cell.square, 1, self.dir, 'strait'))
        self.renew_image_rect()

    def insert_cell(self, cell, idx=0):
        if idx == -1:
            self.cells.append(cell)
        else:
            self.cells.insert(idx, cell)

    def get_length(self):
        return len(self.cells)

    def get_last_cell(self):
        return self.cells.pop(-1)


class Snake_cell:
    def __init__(self, square):
        self.square = square
        
    def update(self, square):
        self.square = square
        

        
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
    fps = 10
    clock = pygame.time.Clock()

    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN) and \
                   game.snake.dir not in ('up', 'down'):
                    game.snake.change_dir(DIR_KEYS[event.key])
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT) and \
                     game.snake.dir not in ('left', 'right'):
                    game.snake.change_dir(DIR_KEYS[event.key])
            
        screen.fill('white')
        game.snake.draw(screen)

        game.next_move()

        
        clock.tick(fps)
        pygame.display.flip()
        

    pygame.quit()
