import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.tree import DecisionTreeClassifier

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

X_train = X_train.copy()
X_test = X_test.copy()
kolonlar = ["age", "fare", "sibsp", "parch"]

scaler = StandardScaler()
X_train[kolonlar] = scaler.fit_transform(X_train[kolonlar])
X_test[kolonlar] = scaler.transform(X_test[kolonlar])

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

tahminler = model.predict(X_test)

# print("Accuracy:", accuracy_score(y_test, tahminler))
# print(confusion_matrix(y_test, tahminler))
# print(classification_report(y_test, tahminler))

baseline = np.zeros(len(y_test))
# print("Baseline:", accuracy_score(y_test, baseline))


katsayilar = pd.DataFrame({
    "ozellik": X.columns,
    "katsayi": model.coef_[0]
}).sort_values("katsayi")

# print(katsayilar)

agac = DecisionTreeClassifier(random_state=42)
agac.fit(X_train, y_train)

# print("Train:", agac.score(X_train, y_train))
# print("Test:", agac.score(X_test, y_test))

agac2 = DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=42)
agac2.fit(X_train, y_train)

# print("Train:", agac2.score(X_train, y_train))
# print("Test:", agac2.score(X_test, y_test))

for d in range(1, 15):
    a = DecisionTreeClassifier(max_depth=d, random_state=42)
    a.fit(X_train, y_train)
    print(d, round(a.score(X_train, y_train), 3), round(a.score(X_test, y_test), 3))
