#| echo: false
#| label: fig-steep-supply-curves-shifting
#| fig-cap: "Equilibrium in the Software Engineering Firm with Steeper Labor Supply Curves"

import matplotlib.pyplot as plt
import numpy as np

# Data points from the example
years = ['2023', '2024']
wages = [100000, 110000]  # In dollars
employees = [100, 120]

plt.figure(figsize=(8, 6))

# Create a range for plotting
x_line = np.linspace(60, 140, 100)

# Create two STEEPER labor supply curves (much steeper than the previous graph)
supply_slope = 1000  # Steeper than the flat example; keeps equilibrium MFC values round

# 2023 Labor supply curve: passes through (100, 100000)
supply_2023_intercept = wages[0] - supply_slope * employees[0]
y_supply_2023 = supply_slope * x_line + supply_2023_intercept

# 2024 Labor supply curve: shifted down, passes through (120, 110000)
supply_2024_intercept = wages[1] - supply_slope * employees[1]
y_supply_2024 = supply_slope * x_line + supply_2024_intercept

# Create corresponding MFC curves (twice the slope of supply curves)
mfc_slope = 2 * supply_slope

# For supply w(L) = a + bL, payroll is aL + bL^2, so MFC = a + 2bL.
# MFC therefore has the SAME intercept as its corresponding supply curve.
mfc_2023_intercept = supply_2023_intercept
y_mfc_2023 = mfc_slope * x_line + mfc_2023_intercept

mfc_2024_intercept = supply_2024_intercept
y_mfc_2024 = mfc_slope * x_line + mfc_2024_intercept

# Calculate MFC values at the equilibrium employment levels
mfc_2023_eq = mfc_slope * employees[0] + mfc_2023_intercept  # MFC at L=100
mfc_2024_eq = mfc_slope * employees[1] + mfc_2024_intercept  # MFC at L=120

# Create two downward sloping MRP curves
# Both curves should be downward sloping with the same slope
mrp_slope = -800  # Negative slope for downward sloping MRP

# 2023 MRP curve: passes through (100, mfc_2023_eq)
mrp_2023_intercept = mfc_2023_eq - mrp_slope * employees[0]
y_mrp_2023 = mrp_slope * x_line + mrp_2023_intercept

# 2024 MRP curve: shifted right, passes through (120, mfc_2024_eq)
mrp_2024_intercept = mfc_2024_eq - mrp_slope * employees[1]
y_mrp_2024 = mrp_slope * x_line + mrp_2024_intercept

# Plot the curves
plt.plot(x_line, y_supply_2023, color='#2E86AB', linewidth=2, linestyle='--', label='Labor Supply 2023')
plt.plot(x_line, y_supply_2024, color='#2E86AB', linewidth=2, linestyle='-', label='Labor Supply 2024')
plt.plot(x_line, y_mfc_2023, color='#DC3545', linewidth=2, linestyle='--', label='MFC 2023')
plt.plot(x_line, y_mfc_2024, color='#DC3545', linewidth=2, linestyle='-', label='MFC 2024')
plt.plot(x_line, y_mrp_2023, color='#28A745', linewidth=2, linestyle='--', label='MRPL 2023')
plt.plot(x_line, y_mrp_2024, color='#28A745', linewidth=2, linestyle='-', label='MRPL 2024')

# Plot the equilibrium points (wages paid, from supply curve)
plt.scatter(employees, wages, s=100, color='#F18F01', alpha=0.8, edgecolors='black', linewidth=1, zorder=5)

# Plot the MRP-MFC intersection points (true equilibrium points)
mfc_eq_values = [mfc_2023_eq, mfc_2024_eq]
plt.scatter(employees, mfc_eq_values, s=80, color='#8B0000', alpha=0.8, edgecolors='black', linewidth=1, zorder=5, marker='s')

# Add labels for wage points
for i, year in enumerate(years):
    if year == '2023':
        plt.annotate(f'{year}\nWage Paid', (employees[i], wages[i]), 
                    xytext=(10, -25), textcoords='offset points',
                    fontsize=9, ha='left', va='top')
    else:
        plt.annotate(f'{year}\nWage Paid', (employees[i], wages[i]), 
                    xytext=(10, 15), textcoords='offset points',
                    fontsize=9, ha='left', va='bottom')

# Add vertical lines to show the difference between MFC and wage
for i in range(len(employees)):
    plt.plot([employees[i], employees[i]], [wages[i], mfc_eq_values[i]], 
             color='gray', linestyle=':', linewidth=1, alpha=0.7)

plt.xlabel('Number of Employees')
plt.ylabel('Annual Wage ($)')
plt.title('Equilibrium in the Software Engineering Firm with Steeper Labor Supply Curves')
plt.grid(True, alpha=0.3)
plt.legend(loc='lower left')

# Set axis ranges and ticks - standardized scale
plt.xlim(50, 150)
plt.ylim(25000, 275000)
plt.xticks(range(50, 175, 25))  # 50, 75, 100, 125, 150
plt.yticks(range(25000, 300000, 25000))  # 25k, 50k, 75k, ..., 275k

plt.tight_layout()

# Format y-axis to show wages in thousands
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${int(x/1000)}K'))

plt.show()
