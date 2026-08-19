import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
import matplotlib.pyplot as plt


np.random.seed(42)

m2 = np.random.randint(40, 251, 200)

oda = np.random.randint(1, 6, 200)

yas = np.random.randint(0, 51, 200)

mahalleler = ["Merkez", "Kadikoy", "Besiktas", "Uskudar", "Bakirkoy"]

mahalle = np.random.choice(mahalleler, 200)

durumlar = ["Kotu", "Orta", "Iyi", "Cok iyi", "Mukemmel"]

durum = np.random.choice(durumlar, 200)

balkonlar = ["Var", "Yok"]

balkon = np.random.choice(balkonlar, 200)

# print(balkon[:10])

fiyat = (

    m2 * 35 
    + oda * 250
    - yas * 30
    + np.random.normal(0, 500, 200)

)


df = pd.DataFrame({
    "m2": m2,
    "oda": oda,
    "yas": yas,
    "mahalle": mahalle,
    "durum": durum,
    "balkon": balkon,
    "fiyat": fiyat
})

# print(df.head())
# print(df.shape)
# print(df.info())


durum_sirasi = {
    "Kotu": 1,
    "Orta": 2,
    "Iyi": 3,
    "Cok iyi": 4,
    "Mukemmel": 5
}

df["durum_kod"] = df["durum"].map(durum_sirasi)
df["balkon_kod"] = (df["balkon"] == "Var").astype(int)


df_encoded = pd.get_dummies(df, columns=["mahalle"], dtype=int)

# print(df.shape)
# print(df_encoded.shape)

df_encoded_drop = pd.get_dummies(
    df,
    columns=["mahalle"],
    drop_first=True
)


# print(df_encoded_drop.shape)


df["m2_oda"] = df["m2"] / df["oda"]

df_encoded["m2_oda"] = df_encoded["m2"] / df_encoded["oda"]

# print(df[["m2", "oda", "m2_oda"]].head(10))


df_encoded["fiyat_log"] = np.log1p(df_encoded["fiyat"])


# print(df_encoded[["fiyat", "fiyat_log"]].describe())


df_encoded["m2_yas"] = df_encoded["m2"] / (df_encoded["yas"] + 1)

# print(df_encoded[["m2", "yas", "m2_yas"]].head(10))

# print(df_encoded[["m2", "yas", "oda", "m2_oda", "m2_yas", "fiyat"]].corr())

# plt.figure(figsize=(10, 6))

# sns.heatmap(
#     df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas", "fiyat"]].corr(),
#     annot=True,
#     cmap="coolwarm"
# )

# plt.show()

# scaler = StandardScaler()

# scaler.fit(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]])

# print(scaler.mean_)
# print(scaler.scale_)

# scaled_data = scaler.transform(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]])

# print(scaled_data[:5])

# scaled_df = pd.DataFrame(scaled_data,columns=["m2", "oda", "yas", "m2_oda", "m2_yas"])

# print(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]].head())
# print(scaled_df.head())

# print(scaled_df.describe())

# df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]] = scaled_df


df_encoded = df_encoded.drop(["durum", "balkon"], axis=1)


# print(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]].head())

# print(df_encoded.columns)
# print(df_encoded.head())

X = df_encoded.drop(["fiyat", "fiyat_log"], axis=1)
y = df_encoded["fiyat"]

# print(X.shape)
# print(y.shape)
# print(X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

sayisal_kolonlar = ["m2", "oda", "yas", "m2_oda", "m2_yas"]

scaler = StandardScaler()

X_train[sayisal_kolonlar] = scaler.fit_transform(X_train[sayisal_kolonlar])
X_test[sayisal_kolonlar] = scaler.transform(X_test[sayisal_kolonlar])

# print(X_train[sayisal_kolonlar].describe())
# print(X_test[sayisal_kolonlar].describe())

model = LinearRegression()
model.fit(X_train, y_train)

# print(model.score(X_train, y_train))
# print(model.score(X_test, y_test))



katsayilar = pd.DataFrame({
    "ozellik": X.columns,
    "katsayi": model.coef_
}).sort_values("katsayi", ascending=False)

# print(katsayilar)
# print(model.intercept_)


tahminler = model.predict(X_test)

mae = mean_absolute_error(y_test, tahminler)

# print("MAE:", mae)

mse = mean_squared_error(y_test, tahminler)
rmse = np.sqrt(mse)

# print("MSE:", mse)
# print("RMSE:", rmse)

mape = mean_absolute_percentage_error(y_test, tahminler)

# print("MAPE:", mape * 100)

baseline_tahmin = np.full(len(y_test), y_train.mean())
baseline_mae = mean_absolute_error(y_test, baseline_tahmin)

# print("Baseline MAE:", baseline_mae)
# print("Model MAE:", mae)

# plt.scatter(y_test, tahminler, alpha=0.6)

# plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--")

# plt.xlabel("Gerçek fiyat")
# plt.ylabel("Tahmin edilen fiyat")


artiklar = y_test - tahminler

# plt.scatter(tahminler, artiklar, alpha = 0.6)
# plt.axhline(0, color = "red", linestyle = "--")
# plt.xlabel("Tahmin edilen fiyat")
# plt.ylabel("Artık (gerçek - tahmin)")

# plt.show()

sonuc = pd.DataFrame({"gercek": y_test, "tahmin": tahminler, "hata": y_test - tahminler})

sonuc["mutlak_hata"] = sonuc["hata"].abs()

# print(sonuc.sort_values("mutlak_hata", ascending=False).head(10))

en_kotuler = sonuc.sort_values(
    "mutlak_hata",
    ascending=False
).head(10)

en_kotuler = en_kotuler.join(X_test)

print(en_kotuler)