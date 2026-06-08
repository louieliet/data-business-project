# Plan de Trabajo - Flight Delay Prediction

## 1. Objetivo del Proyecto

Construir y demostrar un modelo de Machine Learning para estimar los minutos de retraso de llegada de un vuelo usando el dataset **2015 Flight Delays & Cancellations** de Kaggle. El proyecto debe incluir analisis exploratorio, seleccion de variables, entrenamiento del modelo, empaquetado, exposicion mediante una API publicada con ngrok y un libro de trabajo externo que consuma el modelo.

## 2. Alcance

### Incluido

- Analisis exploratorio de datos sobre retrasos, aerolineas, rutas, horarios, meses y causas de demora.
- Limpieza de datos y construccion de variables predictivas.
- Entrenamiento y comparacion de modelos de regresion no simple.
- Seleccion de un modelo final no trivial, con mas de 5 variables predictoras.
- Empaquetado del modelo entrenado para inferencia.
- API de prediccion para recibir datos de un vuelo y devolver minutos estimados de retraso.
- Publicacion temporal de la API mediante ngrok.
- Workbook externo que invoque la API usando HTTP.
- Documentacion de plan de trabajo y matriz RACI.

### Fuera de Alcance

- Integracion real con sistemas aeroportuarios.
- Consumo en tiempo real de APIs de clima o ATC.
- Despliegue permanente en cloud.
- Reentrenamiento automatico en produccion.
- Monitoreo de drift en ambiente productivo.

## 3. Entregables

| Entregable | Descripcion | Ubicacion sugerida |
|---|---|---|
| Documento base del caso | Contexto de negocio, datos, metodologia y valor esperado | `docs/Flight Delay Prediction.md` |
| Notebook EDA + ML | Exploracion, features, etiqueta, entrenamiento y evaluacion | `docs/Flight Delay Prediction EDA ML.ipynb` |
| Plan de trabajo | Fases, actividades, entregables y criterios de aceptacion | `docs/Plan de Trabajo - Flight Delay Prediction.md` |
| Matriz RACI | Responsabilidades por actividad | `docs/Matriz RACI - Flight Delay Prediction.md` |
| Codigo de features | Definicion compartida de features y metadata del modelo | `src/flight_delay_features.py` |
| API de inferencia | Servicio FastAPI para predicciones | `src/flight_delay_api.py` |
| Modelo empaquetado | Archivo serializado del modelo entrenado | `models/flight_delay_model.joblib` |
| Notebook ngrok | Levanta la API y publica el endpoint con ngrok | `docs/Flight Delay API Ngrok Demo.ipynb` |
| Workbook externo | Invoca la URL publica de ngrok como consumidor externo | `docs/Flight Delay External Invocation Workbook.ipynb` |

## 4. Fases del Proyecto

### Fase 1: Entendimiento del Negocio

**Objetivo:** Definir el problema, usuarios, impacto esperado y metrica de exito.

**Actividades:**

- Definir el caso de uso: anticipar vuelos con alto riesgo de retraso.
- Identificar usuarios: operaciones, servicio al cliente, planeacion de tripulaciones y data science.
- Definir la etiqueta de negocio: `ARRIVAL_DELAY`, minutos de retraso de llegada.
- Alinear metricas: MAE, RMSE y R2.

**Criterio de aceptacion:** El proyecto explica por que la prediccion genera valor operativo y cuales decisiones soporta.

### Fase 2: Adquisicion y Exploracion de Datos

**Objetivo:** Cargar el dataset y entender calidad, distribuciones y patrones relevantes.

**Actividades:**

- Cargar `flights.csv`, `airlines.csv` y `airports.csv`.
- Revisar tipos de datos, nulos, registros cancelados y distribucion de `ARRIVAL_DELAY`.
- Analizar retrasos por aerolinea, horario, mes, aeropuerto y ruta.
- Identificar posibles variables con riesgo de leakage.

**Criterio de aceptacion:** El notebook muestra un EDA claro, visual y reproducible.

### Fase 3: Feature Engineering

**Objetivo:** Transformar datos crudos en variables utiles para el modelo.

**Actividades:**

- Crear `ARRIVAL_DELAY` como variable objetivo numerica.
- Crear variables temporales: `HOUR_OF_DAY`, `IS_PEAK_HOUR`, `IS_WEEKEND`, `IS_HIGH_SEASON`.
- Crear variables historicas agregadas: `ROUTE_AVG_DELAY`, `AIRLINE_AVG_DELAY`.
- Codificar variables categoricas necesarias.
- Documentar claramente features y etiqueta.

**Criterio de aceptacion:** El modelo usa mas de 5 variables y cada variable tiene justificacion.

### Fase 4: Modelado y Evaluacion

**Objetivo:** Entrenar modelos no triviales y seleccionar el mejor con evidencia.

**Actividades:**

- Separar datos en train/test con estratificacion.
- Evaluar errores con MAE, RMSE, R2 y analisis residual.
- Entrenar Random Forest Regressor y XGBoost Regressor.
- Comparar MAE, RMSE, R2, errores residuales y feature importance.
- Seleccionar modelo final por menor error y mejor interpretabilidad operativa.

**Criterio de aceptacion:** Existe un modelo ganador defendible y se explica por que fue seleccionado.

### Fase 5: Empaquetado del Modelo

**Objetivo:** Guardar el modelo entrenado y su metadata para reutilizarlo fuera del notebook.

**Actividades:**

- Guardar modelo final con `joblib`.
- Guardar lista de features, nombre del target y version del modelo.
- Asegurar que la API use exactamente las mismas features del entrenamiento.

**Criterio de aceptacion:** El modelo puede cargarse desde disco sin volver a entrenar.

### Fase 6: Servicio API y ngrok

**Objetivo:** Exponer el modelo mediante una API invocable desde otro entorno.

**Actividades:**

- Crear endpoint `/health` para validar que la API esta viva.
- Crear endpoint `/predict` para recibir features de un vuelo.
- Levantar FastAPI con `uvicorn`.
- Abrir tunel publico con `pyngrok`.
- Mostrar la URL publica en clase.

**Criterio de aceptacion:** La API responde predicciones desde una URL publica de ngrok.

### Fase 7: Workbook de Invocacion Externa

**Objetivo:** Simular que otra persona consume el modelo publicado.

**Actividades:**

- Crear un notebook separado del entrenamiento.
- Definir `NGROK_URL`.
- Enviar un payload de ejemplo con `requests.post`.
- Mostrar minutos estimados de retraso y nivel de riesgo operativo.

**Criterio de aceptacion:** El workbook externo consume la API sin acceder directamente al modelo local.

## 5. Cronograma Sugerido

| Fase | Actividad | Duracion estimada |
|---|---|---|
| 1 | Entendimiento del negocio | 0.5 dia |
| 2 | EDA | 1 dia |
| 3 | Feature engineering | 0.5 dia |
| 4 | Entrenamiento y evaluacion | 1 dia |
| 5 | Empaquetado | 0.5 dia |
| 6 | API + ngrok | 0.5 dia |
| 7 | Workbook externo y ensayo de demo | 0.5 dia |

## 6. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigacion |
|---|---|---|
| Dataset muy grande para Colab | Alto | Usar muestra representativa con `SAMPLE=True` |
| Variables con leakage | Medio | Documentar variables disponibles antes/despues del vuelo |
| ngrok sin token configurado | Medio | Incluir celda opcional para `NGROK_AUTHTOKEN` |
| Modelo no serializado correctamente | Alto | Guardar modelo, features y metadata juntos |
| API recibe features incompletas | Medio | Validar payload y devolver errores claros |

## 7. Criterios de Exito

- El notebook muestra EDA y entrenamiento de un modelo no trivial.
- El modelo usa mas de 5 variables.
- La etiqueta y las features estan documentadas de forma explicita.
- El modelo se guarda y se carga desde un archivo empaquetado.
- La API local responde correctamente.
- ngrok expone la API con una URL publica.
- Un workbook externo invoca la API y muestra una prediccion.
