# -*- coding: latin-1 -*-
import numpy as np
import pickle

# METODO: se obtiene el actual modelo del sistema
# PARAMETROS DE ENTRADA:
# - Ninguno
# PARAMETROS DE SALIDA:
# - model(Model): actual modelo del sistema
def getModel():
    #¡¡¡REEMPLAZAR POR EL MODELO EN EL SERVIDOR!!!
    route = open('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\model.pckl')
    model = pickle.load(route)
    route.close()
    return model

# Método para calcular los valores de F1 a partir de los porcentajes de disolución de dos matrices. Cada fila en la matices
# representa un perfil de disolución.
# Parámetros: 
# - val1: matriz con los porcentajes de disolución de los perfiles de referencia reales. Cada fila representa un perfil
#   diferente.
# - val2: matriz con los porcentajes de disolución de los perfiles estimados. Cada fila representa un perfil
#   diferente.
def validateF1(val1,val2):
    R = np.array(val1, dtype=float)
    T = np.array(val2, dtype=float)
    F1 = (((np.absolute(R-T)).sum(axis=1))/(R.sum(axis=1)))*100
    return(F1)

# Método para calcular los valores de F2 a partir de los porcentajes de disolución de dos matrices. Cada fila en la matices
# representa un perfil de disolución.
# Parámetros: 
# - val1: matriz con los porcentajes de disolución de los perfiles de referencia. Cada fila representa un perfil
#   diferente.
# - val2: matriz con los porcentajes de disolución de los perfiles estimados. Cada fila representa un perfil
#   diferente.
def validateF2(val1,val2):    
    R = np.array(val1, dtype=float)
    T = np.array(val2, dtype=float)
    n = R.shape[1]
    F2 = 50*(np.log10((np.power((1+(1.0/n)*((np.power((R-T),2)).sum(axis=1))),-0.5))*100))
    return(F2)