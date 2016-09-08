# -*- coding: latin-1 -*-
import pandas as pd
import numpy as np

# Método: para todos los experimentos registrados, se seleccionan y organizan sus variables según la estructura de entrada 
# del simulador
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con la información organizada según la estructura de entrada del simulador para todos los
#   experimentos registrados
def organizeExperiment(experimentJSON):
    
    # Se adicionan columnas para porcentaje y TP del PA valorado en la formulación
    experimentDF = getInfoPA(experimentJSON)
    
    # Se adicionan columnas para los porcentajes, tamaño de partícula y solubilidad de cada tipo de excipientes en la 
    # formulación
    infoExcipient = getInfoExcipient(experimentJSON)
    
    # Se codifican las variables categóricas Via, Recubrimiento y Metodo
    categorical = getOneHotEncoding(experimentJSON)
    
    # Se obtienen las variables físico químicas del experimento en cuestión
    experimentDF = getPhysicalChemical(experimentDF)
    
    # Se seleccionan los 3 tiempos de la entrada construida y los pocentajes de disolución adecuados para el perfil de 
    # disolucion de referencia
    timesDF = getTimes(experimentJSON)
    
    generalVariables = getInfoGeneral(experimentJSON)
    
    experimentDF = pd.concat([experimentDF,infoExcipient,categorical,timesDF,generalVariables],axis=1)
    
    # Se ordenan las variables para que esten en el orden que las necesita el simulador
    experimentDF = organizeVariables(experimentDF)
    
    return (experimentDF)

# METODO: para la información registrada para un conjunto de experimento, se crean variables para el código, porcentaje del 
# principio activo valorado y para su correspondiente tamaño de partícula de cada experimento.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados.
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla construida con la información de todos los experimentos de acuerdo a la estructura de 
#   entrada del simulador
def getInfoPA(experimentsJSON):
    experiments = experimentsJSON['experimentos']
    experimentsDF = pd.DataFrame(columns=['Codigo','Porcentaje','Tamano_Particula'])
    
    for i in range(len(experiments)):
        PAs = experiments[i]['principiosActivos']
        namePA = experiments[i]['principioactivovalorado']

        percentage = 0
        size = 0
        for PA in PAs:
            if(int(PA['nombre']) == namePA):
                code = int(PA['nombre'])
                percentage = PA['porcentaje']
                size = PA['tamanoParticula']    
        
        experimentsDF = experimentsDF.append(pd.Series([code,percentage,size],index=experimentsDF.columns),ignore_index=True)
    
    return experimentsDF

# METODO: para la información registrada para un conjunto de experimento, se crean las variables que indican el porcentaje, 
# el tamaño de partícula y la solubilidad de cada tipo de excipiente presente en la formulación de cada experimento.
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados.
# - experimentDF(Data Frame): tabla construida con la información de todos los experimentos de acuerdo a la estructura de 
#   entrada del simulador
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): misma variable de entrada junto con las variables que indican el porcentaje, el tamaño de 
#   partícula y la solubilidad de cada tipo de excipiente presentes en cada formulación
def getInfoExcipient(experimentJSON):
    # Se obtiene la inforamación, por tipo, de cada excipiente, su porcentaje y su tamaño de partícula
    infoExperiExci = getMultiInputs(experimentJSON)
    
    # Se asocia por tipo la solubilidad para cada excipiente presente en una formulación
    experiSolubilities = getSolubility(infoExperiExci)
    
    names = ['Aglutinantes','Desintegrantes','Deslizantes','Diluyentes','Lubricantes','Surfactantes','Otros',
             'Tamano_Aglutinantes','Tamano_Desintegrantes','Tamano_Deslizantes','Tamano_Diluyentes','Tamano_Lubricantes',
             'Tamano_Surfactantes','Tamano_Otros','Solubilidad_Aglutinantes','Solubilidad_Desintegrantes',
             'Solubilidad_Deslizantes','Solubilidad_Diluyentes','Solubilidad_Lubricantes','Solubilidad_Surfactantes']
    infoExcipients = pd.DataFrame(columns=names)
    
    for experiment, solubilities in zip(infoExperiExci, experiSolubilities):
        
        percentageExcipients = []    
        sizeExcipients = []    
        for excipient in experiment:
            percentageExcipients.append(excipient[1].sum())
            sizeExcipients.append(((excipient[1]*excipient[2])/excipient[1].sum()).sum())

        soluExcipients = []
        for i in range(len(solubilities)):
            iSolubility = ((experiment[i][1]*solubilities[i])/experiment[i][1].sum()).sum()
            soluExcipients.append(iSolubility)
        
        info = []
        info.extend(percentageExcipients)
        info.extend(sizeExcipients)
        info.extend(soluExcipients)
        
        infoExcipients = infoExcipients.append(pd.Series(info,index=names),ignore_index=True)
    
    return infoExcipients

# METODO: Se extrae la información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
# cada experimento registrado
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados.
# PARAMETROS DE SALIDA
# - infoExcipient(List): información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
#   cada experimento registrado
#   Estructrura:
#   - Experimento
#     - Tipo Excipiente
#       - Codigo
#       - Porcentaje
#       - Tamaño Particula
def getMultiInputs(experimentsJSON):
    experiments = experimentsJSON['experimentos']
    excipients = ['aglutinantes','desintegrantes','deslizantes','diluyentes','lubricantes','surfactantes','otros']
    
    infoExperiExci = []
    for experiment in experiments:
        
        infoExcipients = []
        for excipient in excipients:
            iExcipient = experiment[excipient]

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
        
        infoExperiExci.append(infoExcipients)    
    
    return infoExperiExci

# METODO: se extrae la información de solubilidad de excipientes presentes en cada tipo para todos los experimentos 
# resgistrados.
# PARAMETROS DE ENTRADA
# - infoExcipients(List): información de excipientes presentes en cada tipo(códigos, porcentajes, tamaños de partículas) para
#   cada experimento registrado
# PARAMETROS DE SALIDA
# - experiSolubilities(List):  solubilidad de excipientes presentes en cada tipo para todos los experimentos resgistrados.
#   Estructura:
#   - Experiment(List)
#     - Tipo Excipient(List)
#       - Solubilidad(Array)
def getSolubility(infoExperiExci):
    solubility = pd.read_excel('C:\Users\ing-y-soft\Documents\Proyecto\Data\Info_Fija\Solubilidad_de_Excipientes_en_Agua.xlsx')
    solubility.Codigo = [int(s[1:]) for s in solubility.Codigo]
    
    experiSolubilities = []
    for experiment in infoExperiExci:        
    
        typeExcipients = []    
        for excipient in experiment[:-1]:
            typeExcipients.append(pd.DataFrame(excipient[0],columns=['Codigo']))

        typeSolu = []
        for df in typeExcipients:
            typeSolu.append(pd.merge(df,solubility,on='Codigo'))

        solubilities = []
        for element in typeSolu:
            solubilities.append(np.array(element.Solubilidad_En_Agua))
        
        experiSolubilities.append(solubilities)
    
    return experiSolubilities

# METODO: se codifican la variables categóricas Via, Recubrimiento y Metodo según One Hot Encoding 
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados
# PARAMETROS DE SALIDA
# - categorical(Data Frame): tabla con las variables categoricas codificadas de cada experimento
def getOneHotEncoding(experimentJSON):
    experiments = experimentJSON['experimentos']
    names = ['Via_Seca','Via_Humeda','Tableta_Recubierta','Tableta_No_Recubierta','Metodo_HPLC','Metodo_UV','Aparato_Dis1',
             'Aparato_Dis2']
    categorical = pd.DataFrame(columns=names)
    
    for experiment in experiments:        
        via = experiment['via']
        recubrimiento = experiment['recubrimiento']
        metodo = experiment['metodo']
        aparato = experiment['aparatodisolucion']

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
        
        categorical = categorical.append(pd.Series(values,index=names),ignore_index=True)
    
    return categorical

# METODO: se agregan las variables físico químicas del pricipio activo valorado en cada experimento.
# PARAMETROS DE ENTRADA 
# - experimentDF(Data Frame): tabla construida con la información de todos los experimentos de acuerdo a la estructura de 
#   entrada del simulador
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

# METODO: para cada experimento, del perfil de disolución se seleccionan los tiempos correspondientes al primer porcentaje, 
# al inmediatamente inferior a 85% y al inmediatamente mayor a 85%
# PARAMETROS DE ENTRADA
# - experimentJSON(JSON): arreglo de experimentos registrados
# PARAMETROS DE SALIDA
# - timesDF(Data Frame): tablas con los tiempos seleccionados del perfil de disolución de cada experimento
def getTimes(experimentJSON):
    experiments = experimentJSON['experimentos']
    
    names = ['Tiempo_1','Tiempo_2','Tiempo_3']
    timesDF = pd.DataFrame(columns=names)
    
    for experiment in experiments:
        times = experiment['tiempos']
        i = 0
        while(times[i]['media'] < 85):
            i += 1
        values = [times[0]['tiempo'],times[i-1]['tiempo'],times[i]['tiempo']]
        timesDF = timesDF.append(pd.Series(values,index=timesDF.columns),ignore_index=True)
    
    return(timesDF)

# METODO: para cada experimento registrado se extrae la información de las variables que no requieren ningún tipo de 
# procesamiento.
# PARAMETROS DE ENTRADA: 
# - experimentJSON(JSON): arreglo de experimentos registrados
# PARAMETROS DE SALIDA:
# - generalVariables(Data Frame): tabla con información de variables que no requieren ningún tipo de procesamiento para cada 
#   experimento registrado
def getInfoGeneral(experimentJSON):
    experiments = experimentJSON['experimentos']
    
    names = ['humedadgranulado','proporciongranulado','tiempomezcladogranulado','proporcionsolvente','temperaturasecado',
             'tiemposecado','largopromedio','largostd','anchopromedio','anchostd','alturapromedio','alturastd',
             'tiempomezclatotalformula','pesopromedio','pesostd','durezapromedio','durezastd','tamanoparticulamezcla',
             'humedadmezcla','tiempodesintegracionminima','tiempodesintegracionmaxima', 'longitudondamedicion',
             'velocidadrotacional','phmedio','volumen']
    generalVariables = pd.DataFrame(columns=names)
    
    for experiment in experiments:
        variables = []
        for var in names:
            variables.append(experiment[var])            
        generalVariables = generalVariables.append(pd.Series(variables,index=names),ignore_index=True)
    return generalVariables

# METODO: se organizan las variables de la tabla construida con la información de los experimentos de acuerdo al orden de 
# entrada del simulador
# PARAMETROS DE ENTRADA
# - experimentDF(Data Frame): tabla con los valores de todos los experimentos registrados
# PARAMETROS DE SALIDA
# - experimentDF(Data Frame): tabla con las variables organizadas
def organizeVariables(experimentDF):
    order = ['humedadgranulado','proporciongranulado','tiempomezcladogranulado','proporcionsolvente','temperaturasecado',
             'tiemposecado','largopromedio','largostd','anchopromedio','anchostd','alturapromedio','alturastd',
             'tiempomezclatotalformula','pesopromedio','pesostd','durezapromedio','durezastd','tamanoparticulamezcla',
             'humedadmezcla','tiempodesintegracionminima','tiempodesintegracionmaxima','Via_Humeda','Via_Seca','Tableta_No_Recubierta',
             'Tableta_Recubierta','longitudondamedicion','velocidadrotacional','phmedio','volumen','Metodo_HPLC','Metodo_UV',
             'Aparato_Dis1','Aparato_Dis2','Porcentaje','Tamano_Particula','Peso_Molecular','LogP','pKa_Basico','Solubilidad_en_Agua',
             'LogS','Area_Superficial_Polar','Carga_Fisiologica','Enlaces_Rotables','Enlaces_Aceptores_de_Hidrogeno',
             'Enlaces_Donadores_de_Hidrogeno','Aglutinantes','Desintegrantes','Deslizantes','Diluyente','Lubricantes','Otros',
             'Surfactantes','Solubilidad_Aglutinantes','Solubilidad_Desintegrantes','Solubilidad_Deslizantes','Solubilidad_Diluyentes',
             'Solubilidad_Lubricantes','Solubilidad_Surfactantes','Tamano_Aglutinantes','Tamano_Desintegrantes','Tamano_Deslizantes',
             'Tamano_Diluyentes','Tamano_Lubricantes','Tamano_Otros','Tamano_Surfactantes','Tiempo_1','Tiempo_2','Tiempo_3']
    experimentDF = experimentDF.loc[:,order]
    
    return experimentDF