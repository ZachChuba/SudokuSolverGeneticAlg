# SudokuSolverGeneticAlg

This is scalable genetic algorithm for solving sudoku puzzles.

# Methodology
## Form
Data is formatted as a 2d array, with each 3x3 sub-block a row in the array.

## Start
Fill each box that don't contain values with unique values that don't conflict with the rest of the block. This guarentees that one of the three rules (unique blocks) is satisfied

## Fitness Function
Given 3 boxes (3 rows or 27 values) and a metric (row, col), return the number of unique values in that metric (low 0, high 27)

## Crossover
We try to preserve the best blocks and shift the burden of creating population diversity to the mutation function.
Two children are generated from two parents in the following way:
Child 1) 
  Each row (3 boxes on the same verticle) is rated from 0-27 (fitness function) based on the number of unique values in each row (27 is the best and means all rows have no duplicates within them)
  The child takes the row of boxes from the parent with the highest score (or random if both scores are equal)
Child 2) Same as Child 1, except using columns

### Image Representation [source](https://www.researchgate.net/publication/224180108_Solving_Sudoku_with_genetic_operations_that_preserve_building_blocks)

![image](https://user-images.githubusercontent.com/49295341/142952079-534bf620-4f4b-416e-8eaf-8acc23982913.png)

The purpose for this unusual crossover function is to
avoid the destruction of highly fit building blocks during crossover, which allows faster convergence.

## Special Crossover
In order to ensure that crossover heads closer to the correct solution instead of making no progress or going backwards, each parent generates 3 children, two of which are a mutated version of the crossover, the other is the unmutated crossover. A tournament (with size=3) is held, such that the highest-rated child is selected with p=.9 and the 2nd highest child is selected with p=.1. The child selected by the tournament makes it to the next generation.
### How this lowers number of generations [source](https://www.researchgate.net/publication/224180108_Solving_Sudoku_with_genetic_operations_that_preserve_building_blocks)


![image](https://user-images.githubusercontent.com/49295341/144790771-8a154393-c042-408c-baa9-3f272b40099c.png)


## Mutation
Each sub-block (3x3) rolls a mutation based on the mutation probability
Two values in the sub block (that weren't given in the initial problem) are randomly selected and swapped. Preserves the uniqueness of the block, which allows for faster convergence.

## Results

### Example Easy:
![ga_solver_easy](https://user-images.githubusercontent.com/49295341/144789430-6da88db9-b383-4dcc-af96-18c45f872f01.PNG)

### Example Medium:
![ga_solver_medium](https://user-images.githubusercontent.com/49295341/144789466-fe8cfdf2-7a01-468f-823c-d2ff21060fa2.PNG)

### Example Hard (lucky):
![ga_solver_hard](https://user-images.githubusercontent.com/49295341/144789511-91bc9748-bc37-42f0-960d-02ea3beedccf.PNG)

### Averages [source](https://www.researchgate.net/publication/224180108_Solving_Sudoku_with_genetic_operations_that_preserve_building_blocks):
Count = Number of trials that solved the problem in <=100,000 generations
Avergage = Average number of generations

![image](https://user-images.githubusercontent.com/49295341/144789308-9a71b197-f31e-4fda-a6dd-8fbe0e68eb74.png)



## Reasoning
### If you're trying to optimize this in the fewest generations and runtime, why is the population size so small?
Because I'm using elitism (that is, the best of 5% each generation are guarenteed to carry over to the next), it's better to get to the next generation so that those top candidates can mutate and crossover again. Also, if the generation size is massive (so massive that a solution could be found in a single digit number of generations) that's kind of cheating -- the goal is to solve puzzles in a low number of generations but doesn't take seconds for each generation.


### Obligatory notice
Uses and modifies pyeasyga which has the following license agreement:
Copyright (c) 2014, Ayodeji Remi-Omosowon
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of pyeasyga nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
