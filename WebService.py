#!/usr/bin/env python
import json

import web
import xml.etree.ElementTree as ET
from ServicesDisolution.Simulation import Prediction
from ServicesDisolution.DataProcessing import Processing

urls = (
    '/simulator', 'simulator',
    '/data_processing', 'dataProcessing',
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

if __name__ == "__main__":
    app.run()
