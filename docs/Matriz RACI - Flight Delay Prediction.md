# Matriz RACI - Flight Delay Prediction

## Roles

| Rol | Descripcion |
|---|---|
| Project Owner | Responsable de que el proyecto responda al objetivo de negocio y a los requisitos de la clase. |
| Business Stakeholder | Usuario de negocio que valida que las predicciones sean accionables para operaciones aeroportuarias. |
| Data Scientist | Responsable del EDA, feature engineering, entrenamiento, evaluacion y explicacion del modelo. |
| Data Engineer | Responsable de carga, calidad, estructura del dataset y preparacion de datos reutilizable. |
| ML Engineer | Responsable de empaquetar el modelo, exponerlo en API y conectarlo con ngrok. |
| QA / Reviewer | Responsable de revisar reproducibilidad, consistencia de resultados y claridad de la demo. |
| Instructor | Persona informada sobre avance y resultado final de la entrega academica. |

## Leyenda

| Letra | Significado |
|---|---|
| R | Responsible: ejecuta la actividad. |
| A | Accountable: aprueba y responde por el resultado. |
| C | Consulted: aporta criterio o validacion. |
| I | Informed: se mantiene informado del avance. |

## Matriz

| Actividad | Project Owner | Business Stakeholder | Data Scientist | Data Engineer | ML Engineer | QA / Reviewer | Instructor |
|---|---|---|---|---|---|---|---|
| Definir problema de negocio y objetivo | A | C | R | I | I | C | I |
| Definir variable objetivo `IS_DELAYED` | A | C | R | C | I | C | I |
| Identificar fuentes de datos | A | C | R | R | I | I | I |
| Cargar `flights.csv`, `airlines.csv`, `airports.csv` | I | I | C | R | I | C | I |
| Revisar calidad de datos y nulos | I | C | R | R | I | C | I |
| Ejecutar EDA visual | I | C | R | C | I | C | I |
| Crear features del modelo | I | C | R | C | I | C | I |
| Revisar riesgo de leakage | A | C | R | C | C | R | I |
| Separar train/test | I | I | R | C | I | C | I |
| Entrenar modelos candidatos | I | I | R | I | C | C | I |
| Comparar metricas y seleccionar modelo | A | C | R | I | C | C | I |
| Definir threshold operativo | A | C | R | I | C | C | I |
| Guardar modelo y metadata con `joblib` | I | I | C | I | R | C | I |
| Crear API de inferencia | I | I | C | I | R | C | I |
| Probar endpoint `/health` | I | I | I | I | R | R | I |
| Probar endpoint `/predict` | I | C | C | I | R | R | I |
| Exponer API con ngrok | I | I | I | I | R | C | I |
| Crear workbook consumidor externo | I | C | C | I | R | R | I |
| Preparar documentacion final | R | C | C | I | C | C | I |
| Presentar demo final | A | I | R | I | R | C | I |

## Responsabilidades Clave por Entregable

| Entregable | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| EDA + ML notebook | Data Scientist | Project Owner | Data Engineer, QA / Reviewer | Instructor |
| Plan de trabajo | Project Owner | Project Owner | Data Scientist, QA / Reviewer | Instructor |
| Matriz RACI | Project Owner | Project Owner | Data Scientist, ML Engineer | Instructor |
| Modelo empaquetado | ML Engineer | Project Owner | Data Scientist, QA / Reviewer | Instructor |
| API con FastAPI | ML Engineer | Project Owner | Data Scientist, QA / Reviewer | Instructor |
| Demo ngrok | ML Engineer | Project Owner | Data Scientist, QA / Reviewer | Instructor |
| Workbook externo | ML Engineer | Project Owner | Business Stakeholder, QA / Reviewer | Instructor |

## Criterios de Revision

- Cada actividad tiene exactamente un responsable final de aprobacion.
- Las tareas tecnicas principales tienen un responsable ejecutor claro.
- El Data Scientist conserva propiedad sobre la validez del modelo.
- El ML Engineer conserva propiedad sobre empaquetado, API e invocacion.
- El Project Owner mantiene la alineacion con la entrega academica y el valor de negocio.
