# Face mask advisor

Para esta aplicación se utilizó la arquitectura [GoogLeNet](https://arxiv.org/abs/1409.4842v1) modificada para que genere una salida binaria mostrando la probabilidad de que se use bien el cubrebocas.

Para el dataset utilizado fue [MaskedFace-Net](https://github.com/cabani/MaskedFace-Net). De este dataset solamente utilizamos 4,000 muestras (2,000 de un uso correcto y 2,000 de un uso incorrecto) para entrenar la red. El optimizador que se utilizo fue *Stochastic Gradient Descent* con un learning-rate de 0.001, un momentum de 0.9 y un weight-decay de 0.0005 usando batches de 64 muestras.

## Instalación y ejecución
Se necesita instalar previamente *python 3* y *virtualvenv*
Para instalarlo se ejecutan los siguientes comandos: 
```sh
pip install virtualenv
python -m venv venv
./venv/Scripts/activate		# Para Windows
source ./venv/bin/activate	# Para Linux
pip install -r requirements.txt
```
Para ejecutarlo se utilizan las siguientes instrucciones:
```sh
./venv/Scripts/activate			# Para Windows
source ./venv/bin/activate		# Para Linux
flask run 
```