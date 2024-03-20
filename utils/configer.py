#!/usr/binn/env python3
# -*-coding:utf-8 -*-
# ---------------------------------------------
# Created By : TSHG AIOT
# Created Date: 2021/11/10
# Version = beta
# ---------------------------------------------

class Configer():
  
  def __init__(self):

    self.config_path = ""
    self._ini_path = ""  

  def covert_param_type(self, param, type):
    
    if type == "float":
      for k in param:
        param[k] = float(param[k])
    elif type == "integer":
      for k in param:
        param[k] = int(param[k])
    
    return param
    
  def list_sections(self, param)-> list:
    
    return list(param.keys())


  
  
  
