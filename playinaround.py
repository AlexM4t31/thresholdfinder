import matplotlib.pyplot as plt 
x_ids = [2, 5, 8, 11, 14, 17, 26, 35, 47, 59]

decided_leak_values = [[8.0, 20.0, 39.0, 72.0, 73.0, 165.0, 175.0, 191.0, 232.0, 326.0, 364.0, 394.0, 433.0, 779.0, 1754.0], [17.0, 34.0, 66.0, 73.0, 75.0, 87.0, 96.0, 98.0, 109.0, 163.0, 227.0, 256.0, 268.0, 300.0, 453.0], [4.0, 10.0, 64.0, 82.0, 96.0, 115.0, 173.0, 200.0, 229.0, 236.0, 242.0, 365.0, 389.0, 941.0, 1082.0], [8.0, 10.0, 41.0, 41.0, 55.0, 62.0, 68.0, 89.0, 168.0, 265.0, 287.0, 402.0, 650.0, 1607.0, 1705.0], [11.0, 20.0, 41.0, 53.0, 55.0, 120.0, 121.0, 123.0, 138.0, 184.0, 200.0, 345.0, 613.0, 633.0, 715.0], [26.0, 31.0, 69.0, 74.0, 90.0, 110.0, 124.0, 132.0, 145.0, 168.0, 183.0, 240.0, 256.0, 265.0, 417.0], [116.0, 148.0, 173.0, 173.0, 185.0, 204.0, 205.0, 228.0, 235.0, 289.0, 296.0, 309.0, 435.0, 592.0, 877.0], [8.0, 100.0, 170.0, 201.0, 218.0, 238.0, 251.0, 351.0, 395.0, 491.0, 554.0, 1142.0, 1148.0, 1431.0, 1523.0], [34.0, 39.0, 99.0, 123.0, 182.0, 393.0, 413.0, 435.0, 438.0, 450.0, 559.0, 602.0, 620.0, 806.0, 858.0], [0.0, 35.0, 41.0, 81.0, 133.0, 139.0, 151.0, 204.0, 245.0, 248.0, 289.0, 361.0, 466.0, 486.0, 933.0]]

decided_valid_values = [[2.0, 4.0, 34.0, 87.0], [0.0, 1.0, 30.0, 47.0], [0.0, 8.0, 65.0, 152.0], [19.0], [0.0, 0.0, 0.0, 1.0, 2.0, 5.0, 5.0, 7.0, 7.0, 8.0, 15.0, 17.0, 18.0, 21.0, 25.0, 26.0, 34.0, 38.0, 44.0, 78.0, 110.0, 154.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 3.0, 4.0, 7.0, 7.0, 7.0, 7.0, 9.0, 9.0, 9.0, 15.0, 15.0, 18.0, 19.0, 25.0, 29.0, 39.0, 39.0, 54.0, 59.0, 70.0, 74.0, 77.0, 119.0, 152.0], [0.0, 5.0, 8.0, 9.0, 10.0, 18.0, 19.0, 20.0, 21.0, 22.0, 30.0, 35.0, 48.0, 68.0, 74.0, 80.0, 86.0, 143.0, 151.0, 166.0, 187.0], [10.0, 41.0, 44.0, 86.0, 124.0], [16.0, 18.0, 61.0, 128.0], []]

fig, ax = plt.subplots(figsize=(10, 6))

positions = list(range(len(x_ids)))
half_width = 0.42  # makes neighboring columns nearly touch

for i, (leak_vals, valid_vals) in enumerate(zip(decided_leak_values, decided_valid_values)):
    if leak_vals:
        ax.hlines(
            y=leak_vals,
            xmin=i - half_width,
            xmax=i + half_width,
            colors='red',
            linewidth=1.8,
            alpha=0.8,
            label='Leak' if i == 0 else None
        )
    if valid_vals:
        ax.hlines(
            y=valid_vals,
            xmin=i - half_width,
            xmax=i + half_width,
            colors='blue',
            linewidth=1.8,
            alpha=0.8,
            label='Valid' if i == 0 else None
        )

ax.set_xticks(positions)
ax.set_xticklabels(x_ids)
ax.set_xlabel('Simulation parameter combo id')
ax.set_ylabel('Metric value')
ax.set_title('Leak vs valid metric values by parameter combo id')
ax.set_ylim(0, 500)
ax.set_xlim(-0.5, len(x_ids) - 0.5)
ax.grid(axis='y', linestyle='--', alpha=0.35)
ax.legend()

plt.tight_layout()
#plt.show()
plt.savefig("myfig.png") 

"""
for tmpIndex,tmpId in enumerate(x):
    
    tmpLeakLen = len(decided_leak_values[tmpIndex])
    tmpValidLen = len(decided_valid_values[tmpIndex])

    totalLookedAt = tmpLeakLen + tmpValidLen

    print("for id " + str(tmpId) + ", there were " + str(tmpLeakLen) + " leaks, out of " + str(totalLookedAt) + " cases looked at.")

"""