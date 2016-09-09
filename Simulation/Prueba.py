from ServicesDisolution.Simulation import Prediction
import json

fin = open('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\JSONSimulacionArray.json')
fJSON = json.load(fin)
fin.close()

estimate = Prediction.makePrediction(fJSON)

print estimate