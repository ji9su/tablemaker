
import pandas as pd
from analysis.method.utils import utils

class Logistic(utils):

    def __init__(self):
        super().__init__()

        self._or_template = "{coef:.2f}({lower:.2f}, {upper:.2f})"

    def set_parameter(self, data, sub_method, variable_dict):

        self._data = data
        self._sub_method = sub_method
        self._variable_dict = variable_dict

    def _create_result_df(self, no_adjustment):

        colnames = {}
        if no_adjustment:
            colnames["OR(95%CI)"] = []
            colnames["p-value"] = []
        else:
            colnames["Crude−OR(95%CI)"] = []
            colnames["p-value"] = []
            colnames["Adj−OR(95%CI)"] = []
            colnames["p-value(Adj)"] = []

        result_df = pd.DataFrame(colnames, dtype=str)
        result_df.index.names = ['Independentvariable']
        # result_df.columns.names = ['Independentvariable']

        return result_df
    
    def _get_cate_name(self, variable):

        lvls = list(pd.factorize(self._data[variable])[1].sort_values())
        name = [self._name_template.format(variable=variable, lvl=lvls[i]) for i in range(len(lvls))]
        sub_variable = ["C({variable})[T.{lvl:.0f}.0]".format(variable=variable, lvl=lvls[i]) for i in range(1, len(lvls))]

        return name, sub_variable

    def _process_formula(self, dependent, independent, type, adjustment = None):

        if type in ["continuous", "multiple"]:
            formula = "{dependent} ~ {independent}".format(dependent=dependent, independent=independent)
        elif type in ["categorical"]:
            formula = "{dependent} ~ C({independent})".format(dependent=dependent, independent=independent)

        if adjustment is not None:
            formula = formula + " + " + "+".join(adjustment)

        return formula

    def _process_analysis_result(self, variable_list):
        
        result = []
        for variable in variable_list:
            try:
                beta_ci = self._or_template.format(coef=self._coef.loc[variable], lower=self._ci.loc[variable, 0], upper=self._ci.loc[variable, 1])
                crude_p_value = self._process_pvalue(p_value=self._p_value.loc[variable])
            except:
                beta_ci = self._or_template.format(coef=self._coef.loc[variable.replace(".0", "")],
                                                   lower=self._ci.loc[variable.replace(".0", ""), 0],
                                                   upper=self._ci.loc[variable.replace(".0", ""), 1])

                crude_p_value = self._process_pvalue(p_value=self._p_value.loc[variable.replace(".0", "")])

            result.append([beta_ci, crude_p_value])

        return result

    def _analysis(self, dependent, variable, adjustment, type):

        formula = self._process_formula(dependent=dependent, independent=variable, adjustment=adjustment, type=type)
        self.logistic_model(formula=formula)
        if type == "categorical":
            result = [["Reference", ""]] + self._process_analysis_result(self._sub_variable)
        else:
            result = self._process_analysis_result([variable])

        return result

    def _simple(self):
        
        for dependent in self._variable_dict["dependent"]:
            
            adjustment = [item for item in self._variable_dict["adjusted"] if item not in [dependent]]

            if (len(set(adjustment + self._variable_dict["independent"])) == 1) | (not adjustment):
                no_adjustment = True
            else:
                no_adjustment = False

            result_df = self._create_result_df(no_adjustment=no_adjustment)
            

            for variable in self._variable_dict["independent"]:

                if variable == dependent:
                    continue

                if variable in self._variable_dict["continuous"]:

                    result = self._analysis(dependent=dependent, variable=variable, adjustment = None, type="continuous")
                    result_df.loc[variable, list(result_df.columns)[:2]] = result[0]

                    if no_adjustment == False:
                        result = self._analysis(dependent=dependent, variable=variable, adjustment = adjustment, type="continuous")
                        result_df.loc[variable, list(result_df.columns)[2:]] = result[0]
                
                elif variable in self._variable_dict["categorical"]:
                    
                    name, self._sub_variable = self._get_cate_name(variable)
                    
                    result_df.loc[variable, :] = [""]
                    result = self._analysis(dependent=dependent, variable=variable, adjustment = None, type="categorical")

                    for i in range(len(result)):
                        result_df.loc[name[i], list(result_df.columns)[:2]] = result[i]

                    if no_adjustment == False:
                        sub_adjustment = [item if item != variable else "C("+item+")" for item in adjustment]
                        result = self._analysis(dependent=dependent, variable = variable, adjustment = sub_adjustment, type="categorical")

                        for i in range(len(result)):
                            result_df.loc[name[i], list(result_df.columns)[2:]] = result[i]


            if result_df.empty:
                self._result_df_dict = {}
            else:
                self._result_df_dict["Simple Logistic({dependent})".format(dependent=dependent)] = result_df

    def _multiple(self):

        for dependent in self._variable_dict["dependent"]:

            result_df = self._create_result_df(no_adjustment = True)

            independent_list = [item for item in self._variable_dict["independent"] if item not in [dependent]]
            
            if (not independent_list) == False:
                final_independent = ["C(" + variable + ")" if variable in self._variable_dict["categorical"] else variable for variable in independent_list]
                formula = self._process_formula(dependent=dependent, independent="+".join(final_independent), type="multiple")
                self.logistic_model(formula=formula)

                for variable in independent_list:
                    if variable in self._variable_dict["continuous"]:
                        result = self._process_analysis_result([variable])
                        result_df.loc[variable,:] = result[0]
                    elif variable in self._variable_dict["categorical"]:
                        
                        name, self._sub_variable = self._get_cate_name(variable)
                        result_df.loc[variable, :] = [""]

                        result = self._process_analysis_result(self._sub_variable)
                        result = [["Reference", ""]] + result

                        for i in range(len(result)):
                            result_df.loc[name[i], list(result_df.columns)[:2]] = result[i]

            if result_df.empty:
                self._result_df_dict = {}
            else:
                self._result_df_dict["Multiple Logistic({dependent})".format(dependent=dependent)] = result_df

    def run(self):

        self._result_df_dict = {}

        if self._sub_method == "Simple Logistic Regression":
            self._simple()
        else:
            self._multiple()

    def get_result(self):

        if not self._result_df_dict:
            return None
        else:
            return self._result_df_dict