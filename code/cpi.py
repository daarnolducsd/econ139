import os 
import pandas as pd

os.chdir(os.path.dirname(__file__))

# load cpi csv as pandas dataframe
df =  pd.read_csv('../data/cpi.csv')

cpi_2023 = df[df['Year'] == 2023]['Annual'].values[0]
cpi_1950 = df[df['Year'] == 1950]['Annual'].values[0]

# ratio 
relative = cpi_2023 / cpi_1950

print(cpi_2023)
print(cpi_1950)

print(relative)
print(3000*relative)  # 3000 in 1950 is worth about 40,000 in 2023