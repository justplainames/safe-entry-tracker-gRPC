import pandas as pd
from datetime import datetime as dt
import numpy as np

df = pd.read_csv("se_db.csv")
df['Timestamp'] = df["checkin"]

print(df)

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
print(type(df.loc[0]['Timestamp']))

# df['Timestamp'] = pd.to_datetime(df.Timestamp)
# print(df)

# print(df.between_time('12:00', '12:57'))


df = pd.read_csv("exposure.csv")
check = df.loc[df["nric"] == "s2222d"]
print(check['clear'])

check['clear'] = pd.to_datetime(check['clear'])
