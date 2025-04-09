# Computing the estimated total time to simulate all 5372 floorplans in the Modified Swiss Dwellings dataset
time_20_floors = 4*60 + 6 # 4 minutes and 6 seconds
# Projected time to simulate all 5372 floorplans
total_time = time_20_floors/20 * 5372 # total time in seconds
# number is so large that it should be in days, hours and minutes
days = total_time // (24 * 3600)
hours = (total_time % (24 * 3600)) // 3600
minutes = (total_time % 3600) // 60

print(f"Estimated time to simulate all 5372 floorplans: {days} days, {hours} hours, {minutes} minutes")
