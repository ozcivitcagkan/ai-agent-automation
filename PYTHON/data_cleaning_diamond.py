import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

url =  "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv"

df = pd.read_csv(url)

# print(df.head())


# print(df.isnull().sum())

# print(df.duplicated().sum()) #146

df = df.drop_duplicates()

# print(df.duplicated().sum())

# print(df.shape) #(53940, 10)
# print(df.dtypes)
# print(df.describe())
# print(df.info())

# print((df["x"] == 0).sum()) 7
# print((df["y"] == 0).sum()) 6
# print((df["z"] == 0).sum()) 19

# print(df[(df["x"] == 0) | (df["y"] == 0) | (df["z"] == 0)])
# print(df.sort_values("y", ascending=False).head(3))

# fig, axes = plt.subplots(1, 3, figsize=(16, 4))
# sns.histplot(df["price"], bins=50, ax=axes[0])
# sns.histplot(df["carat"], bins=100, ax=axes[1])
# sns.boxplot(x=df["price"], ax=axes[2])
# plt.tight_layout()
# plt.show()

# print(df[(df["carat"] > 0.9) & (df["carat"] < 1.1)]["carat"].value_counts().sort_index())

# print(df.corr(numeric_only=True)["carat"].sort_values(ascending=False))
# sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
# plt.show()

# sns.scatterplot(x="carat", y="price", data=df, alpha=0.1)
# plt.show()

# print(df.groupby("cut")["price"].mean())
# print(df.groupby("cut")["carat"].mean())     

# df["carat_grup"] = pd.cut(df["carat"], bins=[0, 0.5, 1, 1.5, 2, 6])
# print(df.groupby(["carat_grup", "cut"], observed=True)["price"].mean())

df["fiyat_karat"] = df["price"] / df["carat"]
print(df.groupby("cut")["fiyat_karat"].mean())
print(df.groupby("clarity")["fiyat_karat"].mean())