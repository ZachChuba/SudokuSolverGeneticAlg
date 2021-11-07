# Method from this paper: https://www.researchgate.net/publication/224180108_Solving_Sudoku_with_genetic_operations_that_preserve_building_blocks
import random
import numpy as np

# Each array is a box of the sudoku
# The first box is top left, the second is middle top, etc.
DIM = 9
SQRT_DIM = int(DIM**0.5)

def generate_initial_boxes(given_puzzle):
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

def fitness_rows(board, row):
  fitness = []
  if row:
    for i in range(SQRT_DIM):
      fitness.append(fitness_row(board[SQRT_DIM*i:(i+1)*SQRT_DIM]))
  else:
    for i in range(SQRT_DIM):
      fitness.append(fitness_col(board[i*SQRT_DIM:(i+1)*SQRT_DIM]))
  return fitness

def fitness_col(group):
  fitness = 0
  for k in range(SQRT_DIM):
    unique_set = set()
    for i in range(SQRT_DIM):
      for j in range(SQRT_DIM):
        unique_set.add(group[i][SQRT_DIM*j+k])
    fitness += len(unique_set)
  return fitness

def fitness_row(group):
  fitness = 0
  for i in range(SQRT_DIM):
    unique_set = set()
    for j in range(SQRT_DIM):
      for element in group[j][i*SQRT_DIM:(i+1)*SQRT_DIM]:
        unique_set.add(element)
    fitness += len(unique_set)
  return fitness

def reduced_fitness(board):
  fitness = 0
  for col in board.T:
    fitness += np.unique(col).size


def crossover(parent1, parent2):
  # Hard coded for 9x9 board for now; can be improved
  # TODO: Make this more general
  p1_fitness = fitness_rows(parent1, True)
  p2_fitness = fitness_rows(parent2, True)
  p2_col_fitness = fitness_rows(parent2, False)
  p1_col_fitness = fitness_rows(parent1, False)

  child1 = np.zeros((DIM,DIM), dtype=int)
  child2 = np.zeros((DIM,DIM), dtype=int)

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

def modifiable_cell(board):
  # Return a list of sets with indexes of non-bound locations within box
  l = []
  for i in range(DIM):
    l.append(set())
    for j in range(DIM):
      if board[i][j] == 0:
        l[i].add(j)
  return l

def mutate(gene, chance):
  for i in range(DIM):
    if random.random() < chance:
      choice1 = random.choice(MODIFIABLE_CELLS[i])
      # Ensure no duplicates
      MODIFIABLE_CELLS[i].remove(choice1)
      choice2 = random.choice(MODIFIABLE_CELLS[i])
      # Restore the modifiables
      MODIFIABLE_CELLS[i].add(choice1)
      # Swap
      gene[i][choice1], gene[i][choice2] = gene[i][choice2], gene[i][choice1]
  return gene


test_boxes = [[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],[7,8,9,1,2,3,4,5,6,]]

parent1 = np.array([[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],[7,8,9,1,2,3,4,5,6,],
           [9,1,2,3,4,5,6,7,8,],[1,2,3,4,5,6,7,8,9,],[4,5,6,7,8,9,1,2,3,],
           [7,8,9,1,2,3,4,5,6,],[9,1,2,3,4,5,6,7,8,],[1,2,3,4,5,6,7,8,9,]])
parent2 = np.array([np.array([9,8,7,6,5,4,3,2,1,]),np.array([8,7,6,5,4,3,2,1,9,]),np.array([7,6,5,4,3,2,1,9,8,]),
           np.array([6,5,4,3,2,1,9,8,7,]),np.array([5,4,3,2,1,9,8,7,6,]),np.array([4,3,2,1,9,8,7,6,5,]),
           np.array([3,2,1,9,8,7,6,5,4,]),np.array([2,1,9,8,7,6,5,4,3,]),np.array([1,9,8,7,6,5,4,3,2,])])

MODIFIABLE_CELLS = modifiable_cell(parent1)

print(crossover(parent1, parent2))