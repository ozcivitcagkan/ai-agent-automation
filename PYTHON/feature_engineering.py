import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler


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

print(balkon[:10])

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

df_encoded = pd.get_dummies(df, columns=["mahalle"])

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

scaler = StandardScaler()

scaler.fit(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]])

# print(scaler.mean_)
# print(scaler.scale_)

scaled_data = scaler.transform(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]])

# print(scaled_data[:5])

scaled_df = pd.DataFrame(scaled_data,columns=["m2", "oda", "yas", "m2_oda", "m2_yas"])

# print(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]].head())
# print(scaled_df.head())

# print(scaled_df.describe())

df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]] = scaled_df


# print(df_encoded[["m2", "oda", "yas", "m2_oda", "m2_yas"]].head())

print(df_encoded.columns)
print(df_encoded.head())