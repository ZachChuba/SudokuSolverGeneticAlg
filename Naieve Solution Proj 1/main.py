import ga
import stdgenomes
from random import choice

# Data is formatted in rows; 1 is the first row
'''
A puzzle:
0,0,0,8,0,0,0,0,7,
3,0,0,0,4,7,0,0,0,
8,0,1,0,0,2,3,6,0,
0,6,0,0,0,8,0,0,2,
0,0,5,9,2,4,7,0,0,
2,0,0,6,0,0,0,3,0,
0,8,4,7,0,0,2,0,1,
0,0,0,2,1,0,0,0,8,
5,0,0,0,0,6,0,0,0
'''
def initialize_board(given_board: list) -> list:
  board = []
  counted = set()
  for i in range(18):
    if i % 2 == 0:
      for element in given_board[i*9:i*9+9]:
        if element != 0:
          counted.add(element)
    else:
      board.append([])
      for element in given_board[i//2*9:i//2*9+9]:
        if element == 0 and len(counted) < 9:
          chosen = choice([i for i in range(1,10) if i not in counted])
          # 0 is if it is in the puzzle given, 1 is its value
          board[i//2].append({0: False, 1: chosen})
          counted.add(chosen)
        else:
          board[i//2].append({0: True, 1: element})
      counted = set()
  return board

def rowify(board):
  # split up solution into rows
  rows = []
  for i in range(9):
    rows.append([])
    for j in range(9):
      rows[i].append(board[i*9+j])
  return rows

def boxify(board1d):
  # Turn board1d into 3x3 boxes represented in a list of lists
  BOX_START_LOCATIONS = (0, 3, 6, 27, 30, 33, 54, 57, 60)
  box_board_2d = []
  for i in range(len(BOX_START_LOCATIONS)):
    box_board_2d.append((lambda list, i: list[i:i+3] + list[i+9:i+12] + list[i+18:i+21])(board1d, BOX_START_LOCATIONS[i]))
  return box_board_2d

def legalness_within_measure(solution):
  # Return a numerical rating (0 being best) of if the solution is legal
  # The number returned is the number of illegal numbers
  # Measure refers to row, box, or column (all are translated before passing)
  aggregate_score = 0
  for measure in solution:
    aggregate_score += 9 - len(set(measure))
  return aggregate_score

def fitness_function(solution, puzzle):
  # split up solution into rows
  solution2d = rowify(solution)
  # zip(*solution2d) is the transpose of solution2d (columns)
  # Start by seeing how many rules illegal numbers are in it
  fitness_score = 0
  fitness_score += legalness_within_measure(solution2d) # rows
  fitness_score += legalness_within_measure(zip(*solution2d)) # columns
  fitness_score += legalness_within_measure(boxify(solution)) # boxes
  # Now, make sure that the solution actually matches the given puzzle
  # Multiply by 10 to heavily weight them into the genome
  fitness_score += sum(1 if in_given and in_given != curr_val else 0 for in_given, curr_val in zip(puzzle, solution)) * 10
  # Fitness score of 0 is the solution
  return fitness_score


def fitness_function_wrapper(init_puzzle):
  # Use wrapper because library requires fitness function as arugment
  def fitness_for_this_puzzle(population_member):
    # population_member.genes is the solution board it holds
    return fitness_function(population_member.genes, init_puzzle)
  return fitness_for_this_puzzle


test_board = [0,0,0,8,0,0,0,0,7,3,0,0,0,4,7,0,0,0,8,0,1,0,0,2,3,
6,0,0,6,0,0,0,8,0,0,2,0,0,5,9,2,4,7,0,0,2,0,0,6,0,0,0,3,0,0,8,4,7,0,0,2,0,1,
0,0,0,2,1,0,0,0,8,5,0,0,0,0,6,0,0,0]
#result = initialize_board(test_board)
#print(result[0])

# data is formatted as a list of lists. The list is a list of all rows,
# and embedded list contains maps of all elements in that row.

# Create vector of a board labeled 1-9 that will be permuted into
# All other boards
init_solution = []
for i in range(81):
  init_solution.append(i % 9 + 1)

genome = stdgenomes.PermutateGenome(init_solution)
solver = ga.GA(fitness_function_wrapper(test_board), genome)
solver.evolve(target_fitness=0)