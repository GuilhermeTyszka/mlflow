import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
import warnings

warnings.filterwarnings("ignore")

# Carregar o dataset
df = pd.read_csv('../data/diamonds.csv', index_col=0)

X = df.drop(columns=['price'])
y = df['price']

# Dividir o dataset em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pré-processamento: OneHotEncoder para variáveis categóricas e StandardScaler para variáveis numéricas
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), X.select_dtypes(include=['int64', 'float64']).columns),
        ('cat', OneHotEncoder(drop='first'), X.select_dtypes(include=['category']).columns)
    ])

# Modelos e parametros de treino
param_grid = [
    {
        'model': [Ridge(random_state=42)],
        'model__alpha': [0.1, 1.0, 10.0]
    },
    {
        'model': [Lasso(random_state=42)],
        'model__alpha': [0.1, 1.0, 10.0]
    },
    {
        'model': [RandomForestRegressor(random_state=42)],
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [None, 5, 10, 20]
    }
]

# Realizar GridSearchCV para encontrar os melhores hiperparâmetros
grid_search = GridSearchCV(Pipeline([('preprocessor', preprocessor), ('model', Ridge())]),
                           param_grid, cv=3, n_jobs=-1)

with mlflow.start_run():
    grid_search.fit(X_train, y_train)
    
    # Fazer previsões com o melhor modelo encontrado
    best_model = grid_search.best_estimator_
    predictions = best_model.predict(X_test)

    # Calcular métricas de desempenho
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions, squared=False)
    r2 = r2_score(y_test, predictions)
    
    # Logar os hiperparâmetros, o modelo e as métricas com MLflow
    mlflow.log_params(grid_search.best_params_)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    mlflow.sklearn.log_model(best_model, "model")

print(f'Melhores Hiperparâmetros: {grid_search.best_params_}')
print(f'MAE: {mae}')
print(f'RMSE: {rmse}')
print(f'R²: {r2}')