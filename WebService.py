#!/usr/bin/env python
import json

import web
import xml.etree.ElementTree as ET
from ServicesDisolution.Simulation import Prediction
from ServicesDisolution.DataProcessing import Processing
from ServicesDisolution.Optimization import OptimizationExperiment

urls = (
    '/simulator', 'simulator',
    '/data_processing', 'dataProcessing',
    '/optimization', 'optimization',
)

app = web.application(urls, globals())

class simulator:
    def POST(self):
        web.header('Content-Type', 'application/json')
        requestJSON = web.data()
        json_load = ""
        try:
            json_load = json.loads(requestJSON)
        except ValueError:
            print "Datos enviados no son un JSON Valido"

        return Prediction.makePrediction(json_load)

class dataProcessing:
    def POST(self):
        web.header('Content-Type', 'application/json')
        requestJSON = web.data()
        json_load = ""
        try:
            json_load = json.loads(requestJSON)
        except ValueError:
            print "Datos enviados no son un JSON Valido"
        
        return Processing.getInputExperiment(json_load)

class optimization:
    
    def POST(self):
        print('llegooo')
        web.header('Content-Type', 'application/json')
        requestJSON = web.data()
        json_load = ""
        try:
            json_load = json.loads(requestJSON)
        except ValueError:
            print "Datos enviados no son un JSON Valido"
        
        return OptimizationExperiment.makeOptimization(json_load)

if __name__ == "__main__":
    app.run()
