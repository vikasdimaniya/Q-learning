import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Function to read data from file
def read_data(file_name):
    with open(file_name, 'r') as file:
        data = [float(line.strip()) for line in file]
    return data

# Function to update the plot
def update(frame):
    data = read_data(file_name)
    x = np.arange(len(data))

    # Fit a polynomial of a chosen degree
    degree = 3
    p = Polynomial.fit(x, data, degree)
    x_fit = np.linspace(0, len(data) + 10, 200)  # Including 10 future points
    y_fit = p(x_fit)
    
    ax.clear()
    ax.plot(x, data, marker='o', linestyle='-', color='b', label='Original reward Data')
    ax.plot(x_fit, y_fit, linestyle='--', color='r', label=f'Polynomial Fit (degree {degree})')
    ax.set_title('Polynomial Fit for Future Prediction')
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.legend()

# File name containing the data
file_name = 'no_decay_attack_only_reward.txt'

# Set up the figure and axis
fig, ax = plt.subplots()
ani = animation.FuncAnimation(fig, update, interval=1000)  # Update every 1000 ms (1 second)

# Show the plot
plt.show()
