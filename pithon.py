import pygame
import random
from itertools import product
from operator import itemgetter

DIRS_POINTS = (((1, 0), (0, 0)),
               ((0, 0), (1, 0)),
               ((0, 1), (0, 0)),
               ((0, 0), (0, 1)))
DIRS_SIDES = (((0, 0), (0, 1)),
              ((1, 0), (1, 1)),
              ((0, 0), (1, 0)),
              ((0, 1), (1, 1)))
DIRS_P_S = dict(zip(DIRS_POINTS, DIRS_SIDES))
DIRS_S_P = dict(zip(DIRS_SIDES, DIRS_POINTS))
FACTOR_POINT_N = {1: 0, -1: 1}


# Получить значение именованного параметра или значение по-умолчанию
def get_kwarg(kwargs, kwarg_name, else_arg=False):
    if else_arg:
        return kwargs[kwarg_name] if kwarg_name in kwargs else else_arg
    else:
        return kwargs[kwarg_name]


def listerize(seq):
    return list(map(lambda x: listerize(x)
                    if isinstance(x, (tuple, list)) else x, seq))


def tuplerize(seq):
    return tuple(map(lambda x: tuplerize(x)
                     if isinstance(x, (tuple, list)) else x, seq))


def growth_dir(dir_):
    return tuple(reversed(dir_))


# Суммировать координаты двух точек в одну
def pair_sum(*pair):
    return tuple(map(lambda el: pair_sum(*el)
                     if isinstance(pair[0][0], tuple) else sum(el),
                     zip(*pair)))


# Получение НомКоорд и Фактора (множителя)
def get_coords_ns_factors(dir_):
    coords_ns_factors = tuple(map(lambda i: (i, dir_[1][i] - dir_[0][i]),
                                  range(len(dir_[0]))))
    return tuple(filter(lambda x: x[1], coords_ns_factors))[0]


# Обрезка квадрата на 'val' по 'dir'
def cut_rect_points(rect, dir_, val):
    rect = listerize(rect)
    coord_n, factor = get_coords_ns_factors(dir_)
    point_n = FACTOR_POINT_N[factor]
    rect[point_n] = move_coords(rect[point_n], coord_n, factor, val)
    return tuplerize(rect)


def move_coords(coords, coord_n, factor, val):
    coords = listerize(coords)
    coords[coord_n] += factor * val
    return tuplerize(coords)


def factors_to_coords(seq, sq_size):
    return tuple(map(lambda p: (factors_to_coords(p, sq_size)
                                if isinstance(p, (tuple, list))
                                else p * sq_size), seq))


def square_to_point_coords(sq_coords, sq_size):
    return tuple(map(lambda coord: coord * sq_size, sq_coords))


# Преобразовать точечные координаты в квадратные с округлением
def points_to_square(coord, sq_size):
    return coord // sq_size, coord % sq_size  # Номер квадрата и !номер! линии



# Test-Grid

class GridLine(pygame.sprite.Sprite):
    def __init__(self, group, rect, pos, coord_n):
        super().__init__(group)
        self.rect = self.gen_rect(rect, pos, coord_n)
        x = self.rect[1][0] - self.rect[0][0]
        y = self.rect[1][1] - self.rect[0][1]
        x += 1 if x == 0 else 0
        y += 1 if y == 0 else 0
        self.image = pygame.Surface((x, y))
        self.image.fill('red')

    def gen_rect(self, rect, pos, coord_n):
        line_rect = tuple(map(lambda p: move_coords(p, coord_n, 1, pos), rect))
        return line_rect

def gen_grid(screen_size, sq_size, group):

    hor_rect_factors_points = ((0, 0), (1, 0))
    hor_rect = tuple([(p[0] * screen_size[0], p[1] * screen_size[0])
                      for p in hor_rect_factors_points])
    for i in range(0, screen_size[1], sq_size):
        GridLine(group, hor_rect, i, 1)

    vert_rect_factors_points = ((0, 0), (0, 1))
    vert_rect = tuple([(p[0] * screen_size[0], p[1] * screen_size[1])
                      for p in vert_rect_factors_points])
    for j in range(0, screen_size[0], sq_size):
        GridLine(group, vert_rect, j, 0)


# Test-Grid



class Game:
    def __init__(self):
        # Определить размеры Квадрата и Поля
        self.square_size = 32
        self.field_size_sq = size[0] // self.square_size, \
                             size[1] // self.square_size  # Кол-во ячеек по-вертик. и по-гориз.

        # Определить направление и длину Змеи в квадратах
        # snake_dir = random.choice(DIRS_POINTS)  # Случайное направление Змеи
        snake_dir = DIRS_POINTS[1]  # Test - uncomment prev.
        snake_len_in_sq = 3  # Длина в квадратах

        # Создать и перенести координаты 2-х квадратов - границ игрового поля
        # для выбора головного квадрата
        field_rect = ((0, 0), (self.field_size_sq[0] - 1,
                               self.field_size_sq[1] - 1))
        field_rect_cut = cut_rect_points(field_rect, snake_dir, 2)

        # Выбрать квадрат (координаты) Головн.Яч.
        (x1, y1), (x2, y2) = field_rect_cut
        # head_square = (random.randint(x1, x2),
        #                random.randint(y1, y2))
        head_square = (10, 4)  # Test - uncomment 2 prev.
        self.snake = Snake(self, snake_dir, snake_len_in_sq, head_square)
        # Создать группу спрайтов Яблок
        # self.apples = pygame.sprite.Group()

    def next_move(self):
        # test
        self.snake.make_move()
        # test

        # self.snake.update()

    ##        self.apples.update()

    def gen_apple(self):
        pass


class Snake(pygame.sprite.Group):
    def __init__(self, game, snake_dir, snake_len_in_sq, head_coords_sq):
        super().__init__()
        self.color = 'black'
        self.head_color = 'red'

        self.game = game
        self.dir_ = snake_dir
        self.lines = []

        # Генерация Линий в Кв-тах
        for sq_n in range(snake_len_in_sq):  # Для каждого номера кв-та
            coord_n, factor = get_coords_ns_factors(growth_dir(self.dir_))
            square = move_coords(head_coords_sq, coord_n, factor, sq_n)
            for line_n in range(self.game.square_size):  # Для кажд. номера линии (в кв-те) (0,1,...,15)
                line = Line(self, self.game.square_size, square, self.dir_, line_n)
                # Поместить в 'self.cells' в начало (стек) Линию с направлением,
                # координатами квадрата, номером линии
                self.lines.append(line)

        # print(self.dir_, head_coords_sq)
        # for line in self.lines:
        #     print(line.square, line.line_n, line.rect)

    def move_forward(self):
        tail_line = self.lines.pop(-1)
        square, line_n = self.lines[0].square, self.lines[0].line_n
        tail_line.update(square=square, line_n=line_n - 1)
        self.lines.insert(0, tail_line)



    def change_dir(self, direction):
        self.dir = direction


class Line(pygame.sprite.Sprite):
    def __init__(self, snake, square_size, square, dir_, line_n):
        super().__init__(snake)
        self.snake = snake
        self.length = square_size
        self.square = square
        self.dir_ = dir_

        self.length = self.snake.game.square_size

        self.line_n = line_n
        self.update_rect_image()

    def gen_rect(self):
        # Получить Прямоугольник (координаты точек) Линии внутри Квадрата
        rect_factors_points = DIRS_P_S[self.dir_]  # Факторы координат стороны "точки отсчета" по напр-ю
        rect_in_sq = factors_to_coords(rect_factors_points, self.length)  # Координаты точек из факторов
        coord_n, factor = get_coords_ns_factors(growth_dir(self.dir_))  # № координаты с Фактором 1 и Фактор (1)
        # Сдвинуть координаты на номер линии в квадрате
        line_rect_in_sq = tuple(map(lambda p:
                                    move_coords(p, coord_n, factor,
                                                self.line_n), rect_in_sq))

        # Получить координаты точки Квадрата Линии (первой точки Квадрата от начала координат)
        point_coords_of_square = square_to_point_coords(self.square, self.length)

        # Получить сумму координат точек
        return pair_sum(line_rect_in_sq, (point_coords_of_square,
                                          point_coords_of_square))

    def gen_image(self):
        x = self.rect[1][0] - self.rect[0][0]
        y = self.rect[1][1] - self.rect[0][1]
        x += 1 if not x else 0
        y += 1 if not y else 0
        return x, y

    def update(self, **kwargs):

        if 'dir_' in kwargs:
            dir_ = get_kwarg(kwargs, 'dir_')
            if dir_:
                self.dir_ == dir_

        if 'square' in kwargs:
            square = get_kwarg(kwargs, 'square')
            if square:
                self.square = square

        if 'line_n' in kwargs:
            line_n = get_kwarg(kwargs, 'line_n')
            if line_n:
                self.line_n = line_n
                if self.line_n >= self.length:
                    val = self.line_n // self.length
                    coord_n, factor = get_coords_ns_factors(growth_dir(self.dir_))
                    self.square = move_coords(self.square, coord_n, factor, val)
                    self.line_n %= self.length

        self.update_rect_image()

    def update_rect_image(self):
        self.rect = self.gen_rect()
        self.image = pygame.Surface(self.gen_image())
        self.image.fill(self.snake.color)


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
    size = 960, 640
    screen = pygame.display.set_mode(size)
    screen.fill('white')
    fps = 50
    clock = pygame.time.Clock()

    game = Game()


    # test
    screen_grid = pygame.sprite.Group()
    gen_grid(size, game.square_size, screen_grid)
    screen_grid.draw(screen)
    # for i in range(50):
    #     game.next_move()
    # test

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

        game.snake.move_forward()

        screen.fill('white')
        screen_grid.draw(screen)
        game.snake.draw(screen)

        clock.tick(fps)
        pygame.display.flip()

    pygame.quit()
