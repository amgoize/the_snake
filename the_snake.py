from random import randint
import pygame
from typing import Optional, Tuple, List

# Инициализация PyGame:
pygame.init()

# Константы для размеров экрана и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения змейки:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона экрана - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячеек:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна:
pygame.display.set_caption('Змейка')

# Создание объекта для отслеживания времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для объектов игры."""

    def __init__(self, position: Optional[Tuple[int, int]] = None,
                 body_color: Optional[Tuple[int, int, int]] = None) -> None:
        """
        Инициализация базового объекта на игровом поле.

        Параметры:
        position — позиция объекта на поле.
        Если не задано, используется
        центральная позиция.
        body_color — цвет объекта. Если не задано, используется белый.
        """
        self.position = position or (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color or (255, 255, 255)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод для отрисовки объекта на экране.

        Этот метод должен быть переопределен в дочерних классах.
        """
        pass

    def draw_cell(self, surface: pygame.Surface, position: Tuple[int, int],
                  color: Optional[Tuple[int, int, int]] = None) -> None:
        """
        Отрисовывает одну ячейку на экране с заданной позицией и цветом.

        Параметры:
        surface — поверхность, на которой рисуется объект.
        position — позиция ячейки на экране.
        color — цвет ячейки. Если не задано, используется цвет объекта.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color or self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Представляет яблоко на игровом поле, наследуется от GameObject."""

    def __init__(self) -> None:
        """
        Инициализация яблока.

        Яблоко появляется в случайной позиции на поле.
        """
        super().__init__(None, APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self) -> None:
        """
        Устанавливает случайную позицию для яблока на поле.

        Позиция выбирается так, чтобы яблоко не выходило за пределы экрана.
        """
        self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает яблоко на экране.

        Параметры:
        surface — поверхность, на которой рисуется яблоко.
        """
        self.draw_cell(surface, self.position)


class Snake(GameObject):
    """Представляет змейку на игровом поле, наследуется от GameObject."""

    def __init__(self) -> None:
        """
        Инициализация змейки на поле.

        Изначально змейка имеет длину 1 и расположена в центре экрана.
        """
        super().__init__((GRID_WIDTH // 2 * GRID_SIZE,
                          GRID_HEIGHT // 2 * GRID_SIZE), SNAKE_COLOR)
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None

    def update_direction(self, new_direction: Tuple[int, int]) -> None:
        """
        Обновляет направление движения змейки, если
        новое направление не противоположно текущему.

        Параметры:
        new_direction — новое направление движения змейки.
        """
        if new_direction != (self.direction[0] * -1, self.direction[1] * -1):
            self.next_direction = new_direction

    def move(self) -> None:
        """
        Обновляет позицию змейки.

        Метод добавляет новый сегмент в голову змейки
        и удаляет последний сегмент,
        если длина змейки не увеличилась. Также проверяет
        на столкновение с телом.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        cur_head = self.positions[0]
        x, y = self.direction
        new_head = ((cur_head[0] + (x * GRID_SIZE)) % SCREEN_WIDTH,
                    (cur_head[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает змейку на экране, стирая след.

        Параметры:
        surface — поверхность, на которой рисуется змейка.
        """
        for position in self.positions[:-1]:
            self.draw_cell(surface, position)

        head_position = self.positions[0]
        self.draw_cell(surface, head_position, SNAKE_COLOR)

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки (первый элемент в списке positions).

        Возвращает:
        Позиция головы змейки.
        """
        return self.positions[0]

    def reset(self) -> None:
        """
        Сбрасывает змейку в начальное состояние после столкновения с собой.

        Змейка возвращается в центр экрана, длина равна 1.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None


def handle_keys(snake: Snake) -> None:
    """
    Обрабатывает нажатия клавиш для изменения направления движения змейки.

    Параметры:
    snake — объект змейки, чье направление будет изменено.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.update_direction(UP)
            elif event.key == pygame.K_DOWN:
                snake.update_direction(DOWN)
            elif event.key == pygame.K_LEFT:
                snake.update_direction(LEFT)
            elif event.key == pygame.K_RIGHT:
                snake.update_direction(RIGHT)


def main() -> None:
    """Основной игровой цикл."""
    # Создание объектов змейки и яблока
    snake = Snake()
    apple = Apple()

    while True:
        # Ограничение кадров в секунду (по скорости)
        clock.tick(SPEED)

        # Обработка событий клавиш
        handle_keys(snake)

        # Двигаем змейку
        snake.move()

        # Проверка на съедание яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1  # Увеличиваем длину змейки
            apple.randomize_position()  # Перемещаем яблоко в новое место

        # Проверка на столкновение змейки с собой
        if len(snake.positions) > 2 and \
           snake.get_head_position() in snake.positions[2:]:
            snake.reset()  # Сбрасываем игру после столкновения с собой

        # Отрисовываем элементы на экране
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        # Обновляем экран
        pygame.display.update()


if __name__ == '__main__':
    main()
