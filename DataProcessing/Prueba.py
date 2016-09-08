import json
from ServicesDisolution.DataProcessing.Processing import organizeExperiment

fin = open('C:\Users\ing-y-soft\Documents\Proyecto\Code\Integracion\JSONSimulacionArray.json')
fJSON = json.load(fin)
fin.close()

expes = organizeExperiment(fJSON)
    
print(expes)