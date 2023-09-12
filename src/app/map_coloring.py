from csp import Constraint, CSP
from typing import Dict, List, Optional

class MapColoringConstraint(Constraint[str, str]):
    def __init__(self, place1: str, place2: str):
        super().__init__([place1, place2])
        self.place1: str = place1
        self.place2: str = place2

    def satisfied(self, assignment: Dict[str, str]) -> bool:
        # 두 지역 중 하나가 색상이 할당되지 않았다면 색상 충돌은 발생하지 않는다.
        if self.place1 not in assignment or self.place2 not in assignment:
            return True      
        return assignment[self.place1] != assignment[self.place2]
    

if __name__ == "__main__":
    variables: List[str] = ["WA", "NO", "SA", "QL", "NSW", "VIC", "TM"]
    domains: Dict[str, List[str]] = {}
    for variable in variables:
        domains[variable] = ["빨강", "초록", "파랑"]

    csp: CSP[str,str] = CSP(variables, domains)
    csp.add_constraint(MapColoringConstraint("WA", "NO"))
    csp.add_constraint(MapColoringConstraint("WA", "SA"))
    csp.add_constraint(MapColoringConstraint("SA", "NO"))
    csp.add_constraint(MapColoringConstraint("QL", "NO"))
    csp.add_constraint(MapColoringConstraint("QL", "SA"))
    csp.add_constraint(MapColoringConstraint("QL", "NSW"))
    csp.add_constraint(MapColoringConstraint("NSW", "SA"))
    csp.add_constraint(MapColoringConstraint("VIC", "SA"))
    csp.add_constraint(MapColoringConstraint("VIC", "NSW"))
    csp.add_constraint(MapColoringConstraint("VIC", "TM"))

    solution: Optional[Dict[str, str]] = csp.backtracking_search()
    if solution is None:
        print("There is no Answer!")
    else:
        print(solution)
