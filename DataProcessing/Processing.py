# -*- coding: latin-1 -*-
import pandas as pd
import numpy as np

# METODO: se retorna un JSON con la informaci�n de un experimento registrado de acuerdo a la estructura de entrada del 
# simulador
# PARAMETROS DE ENTRADA:
# - experimentJSON(JSON): arreglo con un experimento registrado.
# PARAMETROS DE SALIDA: 
# - orderedExperiment(JSON): arreglo la informaci�n organizada de acuerdo a la estructura de entrada del simulador para un 
#   experimento registrado
def getInputExperiment(experimentJSON):    
    experimentDF = organizeExperiment(experimentJSON)
    experimentDF = experimentDF.iloc[0]
    return experimentDF.to_json()

# M�todo: para un experimento registrado, se seleccionan y organizan sus variables seg�n la estructura de entrada 
# del simulador
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con la informaci�n organizada seg�n la estructura de entrada del simulador para el
#   experimento registrado
def organizeExperiment(experimentJSON):
    
    # Se crea un Data Frame con atributos para el c�digo, tama�o de part�cula y porcentaje del PA valorado en la formulaci�n
    experimentDF = getInfoPA(experimentJSON)
    
    # Se crea un Data Frame con informaci�n para los porcentajes, tama�o de part�cula y solubilidad de cada tipo de 
    # excipientes en la formulaci�n
    infoExcipient = getInfoExcipient(experimentJSON)
    
    # Se crea un Data Frame con las variables categ�ricas codificadas (Via, Recubrimiento y Metodo)
    categorical = getOneHotEncoding(experimentJSON)
    
    # Se crea un Data Frame con las variables f�sico qu�micas del PA valorado
    experimentDF = getPhysicalChemical(experimentDF)
    
    # Se crea un Data Frame con 3 tiempos seleccionados del perfil de disoluci�n (primer tiempo, el inmediatamente anterior 
    # a 85% y el inmediatamente superior a 85%)
    timesDF = getTimes(experimentJSON)
    
    # Se crea un Data Frame con las demas variables que deben estar presentes en la formulaci�n
    generalVariables = getInfoGeneral(experimentJSON)
    
    # Se juntan todos los Data Frame antes creados 
    experimentDF = pd.concat([experimentDF,infoExcipient,categorical,timesDF,generalVariables],axis=1)
    
    # Se ordenan las variables para que esten en el orden que las necesita el simulador y se retorna    
    return organizeVariables(experimentDF)

# METODO: para la informaci�n registrada de de experimento, se crean variables para el c�digo, porcentaje del 
# principio activo valorado y para su correspondiente tama�o de part�cula de cada experimento.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables para el c�digo, porcentaje y tama�o de part�cula del PA valorado
def getInfoPA(experimentJSON):
    PAs = experimentJSON['principiosActivos']
    namePA = experimentJSON['principioActivoValorado']

    percentage = 0
    size = 0
    for PA in PAs:
        if(int(PA['nombre']) == namePA):
            code = int(PA['nombre'])
            percentage = PA['porcentaje']
            size = PA['tamanoParticula']    

    experimentDF = pd.DataFrame([[code,percentage,size]],columns=['codigo','porcentajePA','tamanoParticulaPA'])
    
    return experimentDF

# METODO: para la informaci�n registrada de un experimento, se crean las variables que indican el porcentaje, 
# el tama�o de part�cula y la solubilidad de cada tipo de excipiente presente en la formulaci�n.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables que indican el porcentaje, el tama�o de part�cula y la 
#   solubilidad de cada tipo de excipiente presente en la formulaci�n
def getInfoExcipient(experimentJSON):
    # Se obtiene la informaci�n, por tipo, de cada excipiente, su porcentaje y su tama�o de part�cula
    infoExcipients = getMultiInputs(experimentJSON)
    
    # Se asocia por tipo la solubilidad para cada excipiente presente en una formulaci�n
    solubilities = getSolubility(infoExcipients)
    
    names = ['aglutinantes','desintegrantes','deslizantes','diluyentes','lubricantes','surfactantes','otros',
             'tamanoAglutinantes','tamanoDesintegrantes','tamanoDeslizantes','tamanoDiluyentes','tamanoLubricantes',
             'tamanoSurfactantes','tamanoOtros','solubilidadAglutinantes','solubilidadDesintegrantes',
             'solubilidadDeslizantes','solubilidadDiluyentes','solubilidadLubricantes','solubilidadSurfactantes']
    
    percentageExcipients = []    
    sizeExcipients = []    
    for excipient in infoExcipients:
        percentageExcipients.append(excipient[1].sum())
        sizeExcipients.append(((excipient[1]*excipient[2])/excipient[1].sum()).sum())

    soluExcipients = []
    for i in range(len(solubilities)):
        iSolubility = ((infoExcipients[i][1]*solubilities[i])/infoExcipients[i][1].sum()).sum()
        soluExcipients.append(iSolubility)

    info = []
    info.extend(percentageExcipients)
    info.extend(sizeExcipients)
    info.extend(soluExcipients)

    infoExcipients = pd.DataFrame([info],columns=names)
    
    return infoExcipients

# METODO: Se extrae la informaci�n de excipientes presentes en cada tipo(c�digos, porcentajes, tama�os de part�culas) para
# un experimento registrado
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - infoExcipient(List): informaci�n de excipientes presentes en cada tipo(c�digos, porcentajes, tama�os de part�culas) para
#   un experimento registrado
#   Estructrura:
#   - Tipo Excipiente(List)
#     - Codigo(list)
#     - Porcentaje(Array)
#     - Tama�o Particula(Array)
def getMultiInputs(experimentJSON):
    excipients = ['aglutinantes','desintegrantes','deslizantes','diluyentes','lubricantes','surfactantes','otros']
        
    infoExcipients = []
    for excipient in excipients:
        iExcipient = experimentJSON[excipient]

        codes = []
        percentages = []
        sizes = []        
        for i in range(len(iExcipient)):
            codes.append(int(iExcipient[i]['nombre']))
            percentages.append(iExcipient[i]['porcentaje'])
            sizes.append(iExcipient[i]['tamanoParticula'])

        percentages = np.array(percentages)
        sizes = np.array(sizes)            
        infoExcipients.append([codes,percentages,sizes])    
    
    return infoExcipients

# METODO: se extrae la informaci�n de solubilidad de excipientes presentes en cada tipo para un experimento resgistrados.
# PARAMETROS DE ENTRADA
# - infoExcipients(List): informaci�n de excipientes presentes en cada tipo(c�digos, porcentajes, tama�os de part�culas) para
#   un experimento registrado
# PARAMETROS DE SALIDA
# - experiSolubilities(List):  solubilidad de excipientes presentes en cada tipo para un experimento resgistrado.
#   Estructura:
#   - Tipo Excipient(List)
#     - Solubilidad(Array)
def getSolubility(infoExcipients):
    # ���REEMPLAZAR POR LA TABLA EN EL SERVIDOR!!!
    solubility = pd.read_excel('C:/Users/ing-y-soft/Documents/Proyecto/Code/Integracion/tablas/Solubilidad_de_Excipientes_Integracion2.xlsx')
    solubility.codigo = [int(s[1:]) for s in solubility.codigo]      
    
    typeExcipients = []    
    for excipient in infoExcipients[:-1]:
        typeExcipients.append(pd.DataFrame(excipient[0],columns=['codigo']))

    typeSolu = []
    for df in typeExcipients:
        typeSolu.append(pd.merge(df,solubility,on='codigo'))

    solubilities = []
    for element in typeSolu:
        solubilities.append(np.array(element.solubilidadEnAgua))

    return solubilities

# METODO: se codifican la variables categ�ricas Via, Recubrimiento y Metodo seg�n One Hot Encoding de un experimento 
# registrado
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA
# - categorical(Data Frame): tabla con las variables categoricas codificadas para un experimento registrado
def getOneHotEncoding(experimentJSON):
    names = ['viaSeca','viaHumeda','tabletaRecubierta','tabletaNoRecubierta','metodoHPLC','metodoUV','aparatoDis1',
             'aparatoDis2']
    
    via = experimentJSON['via']
    recubrimiento = experimentJSON['recubrimiento']
    metodo = experimentJSON['metodo']
    aparato = experimentJSON['aparatoDisolucion']

    values = []
    if(via == 'Via_Seca'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(recubrimiento == 'Tableta_Recubierta'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(metodo == 'Metodo_HPLC'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(aparato == 'Aparato_Dis1'):
        values.extend([1,0])
    else:
        values.extend([0,1])

    categorical = pd.DataFrame([values],columns=names)
    
    return categorical

# METODO: se agregan las variables f�sico qu�micas del pricipio activo en un experimento registrado.
# PARAMETROS DE ENTRADA 
# - experimentDF(Data Frame): tabla que contiene informaci�n del c�digo del PA valorado en un experimento registrado
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): misma tabla de entrada junto con las variables f�sico qu�micas del experimiento
def getPhysicalChemical(experimentDF):
    # ���REEMPLAZAR POR LA TABLA EN EL SERVIDOR!!!
    physicalChemical = pd.read_csv('C:/Users/ing-y-soft/Documents/Proyecto/Code/Integracion/tablas/PA_Esp_Eng_Var_Integracion.csv')
    #physicalChemical = pd.read_csv('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\tablas\PA_Esp_Eng_Var_Integracion.csv')
    physicalChemical.codigo = [int(s[1:]) for s in physicalChemical.codigo]
    
    experimentDF = pd.merge(experimentDF,physicalChemical,on='codigo')
    
    erase = ['codigo','nombreEsp','nombreEng','hidroxilos','aldehidos','cetonas','carboxilos','aminas','iminas',
             'amidas','imidas','nitro','nitrilo','hidrazina','haluros','eter','azoNitrogenado']
    experimentDF.drop(erase,axis=1,inplace=True)
    
    return experimentDF

# METODO: para un experimento registrado, del perfil de disoluci�n se seleccionan los tiempos correspondientes al primer 
# porcentaje, al inmediatamente inferior a 85% y al inmediatamente mayor a 85%
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA
# - timesDF(Data Frame): tabla con los tiempos seleccionados del perfil de disoluci�n de un experimento registrado
def getTimes(experimentJSON):    
    names = ['tiempo1','tiempo2','tiempo3']
    times = experimentJSON['tiempos']
    i = 0
    while(times[i]['media'] < 85):
        i += 1
    values = [times[0]['tiempo'],times[i-1]['tiempo'],times[i]['tiempo']]
    timesDF = pd.DataFrame([values],columns=names)
    
    return(timesDF)

# METODO: para un experimento registrado se extrae la informaci�n de las variables que no requieren ning�n tipo de 
# procesamiento.
# PARAMETROS DE ENTRADA: 
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA:
# - generalVariables(Data Frame): tabla con informaci�n de variables que no requieren ning�n tipo de procesamiento para un 
#   experimento registrado
def getInfoGeneral(experimentJSON):    
    names = ['humedadGranulado','proporcionGranulado','tiempoMezcladoGranulado','proporcionSolvente','temperaturaSecado',
             'tiempoSecado','largoPromedio','largoSTD','anchoPromedio','anchoSTD','alturaPromedio','alturaSTD',
             'tiempoMezclaTotalFormula','pesoPromedio','pesoSTD','durezaPromedio','durezaSTD','tamanoParticulaMezcla',
             'humedadMezcla','tiempoDesintegracionMinima','tiempoDesintegracionMaxima', 'longitudOnda',
             'velocidadRotacional','PHMedio','volumen']
    
    variables = []
    for var in names:
        variables.append(experimentJSON[var])            
    generalVariables = pd.DataFrame([variables],columns=names)
    return generalVariables

# METODO: se organizan las variables de la tabla construida con la informaci�n de un experimento de acuerdo al orden de 
# entrada del simulador
# PARAMETROS DE ENTRADA
# - experimentDF(Data Frame): tabla con los valores de un experimento registrado
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables organizadas
def organizeVariables(experimentDF):
    order = ['humedadGranulado','proporcionGranulado','tiempoMezcladoGranulado','proporcionSolvente','temperaturaSecado',
             'tiempoSecado','largoPromedio','largoSTD','anchoPromedio','anchoSTD','alturaPromedio','alturaSTD',
             'tiempoMezclaTotalFormula','pesoPromedio','pesoSTD','durezaPromedio','durezaSTD','tamanoParticulaMezcla',
             'humedadMezcla','tiempoDesintegracionMinima','tiempoDesintegracionMaxima','viaSeca','viaHumeda',
             'tabletaRecubierta','tabletaNoRecubierta','longitudOnda','velocidadRotacional','PHMedio','volumen','metodoHPLC',
             'metodoUV','aparatoDis1','aparatoDis2','porcentajePA','tamanoParticulaPA','pesoMolecular','logP','pKaBasico',
             'solubilidadEnAgua','logS','areaSuperficialPolar','cargaFisiologica','enlacesRotables',
             'enlacesAceptoresDeHidrogeno','enlacesDonadoresDeHidrogeno','aglutinantes','desintegrantes','deslizantes',
             'diluyentes','lubricantes','otros','surfactantes','solubilidadAglutinantes','solubilidadDesintegrantes',
             'solubilidadDeslizantes','solubilidadDiluyentes','solubilidadLubricantes','solubilidadSurfactantes',
             'tamanoAglutinantes','tamanoDesintegrantes','tamanoDeslizantes','tamanoDiluyentes','tamanoLubricantes',
             'tamanoOtros','tamanoSurfactantes','tiempo1','tiempo2','tiempo3']
    experimentDF = experimentDF.loc[:,order]
    
    return experimentDF