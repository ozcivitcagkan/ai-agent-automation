import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score
)

url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"

df = pd.read_csv(url)

# print(df.head())

df = df.drop(
    [
        "deck",
        "alive",
        "class",
        "embark_town",
        "who",
        "adult_male",
        "alone"
    ],
    axis=1
)

df["age"] = df["age"].fillna(df["age"].median())

df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])

df["sex"] = df["sex"].map({"male": 0, "female":1})

df = pd.get_dummies(df, columns=["embarked"], dtype=int)

X = df.drop("survived", axis=1)

y = df["survived"]

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)

sayisal_kolonlar = ["age", "fare", "sibsp", "parch"]

scaler = StandardScaler()

x_train[sayisal_kolonlar] = scaler.fit_transform(x_train[sayisal_kolonlar])

x_test[sayisal_kolonlar] = scaler.transform(x_test[sayisal_kolonlar])

model = LogisticRegression(max_iter=1000)
model.fit(x_train, y_train)

tahminler = model.predict(x_test)
# print(tahminler[:10])

olasiliklar = model.predict_proba(x_test)
# print(olasiliklar[:5])

olasilik_1 = model.predict_proba(x_test)[:,1]
# print(olasilik_1[:10])

accuracy = accuracy_score(y_test, tahminler)
# print(accuracy)

cm = confusion_matrix(y_test, tahminler)
# print(cm)

print(
    classification_report(
        y_test,
        tahminler
    )
)