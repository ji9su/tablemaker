
import io
import re
import pandas as pd
# import mammoth
import streamlit as st
from streamlit import session_state as state
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

from basic import Basic
from analysis.statistic import Statistic
from csv_to_docx_draw_line import  csv_to_docx

class App(Basic):

    def __init__(self):
        super().__init__()

        self._set_page_style()
        self._is_submit = True
        self.statistic = Statistic()

    
    def _set_page_style(self):

        st.set_page_config(
            layout="wide",
        )

    def _warn_messages_overlap_variable(self):
        
        if state["top_variables"] is not None:
            if len(set(state["top_variables"]) & set(state["bottom_variables"])) > 0:
                overlap = ', '.join(set(state["top_variables"]) & set(state["bottom_variables"]))
                st.warning(
                    'Continuous variables and Categorical variables are overlap: {overlap}'.format(overlap=overlap),
                    icon="⚠️")

                self._is_submit = False
            else:
                if self._is_submit == True:
                    self._is_submit = True


    def _warn_messages_no_id_variable(self, id_list):
        
        if not id_list:
            
            st.warning(
                'Aanalyze data do not have ID variable',
                icon="⚠️")

            self._is_submit = False
        else:
            if self._is_submit == True:
                self._is_submit = True


    def _warn_messages_no_def_variable(self, aanalyze_variables):

        if aanalyze_variables is not None:

            def_variables = set(state["top_variables"] + state["bottom_variables"])
            no_def_variables = set(aanalyze_variables) - def_variables

            if len(no_def_variables) > 0:
                no_def = ', '.join(no_def_variables)
                st.warning(
                    'Aanalyze variables are not defined to continuous or categorical: {no_def}'.format(
                        no_def=no_def),
                    icon="⚠️")

                self._is_submit = False
        else:
            if self._is_submit == True:
                self._is_submit = True


    def container1(self):

        with self._col1:
            st.header("Step 1: Data Selection")

            st.selectbox(
                'Choose an encoding',
                self._selectbox_config["encoding"],
                index = self._selectbox_config["encoding"].index(state["encoding"]),
                key = 'new_encoding',
                on_change = self._encoding_callback
            )

            st.write(
                "Note: Data columns name don't have any numeric and mark"
            )

            uploaded_file = st.file_uploader(
                "Please upload your data file (user only):",
                on_change = self._variable_callback
            )

            # state["data"] = pd.read_csv("data/Example1.csv", encoding=state["new_encoding"])
            # state["variables"] = list(state["data"].columns)
            if uploaded_file is not None:
                data = pd.read_csv(uploaded_file, encoding=state["new_encoding"])
                # data.columns = [re.sub("\d+|\\.", "", name) for name in data.columns]
                state["data"] = data
                state["variables"] = list(state["data"].columns)

            st.slider(
                'Automatically assign variables whose <= x categories as categorical variables:',
                min_value = 2, max_value = 20, value = state["factor_cut"],
                key = 'new_factor_cut',
                on_change = self._factor_cut_callback
            )

            st.write(
                "Note: if a variables have > x categories and its property is character, it will be automatically classified as the non-analyzed variable."
            )


    def container2(self):

        with self._col2:
            st.header("Step 2: Select Variables:")
            if state["data"] is not None:

                if state["top_variables"] is None:
                    state["top_variables"] = list(
                        filter(lambda variable:
                               len(pd.factorize(state["data"][variable])[1]) > state["new_factor_cut"],
                               state["variables"]
                               )
                    )

                    state["bottom_variables"] = list(
                        filter(lambda variable:
                               len(pd.factorize(state["data"][variable])[1]) <= state["new_factor_cut"],
                               state["variables"]
                               )
                    )

                st.multiselect(
                    'To choose continuous variables:',
                    list(state["data"].columns),
                    state["top_variables"],
                    key = "new_top_variables",
                    on_change = self._top_variables_callback
                )

                st.multiselect(
                    'To choose categorical variables:',
                    list(state["data"].columns),
                    state["bottom_variables"],
                    key = "new_bottom_variables",
                    on_change = self._bottom_variables_callback
                )

                self._warn_messages_overlap_variable()

    def sidebar2(self):
        if self._sidebar_config[self._selected] == 1:

            self._warn_messages_overlap_variable()

            col1, col2, col3 = st.columns([3, 3, 5])
            with col1:

                st.subheader("Step 4: Method type selection:")
                
                st.selectbox(
                    '  ',
                    list(self._method_config.keys()),
                    index=list(self._method_config.keys()).index(state["method"]),
                    key="new_method",
                    on_change = self._method_callback
                )

                st.subheader("Step 4-1: Method Details:")

                st.radio(
                    "{method}: ".format(method=state["method"]),
                    self._parameters_config[state["method"]],
                    index=self._parameters_config[state["method"]].index(state["sub_method"]),
                    key="new_sub_method",
                    on_change = self._sub_method_callback
                )

            with col2:
                
                # variables = list(filter(lambda item: item in state["top_variables"] + state["bottom_variables"], state["variables"]))
                variables = state["variables"]
                continuous_variables = state["top_variables"]
                categorical_variables = state["bottom_variables"]

                st.subheader("Step 5-1: Variables selection")

                if state["method"] == "Description":
                    if state["sub_method"] == "No Group":

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                st.multiselect(
                                    'To choose the variables needed to analyze:',
                                    variables,
                                    state["independent_variables1"],
                                    key = "new_independent_variables1",
                                    on_change = self._independent_variables1_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables1"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables1"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )                                    
                                    
                    elif state["sub_method"] == "Group":

                        if state["data"] is not None:
                            st.multiselect(
                                'To choose a grouping variable:',
                                state["bottom_variables"],
                                state["group_variables1"],
                                key = "new_group_variables1",
                                on_change = self._group_variables1_callback
                            )
                            st.write("Note: Categorical only.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                st.multiselect(
                                    'To choose the variables needed to analyze:',
                                    variables,
                                    state["independent_variables2"],
                                    key = "new_independent_variables2",
                                    on_change = self._independent_variables2_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables2"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables2"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "groups": state["group_variables1"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )

                elif state["method"] == "Linear regression":
                    if state["sub_method"] == "Simple Linear Regression":
                        
                        if state["data"] is not None:
                            st.multiselect(
                                'To choose a continuous dependent variables:',
                                state["top_variables"],
                                state["dependent_variables1"],
                                key="new_dependent_variables1",
                                on_change=self._dependent_variables1_callback
                            )

                            st.write("Note: the selectable variables must be continuous variables.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                dependent_variables1 = [None] if state["dependent_variables1"] is None else state[
                                    "dependent_variables1"]

                                st.multiselect(
                                    'To choose independent variables:',
                                    variables,
                                    state["independent_variables3"],
                                    key="new_independent_variables3",
                                    on_change=self._independent_variables3_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables3"])

                                # TOOD auto adjusted variables

                                st.multiselect(
                                    'To choose adjusted variables:',
                                    variables,
                                    state["adjusted_variables1"],
                                    key = "new_adjusted_variables1",
                                    on_change = self._adjusted_variables1_callback
                                )

                                self._warn_messages_no_def_variable(state["adjusted_variables1"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables3"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "dependent": state["dependent_variables1"],
                                        "adjusted": state["adjusted_variables1"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )

                    elif state["sub_method"] == "Multiple Linear Regression":
                        
                        if state["data"] is not None:

                            st.multiselect(
                                'To choose a continuous dependent variables:',
                                state["top_variables"],
                                state["dependent_variables2"],
                                key = "new_dependent_variables2",
                                on_change = self._dependent_variables2_callback
                            )

                            st.write("Note: the selectable variables must be continuous variables.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                dependent_variables2 = [None] if state["dependent_variables2"] is None else state["dependent_variables2"]

                                st.multiselect(
                                    'To choose independent variables:',
                                    variables,
                                    state["independent_variables4"],
                                    key = "new_independent_variables4",
                                    on_change = self._independent_variables4_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables4"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables4"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "dependent": state["dependent_variables2"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )

                elif state["method"] == "Logistic regression":
                    if state["sub_method"] == "Simple Logistic Regression":
                        
                        if state["data"] is not None:
                            
                            binary_dependent = []
                            for variable in state["bottom_variables"]:
                                lvls = list(pd.factorize(state["data"][variable])[1].sort_values())
                                if lvls == [0.0, 1.0]:
                                    binary_dependent.append(variable)

                            st.multiselect(
                                'To choose a binary dependent variables:',
                                binary_dependent,
                                state["dependent_variables3"],
                                key="new_dependent_variables3",
                                on_change=self._dependent_variables3_callback
                            )

                            st.write("Note: the selectable variables must be coded as 0 (ref) and 1.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                dependent_variables3 = [None] if state["dependent_variables3"] is None else state["dependent_variables3"]

                                st.multiselect(
                                    'To choose independent variables:',
                                    variables,
                                    state["independent_variables5"],
                                    key="new_independent_variables5",
                                    on_change=self._independent_variables5_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables5"])

                                st.multiselect(
                                    'To choose adjusted variables:',
                                    variables,
                                    state["adjusted_variables3"],
                                    key="new_adjusted_variables3",
                                    on_change=self._adjusted_variables3_callback
                                )

                                self._warn_messages_no_def_variable(state["adjusted_variables3"])

                                if state["clicked"]:
                                    
                                    variable_dict = {
                                        "independent": state["independent_variables5"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "dependent": state["dependent_variables3"],
                                        "adjusted": state["adjusted_variables3"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )

                    elif state["sub_method"] == "Multiple Logistic Regression":

                        if state["data"] is not None:

                            binary_dependent = []
                            for variable in state["bottom_variables"]:
                                lvls = list(pd.factorize(state["data"][variable])[1].sort_values())
                                if lvls == [0.0, 1.0]:
                                    binary_dependent.append(variable) 

                            st.multiselect(
                                'To choose a binary dependent variables:',
                                binary_dependent,
                                state["dependent_variables4"],
                                key="new_dependent_variables4",
                                on_change=self._dependent_variables4_callback
                            )

                            st.write("Note: the selectable variables must be coded as 0 (ref) and 1.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                dependent_variables4 = [None] if state["dependent_variables4"] is None else state["dependent_variables4"]

                                st.multiselect(
                                    'To choose independent variables:',
                                    variables,
                                    state["independent_variables6"],
                                    key="new_independent_variables6",
                                    on_change=self._independent_variables6_callback
                                )

                                self._warn_messages_no_def_variable(state["independent_variables6"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables6"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "dependent": state["dependent_variables4"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )
                
                elif state["method"] == "GEE":
                    if state["sub_method"] == "Simple Regression":
                        
                        if state["data"] is not None:
                            st.multiselect(
                                'To choose a continuous dependent variables:',
                                state["top_variables"],
                                state["dependent_variables5"],
                                key="new_dependent_variables5",
                                on_change=self._dependent_variables5_callback
                            )

                            st.write("Note: the selectable variables must be continuous variables.")

                            if "ID" in variables:
                                st.multiselect(
                                    'To choose a ID variable:',
                                    ["ID"],
                                    state["id_variables1"],
                                    key="new_id_variables1",
                                    on_change=self._id_variables1_callback
                                )

                                st.write("Note: ID variable names must be ID.")

                            if "time" in variables:
                                st.multiselect(
                                    'To choose a time variable:',
                                    ["time"],
                                    state["time_variables1"],
                                    key="new_time_variables1",
                                    on_change=self._time_variables1_callback
                                )

                                st.write("Note: time variable names must be time.")

                            if "group" in variables:
                                st.multiselect(
                                    'To choose a group variable:',
                                    ["group"],
                                    state["group_variables2"],
                                    key="new_group_variables2",
                                    on_change=self._group_variables2_callback
                                )

                                st.write("Note: group variable names must be group.")

                    #     with col3:
                    #         st.subheader("Step 5-2: Variables selection")
                    #         if state["data"] is not None:

                    #             dependent_variables1 = [None] if state["dependent_variables1"] is None else state[
                    #                 "dependent_variables1"]

                    #             st.multiselect(
                    #                 'To choose independent variables:',
                    #                 variables,
                    #                 state["independent_variables3"],
                    #                 key="new_independent_variables3",
                    #                 on_change=self._independent_variables3_callback
                    #             )

                    #             self._warn_messages_no_id_variable(state["id_variables1"])
                    #             self._warn_messages_no_def_variable(state["independent_variables3"])

                    #             # TOOD auto adjusted variables

                    #             st.multiselect(
                    #                 'To choose adjusted variables:',
                    #                 variables,
                    #                 state["adjusted_variables1"],
                    #                 key = "new_adjusted_variables1",
                    #                 on_change = self._adjusted_variables1_callback
                    #             )

                    #             self._warn_messages_no_def_variable(state["adjusted_variables1"])

                    #             if state["clicked"]:

                    #                 variable_dict = {
                    #                     "independent": state["independent_variables3"],
                    #                     "continuous": continuous_variables,
                    #                     "categorical": categorical_variables,
                    #                     "dependent": state["dependent_variables1"],
                    #                     "adjusted": state["adjusted_variables1"]
                    #                     }
                                    
                    #                 state["result"] = self.statistic._analysis(
                    #                     data = state["data"],
                    #                     method = state["method"],
                    #                     sub_method = state["sub_method"],
                    #                     variable_dict = variable_dict
                    #                 )

                    elif state["sub_method"] == "Multiple Regression":
                        
                        if state["data"] is not None:

                            st.multiselect(
                                'To choose a continuous dependent variables:',
                                state["top_variables"],
                                state["dependent_variables6"],
                                key = "new_dependent_variables6",
                                on_change = self._dependent_variables6_callback
                            )

                            st.write("Note: the selectable variables must be continuous variables.")

                            if "ID" in variables:

                                st.multiselect(
                                    'To choose a ID variable:',
                                    ["ID"],
                                    state["id_variables2"],
                                    key="new_id_variables2",
                                    on_change=self._id_variables2_callback
                                )

                                st.write("Note: ID variable names must be ID.")

                            if "time" in variables:

                                st.multiselect(
                                    'To choose a time variable:',
                                    ["time"],
                                    state["time_variables2"],
                                    key="new_time_variables2",
                                    on_change=self._time_variables2_callback
                                )

                                st.write("Note: time variable names must be time.")

                            if "group" in variables:

                                st.multiselect(
                                    'To choose a group variable:',
                                    ["group"],
                                    state["group_variables3"],
                                    key="new_group_variables3",
                                    on_change=self._group_variables3_callback
                                )

                                st.write("Note: group variable names must be group.")

                        with col3:
                            st.subheader("Step 5-2: Variables selection")
                            if state["data"] is not None:

                                dependent_variables6 = [None] if state["dependent_variables6"] is None else state["dependent_variables6"]

                                st.multiselect(
                                    'To choose independent variables:',
                                    [item for item in variables if item not in ["ID", "time", "group"]],
                                    state["independent_variables8"],
                                    key = "new_independent_variables8",
                                    on_change = self._independent_variables8_callback
                                )

                                self._warn_messages_no_id_variable(state["id_variables2"])
                                self._warn_messages_no_def_variable(state["independent_variables8"])

                                if state["clicked"]:

                                    variable_dict = {
                                        "independent": state["independent_variables8"],
                                        "continuous": continuous_variables,
                                        "categorical": categorical_variables,
                                        "dependent": state["dependent_variables6"],
                                        "id": state["id_variables2"],
                                        "time": state["time_variables2"],
                                        "group": state["group_variables3"]
                                        }
                                    
                                    state["result"] = self.statistic._analysis(
                                        data = state["data"],
                                        method = state["method"],
                                        sub_method = state["sub_method"],
                                        variable_dict = variable_dict
                                    )



            st.write("---")
            col4, col5 = st.columns([2, 10])
            with col4:
                st.subheader("Step 6: Analyze:")

                if self._is_submit:
                    st.button('Click me', on_click = self._click_button)
                    state["clicked"] = False

            with col5:
                st.subheader("Step 7: Result")

                if state["result"] is not None:
                    
                    col6, _ = st.columns([6, 9])
                    with col6:
                        st.selectbox(
                            "Choose dependent variable table",
                            list(state["result"].keys()),
                            index = list(state["result"].keys()).index(state["show_result"]) if state["show_result"] in list(state["result"].keys()) else None,
                            key = "new_show_result",
                            on_change = self._show_result_callback
                            )

                    if (state["show_result"] is not None) & (state["show_result"] in list(state["result"].keys())):
                        if state["result"][state["show_result"]].empty == False:

                            st.table(state["result"][state["show_result"]].reset_index())
                            # st.markdown(state["result"].to_html(), unsafe_allow_html = True)
                            # st.dataframe(state["result"])

                            col7, col8, _ = st.columns([3, 3, 9])
                            
                            with col7:
                                @st.cache_data
                                def convert_df(df):
                                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                                    try:
                                        return df.to_csv().encode('cp950')
                                    except:
                                        return df.to_csv().encode('utf-8')

                                csv = convert_df(state["result"][state["show_result"]])

                                st.download_button(
                                    label="Download Table (Excel form)",
                                    data=csv,
                                    file_name=state["show_result"] + '.csv',
                                    mime='text/csv',
                                )

                            with col8:

                                doc_download = csv_to_docx(state["result"][state["show_result"]].reset_index())

                                bio = io.BytesIO()
                                doc_download.save(bio)

                                st.download_button(
                                    label="Download Table (Word form)",
                                    data=bio.getvalue(),
                                    file_name=state["show_result"] + '.docx',
                                    mime='doc/docx',
                                )
                            
                            


    def make_sidebar(self):
        # 1. as sidebar menu
        with st.sidebar:
            self._selected = option_menu("TableMaker", list(self._sidebar_config.keys()),
                                   menu_icon = "cast", default_index = 0,
                                   styles = {
                                       "container": {"padding": "0!important", "background-color": "#fafafa"},
                                       "icon": {"color": "orange"},
                                       "nav-link": {"text-align": "left", "margin": "0px",
                                                    "--hover-color": "#eee"}
                                        }
                                   )

    def sidebar1(self):

        if self._sidebar_config[self._selected] == 0:
            self._col1, self._col2 = st.columns([4, 8])

            self.container1()
            self.container2()

            st.write("---")
            st.header("Step 3: Edit and filter your data")
            st.write("Data Summary:")
            if state["data"] is not None:
                st.table(state["data"].describe())

            st.write("---")
            st.write("Data Details:")
            if state["data"] is not None:
                st.write(state["data"])


    def run(self):

        self.make_sidebar()
        self.sidebar1()
        self.sidebar2()



if __name__=="__main__":

    app = App()
    app.run()

