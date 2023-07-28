import googletrans
import pandas as pd

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)


def translate(x):
    try:
        translator = googletrans.Translator()
        return translator.translate(x, dest="es")
    except TypeError:
        print(x)


def clean_data(dataframe):
    counts = dataframe['Empresa'].value_counts()
    dataframe = dataframe[~dataframe['Empresa'].isin(counts[counts < 50].index)]
    dataframe.dropna(inplace=True)
    dataframe.reset_index(inplace=True)
    return dataframe


if __name__ == '__main__':
    df_spain = pd.read_csv("glassdoor_datasets(csv)/spain_jobs_salaries_by_company.csv")
    df_france = pd.read_csv("glassdoor_datasets(csv)/france_jobs_salaries_by_company.csv")
    df_f_copy = df_france.copy()
    df_s_copy = df_spain.copy()
    df_s_unique = df_s_copy.drop_duplicates(subset="Empleo", ignore_index=True)
    df_f_unique = df_f_copy.drop_duplicates(subset="Empleo", ignore_index=True)
    df_f_clean = clean_data(df_f_unique)
    df_s_clean = clean_data(df_s_unique)
    df_s_clean = df_s_clean.loc[df_s_clean["Sector"] != "N/D"]
    # df_s_clean.to_excel("final_datasets(xlsx)/clean_spain_glassdoor.xlsx")
    # df_f_unique.to_excel("final_datasets(xlsx)/clean_france_glassdoor.xlsx")
    df_merged = pd.merge(df_s_clean, df_f_clean, how="inner", on=["Empleo", "Empresa"], suffixes=("_España", "_Francia"))
    df_merged.drop(["index_Francia", "index_España", "Sector_Francia"], axis=1, inplace=True)
    df_merged.rename(columns={"Sector_España": "Sector"}, inplace=True)
    print(df_merged)
    # df_merged.to_excel("final_datasets(xlsx)/clean_spain_france.xlsx")

