import streamlit as st
from streamlit import session_state as state
from configs.basic import BasicConfigs
from configs.method import MethodConfigs


class Basic():

    def __init__(self):

        self._set_basicConfigs()
        self._set_MethodConfigs()

        self._initial_session_state()
        self._reset_session_state()

    def _set_basicConfigs(self):

        self._sidebar_config = BasicConfigs.sidebar
        self._selectbox_config = BasicConfigs.selectbox
        self._method_config = BasicConfigs.method

    def _set_MethodConfigs(self):

        self._parameters_config = MethodConfigs.parameters

    def _initial_session_state(self):

        # Store the initial value of widgets in session state
        if state == {}:
            state["data"] = None
            state["result"] = None
            state["variables"] = None
            state["top_variables"] = None
            state["bottom_variables"] = None

            state.update({"independent_variables{index}".format(index=index): [] for index in range(1, 9)})
            state.update({"dependent_variables{index}".format(index=index): [] for index in range(1, 7)})
            state.update({"adjusted_variables{index}".format(index=index): [] for index in range(1, 5)})
            state.update({"group_variables{index}".format(index=index): [] for index in range(1, 4)})
            state.update({"id_variables{index}".format(index=index): [] for index in range(1, 3)})
            state.update({"time_variables{index}".format(index=index): [] for index in range(1, 3)})

            # select items
            state['encoding'] = self._selectbox_config["encoding"][0]
            state["factor_cut"] = 10
            state["method"] = list(self._method_config.keys())[0]
            state["sub_method"] = self._parameters_config[state["method"]][0]

            state["sub_method_dic"] = {key: value[0] for key, value in self._parameters_config.items()}
            state["show_result"] = None
            state["clicked"] = False

            # old items
            old_item_list = [
                "old_encoding", "old_show_result", "old_factor_cut", "old_top_variables", "old_bottom_variables",
                "old_method", "old_sub_method"
            ]

            state["old_show_result"] = False
            state.update({item: "" for item in old_item_list})
            state.update({"old_independent_variables{index}".format(index=index): "" for index in range(1, 9)})
            state.update({"old_dependent_variables{index}".format(index=index): "" for index in range(1, 7)})
            state.update({"old_adjusted_variables{index}".format(index=index): "" for index in range(1, 5)})
            state.update({"old_group_variables{index}".format(index=index): "" for index in range(1, 4)})
            state.update({"old_id_variables{index}".format(index=index): "" for index in range(1, 3)})
            state.update({"old_time_variables{index}".format(index=index): "" for index in range(1, 3)})

    def _reset_session_state(self):
        # Check if value exists in the new options. if it does retain the selection, else reset
        if state["encoding"] not in self._selectbox_config["encoding"]:
            state["encoding"] = self._selectbox_config["encoding"][0]

        if state["method"] not in list(self._method_config.keys()):
            state["method"] = list(self._method_config.keys())[0]

        if state["sub_method"] not in self._parameters_config[state["method"]]:
            state["sub_method"] = state["sub_method_dic"][state["method"]]

    def _click_button(self):
        state["clicked"] = True

    def _callback(self, raw, old, new):
        state[old] = state[raw]
        state[raw] = state[new]

    def _encoding_callback(self):
        self._callback("encoding", "old_encoding", "new_encoding")

    def _show_result_callback(self):
        self._callback("show_result", "old_show_result", "new_show_result")

    def _variable_callback(self):
        
        state["top_variables"] = None
        state["bottom_variables"] = None

        state.update({"independent_variables{index}".format(index=index): [] for index in range(1, 9)})
        state.update({"dependent_variables{index}".format(index=index): [] for index in range(1, 7)})
        state.update({"adjusted_variables{index}".format(index=index): [] for index in range(1, 5)})
        state.update({"group_variables{index}".format(index=index): [] for index in range(1, 4)})
        state.update({"id_variables{index}".format(index=index): [] for index in range(1, 3)})
        state.update({"time_variables{index}".format(index=index): [] for index in range(1, 3)})

    def _factor_cut_callback(self):
        self._callback("factor_cut", "old_factor_cut", "new_factor_cut")

    def _top_variables_callback(self):
        self._callback("top_variables", "old_top_variables", "new_top_variables")

        state.update({"independent_variables{index}".format(index=index): [] for index in range(1, 9)})

        state["dependent_variables1"] = []
        state["dependent_variables2"] = []
        state["dependent_variables5"] = []
        state["dependent_variables6"] = []

        state.update({"adjusted_variables{index}".format(index=index): [] for index in range(1, 5)})

    def _bottom_variables_callback(self):
        self._callback("bottom_variables", "old_bottom_variables", "new_bottom_variables")

        state.update({"independent_variables{index}".format(index=index): [] for index in range(1, 9)})

        state["dependent_variables3"] = []
        state["dependent_variables4"] = []

        state.update({"adjusted_variables{index}".format(index=index): [] for index in range(1, 5)})

        state["group_variables1"] = []

    def _method_callback(self):
        self._callback("method", "old_method", "new_method")

    def _sub_method_callback(self):
        self._callback("sub_method", "old_sub_method", "new_sub_method")
        state["sub_method_dic"][state["method"]] = state["new_sub_method"]

    def _independent_variables1_callback(self):
        self._callback("independent_variables1", "old_independent_variables1", "new_independent_variables1")

    def _independent_variables2_callback(self):
        self._callback("independent_variables2", "old_independent_variables2", "new_independent_variables2")

    def _independent_variables3_callback(self):
        self._callback("independent_variables3", "old_independent_variables3", "new_independent_variables3")

    def _independent_variables4_callback(self):
        self._callback("independent_variables4", "old_independent_variables4", "new_independent_variables4")

    def _independent_variables5_callback(self):
        self._callback("independent_variables5", "old_independent_variables5", "new_independent_variables5")

    def _independent_variables6_callback(self):
        self._callback("independent_variables6", "old_independent_variables6", "new_independent_variables6")

    def _independent_variables7_callback(self):
        self._callback("independent_variables7", "old_independent_variables7", "new_independent_variables7")

    def _independent_variables8_callback(self):
        self._callback("independent_variables8", "old_independent_variables8", "new_independent_variables8")

    def _dependent_variables1_callback(self):
        self._callback("dependent_variables1", "old_dependent_variables1", "new_dependent_variables1")

    def _dependent_variables2_callback(self):
        self._callback("dependent_variables2", "old_dependent_variables2", "new_dependent_variables2")

    def _dependent_variables3_callback(self):
        self._callback("dependent_variables3", "old_dependent_variables3", "new_dependent_variables3")

    def _dependent_variables4_callback(self):
        self._callback("dependent_variables4", "old_dependent_variables4", "new_dependent_variables4")

    def _dependent_variables5_callback(self):
        self._callback("dependent_variables5", "old_dependent_variables5", "new_dependent_variables5")

    def _dependent_variables6_callback(self):
        self._callback("dependent_variables6", "old_dependent_variables6", "new_dependent_variables6")

    def _adjusted_variables1_callback(self):
        self._callback("adjusted_variables1", "old_adjusted_variables1", "new_adjusted_variables1")

    def _adjusted_variables2_callback(self):
        self._callback("adjusted_variables2", "old_adjusted_variables2", "new_adjusted_variables2")

    def _adjusted_variables3_callback(self):
        self._callback("adjusted_variables3", "old_adjusted_variables3", "new_adjusted_variables3")

    def _adjusted_variables4_callback(self):
        self._callback("adjusted_variables4", "old_adjusted_variables4", "new_adjusted_variables4")

    def _group_variables1_callback(self):
        self._callback("group_variables1", "old_group_variables1", "new_group_variables1")

    def _group_variables2_callback(self):
        self._callback("group_variables2", "old_group_variables2", "new_group_variables2")

    def _group_variables3_callback(self):
        self._callback("group_variables3", "old_group_variables3", "new_group_variables3")

    def _id_variables1_callback(self):
        self._callback("id_variables1", "old_id_variables1", "new_id_variables1")

    def _id_variables2_callback(self):
        self._callback("id_variables2", "old_id_variables2", "new_id_variables2")

    def _time_variables1_callback(self):
        self._callback("time_variables1", "old_time_variables1", "new_time_variables1")

    def _time_variables2_callback(self):
        self._callback("time_variables2", "old_time_variables2", "new_time_variables2")