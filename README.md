# Master Data Science KSchool: 8ª Edición
## TFM: Spread entre mercados en el Mercado Eléctrico español

### 1) Introducción

Este trabajo final de master está ambientado en el Mercado eléctrico español de la electricidad. En la presentación adjunta *Propuesta_TFM_Mercado_electrico.pptx* se dan unas pinceladas de los fundamentos básicos de funcionamiento de este mercado, pero para profundizar en ello se puede consultar la web:

http://www.omie.es/inicio/mercados-y-productos/conoces-nuestro-mercado-de-electricidad.

El objetivo de este problema es intentar predecir, previa a la celebración de la subasta diaria (a partir de ahora MD) si el precio del mercado de ajuste intradiario (a partir de ahora MIi, siendo i la subasta intradiaria correspondiente) será inferior o superior al precio del MD, para gestionar una parte de la compra de los clientes en un mercado u otro y conseguir el beneficio del spread entre ambos mercados. 

Los contratos suelen estar referenciados al precio del MD, por tanto, el solo acudir al MD no genera pérdida (tampoco beneficio).

Se trata de un problema de clasificación {0/1} en el que el target RESERVA tomará los siguientes valores:
* Si Precio MI1 > Precio MD -> RESERVA = 0
* Si Precio MI1 < Precio MD -> RESERVA = 1
* Si Precio MI1 == Precio MD:
  * Si Precio MI2 > Precio MD -> RESERVA = 0
  * Si Precio MI2 <= Precio MD -> RESERVA =1

### 2) Descripción de los datos de entrada

Para abordar este problema, con los conocimientos previos sobre el mercado eléctrico, se han considerado las siguientes variables fundamentales inicialmente:

* **FECHA:** día de estudio. Formato %Y-%m-%d
* **PERIODO:** variable categórica que representa la hora del día expresado como la finalización de la hora de estudio. Es decir, el periodo 1 contiene la información del periodo comprendido entre las 00:00 y las 01:00. Toma valores desde 1 a 24.
* **MES:** variable categórica que toma valores del 1 al 12 para considerar el mes al que pertenece el día de estudio.

  No todos los meses son iguales. En electricidad se suele simplificar hablando de Qs (trimestres). Así, el Q1 que comprende los meses de enero, febrero y marzo, se suele caracterizar por alta eolicidad, demanda (invierno), hidraulicidad, mientras que en los meses del Q3, julio, agosto, septiembre, la eolicidad es más baja, desciende la aportación hidráulica, etc. Es por ello que se ha seleccionado el mes como una de las características a tener en cuenta.
* **WD:** variable categórica que toma valores del 1 al 7 para describir el día de la semana. Los festivos nacionales se han considerado tipo 7 (domingo).

  Se ha decidido considerar esta variable porque, tanto el comportamiento de la demanda como de la generación, varía en función del día de la semana. Así, por ejemplo, las plantas de tecnología Cogeneración dejan de producir el fin de semana (6,7) dejando hueco a tecnologías más caras; la demanda es inferior el domingo/festivo que cualquier otro día lo que también impacta en estrategias de paradas/arranques de plantas y los costes que les suponen...
* **PRECIO_MD_ESP:** variable cuantitativa del precio de casación en el mercado diario para un PERIODO, FECHA.
* **ACOPLADO_FR:** variable categórica que representa el estado de la interconexión con Francia en el mercado diario MD. Toma valores:
  * -1: cuando la interconexión con Francia no se ha saturado en el MD y se está exportando generación de España a Francia (Acoplados, mismo precio en ambos países en el MD)
  * 1: cuando la interconexión con Francia no se ha saturado en el MD y se está exportando generación de Francia a España (Acoplados, mismo precio en ambos países en el MD)
  * 0: la interconexión está saturada en el MD. Ambos mercados desacoplados (no hay más hueco en la interconexión en uno de los dos sentidos) y los precios de casación en el MD son distintos.
* **RESERVA_D-1:** Variable categórica que representa si en ese PERIODO, el día anterior, el precio del mercado intradiario fue inferior (1) o superior (0). 

  Se considera en el dataset por pensar que puede haber una cierta tendencia e influencia de lo que ocurre el día anterior en el comportamiento de los agentes de mercado (reflejado en sus ofertas) y que tenga impacto en el resultado del día.
* **P48_EOLICA:** Variable cuantitativa de la producción eólica horaria. En el caso histórico será el programa al final del día (p48), mientras que, a la hora de predecir qué ocurrirá en el mercado (Reserva,target) será la mejor previsión de la misma, publicada por un proveedor particular de la empresa.

  La eólica, desde el cambio regularorio en el que se impuso el impuesto a la generación, oferta a un precio próximo a los 5€/MWh. Recientemente se ha eliminado dicho impuesto, aunque no se ha visto reflejado en el comportamiento del precio del mercado intradiario frente al diario.
* **P48_DEMANDA:** Variable cuantitativa de la demanda horaria. En el caso histórico será el programa al final del día (p48), mientras que, a la hora de predecir qué ocurrirá en el mercado (Reserva,target) será la mejor previsión de la misma.
* **POT_DISP_CARBON:** Variable cuantitativa de la potencia de generación disponible de carbón.
* **P48_CARBON_D-1:** Variable cuantitativa de la producción de carbón horaria que hubo el día anterior (a priori no tengo una previsión de la misma para el día D).
* **NUM_PLANTAS_D-1:** Variable cuantitativa del número de centrales de carbón que estaban arrancadas el día anterior (a priori no tengo una previsión de la misma para el día D).
* **EMB_ANUALES y EMB_HIPERANUALES:** Variable cuantitativa del total peninsular de la cantidad de energía eléctrica que se produciría en su propia central y en todas las centrales situadas aguas abajo, con el vaciado completo de su reserva útil de agua en dicho momento, en el supuesto de que este vaciado se realice sin aportaciones naturales. 

  Los primeros son aquellos cuyo ciclo de llenado y vaciado dura un año mientras que los embalses de régimen hiperanual son aquellos que permiten compensar las variaciones de hidraulicidad en ciclos de más de un año de duración.

En los notebooks de descarga aparecen más detalles sobre las características de cada una de las variables.

### 3) Metodología

La realización de este TFM se divide en 4 fases, coincidentes con el correspondiente nombre de carpeta:

I.	Extracción datos:

Para construir el dataset final (*data_processed/data_processed.csv*), se han utilizado los notebooks que se encuentran en la carpeta Extracción de datos.
Los datos se han conseguido de 3 fuentes distintas consiguiendo 3 conjuntos de datos (almacenados en formato .csv en la carpeta data). Por ello, los notebooks a ejecutar para su extracción son (sin un orden prioritario):
* Carbón_D-1.ipynb -> genera carbón_dia_ant.csv
* Descarga_esios.ipynb -> genera datos_esios.csv
* Embalses.ipynb -> genera embalses_dia.csv

Por último, para unificar los datos en un único dataset y hacer el tratamiento que corresponda (duplicados, NaN, transformaciones, etc), se ha utilizado el notebook *dataset_final.ipynb*. De este notebook se obtiene:
* data/datos_totales.csv: dataset final “crudo”, es decir, con las variables auxiliares utilizadas en el notebook.
* data_processed/data_processed.csv: dataset final, con las features y target del problema.

II.	Exploración datos:

Análisis estadístico y gráfico de las features preseleccionadas para el modelo y del target RESERVA.

El objetivo de este notebook es corroborar la validez de las variables escogidas, ver si son representativas y que no están desvirtuadas ni existen valores anómalos.

Además, estudiar el comportamiento y las relaciones existentes tanto de las características como del target RESERVA para ayudar a comprender los resultados que se obtendrán posteriormente.

De este notebook sale el dataset final definitivo, tras la conversión de alguna de las variables, que se utilizará en la siguiente fase de selección y entrenamiento de los modelos (*data_processed/data_processed_definitivo.csv*)

*NOTA: Para la correcta visualización de este notebook es necesario tener seaborn actualizado a la versión v0.9.0.*

III.	Modelo:

Elección del modelo y sus hiperparámetros. Se distinguen 4 notebooks:

a)	Modelo_Clasificador_1.ipynb: Primer intento, considerando el dataset *data_processed_definitivo.csv*. En este notebook se realizan las siguientes acciones:
* Separación de los datos en los subconjuntos TRAIN/TEST mediante la función train_test_split. Estos subconjuntos se guardan en local en formato *.pkl* para su utilización en los notebooks posteriores. No están subidos a github, por tanto, para su utilización en los notebooks posteriores, habrá que ejecutar este notebook previamente.
* Ajuste de hiperparámetros para los modelos de clasificación K-Neighbors, SVC, Árbol de decisión, Random Forest, XGBoost y Bagging.
* Comparativa de los modelos (para el ajuste de hiperparámetros óptimo) según diferentes métricas.

b)	**Modelo_Clasificador_2.ipynb:** Repetición del ajuste de hiperparámetros y de comparativa de modelos eliminando ACOPLADO_FR como feature de entrada.

En este notebook se hace una comparativa de la métrica con lo obtenido en *Modelo_Clasificador_1.ipynb*, guardado en local en formato *.pkl*. Por tanto, se ha debido procesar previamente este notebook y guardado el modelo en la ruta local.

c)	**Modelo_Clasificador_3.ipynb:** Repetición del ajuste de hiperparámetros y de comparativa de modelos seleccionando 2 años del dataset y con ACOPLADO_FR eliminado como feature de entrada.

La comparativa aquí es con el resultado de *Modelo_Clasificador_2.ipynb*, con la misma operativa descrita en el apartado b).

d)	**Modelo_XGBoost_FSelect:** Seleccionado el modelo XGBoost (con las características y nº de datos de *Modelo_Clasificador_3.ipynb*), análisis de la eliminación de las características de menor importancia. Se utilizan los datos y resultados de *Modelo_Clasificador_3.ipynb*.

Adicionalmente, en esta carpeta se encuentra el notebook **Extra_Modelo_XGBoost_Hiperparam.ipynb**: Este notebook es un comienzo de la línea de trabajo a seguir, intentando mejorar el score de mi modelo. Sin haber realizado un análisis en profundidad de los resultados, el primer ajuste de 2 de sus parámetros **incrementa el accuracy al 76%**.

IV. Resultado

Presentación y análisis de lo conseguido. Realización del frontend para su puesta en producción.

### 4) Resumen de Resultado

Dentro de la carpeta *Resultado*, se deben consultar 3 fuentes:

1- Notebook *XGBoost.ipynb*, en el que se presenta la elección del modelo y el análisis completo de la salida del mismo. 

2- Notebook *Comparativa_modelos.ipynb*, que muestra el resumen comparativo de los resultados que se obtuvieron en las diferentes fases de selección.

3- Dos dashboard de Tableau (necesario el programa para su visualización):
* *Principales_features.twbx*: visualización de lo más destacable del análisis realizado sobre las features más importantes para el modelo. Dispone de un filtro de rango de fecha para modificar el periodo de visualización en todos los gráficos simultáneamente y obtener mejores conclusiones.
* *Estadística_resultados.twbx*: visualización de los principales resultados obtenidos.

El modelo clasificará {1/0} con una probabilidad, y la actuación será:

* Cuando la predicción es **RESERVA=1**, se considera fiable a partir de valores de **probabilidad entre el 60-70%**.

* Cuando la predicción es **RESERVA=0**, exigiré que la **probabilidad** con la que lo predice sea **>=65%**.

El modelo escogido, ya entrenado, se ha guardado en la carpeta *Resultado/data&model/* al igual que los conjuntos de datos train-test que se usaron para el entrenamiento y validación del mismo.

### 5) Descripción de usuario del frontend

La utilización del modelo en producción se hará ejecutando el notebook *Ejecución_modelo.ipynb*, dentro de la carpeta *Resultado*.

El único requisito previo es rellenar la plantilla Excel que se encuentra en *Resultados/data&model/Plantilla.xlsx* con los datos internos no automatizables. 

La salida es un dataframe con la predicción de la clasificación y la probabilidad de la misma, que se guardará en la carpeta *Resultados/data&model/resultado/resultado_aaaa-mm-dd.csv* para un posterior seguimiento del acierto del mismo.

También se guarda, en la misma ruta, un gráfico resumen de la salida, con el mismo nombre en formato *.png*.

Dejo subido a github un ejemplo (de datos ficticios) para visualizar como quedaría rellena la plantilla y la salida del resultado.

Se hará un mantenimiento del modelo, realimentándolo con nuevos datos al menos cada 14 días y manteniendo el tamaño del set de entrenamiento (móvil). El modelo debe aprender rápido de los cambios que se produzcan en el mercado eléctrico.


Por último, además de las referencias nombradas en los propios notebooks, destacar entre la bibliografia:
*"Hands-On Machine Learning with Scikit-Learn & TensorFlow"*
