import pandas as pd


df = pd.read_csv("prefab-dataset/spain_salary_distribution.csv")
df.gross_income_euros = df.gross_income_euros.apply(lambda x: str(int(x)))


# df.to_csv("prefab-dataset/spain_salary_clean.csv")
# df.to_excel("final_datasets(xlsx)/spain_salary_clean.xlsx")

