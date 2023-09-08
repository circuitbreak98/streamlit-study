import streamlit as st
import pandas as pd
import networkx as nx
from st_aggrid import AgGrid

# Load the Excel data and clean it
def load_data():
    df = pd.read_excel('./resource/문서의존성.xlsx')
    df.replace('\xa0', ' ', regex=True, inplace=True)
    return df

# Create dependency edges from the dataframe
def create_dependency_edges(dependency_list):
    dependencies = [[elem, lst[0], 2] for lst in dependency_list for elem in lst[1:] if not pd.isna(elem)]
    return dependencies

# Sort the documents based on their dependencies
def sort_ordered_docs(documents, dependencies):
    G = nx.DiGraph()
    G.add_nodes_from(documents)
    G.add_weighted_edges_from(dependencies)
    ordered_docs = list(nx.topological_sort(G))
    date_dependencies = {docA:[docB, weight] for docA, docB, weight in dependencies}
    return ordered_docs, date_dependencies

# Select the publication stages from the dataframe
def select_publication_stages(stage):
    dependency_list = stage.loc[:, '문서명':].values.tolist()
    documents, dependencies = stage['문서명'].values.tolist(), create_dependency_edges(dependency_list)
    st.write(dependencies)
    dependencies
    return sort_ordered_docs(documents, dependencies)

# Allocate publication dates for documents between start_date and end_date.
# Not Used Function
def allocate_dates_between(start_date, end_date, ordered_docs, holidays=[]):
    allocated_dates = {}
    current_date = start_date
    num_docs = len(ordered_docs)
    days_between = (end_date - start_date) / num_docs
    
    for item in ordered_docs:
        while current_date.weekday() >= 5 or current_date in holidays:
            current_date += pd.Timedelta(days=1)
        allocated_dates[item] = current_date
        current_date += days_between
        
    return allocated_dates

# Main Streamlit app
def app():

    st.title("FW issue-date-generator")
    
    st.sidebar.subheader("설정")
    
    df = load_data()

    documents_display = st.multiselect(
        "## 발행할 문서를 고르세요 :sunglasses:", list(df[df.columns[1]]), list(df[df.columns[1]])
    )
    
    filtered_df = df[df['문서명'].isin(documents_display)]
    ordered_docs, date_dependencies = select_publication_stages(filtered_df)
    
    # Sample holidays list
    holidays = [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]
    
    # Assign publication dates
    spec_date = st.sidebar.date_input('요구사항 명세서 발행일')
    design_date = st.sidebar.date_input('설계 명세서 발행일')
    impl_date = st.sidebar.date_input('구현 명세서 발행일')
    end_date = st.sidebar.date_input('발행 마감일')
    ct_dates = st.sidebar.number_input("CT 시험 수행일", min_value=1, value=3)
    it_dates = st.sidebar.number_input("IT 시험 수행일", min_value=1, value=3)
    st_dates = st.sidebar.number_input("ST 시험 수행일", min_value=1, value=3)


    allocated_dates = {}
    
    for item in ordered_docs:
        while spec_date.weekday() >= 5 or spec_date in holidays:
            spec_date += pd.Timedelta(days=1)
        allocated_dates[item] = spec_date
        spec_date += pd.Timedelta(days=date_dependencies.get(item, [None, 1])[1])
    
        
    # Display the dates in AgGrid
    st.write('## dates_df')
    dates_df = pd.DataFrame(list(allocated_dates.items()), columns=['문서명','날짜'])
    grid_response = AgGrid(dates_df, editable=True, height=600, width=400, fit_columns_on_grid_load=True)
    updated_df = pd.DataFrame(grid_response["data"])
    
    st.subheader("Updated DataFrame:")
    st.write(updated_df)

if __name__ == '__main__':
    app()
