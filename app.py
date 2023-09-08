import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx

from st_aggrid import AgGrid
from tabulate import tabulate

#f = open('./resource/문서의존성.xlsx', encoding='UTF-8')
df = pd.read_excel('./resource/문서의존성.xlsx').loc[:, '단계':'의존 문서#3']
df.replace('\xa0', ' ', regex=True, inplace=True)

#dependency_list = df.loc[:, '문서명':].values.tolist()

spec = df[(df['단계']== '요건')]
design = df[(df['단계']== '설계')]
design
impl = df[(df['단계']== '구현')]
integration = df[(df['단계']== '통합')]

def create_dependency_edges(dependency_list):
    dependencies = []
    for lst in dependency_list:
        result = [[elem, lst[0], 2] for elem in lst[1:] if not pd.isna(elem)]
        dependencies.extend(result)
    return dependencies

def sort_ordered_docs(documents, dependencies):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes (documents) to the graph
    G.add_nodes_from(documents)

    # Add edges (dependencies) to the graph
    # This means docA should be published before docB, and so on.
    G.add_weighted_edges_from(dependencies)
    date_dependencies = {docA:[docB, weight] for docA, docB, weight in dependencies}

    # Perform topological sort
    ordered_docs = list(nx.topological_sort(G))
    return ordered_docs, date_dependencies

def select_publication_stages(stage):
    dependency_list = stage.loc[:, '문서명':].values.tolist()
    
    documents, dependencies = stage['문서명'].values.tolist(), create_dependency_edges(dependency_list)

    spec_ordered_docs, spec_date_dependencies = sort_ordered_docs(documents, dependencies)

    return spec_ordered_docs, spec_date_dependencies

ordered_docs, date_dependencies = select_publication_stages(impl)

ordered_docs

def app():
    st.title("FW issue-date-generator")
    st.sidebar.subheader("설정")

    # Assign publication dates
    spec_date = st.sidebar.date_input('요구사항 명세서')
    design_date = st.sidebar.date_input('설계 명세서')
    impl_date = st.sidebar.date_input('구현 명세서')
    due_date = st.sidebar.date_input('due date')
    #b = st.sidebar.date_input('end_date')
    
    holidays = [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]

    # Sample holidays list (e.g., '2023-07-04' for Independence Day)

    # Dictionary to store the allocated Timestamp for each item
    allocated_dates = {}
    try:
        for item in ordered_docs:
            # Check if the current date is a weekday and not a holiday
            while spec_date.weekday() >= 5 or spec_date in holidays:
                spec_date += pd.Timedelta(days=1)
            allocated_dates[item] = spec_date
            date_dependencies[item][1]=1
            spec_date += pd.Timedelta(days=date_dependencies[item][1])
            print(item)
    except KeyError:
        print(f'KeyError item: {item}')

    # Use AgGrid for inline editing
    dates_df = pd.DataFrame(list(allocated_dates.items()), columns=['문서명','날짜'])
    grid_response = AgGrid(dates_df, editable=True, height=600, width=400, fit_columns_on_grid_load=True)
    updated_df = pd.DataFrame(grid_response["data"])
    
    st.subheader("Updated DataFrame:")
    st.write(updated_df)

if __name__ == '__main__':
    app()
