
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
# from scipy.stats import levene, ttest_ind, ranksums, kruskal, chi2_contingency, zscore
# import rpy2.robjects.numpy2ri
# from rpy2.robjects.packages import importr
import ast

class utils():

    def __init__(self):

        self._set_template()

    def _set_template(self):

        self._name_template = "{variable}:{lvl:.0f}"
        self._p_value_temlpate = "{p_value:.3f}"

    def _levels(self, data):

        levels = list(pd.factorize(data)[1].sort_values())

        return levels

    def _table(self, data, colname_list):

        colname_list = list(filter(lambda item: item is not None, colname_list))

        if len(colname_list) == 1:
            table = data.groupby(colname_list).size()
        else:
            table = data.groupby(colname_list).size().unstack()

        return table

    def _process_pvalue(self, p_value):

        p_value = "<0.001" if p_value < 0.001 else self._p_value_temlpate.format(p_value=p_value)

        return  p_value

    # def var_test(self, variable, group):

    #     var_result = levene(self._data.loc[self._data[group] == self._lvls[0], variable].dropna(),
    #                         self._data.loc[self._data[group] == self._lvls[1], variable].dropna(),
    #                         center='mean')

    #     return var_result.pvalue

    # def t_test(self, variable, group, var_equal):

    #     #stats.ttest_rel(a, b) Paired t - test
    #     ttest_result = ttest_ind(self._data.loc[self._data[group] == self._lvls[0], variable].dropna(),
    #                              self._data.loc[self._data[group] == self._lvls[1], variable].dropna(),
    #                              equal_var=var_equal)

    #     return ttest_result.pvalue


    def expected_test(self, variable, group):

        table = self._data.groupby([variable, group]).size().sum()
        marginal_n1 = np.array(self._data.groupby([variable, group]).size().unstack().sum(0), ndmin=2)
        marginal_n2 = np.array(self._data.groupby([variable, group]).size().unstack().sum(1), ndmin=2)

        expected_TABLE = marginal_n1.T @ marginal_n2 / table
        expected_result = expected_TABLE > 5
        expected_bool = expected_result.sum() / expected_result.size > 0.8

        return expected_bool

    # def chisq_test(self, variable, group):

    #     table = np.array(self._data.groupby([variable, group]).size().unstack())
    #     chisq_result = chi2_contingency(table)

    #     return chisq_result[1]

    # def fisher_test(self, variable, group):

    #     rpy2.robjects.numpy2ri.activate()
    #     stats = importr('stats')

    #     table = np.array(self._data.groupby([variable, group]).size().unstack())
    #     fisher_result = stats.fisher_test(table)

    #     return fisher_result[0][0]


    # def kruskal_test(self, variable, group):

    #     if len(self._lvls) <= 3:
    #         kruskal_result = kruskal(self._data.loc[self._data[group] == self._lvls[0], variable].dropna(),
    #                                  self._data.loc[self._data[group] == self._lvls[1], variable].dropna(),
    #                                  self._data.loc[self._data[group] == self._lvls[2], variable].dropna())
    #     elif len(self._lvls) == 4:
    #         kruskal_result = kruskal(self._data.loc[self._data[group] == self._lvls[0], variable].dropna(),
    #                                  self._data.loc[self._data[group] == self._lvls[1], variable].dropna(),
    #                                  self._data.loc[self._data[group] == self._lvls[2], variable].dropna(),
    #                                  self._data.loc[self._data[group] == self._lvls[3], variable].dropna())
    #     else:
    #         print("warning group factor over 4")
    #         return ""

    #     return kruskal_result.pvalue

    def one_way_anova(self, variable, group):

        formula_template = "{dependent} ~ C({group})".format(dependent=variable, group=group)

        my_model = smf.ols(formula=formula_template, data=self._data).fit()
        anova_table = sm.stats.anova_lm(my_model, typ=2)

        return anova_table["PR(>F)"][0]

    def linear_model(self, formula):

        self._model = smf.ols(formula=formula, data=self._data).fit()
        self._coef = self._model.params
        self._p_value = self._model.pvalues
        self._ci = self._model.conf_int(alpha=0.05, cols=None)
    
    def collinearity_test(self):

        variables = self._model.model.exog
        vif = np.array([variance_inflation_factor(variables, i) for i in range(variables.shape[1])])[1:]
        vifs = {'Variables': self._model.model.exog_names[1:], 'vif': ['{elem:.2f}'.format(elem=elem) for elem in vif]}
        vifs = pd.DataFrame(vifs).set_index('Variables')

        return vifs

    def logistic_model(self, formula):
        
        self._model = smf.logit(formula=formula, data=self._data).fit()
        self._coef = np.exp(self._model.params)
        self._ci = np.exp(self._model.conf_int(alpha=0.05, cols=None))
        self._p_value = self._model.pvalues

    def gee_model(self, formula):

        fam = sm.families.Gaussian()
        ind = sm.cov_struct.Exchangeable()
        
        self._model = smf.gee(formula, "ID", self._data, cov_struct=ind, family=fam).fit()
        self._coef = self._model.params
        self._p_value = self._model.pvalues
        self._ci = self._model.conf_int(alpha=0.05, cols=None)
