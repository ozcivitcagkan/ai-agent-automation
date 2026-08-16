import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"
df = pd.read_csv(url)

# print(df.shape) # (891, 15)
# print(df.head())
# print(df.info())
# print(df.describe())

# print(df.isnull().sum())
# print(df.isnull().sum()/len(df) * 100)
# print(df.duplicated().sum())

# for sutun in df.select_dtypes(include="object").columns:
#     print(sutun)
#     print(df[sutun].value_counts())
#     print()


# sns.histplot(df["age"])
# plt.show()

# sns.countplot(x= "class", data=df)
# plt.show()

# print(df["survived"].value_counts())
# print(df["survived"].value_counts(normalize=True)) %62 dead, %32 survived

# print(df.groupby("sex")["survived"].mean()) kadinların %74 u kurtuldu, erkeklerin 19.

# print(df.groupby("class")["survived"].mean())
# print(df.groupby(["sex", "class"])["survived"].mean())

# print(df.groupby("survived")["age"].mean())
# print(df.groupby("survived")["fare"].mean())

# sns.boxplot(x= "survived", y = "fare", data =df)
# plt.show()

# sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
# # plt.show()

# print(pd.crosstab(df["embark_town"], df["class"], normalize="index"))

# print(df["alive"]  )