import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
df = pd.read_csv(url)


df = df.drop("deck", axis=1)                                         
df["age"] = df["age"].fillna(df["age"].median())                      
df["embark_town"] = df["embark_town"].fillna(df["embark_town"].mode()[0])
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])


# print(df.isnull().sum())
# print(df.shape)


# sns.histplot(df["age"], bins = 30)
# plt.title("Yaş Dağılımı")
# plt.show()


# sns.boxenplot(x=df["fare"])
# plt.show()


# sns.boxenplot(x="class", y = "age", data=df)
# plt.show()

# sns.countplot(x = "class", data=df)
# plt.show()

# sns.countplot(x = "class", hue = "survived", data = df)
# plt.show()

# sns.scatterplot(x = "age", y = "fare", data=df)
# plt.show()

# sns.scatterplot(x = "age", y = "fare", hue="survived", data=df)
# plt.show()

# sayisal = df[["survived", "age", "fare","pclass","sibsp", "parch"]]
# sns.heatmap(sayisal.corr(), annot=True, cmap= "coolwarm")
# plt.show()

# fig, axes = plt.subplots(1, 2, figsize = (12, 5))

# sns.histplot(df["age"], ax=axes[0])
# sns.histplot(df["fare"], ax=axes[1])


# fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# sns.histplot(df["age"], ax=axes[0, 0])      
# sns.histplot(df["fare"], ax=axes[0, 1])    
# sns.boxplot(x=df["age"], ax=axes[1, 0])      
# sns.boxplot(x=df["fare"], ax=axes[1, 1])     

# plt.tight_layout()     
# plt.show()

# plt.savefig("grafik_terk.png", dpi=150, bbox_inches="tight")
# plt.show()