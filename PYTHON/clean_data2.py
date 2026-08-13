import pandas as pd

url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"

df = pd.read_csv(url)

# print(df.info())

# print(df.isnull().sum())

# print((df.isnull().sum())/len(df)* 100) 

# print(df)

df = df.drop("deck", axis = 1)

df["age"] = df["age"].fillna(df["age"].median())

# print(df.isnull().sum())

# print(df)

df["embark_town"] = df["embark_town"].fillna((df["embark_town"]).mode()[0])
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])



# print(df.isnull().sum())

# print(df.duplicated().sum())
df = df.drop_duplicates()

# print(df.duplicated().sum())

# print(df.shape)
# print(df.dtypes)

# print(df.groupby("sex")["survived"].mean())
# print(df.groupby("class")["survived"].mean())

