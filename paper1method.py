# Method from this paper: https://www.researchgate.net/publication/224180108_Solving_Sudoku_with_genetic_operations_that_preserve_building_blocks
import random
import modified_pyeasyga
from operator import attrgetter
# import pygame
import numpy as np
import sys
import time
import json
import requests

# Each array is a box of the sudoku
# The first box is top left, the second is middle top, etc.
DIM = 9
SQRT_DIM = int(DIM**0.5)
TOURNAMENT_SIZE = 3
TOURNAMENT_PROB = .9
random.seed(time.time())
random_board = [0,0,0,8,0,0,0,0,7,3,0,0,0,4,7,0,0,0,8,0,1,0,0,2,3,
6,0,0,6,0,0,0,8,0,0,2,0,0,5,9,2,4,7,0,0,2,0,0,6,0,0,0,3,0,0,8,4,7,0,0,2,0,1,
0,0,0,2,1,0,0,0,8,5,0,0,0,0,6,0,0,0]
easy_board = [[0,0,4,6,7,0,5,0,8],[8,0,0,9,0,0,0,3,0],
              [0,1,7,0,0,0,0,0,4],[3,0,0,0,6,9,0,0,1],
              [7,4,0,0,0,0,0,6,9],[1,0,0,7,8,0,0,0,5],
              [1,0,0,0,0,0,2,4,0],[0,8,0,0,0,6,0,0,1],
              [3,0,6,0,9,1,5,0,0]]
hard_board = [[7,5,0,0,1,0,4,0,0],[2,0,0,0,9,6,0,5,0],[0,0,0,0,0,4,0,0,3],
              [0,0,0,0,0,7,5,0,1],[0,3,0,0,4,0,0,0,2],[0,0,5,0,3,0,9,0,0],
              [9,0,0,0,0,0,0,0,4],[0,0,0,0,6,0,0,0,8],[3,8,7,0,0,0,5,1,0]]
BOARD_CHOICE = easy_board

def generate_initial_boxes(given_puzzle, DIM=9, SQRT_DIM=3):
  board = []
  counted = set()
  for i in range(DIM * 2):
    if i % 2 == 0:
      for element in given_puzzle[i//2]:
        if element != 0:
          counted.add(element)
    else:
      board.append([])
      for element in given_puzzle[i//2]:
        if element == 0 and len(counted) < DIM:
          chosen = random.choice([i for i in range(1,DIM+1) if i not in counted])
          board[i//2].append(chosen)
          counted.add(chosen)
        else:
          board[i//2].append(element)
      counted = set()
  return board

def rows_to_boxes(board):
  newboard = []
  for i in range(SQRT_DIM):
    for j in range(SQRT_DIM):
      for k in range(SQRT_DIM):
        for l in range(SQRT_DIM):
          newboard.append(board[i*SQRT_DIM+k][j*SQRT_DIM+l])
  newbox2d = []
  for i in range(DIM):
    newbox2d.append(newboard[i*DIM:(i+1)*DIM])
  return newbox2d


def cols_to_boxes(board):
  newboard = []
  for i in range(SQRT_DIM):
    for j in range(SQRT_DIM):
      for k in range(SQRT_DIM):
        for l in range(SQRT_DIM):
          newboard.append(board[j*SQRT_DIM+l][i*SQRT_DIM+k])
  newbox2d = []
  for i in range(DIM):
    newbox2d.append(newboard[i*DIM:(i+1)*DIM])
  return newbox2d

def fitness_rows(board, row, DIM=9, SQRT_DIM=3):
  fitness = []
  if row:
    for i in range(SQRT_DIM):
      fitness.append(fitness_row(board[SQRT_DIM*i:(i+1)*SQRT_DIM]))
  else:
    for i in range(SQRT_DIM):
      fitness.append(fitness_col(board[i::SQRT_DIM]))
  return fitness

def fitness_col(group, DIM=9, SQRT_DIM=3):
  fitness = 0
  for k in range(SQRT_DIM):
    unique_set = set()
    for i in range(SQRT_DIM):
      for j in range(SQRT_DIM):
        unique_set.add(group[i][SQRT_DIM*j+k])
    fitness += len(unique_set)
  return fitness

def fitness_row(group, DIM=9, SQRT_DIM=3):
  fitness = 0
  for i in range(SQRT_DIM):
    unique_set = set()
    for j in range(SQRT_DIM):
      for element in group[j][i*SQRT_DIM:(i+1)*SQRT_DIM]:
        unique_set.add(element)
    fitness += len(unique_set)
  return fitness

def fitness_for_all(board, DIM=9, SQRT_DIM=3):
  fitness = 0
  for i in range(SQRT_DIM):
    fitness += fitness_row(board[i*SQRT_DIM:(i+1)*SQRT_DIM])
    fitness += fitness_col(board[i::SQRT_DIM])
  return fitness


def crossover(parent1, parent2, DIM=9, SQRT_DIM=3):
  # Hard coded for 9x9 board for now; can be improved
  # TODO: Make this more general
  p1_fitness = fitness_rows(parent1, True)
  p2_fitness = fitness_rows(parent2, True)
  p2_col_fitness = fitness_rows(parent2, False)
  p1_col_fitness = fitness_rows(parent1, False)

  child1 = [[],[],[],[],[],[],[],[],[]]# np.zeros(DIM,DIM)
  child2 = [[],[],[],[],[],[],[],[],[]]# np.zeros(DIM,DIM)

  for i in range(SQRT_DIM):
    if p1_fitness[i] < p2_fitness[i]:
      child1[i*SQRT_DIM] = parent2[i*SQRT_DIM]
      child1[i*SQRT_DIM+1] = parent2[i*SQRT_DIM+1]
      child1[i*SQRT_DIM+2] = parent2[i*SQRT_DIM+2]
    elif p1_fitness[i] > p2_fitness[i]:
      child1[i*SQRT_DIM] = parent1[i*SQRT_DIM]
      child1[i*SQRT_DIM+1] = parent1[i*SQRT_DIM+1]
      child1[i*SQRT_DIM+2] = parent1[i*SQRT_DIM+2]
    else:
      selection = random.choice([parent1, parent2])
      child1[i*SQRT_DIM] = selection[i*SQRT_DIM]
      child1[i*SQRT_DIM+1] = selection[i*SQRT_DIM+1]
      child1[i*SQRT_DIM+2] = selection[i*SQRT_DIM+2]
  for i in range(SQRT_DIM):
    if p1_col_fitness[i] < p2_col_fitness[i]:
      child2[i] = parent2[i]
      child2[i+3] = parent2[i+3]
      child2[i+6] = parent2[i+6]
    elif p1_col_fitness[i] > p2_col_fitness[i]:
      child2[i] = parent1[i]
      child2[i+3] = parent1[i+3]
      child2[i+6] = parent1[i+6]
    else:
      selection = random.choice([parent1, parent2])
      child2[i] = selection[i]
      child2[i+3] = selection[i+3]
      child2[i+6] = selection[i+6]
  return child1, child2

def modifiable_cell(board, DIM=9, SQRT_DIM=3):
  # Return a list of sets with indexes of non-bound locations within box
  l = []
  for i in range(DIM):
    l.append(set())
    for j in range(DIM):
      if board[i][j] == 0:
        l[i].add(j)
  return l

MODIFIABLE_CELLS = modifiable_cell(BOARD_CHOICE)

def mutate(lOfGenes, PROB=.3, DIM=9, SQRT_DIM=3):
  for i in range(DIM):
    to_add = []
    for gene in lOfGenes:
      if random.random() < PROB:
        choice1 = random.choice([*MODIFIABLE_CELLS[i]])
        # Ensure no duplicates
        MODIFIABLE_CELLS[i].remove(choice1)
        to_add.append(choice1)
        choice2 = random.choice([*MODIFIABLE_CELLS[i]])
        # Restore the modifiables
        # Swap
        gene[i][choice1], gene[i][choice2] = gene[i][choice2], gene[i][choice1]
    for choice in to_add:
      MODIFIABLE_CELLS[i].add(choice)
  # return gene

def tourament_selection(population):
  members = random.sample(population, TOURNAMENT_SIZE)
  members.sort(key=attrgetter('fitness'), reverse=True)
  rand_draw = random.random()
  if rand_draw < TOURNAMENT_PROB:
    return members[0]
  else:
    return members[1]

def print_board_prettily(board):
  '''
  Print a representation of the sudoku board such that each row of board is one
  box and each box is separated by | and _
  '''
  for l in range(SQRT_DIM):
    for i in range(SQRT_DIM):
      for j in range(SQRT_DIM):
        for k in range(SQRT_DIM):
          print(board[l*SQRT_DIM+j][i*SQRT_DIM+k], end=' ')
          if k == 2:
            print('|', end=' ')
          if j == 2 and k == 2:
            print()

      if i == 2:
        print('-----------------------')



test_boxes = [[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],[7,8,9,1,2,3,4,5,6,]]

parent1 = np.array([[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],[7,8,9,1,2,3,4,5,6,],
           [9,1,2,3,4,5,6,7,8,],[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],
           [7,8,9,1,2,3,4,5,6,],[9,1,2,3,4,5,6,7,8,],[1,2,3,4,5,6,7,8,9,]])
parent2 = np.array([np.array([9,8,7,6,5,4,3,2,1,]),np.array([8,7,6,5,4,3,2,1,9,]),np.array([7,6,5,4,3,2,1,9,8,]),
           np.array([6,5,4,3,2,1,9,8,7,]),np.array([5,4,3,2,1,9,8,7,6,]),np.array([4,3,2,1,9,8,7,6,5,]),
           np.array([3,2,1,9,8,7,6,5,4,]),np.array([2,1,9,8,7,6,5,4,3,]),np.array([1,9,8,7,6,5,4,3,2,])])

def main(argv):
  acceptable = ['easy', 'medium', 'hard', 'random']
  if len(argv) >= 2 and argv[1] in acceptable:
    response = requests.get(url=f'https://sugoku.herokuapp.com/board?difficulty={argv[1]}', headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    response_json = json.loads(response.text)
    BOARD_CHOICE = rows_to_boxes(response_json['board'])
  else:
    BOARD_CHOICE = easy_board

  print(f'We start with the board:')
  print_board_prettily(BOARD_CHOICE)
  # Back to GA stuff
  ga = modified_pyeasyga.GeneticAlgorithm(
    seed_data = BOARD_CHOICE,
    population_size=150,
    generations = 10000,
    crossover_probability = 0.3,
    mutation_probability = 0.3,
    elitism = True,
  )
  ga.tournament_size = 3
  ga.tournament_selection = tourament_selection
  ga.create_individual = generate_initial_boxes
  ga.fitness_function = fitness_for_all
  # ga.selection_function = selection
  ga.mutate_function = mutate
  ga.cross_over_function = crossover
  beg_time = time.time()
  ga.run()
  end_time = time.time()

  print(f'''{ga.best_individual()[0]} score in {ga.n_iterations} in generations in
  {end_time-beg_time} seconds  produces
  This board:''')
  print_board_prettily(ga.best_individual()[1])



# This is old code trying to use GUI's here in case I decide to use again
"""
def main_gui_loop(board, finished=False):
  while True:
    drawlines(board)
    if not finished:
      ga = modified_pyeasyga.GeneticAlgorithm(
        seed_data = BOARD_CHOICE,
        population_size=150,
        generations = 10000,
        crossover_probability = 0.3,
        mutation_probability = 0.3,
        elitism = True,
      )
      ga.tournament_size = 3
      ga.tournament_selection = tourament_selection
      ga.create_individual = generate_initial_boxes
      ga.fitness_function = fitness_for_all
      # ga.selection_function = selection
      ga.mutate_function = mutate
      ga.cross_over_function = crossover
      ga.run()
      main_gui_loop(ga.best_individual()[1], finished=True)
# GUI for the game is here
# Code is modified from this tutorial on pygame: https://data-flair.training/blogs/python-sudoku-game/

pygame.font.init()
Window = pygame.display.set_mode((500, 500))
x = 0
z = 0
diff = 500/9
value = 0
pygame.display.set_caption("Watch Sudoku Get Get Solved In Front Of Your Own Eyes")

bigfont = pygame.font.SysFont("arial", 40) # montserrat
smallfont = pygame.font.SysFont("arial", 20)

def drawlines(board):
    for i in range (DIM):
        for j in range (SQRT_DIM):
          for k in range(SQRT_DIM):
            # Board is in boxes
            if board[i][j*SQRT_DIM+k]!= 0:
                pygame.draw.rect(Window, (255, 255, 0), (i * diff, (j * SQRT_DIM + k) * diff, diff + 1, diff + 1))
                text1 = bigfont.render(str(board[i][j*SQRT_DIM+k]), 1, (0, 0, 0))
                Window.blit(text1, (i * diff + 15, (j * SQRT_DIM + k) * diff + 15))
    for l in range(10):
        if l % 3 == 0 :
            thick = 7
        else:
            thick = 1
        pygame.draw.line(Window, (0, 0, 0), (0, l * diff), (500, l * diff), thick)
        pygame.draw.line(Window, (0, 0, 0), (l * diff, 0), (l * diff, 500), thick)

def fillvalue(value):
    text1 = bigfont.render(str(value), 1, (0, 0, 0))
    Window.blit(text1, (x * diff + 15, z * diff + 15))

def gameresult():
    text1 = bigfont.render("game finished", 1, (0, 0, 0))
    Window.blit(text1, (20, 570))

board = BOARD_CHOICE
Window.fill((255,182,193))
drawlines(board)
pygame.display.update()

main_gui_loop(BOARD_CHOICE)
"""

if __name__ == '__main__':
  main(sys.argv)
