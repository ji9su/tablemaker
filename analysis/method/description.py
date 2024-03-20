
import pandas as pd
from analysis.method.utils import utils

class Description(utils):

    def __init__(self):
        super().__init__()
        
        self._set_template()

        self._mean_template = "{mean:.2f} ± {sd:.2f}"
        self._freq_template = "{number:d}({frequency:.1%})"
    
    def set_parameter(self, data, sub_method, variable_dict):
        
        self._data = data
        self._sub_method = sub_method
        self._variable_dict = variable_dict

    def _create_result_df(self, group = None):

        colnames = {}
        if group is None:
            colnames["Total"] = []
        else:
            lvls = self._levels(self._data[group])
            colnames.update({self._name_template.format(variable = group, lvl=lvl): [] for lvl in lvls})
            colnames["p-value"] = []

        result_df = pd.DataFrame(colnames, dtype=str)
        result_df.index.names = ['Variable']
        # result_df.columns.names = ['Variable']

        return result_df

    def _mean_and_std(self, variable, group = None):

        mean_sd_list = []

        if group is None:
            mean = self._data[variable].mean()
            sd = self._data[variable].std()
            mean_sd_list.append(self._mean_template.format(mean=mean, sd=sd))
        else:
            for lvl in self._lvls:
                mean = self._data.loc[self._data[group] == lvl, variable].mean()
                sd = self._data.loc[self._data[group] == lvl, variable].std()

                mean_sd_list.append(self._mean_template.format(mean=mean, sd=sd))

        return mean_sd_list

    def _count_categorical(self, data, variable, group = None):

        lvls = list(pd.factorize(self._data[variable])[1].sort_values())

        count_cate = self._table(self._data, [variable, group])
        freq_cate = count_cate / count_cate.sum()

        for i in range(len(lvls)):
            name = self._name_template.format(variable=variable, lvl=lvls[i])
            if group is None:
                cate_freq_list = [
                    self._freq_template.format(
                        number=count_cate.iloc[i],
                        frequency=freq_cate.iloc[i]
                    )
                ]
                data.loc[name, :] = cate_freq_list
            else:
                cate_freq_list = list(map(
                    lambda count, freq: self._freq_template.format(number=count, frequency=freq),
                    count_cate.iloc[i, :],
                    freq_cate.iloc[i, :]
                ))
                data.loc[name,:] = cate_freq_list + [""]

        return data

    def _pvalue_test(self, variable, group, type):

        sample_size = len(self._data[group].dropna())

        if type == "continuous":
            if len(self._lvls) == 2:
                if sample_size > 25:
                    var_pvalue = self.var_test(variable=variable, group=group)
                    var_equal = var_pvalue > 0.05
                    p_value = self.t_test(variable=variable, group=group, var_equal=var_equal)
                else:
                    p_value = self.wilcox_test(variable=variable, group=group)
            else:
                if sample_size > 25:
                    p_value = self.one_way_anova(variable=variable, group=group)
                else:
                    p_value = self.kruskal_test(variable=variable, group=group)

        elif type == "categorical":
            expected_bool = self.expected_test(variable=variable, group=group)
            if expected_bool:
                p_value = self.chisq_test(variable=variable, group=group)
            else:
                p_value = self.fisher_test(variable=variable, group=group)

        p_value = self._process_pvalue(p_value)

        return p_value


    def _description_no_group(self):
        
        
        result_df = self._create_result_df()

        for variable in self._variable_dict["independent"]:
            if variable in self._variable_dict["continuous"]:

                mean_sd_list = self._mean_and_std(variable=variable)
                result_df.loc[variable, :] = mean_sd_list

            elif variable in self._variable_dict["categorical"]:

                result_df.loc[variable, :] = [""]
                result_df = self._count_categorical(
                    data=result_df, variable=variable, group=None
                )
        
        if result_df.empty:
            self._result_df_dict = {}
        else:
            self._result_df_dict["Description(No Group)"] = result_df

    def _description_group(self):

        for group in self._variable_dict["groups"]:

            result_df = self._create_result_df(group=group)
            self._lvls = self._levels(self._data[group])

            for variable in self._variable_dict["independent"]:
                if variable == group:
                    continue
                if variable in self._variable_dict["continuous"]:

                    mean_sd_list = self._mean_and_std(variable=variable, group=group)
                    # p_value = self._pvalue_test(variable, group, type = "continuous")

                    result_df.loc[variable, :] = mean_sd_list + [""]

                elif variable in self._variable_dict["categorical"]:
                    result_df.loc[variable, :] = [""]
                    result_df = self._count_categorical(
                        data=result_df, variable=variable, group=group
                    )
                    # p_value = self._pvalue_test(variable, group, type="categorical")
                    result_df.loc[variable, "p-value"] = ""
            
            if result_df.empty:
                self._result_df_dict = {}
            else:
                self._result_df_dict["Description({group})".format(group = group)] = result_df
        

    def run(self):

        self._result_df_dict = {}

        if self._sub_method == "No Group":
            self._description_no_group()
        else:
            self._description_group()

    def get_result(self):

        if not self._result_df_dict:
            return None
        else:
            return self._result_df_dict
