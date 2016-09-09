# -*- coding: latin-1 -*-
import json
from ServicesDisolution.Retraining import Comparison
from ServicesDisolution.DataProcessing import Processing

# METODO: dado un conjunto de experimentos de entrada, se realiza predicciones con el actual modelo del sistema
# PARAMETROS DE ENTRADA:
# - experimentsJSON(JSON): arreglo de experimentos registrados
# PARAMETROS DE SALIDA:
# - profileEst(JSON): arreglo con los porcentajes de disolución estimados para los experimentos
def makePrediction(experimentJSON):
    # Se procesa la información de los experimentos para que queden organizados en una tabla según la
    # la estructura de estrada requerida por el simulador
    experiments = Processing.organizeExperiment(experimentJSON)
    
    #Se obtiene el actual modelo del sistema
    model = Comparison.getModel()
    
    experiments = experiments.values
    
    estimate = model.predict(experiments)
    
    estimate = estimate[0]
    data = {}
    names = ['media1','media2','media3']
    for i in range(len(names)):
        data[names[i]] = estimate[i]
    
    means_json = json.dumps(data)
    
    return means_json