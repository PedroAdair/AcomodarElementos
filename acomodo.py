import binpacking
from pymongo import MongoClient
import yaml
import json
import numpy as np

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def coneccionDB(mongo_uri:str,database_name:str,collection_name:str):
    '''Permite realizar una coneccion a una colecccion en base de datos'''
    
    try:
        client = MongoClient(mongo_uri)
        db = client[database_name]
        collection = db[collection_name]
        print(f'coneccion exitosa a la coleccion: {database_name}.{collection_name}')
    except Exception as e:
        print(e)
    return collection 





def initialPopulation(tipo:str):
    collection = coneccionDB(config['connection_url'],config["db_nameChilac"], config['db_cerdos'])
    consulta = collection.aggregate([
        {
            '$match': {'tipo': {'$in': tipo}}
        },
        {
                '$group': {
                '_id': '$lote',
                'count': { '$sum': 1 }
                }
            }
        ])
    poblacion0 = {diccionario['_id']: diccionario['count'] for diccionario in list(consulta)}
    return poblacion0



def Evaluacion(propuesta:list,
               cap_maxima_cont: int, 
               uso_min:float, 
               uso_max:float, 
               dif_max: float):
    """
    Recibe una propuesta de acomodo y con base a los criterios de proporcion se acepta o se modifica.
    """
    registro_cambios = []
    #1. Se evalua si los elementos pueden caben en su respectivo contenedor, 
    for conteiner in propuesta:
        if np.sum(list(conteiner.values())) > cap_maxima_cont:
            print(f'El contenedor {conteiner} excede la capacidad maxima de asignacion de espacios')
            registro_cambios.append((conteiner,'Exceso'))
        elif np.sum(list(conteiner.values())) < cap_maxima_cont*uso_min:
            print(f'El contenedor {conteiner} se encuentra pobremente asignado de asignacion de espacios')
            registro_cambios.append((conteiner,'carencia'))
    
    return registro_cambios

#####ajustes a la poblacion
def dividir_y_reemplazar(diccionario, llave):
    # Obtener el valor correspondiente a la llave
    valor = diccionario.pop(llave)
    
    # Dividir el valor en dos elementos lo más similares posible
    mitad = valor // 2
    nuevo_valor_1 = mitad + valor % 2
    nuevo_valor_2 = mitad

    # Crear nuevas llaves con el formato deseado
    nueva_llave_1 = llave + '_1'
    nueva_llave_2 = llave + '_2'

    # Añadir los nuevos pares llave-valor al diccionario
    diccionario[nueva_llave_1] = nuevo_valor_1
    diccionario[nueva_llave_2] = nuevo_valor_2


def carencia_asinamientoCerdos(propuesta:list, poblacion:dict):
    for observacion in propuesta:
        if observacion[1]=='Exceso':
            dict_inicial = observacion[0]
            lote = max(dict_inicial.items(), key=lambda x: x[1])[0]
            dividir_y_reemplazar(poblacion,lote)
    
# def GeneratePopulation():
#     1
b = initialPopulation(['F2']) #{ 'a': 10, 'b': 10, 'c':11, 'd':1, 'e': 2,'f':7 }

print(b)
#solucion al problema de los almacenamientos
bins = binpacking.to_constant_bin_number(b,3)
print(bins)

a = Evaluacion(bins,23,.90,.80,.15)
carencia_asinamientoCerdos(a,b)
print(b)

print('segundaGeneracion')
print('----------------------------------------------------------')
bins = binpacking.to_constant_bin_number(b,3)
print(bins)
a = Evaluacion(bins,23,.90,.80,.15)
# print(b,'\n',bins)