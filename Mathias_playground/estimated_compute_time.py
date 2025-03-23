# Computing the estimated total time to simulate all 5372 floorplans in the Modified Swiss Dwellings dataset
time_20_floors = 4*60 + 6 # 4 minutes and 6 seconds
# Projected time to simulate all 5372 floorplans
total_time = time_20_floors/20 * 5372
# number is so large that it should be in days, hours and minutes

print(f"Estimated total time to simulate all 5372 floorplans: {total_time//1440} days, {total_time%1440//60} hours and {total_time%60} minutes")