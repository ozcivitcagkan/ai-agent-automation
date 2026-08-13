import pandas as pd

# notlar = pd.Series([70, 85, 60], index = ["Ali", "Ayşe", "Can"])

# print(notlar["Ayşe"])

veri = {
    "isim" : ["Ali", "Ayşe", "Can", "Deniz"],
    "yas" : [25, 30, 35, 28],
    "maas" : [30000, 45000, 60000, 38000]
}

df = pd.DataFrame(veri)

# print(df)
# print(df.head)
# print(df.tail(3))
# print(df.shape)
# print(df.info())
# print(df.describe())
# print(df.columns)
# print(df["maas"])
# print(df[["isim", "maas"]])
# print(df.loc[0, "maas"])
# print(df.iloc[0])
# print(df.iloc[1:3])
# print(df.iloc[0,2])
# print(df[df["yas"] > 28])
# print(df[(df["yas"] > 25) & (df["maas"] > 35000)])
# print(df[(df["yas"] < 26) | (df["maas"] > 50000)])

df["zam"] = df["maas"] * 2
df["kategori"] = df["yas"] > 30
# print(df.sort_values("maas", ascending= False ))

# print(df.groupby("yas")["maas"].mean())

# url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
# df = pd.read_csv(url)

# print(df.head())
