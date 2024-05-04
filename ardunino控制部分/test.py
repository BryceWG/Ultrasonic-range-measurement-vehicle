from sympy import symbols, Eq, solve

# Define the variables
x, y = symbols('x y')

# Define the equations
eq1 = Eq(6*x + 14.7*y, 280)
eq2 = Eq(14.7*x + 53.63*y, 1078)

# Solve the equations
solution = solve((eq1, eq2), (x, y))

# Output the solution in fractional form
x_fraction = solution[x].as_numer_denom()
y_fraction = solution[y].as_numer_denom()

print(f"x = {x_fraction[0]}/{x_fraction[1]}")
print(f"y = {y_fraction[0]}/{y_fraction[1]}")
