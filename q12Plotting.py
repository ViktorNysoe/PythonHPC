import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('all_floors.csv')

plt.hist(df[' mean_temp'], bins=30, edgecolor='black')
plt.title('Histogram of Mean Temperatures')
plt.xlabel('Mean Temperature (ºC)')
plt.ylabel('Number of Buildings')
plt.grid(True)
plt.show()

avg_mean_temp = df[' mean_temp'].mean()
avg_std_temp = df[' std_temp'].mean()
count_above_18 = (df[' pct_above_18'] >= 50).sum()
count_below_15 = (df[' pct_below_15'] >= 50).sum()

avg_mean_temp, avg_std_temp, count_above_18, count_below_15
