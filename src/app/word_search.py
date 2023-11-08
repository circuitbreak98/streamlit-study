from typing import NamedTuple, List, Dict, Optional
from random import choice
from string import ascii_uppercase
from csp import CSP , Constraint
Grid = List[List[str]]


class GridLocation(NamedTuple):
    row: int
    column: int


class WordSearchConstraint(Constraint[str, List[GridLocation]]):
    def __init__(self, words: List[str]) -> None:
        super().__init__(words)
        self.words: List[str] = words

    def satisfied(self, assignment: Dict[str, List[GridLocation]]) -> bool:
        #중복된 격자 위치가 있다면 그 위치는 겹치는 부분이다. 
        all_locations = [locs for values in assignment.values() for locs in values]
        return len(set(all_locations)) == len(all_locations)


def generate_grid(rows:int, columns:int) -> Grid:
    #임의 문자로 격자를 초기화한다.
    return [[choice(ascii_uppercase) for c in range(columns)] for r in(range(rows))]

def display_grid(grid: Grid) -> None:
    for row in grid:
        print("".join(row))

def generate_domain(word:str, grid:Grid)-> List[List[GridLocation]]:
    domain: List[List[GridLocation]] = []
    height: int = len(grid)
    width: int = len(grid[0])
    length: int = len(word)
    for row in range(height):
        for col in range(width):
            columns: range = range(col, col+length+1)
            rows: range = range(row, row+length+1)
            if col+length <= width:
                #왼쪽에서 오른쪽으로
                domain.append([GridLocation(row,c) for c in columns])
                #대각선 오른쪽 아래로
                if row+length <= height:
                    domain.append([GridLocation(r, col+(r-row)) for r in rows])
            if row+length <= height:
                #위에[서 아래로
                domain.append([GridLocation(r, col) for r in rows])
                #대각선 왼쪽 아래로
                if col-length >=0:
                    domain.append([GridLocation(r, col- (r- row)) for r in rows])
    
    return domain

if __name__ == "__main__":
    grid: Grid = generate_grid(9,9)
    words: List[str] = ["MATTHEW", "JOE", "MARY", "SARAH", "SALLY"]
    locations: Dict[str, List[List[GridLocation]]] = {}
    for word in words:
        locations[word] = generate_domain(word, grid)
    csp: CSP[str, List[GridLocation]] = CSP(words, locations)
    csp.add_constraint(WordSearchConstraint(words))
    solution: Optional[Dict[str, List[GridLocation]]
                       ] = csp.backtracking_search()
    if solution is None:
        print("답을 찾을 수 없습니다.")
    else:
        for word, grid_locations in solution.items():
            #50% 확률로 grid_locations를 반전한다.
            if choice([True, False]):
                grid_locations.reverse()
            for index, letter in enumerate(word):
                (row, col) = (grid_locations[index].row, grid_locations[index].column)
                grid[row][col] = letter
        display_grid(grid)
        