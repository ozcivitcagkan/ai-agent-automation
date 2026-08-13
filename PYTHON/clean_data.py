import pandas as pd

url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv"

df = pd.read_csv(url)


# print(df.head())
# print(df.shape)

# print(df.isnull().sum()/len(df) * 100)

# df.dropna(axis = 1)

# df["age"].fillna(df["age"].mode()[0])

# df = df.drop("deck", axis = 1)

# print(df.duplicated().sum())

# df = df.drop_duplicates()

print(df.dtypes)