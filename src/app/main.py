import datetime

import networkx as nx
import pandas as pd
import streamlit as st

from st_aggrid import AgGrid


# Load the Excel data and clean it
def load_data():
    df = pd.read_excel("./resource/문서의존성.xlsx")
    df.replace("\xa0", " ", regex=True, inplace=True)
    return df


# Create dependency edges from the dataframe
def create_dependency_edges(dependency_list, configs):
    dependencies = [[elem, lst[0], 1] for lst in dependency_list for elem in lst[1:] if not pd.isna(elem)]
    return dependencies


# Sort the documents based on their dependencies
def sort_ordered_docs(documents, dependencies):
    G = nx.DiGraph()
    G.add_nodes_from(documents)
    G.add_weighted_edges_from(dependencies)
    ordered_docs = list(nx.topological_sort(G))
    date_dependencies = {docA: [docB, weight] for docA, docB, weight in dependencies}
    return ordered_docs, date_dependencies


# Select the publication stages from the dataframe
def select_publication_stages(stage, configs):
    dependency_list = stage.loc[:, "문서명":].values.tolist()
    documents, dependencies = stage["문서명"].values.tolist(), create_dependency_edges(dependency_list, configs)
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
    st.set_page_config(layout="wide")
    st.title("FW issue-date-generator")

    st.sidebar.subheader("설정")

    df = load_data()
    
    safety_analysis_included = st.sidebar.checkbox("안전성 분석 보고서 포함", value=True)
    cyber_security_included = st.sidebar.checkbox("사이버보안 평가 보고서 포함", value=True)

    if not safety_analysis_included:
        df = df[~df['문서명'].str.contains('안전성 분석')]

    if not cyber_security_included:
        df = df[~df['문서명'].str.contains('사이버보안')]
    
    filtered_df = df


    # Sample holidays list
    holidays = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]

    # Assign publication dates conditions to a single configuration
    with st.sidebar.form('입력문서 발행일자 설정'):
        spec_date = st.date_input("요구사항 명세서 발행일", value=datetime.date(2023,4,19))
        design_date = st.date_input("설계 명세서 발행일", value=datetime.date(2023,4,26))
        impl_date = st.date_input("구현 명세서 발행일", value=datetime.date(2023,5,10))
        end_date = st.date_input("발행 마감일", value=datetime.date(2023,6,2))
        ct_dates = st.number_input("CT 시험 수행일", min_value=1, value=3)
        it_dates = st.number_input("IT 시험 수행일", min_value=1, value=3)
        st_dates = st.number_input("ST 시험 수행일", min_value=1, value=3)
        submitted = st.form_submit_button('확인')

    if submitted:
        st.write(spec_date, design_date, impl_date, end_date, ct_dates, it_dates, st_dates)

    #TODO re-implement date scheduling algorithm
    ordered_docs, date_dependencies = select_publication_stages(filtered_df, None)
    st.write("st.write(date_dependencies)")
    st.write(date_dependencies)
    allocated_dates = {}
    
    #TODO re-implement date scheduling algorithm
    for item in ordered_docs:
        while spec_date.weekday() >= 5 or spec_date in holidays:
            spec_date += pd.Timedelta(days=1)
        allocated_dates[item] = spec_date
        spec_date += pd.Timedelta(days=date_dependencies.get(item, [None, 1])[1])

    # Display the dates in AgGrid
    st.write("## dates_df")
    dates_df = pd.DataFrame(list(allocated_dates.items()), columns=["문서명", "날짜"])
    dates_df['날짜'] = pd.to_datetime(dates_df['날짜']).dt.strftime('%y.%m.%d')
    grid_response = AgGrid(dates_df, editable=True, height=600, width=400, fit_columns_on_grid_load=True)
    updated_df = pd.DataFrame(grid_response["data"])

    st.subheader("Updated DataFrame:")
    st.write(updated_df)


if __name__ == "__main__":
    app()
