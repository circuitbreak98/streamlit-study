from typing import Generic, TypeVar, Dict, List, Optional
from abc import ABC, abstractmethod

V = TypeVar('V') # Variable Type
D = TypeVar('D') # Domain Type 

# base class for all constraint
class Constraint(Generic[V, D], ABC):
    # constraint variable
    def __init__(self, variables:List[V]) -> None:
        self.variables = variables

    @abstractmethod
    def satisfied(self, assignement: Dict[V, D]) -> bool:
        pass

class CSP(Generic[V, D]):
    def __init__(self, variables:List[V], domains: Dict[V, List[D]]) -> None:
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("모든 변수에 도메인이 할당되어야 합니다.")
            
    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("제약 조건 변수가 아닙니다.")
            else:
                self.constraints[variable].append(constraint)

    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True
        
    def backtracking_search(self, assignment: Dict[V, D] = {}) -> Optional[Dict[V, D]]:
        #assignment는 모든 변수가 할당될 때 완료된다.(base condition)
        if len(assignment) == len(self.variables):
            return assignment

        # 할당되지 않은 모든 변수를 가져온다.
        unassigned: List[V] = [v for v in self.variables if v not in assignment]

        # 할당되지 않은 첫 번째 변수의 가능한 모든 도메인 값을 가져온다. 
        first: V = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            #local_assignment 값이 일관적이면 재귀 호출한다.
            if self.consistent(first, local_assignment):
                result: Optional[Dict[V,D]] = self.backtracking_search(
                    local_assignment)
                #결과를 찾지 못하면 백트래킹을 종료한다.
                if result is not None:
                    return result
        return None # 솔루션 없음 