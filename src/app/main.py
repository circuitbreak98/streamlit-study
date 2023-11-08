import datetime

import networkx as nx
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

from csp import CSP
from date_generation import TestPublicationDependencyConstraint, PublicationDependencyConstraint, date_range

# Load the Excel data and clean it
def load_data():
    df = pd.read_excel("./resource/문서의존성.xlsx")
    df.replace("\xa0", " ", regex=True, inplace=True)
    return df

# Create dependency edges from the dataframe
def create_dependency_edges(dependency_list, configs):
    dependencies = [[elem, lst[0]] for lst in dependency_list for elem in lst[1:] if not pd.isna(elem)]
    return dependencies

# Select the publication stages from the dataframe
def select_publication_stages(stage, configs):
    dependency_list = stage.loc[:, "문서명":].values.tolist()
    documents, dependencies = stage["문서명"].values.tolist(), create_dependency_edges(dependency_list, configs)
    return (documents, dependencies)

def allocate_dates_with_csp(spec, design, impl, end, holidays, documents, constraints, test_configs):
    spec_date_list = list(date_range(spec, design, holidays))
    design_date_list = list(date_range(design, impl, holidays))
    remaining_date_list = list(date_range(impl, end, holidays))

    ct_days, it_days, st_days = test_configs

    variables = documents
    domains = {}

    for variable in variables:
        if variable == "요구사항 명세서":
            domains[variable] = [spec]
        elif variable == "설계 명세서":
            domains[variable] = [design]
        elif variable == "소스코드 구현명세서":
            domains[variable] = [impl]
        elif variable in ["요구사항 명세 검증보고서", "시스템 시험 계획서", "요구사항 안전성 분석 보고서", "요건단계 사이버보안 평가 보고서"]:
            domains[variable] = spec_date_list
        elif variable in ["설계 명세 검증보고서", "컴포넌트 시험 계획서", "통합시험 계획서", "설계 안전성 분석 보고서", "설계단계 사이버보안 평가 보고서"]:
            domains[variable] = design_date_list
        else:
            domains[variable] = remaining_date_list
    
    csp = CSP[str, datetime.date](variables, domains)

    for docA, docB in constraints:
    
        csp.add_constraint(PublicationDependencyConstraint(docA, docB))
        if docA == "컴포넌트 시험 절차서" and docB == "컴포넌트 시험 보고서":
            csp.add_constraint(TestPublicationDependencyConstraint(docA, docB, ct_days))
        elif docA == "통합시험 절차서" and docB == "통합시험 보고서":
            csp.add_constraint(TestPublicationDependencyConstraint(docA, docB, it_days))
        elif docA == "시스템시험 절차서" and docB == "시스템시험 보고서":
            csp.add_constraint(TestPublicationDependencyConstraint(docA, docB, st_days))
    
    solution = csp.backtracking_search()

    return solution



# Main Streamlit app
def app():
    st.set_page_config(layout="wide")
    st.title("FW issue-date-generator")

    st.sidebar.subheader("설정")

    df = load_data()

    safety_analysis_included = st.sidebar.checkbox("안전성 분석 보고서 포함", value=True)
    cyber_security_included = st.sidebar.checkbox("사이버보안 평가 보고서 포함", value=True)
    
    if not safety_analysis_included:
        df = df[~df['문서명'].str.contains('안전성', na=False)]
        df.loc[df['의존 문서#1'].str.contains('안전성', na=False), '의존 문서#1'] = None
        df.loc[df['의존 문서#2'].str.contains('안전성', na=False), '의존 문서#2'] = None
        df.loc[df['의존 문서#3'].str.contains('안전성', na=False), '의존 문서#3'] = None
    if not cyber_security_included:
        df = df[~df['문서명'].str.contains('사이버보안', na=False)]
        df.loc[df['의존 문서#1'].str.contains('사이버보안', na=False), '의존 문서#1'] = None
        df.loc[df['의존 문서#2'].str.contains('사이버보안', na=False), '의존 문서#2'] = None
        df.loc[df['의존 문서#3'].str.contains('사이버보안', na=False), '의존 문서#3'] = None
    
    filtered_df = df
    
    # Sample holidays list
    holidays = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]

    # Assign publication dates conditions to a single configuration
    
    with st.sidebar.form('설정'):
        spec_date = st.date_input("요구사항 명세서 발행일",value=datetime.date.today())
        design_date = st.date_input("설계 명세서 발행일", value=datetime.date.today()+datetime.timedelta(days=7))
        impl_date = st.date_input("구현 명세서 발행일", value=datetime.date.today()+datetime.timedelta(days=14))
        end_date = st.date_input("발행 마감일", value=datetime.date.today()+datetime.timedelta(days=28))
        expander = st.expander("시험 수행 소요일자")
        with expander:
            ct_days = st.number_input("CT 시험", min_value=1, value=1)
            it_days = st.number_input("IT 시험", min_value=1, value=1)
            st_days = st.number_input("ST 시험", min_value=1, value=1)
        submitted = st.form_submit_button('확인')

    test_configs = (ct_days, it_days, st_days)

    ordered_docs, date_dependencies = select_publication_stages(filtered_df, None)
    
    
    allocated_dates = allocate_dates_with_csp(spec_date, design_date, impl_date, end_date, holidays, documents=ordered_docs, constraints=date_dependencies, test_configs=test_configs)        
    
    if submitted and allocated_dates is None:
        st.info(" 주어진 설정을 만족시키는 발행일자가 없습니다. 설정한 조건이 올바른지 확인해주세요.", icon="ℹ️")
        
    elif submitted and allocated_dates is not None:
        st.write("## dates_df")
        dates_df = pd.DataFrame(list(allocated_dates.items()), columns=["문서명", "날짜"])
        dates_df['날짜'] = pd.to_datetime(dates_df['날짜']).dt.strftime('%y.%m.%d')
        grid_response = AgGrid(dates_df, editable=True, height=800, width=200)
        updated_df = pd.DataFrame(grid_response["data"])

        st.subheader("Updated DataFrame:")
        st.write(updated_df)
    
    else:
        st.stop()

    #allocated_dates = {}

    # Display the dates in AgGrid



if __name__ == "__main__":
    app()
