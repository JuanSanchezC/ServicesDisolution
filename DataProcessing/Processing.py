# -*- coding: latin-1 -*-
import pandas as pd
import numpy as np

# METODO: se retorna un JSON con la información de un experimento registrado de acuerdo a la estructura de entrada del 
# simulador
# PARAMETROS DE ENTRADA:
# - experimentJSON(JSON): arreglo con un experimento registrado.
# PARAMETROS DE SALIDA: 
# - orderedExperiment(JSON): arreglo la información organizada de acuerdo a la estructura de entrada del simulador para un 
#   experimento registrado
def getInputExperiment(experimentJSON):    
    experimentDF = organizeExperiment(experimentJSON)
    experimentDF = experimentDF.iloc[0]
    return experimentDF.to_json()

# Método: para un experimento registrado, se seleccionan y organizan sus variables según la estructura de entrada 
# del simulador
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con la información organizada según la estructura de entrada del simulador para el
#   experimento registrado
def organizeExperiment(experimentJSON):
    
    # Se crea un Data Frame con atributos para el código, tamaño de partícula y porcentaje del PA valorado en la formulación
    experimentDF = getInfoPA(experimentJSON)
    
    # Se crea un Data Frame con información para los porcentajes, tamaño de partícula y solubilidad de cada tipo de 
    # excipientes en la formulación
    infoExcipient = getInfoExcipient(experimentJSON)
    
    # Se crea un Data Frame con las variables categóricas codificadas (Via, Recubrimiento y Metodo)
    categorical = getOneHotEncoding(experimentJSON)
    
    # Se crea un Data Frame con las variables físico químicas del PA valorado
    experimentDF = getPhysicalChemical(experimentDF)
    
    # Se crea un Data Frame con 3 tiempos seleccionados del perfil de disolución (primer tiempo, el inmediatamente anterior 
    # a 85% y el inmediatamente superior a 85%)
    timesDF = getTimes(experimentJSON)
    
    # Se crea un Data Frame con las demas variables que deben estar presentes en la formulación
    generalVariables = getInfoGeneral(experimentJSON)
    
    # Se juntan todos los Data Frame antes creados 
    experimentDF = pd.concat([experimentDF,infoExcipient,categorical,timesDF,generalVariables],axis=1)
    
    # Se ordenan las variables para que esten en el orden que las necesita el simulador y se retorna    
    return organizeVariables(experimentDF)

# METODO: para la información registrada de de experimento, se crean variables para el código, porcentaje del 
# principio activo valorado y para su correspondiente tamaño de partícula de cada experimento.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables para el código, porcentaje y tamaño de partícula del PA valorado
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

# METODO: para la información registrada de un experimento, se crean las variables que indican el porcentaje, 
# el tamaño de partícula y la solubilidad de cada tipo de excipiente presente en la formulación.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables que indican el porcentaje, el tamaño de partícula y la 
#   solubilidad de cada tipo de excipiente presente en la formulación
def getInfoExcipient(experimentJSON):
    # Se obtiene la información, por tipo, de cada excipiente, su porcentaje y su tamaño de partícula
    infoExcipients = getMultiInputs(experimentJSON)
    
    # Se asocia por tipo la solubilidad para cada excipiente presente en una formulación
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

# METODO: Se extrae la información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
# un experimento registrado
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con experimento registrado.
# PARAMETROS DE SALIDA
# - infoExcipient(List): información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
#   un experimento registrado
#   Estructrura:
#   - Tipo Excipiente(List)
#     - Codigo(list)
#     - Porcentaje(Array)
#     - Tamaño Particula(Array)
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

# METODO: se extrae la información de solubilidad de excipientes presentes en cada tipo para un experimento resgistrados.
# PARAMETROS DE ENTRADA
# - infoExcipients(List): información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
#   un experimento registrado
# PARAMETROS DE SALIDA
# - experiSolubilities(List):  solubilidad de excipientes presentes en cada tipo para un experimento resgistrado.
#   Estructura:
#   - Tipo Excipient(List)
#     - Solubilidad(Array)
def getSolubility(infoExcipients):
    # ¡¡¡REEMPLAZAR POR LA TABLA EN EL SERVIDOR!!!
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

# METODO: se codifican la variables categóricas Via, Recubrimiento y Metodo según One Hot Encoding de un experimento 
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

# METODO: se agregan las variables físico químicas del pricipio activo en un experimento registrado.
# PARAMETROS DE ENTRADA 
# - experimentDF(Data Frame): tabla que contiene información del código del PA valorado en un experimento registrado
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): misma tabla de entrada junto con las variables físico químicas del experimiento
def getPhysicalChemical(experimentDF):
    # ¡¡¡REEMPLAZAR POR LA TABLA EN EL SERVIDOR!!!
    physicalChemical = pd.read_csv('C:/Users/ing-y-soft/Documents/Proyecto/Code/Integracion/tablas/PA_Esp_Eng_Var_Integracion.csv')
    #physicalChemical = pd.read_csv('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\tablas\PA_Esp_Eng_Var_Integracion.csv')
    physicalChemical.codigo = [int(s[1:]) for s in physicalChemical.codigo]
    
    experimentDF = pd.merge(experimentDF,physicalChemical,on='codigo')
    
    erase = ['codigo','nombreEsp','nombreEng','hidroxilos','aldehidos','cetonas','carboxilos','aminas','iminas',
             'amidas','imidas','nitro','nitrilo','hidrazina','haluros','eter','azoNitrogenado']
    experimentDF.drop(erase,axis=1,inplace=True)
    
    return experimentDF

# METODO: para un experimento registrado, del perfil de disolución se seleccionan los tiempos correspondientes al primer 
# porcentaje, al inmediatamente inferior a 85% y al inmediatamente mayor a 85%
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA
# - timesDF(Data Frame): tabla con los tiempos seleccionados del perfil de disolución de un experimento registrado
def getTimes(experimentJSON):    
    names = ['tiempo1','tiempo2','tiempo3']
    times = experimentJSON['tiempos']
    i = 0
    while(times[i]['media'] < 85):
        i += 1
    values = [times[0]['tiempo'],times[i-1]['tiempo'],times[i]['tiempo']]
    timesDF = pd.DataFrame([values],columns=names)
    
    return(timesDF)

# METODO: para un experimento registrado se extrae la información de las variables que no requieren ningún tipo de 
# procesamiento.
# PARAMETROS DE ENTRADA: 
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA:
# - generalVariables(Data Frame): tabla con información de variables que no requieren ningún tipo de procesamiento para un 
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

# METODO: se organizan las variables de la tabla construida con la información de un experimento de acuerdo al orden de 
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