import pandas as pd

veri = {
    "isim": ["Ali", "Ayşe", "Can", "Deniz", "Elif"],
    "yas": [25, 30, 35, 28, 41],
    "maas": [30000, 45000, 60000, 38000, 72000],
    "departman": ["IT", "Satış", "IT", "Satış", "IT"]
}

df = pd.DataFrame(veri)

# print(df)
# print(df.shape)
# print(df.info())
# print(df.describe())
# print(df[["isim","maas"]])

# print(df[df["maas"] > 40000])
# print(df[(df["yas"] > 30) & (df["departman"] == "IT")])

# df["zamli maas"] = df["maas"] * 1.5
# df["kidemli"] = df["yas"] > 30

# print(df.sort_values("maas", ascending=False))

# print(df.groupby("departman")["maas"].mean())
print(df.groupby("departman").size())