# -*- coding: latin-1 -*-
from pyswarm import pso
import pandas as pd
import numpy as np
import json
from ServicesDisolution.Retraining.Comparison import getModel
from ServicesDisolution.Retraining.Comparison import validateF2
from ServicesDisolution.DataProcessing import Processing

# METODO: para las variables que se quieran optimizar se retornar los valores máximos y mínimos de cada una de ellas de
# acuerdo a las entradas actualmente registradas
# PARAMETROS DE ENTRADA:
# - variables(List): lista de variables que se quieren optimizar
# PARAMETROS DE SALIDA:
# - lb(List): límites inferiores de las variables a optimizar
# - ub(List): límites superiores de las variables a optimizar
def getBounds(variables):
    #Se optiene la base de datos actual de entradas al simulador
    inputs = pd.read_csv('C:/Users/ing-y-soft/Documents/Proyecto/Code/Integracion/tablas/3_Entradas_Integracion.csv')    
    #inputs = pd.read_csv('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\tablas\3_Entradas_Integracion.csv')
    
    optimizables = inputs.loc[:,variables.iloc[:,0]]
    lb = optimizables.min().values
    ub = optimizables.max().values
    return (lb,ub)

# METODO: de un perfil pasado como json, se obtiene los 3 valores de disolución que se usarán como criterio
# para optimizar, a saber, el primero, el inmediatamente por debajo de 85% y el inmediatamente por encima de 85%
# PARAMETROS DE ENTRADA
# - referenceProfile(json): perfil de referencia
# PARAMETROS DE SALIDA
# - profile(List): lista con los porcentajes de disolución seleccionado
def getProfile(referenceProfile):
    i = 0
    while(referenceProfile[i]['media'] < 85):
        i += 1
    profile = [referenceProfile[0]['media'],referenceProfile[i-1]['media'],referenceProfile[i]['media']]
    
    return(profile)

# METODO: se retorna dos tablas, una con los nombres de los tipos de excipientes y los nombre de los tamaños de partículas
# asociados a cada uno y otra con los nombres de tamaños de partículas y los nombres de tipos de excipientes asociados a cada
# uno.
# PARAMETROS DE ENTRADA:
# PARAMETROS DE SALIDA:
# - exciVar(DataFrame): nombres de tipo de excipientes junto con los nombres de tamaño de partícula asociados.
# - sizeVar(DataFrame): nombres de tamaño de partículas junto con los nombres de tipo de excipientes asociados.
def getAssociates():
    var1 = [['aglutinantes','tamanoAglutinantes'],['desintegrantes','tamanoDesintegrantes'],
            ['deslizantes','tamanoDeslizantes'],['diluyentes','tamanoDiluyentes'],['lubricantes','tamanoLubricantes'],
            ['otros','tamanoOtros'],['surfactantes','tamanoSurfactantes']]

    var2 = [['tamanoAglutinantes','aglutinantes'],['tamanoDesintegrantes','desintegrantes'],
            ['tamanoDeslizantes','deslizantes'],['tamanoDiluyentes','diluyente'],['tamanoLubricantes','lubricantes'],
            ['tamanoOtros','otros'],['tamanoSurfactantes','surfactantes']]
    
    # Se crea una tabla en donde para cada tipo de excipiente se tiene asociado un tamaño de partícula y viceversa
    exciVar = pd.DataFrame(var1,columns=['variables','associates'])
    sizeVar = pd.DataFrame(var2,columns=['variables','associates'])
    
    return(exciVar,sizeVar)

# METODO: de un grupo de variables a optimizar se eliminan aquellas relacionadas con porcentajes y tamaños de partículas
# que no tienen una variable asociada en el grupo y que en el experimento su variable asociada es cero
# PARAMETROS DE ENTRADA:
# - variables(DataFrame): tabla de variables a optimizar
# PARAMETROS DE SALIDA:
# - variables(DataFrame): misma tabla de entrada sin las variables que cumplen con el criterio
def eliminateVariables(variables, experiment):
    experiment = experiment.transpose()
    experiment['asociadas'] = experiment.index
    experiment.columns = ['values','associates']    
    
    exciVar,sizeVar = getAssociates()
    
    # Se determinan los tipos de excipientes y tamaños de partículas presentes es la formulación
    exciPresents = pd.merge(variables,exciVar,on='variables')
    sizePresents = pd.merge(variables,sizeVar,on='variables')
    
    # De los tipos de excipientes a optimizar, se determina cuáles no tienen un tamaño de partícula asociado en el grupo. Lo
    # mismo para los tipos de tamaño de partícula.
    exciNoAs = exciPresents[~exciPresents.associates.isin(sizePresents.variables)]
    sizeNoAs = sizePresents[~sizePresents.associates.isin(exciPresents.variables)]
    
    exciNoAs = pd.merge(exciNoAs,experiment,on='associates')
    sizeNoAs = pd.merge(sizeNoAs,experiment,on='associates')
    
    exciZero = exciNoAs.loc[exciNoAs['values'] == 0]
    sizeZero = sizeNoAs.loc[sizeNoAs['values'] == 0]
    
    variables = variables[~variables.variables.isin(exciZero.variables)]
    variables = variables[~variables.variables.isin(sizeZero.variables)]
    
    return variables

# METODO: de un grupo de variables a optimizar, se retorna una tabla con los nombres de tipos de excipientes y tamaños de 
# partícula que estan asociados.
# PARAMETROS DE ENTRADA:
# - variables(DataFrame): tabla de variables a optimizar
# PARAMETROS DE SALIDA:
# - associatesVar(DataFrame): tabla de nombres de tipo de excipientes junto con los nombres de tamaño de partícula asociados.
def getAssociatesInVariables(variables):
    exciVar,sizeVar = getAssociates()    
    exciPresents = pd.merge(variables,exciVar,on='variables')
    associatesVariables = exciPresents[exciPresents.associates.isin(variables.variables)]
    return(associatesVariables)

# METODO: de las variables relacionadas con porcentajes de una formulación, se retorna el nombre de las que estan en las
# variables a optimizar y las que no.
# PARAMETROS DE ENTRADA:
# - variables(DataFrame): tabla de variables a optimizar
# PARAMETROS DE SALIDA:
# - inOpt(DataFrame): tabla con los nombres de variables relacionadas con porcentajes que si estan en el grupo de optimización
# - outOpt(DataFrame): tabla con los nombres de variables relacionadas con porcentajes que no estan en el grupo de optimización
def getInOut(variables):
    namePercentages = ['porcentajePA','aglutinantes','desintegrantes','deslizantes','diluyentes','lubricantes','otros','surfactantes']
    namePercentages = pd.DataFrame(namePercentages,columns=['variables'])
    
    inOpt = pd.merge(variables,namePercentages,on='variables')
    outOpt = namePercentages[~namePercentages.variables.isin(variables.variables)]
    return(inOpt,outOpt)

# METODO: a partir de un nuevo arreglo sugerido por el algoritmo de optimización, se verifica consistencia entre los 
# valores correspondientes para tipos de excipientes y tamaños de partícula, es decir, su alguno de ellos es cero, su valor
# asociado debe ser cero.
# PARAMETROS DE ENTRADA
# - variables_x(DataFrame): arreglo de valores determinado por el algoritmo de optimización asociados a los nombres de las 
#   variables a optimizar.
# - associatesVariables(DataFrame): nombres de tipos de excipientes junto con sus correspondientes nombre de tamaño de 
#   partícula asociados.
def ensureConsistency(variables_x,associatesVariables):
    for i in range(len(associatesVariables)):
        iExci = variables_x.loc[variables_x.variables == associatesVariables.iloc[i,0]]
        iSize = variables_x.loc[variables_x.variables == associatesVariables.iloc[i,1]]
        if(iExci.iloc[0,1] == 0 or iSize.iloc[0,1] == 0):
            variables_x.ix[iExci.index,1] = 0
            variables_x.ix[iSize.index,1] = 0
            
    return variables_x

# METODO: restricciones que serán aplicadas para un nuevo conjunto de valores determinado por el algoritmo de optimización
# PARAMETROS DE ENTRADA
# - x(Array): lista de nuevos valores determinados por el algoritmo de optimización
# PARAMETROS DE SALIDA
# - costrain(List): lista de restricciones aplicadas al conjunto de nuevos valores
def constrains(x):
    # globals: variables, inOpt, outOpt, experiment, mixConstrain
    xDF = pd.DataFrame(x,columns=['values'])
    variables_x = pd.concat([variables,xDF],axis=1)
    variables_x = ensureConsistency(variables_x,associatesVariables)
    
    sumOutOpt = experiment.loc[:,outOpt.variables].sum(axis=1)
    #print(variables_x.loc[variables_x.variables.isin(inOpt.variables)])
    sumInOpt = variables_x.loc[variables_x.variables.isin(inOpt.variables)].iloc[:,1].sum()
    sumPerc = sumOutOpt+sumInOpt
    if mixConstrain:
        tMin = variables_x.loc[variables_x.variables == 'tiempoMezcladoGranulado'].iloc[0,1]
        tMax = variables_x.loc[variables_x.variables == 'tiempoMezclaTotalFormula'].iloc[0,1]
        constrain = [100-sumPerc[0],tMax-tMin]
    else:
        constrain = [100-sumPerc[0]]
    
    return constrain

# METODO: función que utilizara el algoritmo de optimizción para maximizar el valor de F2
# PARAMETROS DE ENTRADA
# - x(Array): lista de nuevos valores determinados por el algoritmo de optimización
# PARAMETROS DE SALIDA
# - f2(float): valor de F2 predicho a partir de los nuevos valores para las variables optimizadas
def function(x):
    # globals: experiment, variables, model, profile, associatesVariables
    xDF = pd.DataFrame(x,columns=['values'])
    variables_x = pd.concat([variables,xDF],axis=1)
    variables_x = ensureConsistency(variables_x,associatesVariables)
    
    xExperiment = experiment
    #print(variables.variables)
    #print(variables_x['values'])
    #print(xExperiment.values)
    xExperiment.loc[:,variables.variables] = variables_x['values'].values
    #print(xExperiment.values)
    xExperiment = xExperiment.values
    xEstimate = model.predict(xExperiment)
    f2 = validateF2([profileReference],xEstimate)
    return f2

def makeOptimization(fJSON):
    global experiment
    global model
    global variables
    global profileReference
    global associatesVariables
    global mixConstrain
    global inOpt
    global outOpt
    
    model = getModel()
    experimentJSON = fJSON['experimento']
    experiment = Processing.organizeExperiment(experimentJSON)
    profileExperiment = getProfile(experimentJSON['tiempos'])
    variables = fJSON['variables']
    variables = pd.DataFrame(variables,columns=['variables'])
    referenceProfile = fJSON['perfil']
    
    profileReference = getProfile(referenceProfile)
    firstF2 = validateF2([profileReference],[profileExperiment])
    
    variables = eliminateVariables(variables,experiment)
    variables.reset_index(drop=True,inplace=True)
    associatesVariables = getAssociatesInVariables(variables)
    
    serie = pd.Series(['tiempoMezcladoGranulado','tiempoMezclaTotalFormula'])
    serie = serie.isin(variables.variables)
    mixConstrain = False
    if(serie[0] and serie[1]):
        mixConstrain == True
    
    inOpt,outOpt = getInOut(variables)
    lb,ub = getBounds(variables)
    
    data = {}
    xopt, fopt = pso(function,lb,ub,f_ieqcons=constrains,maxiter=100,swarmsize=50)
    if(fopt == 1e+100):
        data['mensaje'] = 'no_optimizado'
    else:
        print(fopt,firstF2)
        if(fopt[0] > firstF2[0]):
            varOpt = pd.DataFrame([xopt],columns=variables.variables)
            varOpt = varOpt.iloc[0].to_json()
            data['mensaje'] = 'optimizado'
            data['variables'] = varOpt
        else:
            data['mensaje'] = 'no_optimizado'
    
    return json.dumps(data)