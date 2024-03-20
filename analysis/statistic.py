
from analysis.method.description import Description
from analysis.method.linear import Linear
from analysis.method.logistic import Logistic
from analysis.method.gee import GEE

class Statistic():
    def __init__(self):

        self._set_method_fun()

    def _set_method_fun(self):

        self.description = Description()
        self.linear = Linear()
        self.logistic = Logistic()
        self.gee = GEE()

    def _analysis(self, data, method, sub_method, variable_dict):

        if method == "Description":
            self.description.set_parameter(data, sub_method, variable_dict)
            self.description.run()
            result = self.description.get_result()
        elif method == "Linear regression":
            self.linear.set_parameter(data, sub_method, variable_dict)
            self.linear.run()
            result = self.linear.get_result()
        elif method == "Logistic regression":
            self.logistic.set_parameter(data, sub_method, variable_dict)
            self.logistic.run()
            result = self.logistic.get_result()
        elif method == "GEE":
            self.gee.set_parameter(data, sub_method, variable_dict)
            self.gee.run()
            result = self.gee.get_result()

        return result







