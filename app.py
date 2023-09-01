import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx

from st_aggrid import AgGrid
from tabulate import tabulate

#f = open('./resource/문서의존성.xlsx', encoding='UTF-8')
df = pd.read_excel('./resource/문서의존성.xlsx').loc[:, '단계':'의존 문서#3']
df.replace('\xa0', ' ', regex=True, inplace=True)

dependency_list = df.loc[:, '문서명':].values.tolist()

spec = df[(df['단계']== '요건')]
design = df[(df['단계']== '설계')]
impl = df[(df['단계']== '구현')]
integration = df[(df['단계']== '통합')]

dependencies = []
for lst in dependency_list:
  result = [[elem, lst[0], 2] for elem in lst[1:] if not pd.isna(elem)]
  dependencies.extend(result)

documents = df['문서명'].values.tolist()

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


def app():
    st.title("FW issue-date-generator")
    st.sidebar.subheader("options")

    # Assign publication dates
    current_date = st.sidebar.date_input('start_date')
    #b = st.sidebar.date_input('end_date')
    
    holidays = [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]

    # Sample holidays list (e.g., '2023-07-04' for Independence Day)

    # Dictionary to store the allocated Timestamp for each item
    allocated_dates = {}
    for item in ordered_docs:
        # Check if the current date is a weekday and not a holiday
        while current_date.weekday() >= 5 or current_date in holidays:
            current_date += pd.Timedelta(days=1)
        allocated_dates[item] = current_date
        date_dependencies
        current_date += pd.Timedelta(days=date_dependencies[item][1])

    # Use AgGrid for inline editing
    dates_df = pd.DataFrame(list(allocated_dates.items()), columns=['문서명','날짜'])
    grid_response = AgGrid(dates_df, editable=True, height=600, width=400, fit_columns_on_grid_load=True)
    updated_df = pd.DataFrame(grid_response["data"])
    
    st.subheader("Updated DataFrame:")
    st.write(updated_df)

if __name__ == '__main__':
    app()
