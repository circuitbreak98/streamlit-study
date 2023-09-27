import datetime
from typing import Dict, List, Optional, Tuple

from csp import Constraint, CSP


class PublicationDependencyConstraint(Constraint[str, str]):
    def __init__(self, docA: str, docB: str):
        super().__init__([docA, docB])
        self.docA = docA
        self.docB = docB

    def satisfied(self, assignment: Dict[str, datetime.date]) -> bool:
        # If either variable is not in the assignment, then it's not yet possible to violate the constraint
        if self.docA not in assignment or self.docB not in assignment:
            return True
        # Return True if docB's date is after docA's date
        return assignment[self.docA] < assignment[self.docB]


class TestPublicationDependencyConstraint(Constraint[str, Tuple[str, int]]):
    def __init__(self, docA: str, docBanddays: Tuple[str, int]):
        super().__init__([docA, docBanddays])
        self.docA = docA
        self.docB = docBanddays[0]
        self.day = docBanddays[1]

    def satisfied(self, assignment: Dict[str, datetime.date]) -> bool:
        # If either variable is not in the assignment, then it's not yet possible to violate the constraint
        if self.docA not in assignment or self.docB not in assignment:
            return True
        # Return True if docB's date is after docA's date
        return assignment[self.docA] < assignment[self.docB] + datetime.timedelta(days=self.day)

def date_range(start_date, end_date, holidays):
    delta: datetime.timedelta = datetime.timedelta(days=1)
    current_date: datetime.date = start_date
    while current_date <= end_date:
        if current_date.weekday() >= 5 or current_date in holidays:
            pass
        else:
            yield current_date
        current_date += delta

if __name__ == "__main__":
    variables: List[str] = ["요구사항 명세서", "요구사항 명세 검증보고서", "시스템 시험 계획서","요구사항 안전성 분석 보고서", "설계 명세서"]
    domains: Dict[str, List[datetime.date]] = {}
    start = datetime.date(2023, 1, 2)
    end = datetime.date(2023, 1, 10)
    holidays = [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)]
    date_list = list(date_range(start, end, holidays))
    
    for variable in variables:
        if variable == "요구사항 명세서":
            domains[variable] = [start]
        elif variable == "설계 명세서":
            domains[variable] = [end]
        else:
            domains[variable] = date_list
    
    csp: CSP[str,datetime.date] = CSP(variables, domains)
    
    csp.add_constraint(PublicationDependencyConstraint("요구사항 명세서", "요구사항 명세 검증보고서"))
    csp.add_constraint(PublicationDependencyConstraint("요구사항 명세서", "요구사항 안전성 분석 보고서"))
    csp.add_constraint(PublicationDependencyConstraint("요구사항 명세서", "설계 명세서"))
    csp.add_constraint(PublicationDependencyConstraint("요구사항 명세서", "시스템 시험 계획서"))
    csp.add_constraint(PublicationDependencyConstraint("요구사항 명세 검증보고서", "시스템 시험 계획서"))
    

    solution: Optional[Dict[str, datetime.date]] = csp.backtracking_search()
    if solution is None:
        print("There is no Answer!")
    else:
        print(solution)
