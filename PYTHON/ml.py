import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
 
 
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
df = pd.read_csv(url)
 
df = df.drop("deck", axis=1)
df["age"] = df["age"].fillna(df["age"].median())
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
 
df = df.drop(["alive", "class", "embark_town", "who", "adult_male", "alone"], axis=1)
 
df["sex"] = (df["sex"] == "male").astype(int)
df = pd.get_dummies(df, columns=["embarked"], dtype=int)
 
X = df.drop("survived", axis=1)
y = df["survived"]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
 
 
# cross validation
 
model = DecisionTreeClassifier(max_depth=5, random_state=42)
skorlar = cross_val_score(model, X, y, cv=5)
 
print(skorlar)
print(skorlar.mean())
print(skorlar.std())
 
 
for d in range(1, 11):
    m = DecisionTreeClassifier(max_depth=d, random_state=42)
    s = cross_val_score(m, X, y, cv=5)
    print(d, round(s.mean(), 3), round(s.std(), 3))
 
 
# model karsilastirma
 
log = LogisticRegression(max_iter=1000)
log.fit(X_train, y_train)
print("log", log.score(X_train, y_train), log.score(X_test, y_test))
 
agac = DecisionTreeClassifier(max_depth=5, random_state=42)
agac.fit(X_train, y_train)
print("agac", agac.score(X_train, y_train), agac.score(X_test, y_test))
 
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
print("rf", rf.score(X_train, y_train), rf.score(X_test, y_test))
 
gb = GradientBoostingClassifier(random_state=42)
gb.fit(X_train, y_train)
print("gb", gb.score(X_train, y_train), gb.score(X_test, y_test))
 
 
onem = pd.DataFrame({
    "ozellik": X_train.columns,
    "onem": rf.feature_importances_
}).sort_values("onem", ascending=False)
 
print(onem)
 
 
# hiperparametre arama
 
parametreler = {
    "n_estimators": [50, 100, 200],
    "max_depth": [3, 5, 7, None],
    "min_samples_leaf": [1, 5, 10]
}
 
arama = GridSearchCV(RandomForestClassifier(random_state=42), parametreler, cv=5, n_jobs=-1)
arama.fit(X_train, y_train)
 
print(arama.best_params_)
print(arama.best_score_)
print(arama.score(X_test, y_test))
 
 
# pipeline
 
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000))
])
 
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
 
skorlar = cross_val_score(pipe, X, y, cv=5)
print(skorlar.mean())
 
arama2 = GridSearchCV(pipe, {"model__C": [0.01, 0.1, 1, 10]}, cv=5)
arama2.fit(X_train, y_train)
print(arama2.best_params_)
 
 
# kmeans ve pca
 
scaler = StandardScaler()
X_olcekli = scaler.fit_transform(X)
 
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kumeler = kmeans.fit_predict(X_olcekli)
 
sonuc = pd.DataFrame({"kume": kumeler, "survived": y})
print(sonuc.groupby("kume")["survived"].agg(["count", "mean"]))
 
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_olcekli)
 
print(pca.explained_variance_ratio_)
print(pca.explained_variance_ratio_.sum())