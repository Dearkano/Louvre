from copy import deepcopy
from queue import Queue

import xlrd
import numpy

from model.Exit import Exit
from model.Blank import Blank
from model.Floor import Floor
from model.Human import Human
from model.Item import Item
from model.Stair import Stair
import datetime
import random

FLOORS = 5
ROWS = 58 * 1
COLUMNS = 136 * 1
AMOUNT_OF_ANT = 200

start_time = 0

exit_amount = 0
exit_floor = []
connect_floor = []
exits = []  # The position of exit. e.g. [0:[(1,2)],1:[],2:[],3:[],4:[]]
stairs = []  # The position of stair. e.g. [0:[(1,2)],1:[],2:[],3:[],4:[]]
available = []  # The position of block which can stand. e.g. [(1,2,3),(1,3,4)]
location_pool = []  # Copy of available to help iterate. e.g. [(1,2,3),(1,3,4)]
# e.g. [0:[0:[],1:[]],1:[0:[],1:[]]]
louvre_map = numpy.empty([FLOORS, ROWS, COLUMNS], dtype=Item)
humans = numpy.empty(AMOUNT_OF_ANT, dtype=Human)  # e.g. [human1,human2]


def read_data():
    excel = xlrd.open_workbook(r'./data.xlsx')
    for f in range(FLOORS):
        sheet = excel.sheet_by_index(f)
        for i in range(ROWS):
            for j in range(COLUMNS):
                value = int(sheet.cell(int(i / 1), int(j / 1)).value)
                if value == 1:  # Floor
                    louvre_map[f][i][j] = Floor()
                    available.append((f, i, j))
                elif value == 3:  # Up to down stair
                    louvre_map[f][i][j] = Stair(0)
                    stairs[f].append((i, j))
                    available.append((f, i, j))
                elif value == 4:  # Exit
                    louvre_map[f][i][j] = Exit()
                    exits[f].append((i, j))
                    exit_floor.append(f)
                    available.append((f, i, j))
                elif value == 2:  # Down to up stair
                    louvre_map[f][i][j] = Stair(1)
                    stairs[f].append((i, j))
                    available.append((f, i, j))
                else:
                    louvre_map[f][i][j] = Blank()

# Get the neighbor which can reach


def check_neighbor(f, x, y):
    neighbors = []
    for (x2, y2) in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1),
                     (x - 1, y - 1), ]:
        if x2 >= 0 and x2 < ROWS and y2 >= 0 and y2 < COLUMNS and not isinstance(louvre_map[f][x2][y2], Blank) and \
                louvre_map[f][x2][y2].owner is None:
            neighbors.append((x2, y2))
    return neighbors


def initial_graph():
    graph = numpy.full(
        [FLOORS, ROWS * COLUMNS, ROWS * COLUMNS], 9999, dtype=float)
    for f in range(0, FLOORS - 1):
        for r in range(0, ROWS):
            for c in range(0, COLUMNS):
                if not isinstance(louvre_map[f][r][c], Blank):
                    for neighbor in check_neighbor(f, r, c):
                        if r == neighbor[0] or c == neighbor[1]:
                            graph[f][map_coodinate_to_id(r, c)][map_coodinate_to_id(
                                neighbor[0], neighbor[1])] = 1
                        else:
                            graph[f][map_coodinate_to_id(r, c)][map_coodinate_to_id(
                                neighbor[0], neighbor[1])] = 2
            graph[f][r][r] = 0
    return graph


def map_coodinate_to_id(r, c):
    return r * COLUMNS + c


if __name__ == '__main__':
    for i in range(FLOORS):
        exits.append([])
        stairs.append([])
    read_data()
