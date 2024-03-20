
import pandas as pd
from analysis.method.utils import utils


class GEE(utils):

    def __init__(self):
        super().__init__()

        self._beta_template = "{coef:.2f}({lower:.2f}, {upper:.2f})"

    
    def set_parameter(self, data, sub_method, variable_dict):

        self._data = data
        self._sub_method = sub_method
        self._variable_dict = variable_dict

    
    def _create_result_df(self, no_adjustment):

        colnames = {}
        if no_adjustment:
            colnames["beta(95%CI)"] = []
            colnames["p-value"] = []
        else:
            colnames["Crude−beta(95%CI)"] = []
            colnames["p-value"] = []
            colnames["Adj−beta(95%CI)"] = []
            colnames["p-value(Adj)"] = []

        result_df = pd.DataFrame(colnames, dtype=str)
        result_df.index.names = ['Independentvariable']
        # result_df.columns.names = ['Independentvariable']

        return result_df

    def _process_formula(self, dependent, independent, type, adjustment = None):

        if type in ["continuous", "multiple"]:
            formula = "{dependent} ~ {independent}".format(dependent=dependent, independent=independent)
        elif type in ["categorical"]:
            formula = "{dependent} ~ C({independent})".format(dependent=dependent, independent=independent)

        if adjustment is not None:
            formula = formula + " + " + "+".join(adjustment)

        return formula

    def _get_cate_name(self, variable):

        lvls = list(pd.factorize(self._data[variable])[1].sort_values())
        name = [self._name_template.format(variable=variable, lvl=lvls[i]) for i in range(len(lvls))]
        sub_variable = ["C({variable})[T.{lvl:.0f}.0]".format(variable=variable, lvl=lvls[i]) for i in range(1, len(lvls))]

        return name, sub_variable

    def _process_analysis_result(self, variable_list):
        
        result = []
        for variable in variable_list:
            try:
                beta_ci = self._beta_template.format(coef=self._coef.loc[variable], lower=self._ci.loc[variable, 0], upper=self._ci.loc[variable, 1])
                crude_p_value = self._process_pvalue(p_value=self._p_value.loc[variable])
            except:
                beta_ci = self._beta_template.format(coef=self._coef.loc[variable.replace(".0", "")],
                                                     lower=self._ci.loc[variable.replace(".0", ""), 0],
                                                     upper=self._ci.loc[variable.replace(".0", ""), 1])

                crude_p_value = self._process_pvalue(p_value=self._p_value.loc[variable.replace(".0", "")])

            result.append([beta_ci, crude_p_value])

        return result

    def _simple(self):
        pass


    def _multiple(self):
        
        self._variable_dict["independent"] = self._variable_dict["time"] + self._variable_dict["group"] + self._variable_dict["independent"]
        
        for dependent in self._variable_dict["dependent"]:

            result_df = self._create_result_df(no_adjustment = True)

            independent_list = [item for item in self._variable_dict["independent"] if item not in [dependent]]
            
            if ((not self._variable_dict["time"]) == False) & ((not self._variable_dict["group"]) == False):
                independent_list = independent_list[:2] + ["C(time)*C(group)"] + independent_list[2:]
            
            if (not independent_list) == False:
                final_independent = ["C(" + variable + ")" if variable in self._variable_dict["categorical"] else variable for variable in independent_list]
                
                formula = self._process_formula(dependent=dependent, independent="+".join(final_independent), type="multiple")
                self.gee_model(formula=formula)
            
                for variable in independent_list:
                    if variable in self._variable_dict["continuous"]:
                        result = self._process_analysis_result([variable])
                        result_df.loc[variable,:] = result[0]
                    elif variable in self._variable_dict["categorical"]:
                        
                        name, sub_variable = self._get_cate_name(variable)
                        result_df.loc[variable, :] = [""]

                        result = self._process_analysis_result(sub_variable)
                        result = [["Reference", ""]] + result

                        for i in range(len(result)):
                            result_df.loc[name[i], list(result_df.columns)[:2]] = result[i]
                    
                    elif variable in ["C(time)*C(group)"]:

                        result_df.loc["time*group", :] = [""]
                        time_name, sub_time_variable = self._get_cate_name(variable = "time")
                        group_name, sub_group_variable = self._get_cate_name(variable = "group")
                        result_df.loc[time_name[0] + " " + group_name[1] + "/" + group_name[0], :] = ["Reference", ""]
                        for i_index in range(len(sub_group_variable)):
                            for j_index in range(len(sub_time_variable)):
                                result = self._process_analysis_result([sub_time_variable[j_index] + ":" + sub_group_variable[i_index]])
                                result_df.loc[time_name[j_index+1] + " " + group_name[i_index+1] + "/" + group_name[0],:] = result[0]

            
            if result_df.empty:
                self._result_df_dict = {}
            else:
                self._result_df_dict["Multiple GEE({dependent})".format(dependent=dependent)] = result_df
                

    def run(self):

        self._result_df_dict = {}

        if self._sub_method == "Simple Regression":
            self._simple()
        else:
            self._multiple()

    def get_result(self):

        if not self._result_df_dict:
            return None
        else:
            return self._result_df_dict