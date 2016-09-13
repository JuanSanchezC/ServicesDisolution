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
    namePA = experimentJSON['principioactivovalorado']

    percentage = 0
    size = 0
    for PA in PAs:
        if(int(PA['nombre']) == namePA):
            code = int(PA['nombre'])
            percentage = PA['porcentaje']
            size = PA['tamanoParticula']    

    experimentDF = pd.DataFrame([[code,percentage,size]],columns=['Codigo','Porcentaje','Tamano_Particula'])
    
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
    
    names = ['Aglutinantes','Desintegrantes','Deslizantes','Diluyentes','Lubricantes','Surfactantes','Otros',
             'Tamano_Aglutinantes','Tamano_Desintegrantes','Tamano_Deslizantes','Tamano_Diluyentes','Tamano_Lubricantes',
             'Tamano_Surfactantes','Tamano_Otros','Solubilidad_Aglutinantes','Solubilidad_Desintegrantes',
             'Solubilidad_Deslizantes','Solubilidad_Diluyentes','Solubilidad_Lubricantes','Solubilidad_Surfactantes']
    
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
    solubility = pd.read_excel('C:\Users\ing-y-soft\Documents\Proyecto\Data\Info_Fija\Solubilidad_de_Excipientes_en_Agua.xlsx')
    solubility.Codigo = [int(s[1:]) for s in solubility.Codigo]      
    
    typeExcipients = []    
    for excipient in infoExcipients[:-1]:
        typeExcipients.append(pd.DataFrame(excipient[0],columns=['Codigo']))

    typeSolu = []
    for df in typeExcipients:
        typeSolu.append(pd.merge(df,solubility,on='Codigo'))

    solubilities = []
    for element in typeSolu:
        solubilities.append(np.array(element.Solubilidad_En_Agua))

    return solubilities

# METODO: se codifican la variables categóricas Via, Recubrimiento y Metodo según One Hot Encoding de un experimento 
# registrado
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA
# - categorical(Data Frame): tabla con las variables categoricas codificadas para un experimento registrado
def getOneHotEncoding(experimentJSON):
    names = ['Via_Seca','Via_Humeda','Tableta_Recubierta','Tableta_No_Recubierta','Metodo_HPLC','Metodo_UV','Aparato_Dis1',
             'Aparato_Dis2']
    
    via = experimentJSON['via']
    recubrimiento = experimentJSON['recubrimiento']
    metodo = experimentJSON['metodo']
    aparato = experimentJSON['aparatodisolucion']

    values = []
    if(via == 'Via_Seca'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(recubrimiento == 'Tableta_Recubierta'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(metodo == 'HPLC'):
        values.extend([1,0])
    else:
        values.extend([0,1])
    if(aparato == u'Aparato Disolución 1'):
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
    physicalChemical = pd.read_csv('C:\Users\ing-y-soft\Documents\Proyecto\Data\Info_Fija\PA_Esp_Eng_Var.csv')
    physicalChemical.Codigo = [int(s[1:]) for s in physicalChemical.Codigo]
    
    experimentDF = pd.merge(experimentDF,physicalChemical,on='Codigo')
    
    erase = ['Codigo','Nombre_Esp','Nombre_Eng','Hidroxilos','Aldehidos','Cetonas','Carboxilos','Aminas','Iminas',
             'Amidas','Imidas','Nitro','Nitrilo','Hidrazina','Haluros','Eter','Azo_Nitrogenado']
    experimentDF.drop(erase,axis=1,inplace=True)
    
    return experimentDF

# METODO: para un experimento registrado, del perfil de disolución se seleccionan los tiempos correspondientes al primer 
# porcentaje, al inmediatamente inferior a 85% y al inmediatamente mayor a 85%
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo con un experimento registrado
# PARAMETROS DE SALIDA
# - timesDF(Data Frame): tabla con los tiempos seleccionados del perfil de disolución de un experimento registrado
def getTimes(experimentJSON):    
    names = ['Tiempo_1','Tiempo_2','Tiempo_3']
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
    names = ['humedadgranulado','proporciongranulado','tiempomezcladogranulado','proporcionsolvente','temperaturasecado',
             'tiemposecado','largopromedio','largostd','anchopromedio','anchostd','alturapromedio','alturastd',
             'tiempomezclatotalformula','pesopromedio','pesostd','durezapromedio','durezastd','tamanoparticulamezcla',
             'humedadmezcla','tiempodesintegracionminima','tiempodesintegracionmaxima', 'longitudondamedicion',
             'velocidadrotacional','phmedio','volumen']
    
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
    order = ['humedadgranulado','proporciongranulado','tiempomezcladogranulado','proporcionsolvente','temperaturasecado',
             'tiemposecado','largopromedio','largostd','anchopromedio','anchostd','alturapromedio','alturastd',
             'tiempomezclatotalformula','pesopromedio','pesostd','durezapromedio','durezastd','tamanoparticulamezcla',
             'humedadmezcla','tiempodesintegracionminima','tiempodesintegracionmaxima',
             'Via_Humeda','Via_Seca','Tableta_No_Recubierta','Tableta_Recubierta','longitudondamedicion',
             'velocidadrotacional','phmedio','volumen','Metodo_HPLC','Metodo_UV','Aparato_Dis1','Aparato_Dis2','Porcentaje','Tamano_Particula',
             'Peso_Molecular','LogP','pKa_Basico','Solubilidad_en_Agua','LogS','Area_Superficial_Polar','Carga_Fisiologica',
             'Enlaces_Rotables','Enlaces_Aceptores_de_Hidrogeno','Enlaces_Donadores_de_Hidrogeno','Aglutinantes',
             'Desintegrantes','Deslizantes','Diluyentes','Lubricantes','Otros','Surfactantes','Solubilidad_Aglutinantes',
             'Solubilidad_Desintegrantes','Solubilidad_Deslizantes','Solubilidad_Diluyentes','Solubilidad_Lubricantes',
             'Solubilidad_Surfactantes','Tamano_Aglutinantes','Tamano_Desintegrantes','Tamano_Deslizantes',
             'Tamano_Diluyentes','Tamano_Lubricantes','Tamano_Otros','Tamano_Surfactantes','Tiempo_1','Tiempo_2','Tiempo_3']
    experimentDF = experimentDF.loc[:,order]
    
    return experimentDF