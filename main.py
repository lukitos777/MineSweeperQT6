from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication, QPushButton, QGridLayout, QMessageBox
)
from PyQt6.QtCore import ( Qt, pyqtSignal, QSize )

from sys import argv
from random import randint
from functools import wraps
from enum import Enum

rows, columns, mines = 13, 9, 27

class Styles(Enum):
    button_style_1 = 'QPushButton {\nbackground-color: #e2dede;\nwidth: 55px;\nheight: 55px;\n' +\
                    'font-size: 22px;\nfont-weight: bold;\ncolor: _____;\nborder: none;\nborder-radius: 5px;\n}' +\
                    '\nQPushButton:hover {\nbackground-color: #cccbcb;\n}' +\
                    '\nQPushButton:disabled {\nbackground-color: #e2dede;\n}'
    button_style_2 = 'QPushButton {\nbackground-color: #f01111;\nwidth: 55px;\nheight: 55px;\n' +\
                    'font-size: 18px;\nfont-weight: bold;\ncolor: #000000;\nborder: none;\nborder-radius: 5px;\n}' +\
                    '\nQPushButton:disabled {\nbackground-color: #f01111;\n}'
    main_window_style = 'background-color: #3d3b39;'
    value_styles = {
        '1': button_style_1.replace('_____', '#07c3f1'), '2': button_style_1.replace('_____', '#12e8ab'),
        '3': button_style_1.replace('_____', '#f6263f'), '4': button_style_1.replace('_____', '#ed26f6'),
        '5': button_style_1.replace('_____', '#ece72f'), '6': button_style_1.replace('_____', '#f48b23'),
        '7': button_style_1.replace('_____', '#f4238c'), '8': button_style_1.replace('_____', '#be23f4')
    }
    

def dialog_decorator(title: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            msg_box = QMessageBox()
            msg_box.setWindowTitle(title)
            msg_box.setText('Would you like restart or cancel game ?')

            restart_button = msg_box.addButton("Restart", QMessageBox.ButtonRole.AcceptRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            msg_box.exec()

            if msg_box.clickedButton() == restart_button:
                self.restart_game()
            elif msg_box.clickedButton() == cancel_button:
                QApplication.quit()
        return wrapper
    return decorator

class Cell(QPushButton):
    game_over_signal, increament_counter_signal, run_bfs_sinal = pyqtSignal(), pyqtSignal(), pyqtSignal(tuple)
    def __init__(
            self, position: tuple[int, int] = (0, 0), is_mine: bool = False, 
            is_open: bool = False, value: str = '0', is_barier: bool = False
        ) -> None:
        super().__init__()
        self.position = position
        self.is_mine = is_mine
        self.is_open = is_open
        self.value = value
        self.is_barier = is_barier
        self.setStyleSheet(Styles.button_style_1.value)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_cell()
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_flag()
        super().mousePressEvent(event)

    def set_flag(self) -> None:
        self.setText('') if self.text() == 'F' else self.setText('F')

    def open_cell(self) -> None:
        if self.is_mine:
            self.setText('*')
            self.setStyleSheet(Styles.button_style_2.value)
            self.game_over_signal.emit()
        elif self.value == '0':
            self.run_bfs_sinal.emit(self.position)
        else:
            self.setText(self.value)
            self.increament_counter_signal.emit()
        self.is_open = True
        self.setDisabled(True)
        self.set_value_style()

    def open_cell_by_function(self) -> None:
        if self.is_mine:
            self.setStyleSheet(Styles.button_style_2.value)
        self.setText(self.value) if self.value != '0' else self.setText('_')
        self.is_open = True
        self.setDisabled(True)
        self.set_value_style()
        self.increament_counter_signal.emit()

    def set_value_style(self) -> None:
        self.setStyleSheet(Styles.value_styles.value[self.value]) if self.value not in '0*' else ...


class Mine_Sweeper(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.set_UI()
        self.generate_field()
        self.connect_signals()
        self.counter = 0

    def set_UI(self) -> None:
        widget = QWidget()
        main_layout = QGridLayout()

        self.setFixedSize(QSize(500, 720))
        self.setWindowTitle('MineSweeper QT')

        self.field: list[list[Cell]] = [
            [Cell(is_barier=True) for i in range(columns + 2)],
            *[[Cell(is_barier=True), *[Cell() for i in range(columns)], Cell(is_barier=True)] for j in range(rows)],
            [Cell(is_barier=True) for i in range(columns + 2)]
        ]

        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                main_layout.addWidget(self.field[i][j], i, j)
                self.field[i][j].position = (i, j)

        self.setStyleSheet(Styles.main_window_style.value)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def generate_field(self) -> None:
        mines = set()

        while len(mines) != 27:
            mine = (randint(1, rows), randint(1, columns))
            mines.add(mine)

        for mine in list(mines):
            self.field[mine[0]][mine[1]].is_mine = True
            self.field[mine[0]][mine[1]].value = '*'

        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                if not self.field[i][j].is_mine:
                    self.field[i][j].value = str([
                        self.field[i - 1][j - 1].is_mine, self.field[i - 1][j].is_mine,
                        self.field[i - 1][j + 1].is_mine, self.field[i][j - 1].is_mine,
                        self.field[i][j + 1].is_mine, self.field[i + 1][j - 1].is_mine,
                        self.field[i + 1][j].is_mine, self.field[i + 1][j + 1].is_mine
                    ].count(True))
    
    def connect_signals(self) -> None:
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                self.field[i][j].game_over_signal.connect(self.show_game_over_dialog)
                self.field[i][j].increament_counter_signal.connect(self.increment_counter)
                self.field[i][j].run_bfs_sinal.connect(self.breadth_first_search)

    def increment_counter(self) -> None:
        self.counter -= -1
        if self.counter == rows * columns - mines:
            self.show_winner_dialog()

    @dialog_decorator(title='You lost !')
    def show_game_over_dialog(self) -> None:
        self.open_full_field()
    
    @dialog_decorator(title='You won !')
    def show_winner_dialog(self) -> None:
        self.restart_game()

    def restart_game(self) -> None:
        self.set_UI()
        self.generate_field()
        self.connect_signals()

    def breadth_first_search(self, position: tuple[int, int]) -> None:
        cells: list[Cell] = []
        cells.append(self.field[position[0]][position[1]])

        while cells:
            current_cell = cells.pop(0)
            i, j = current_cell.position

            if current_cell.is_open:
                continue

            if current_cell.value != '0':
                current_cell.open_cell_by_function()
                continue

            current_cell.open_cell_by_function()

            for delta_i in [-1, 0, 1]:
                for delta_j in [-1, 0, 1]:
                    new_i, new_j = i + delta_i, j + delta_j

                    if 1 <= new_i <= rows and 1 <= new_j <= columns:
                        neighbor_cell = self.field[new_i][new_j]

                        if not neighbor_cell.is_open and not neighbor_cell.is_barier and not neighbor_cell.is_mine:
                            cells.append(neighbor_cell)

    def open_full_field(self) -> None:
        for i in range(1, rows + 1):
            for j in range(1, columns + 1):
                self.field[i][j].open_cell_by_function()


def main(*args, **kwargs) -> None:
    app = QApplication(argv) 
    window = Mine_Sweeper()
    window.show()   
    app.exec() 

if __name__ == '__main__':
    main()
    