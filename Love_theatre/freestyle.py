import pandas as pd


df1 = pd.read_csv("love_theatre_shows.csv", keep_default_na=False, na_values=[])

# Replace empty strings and whitespace-only strings with 'N/A'
df1.replace(to_replace=r'^\s*$', value='N/A', regex=True, inplace=True)

df1.to_csv("love_theatre_shows.csv", index=False)
print(df1["calender_link"])