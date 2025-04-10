import matplotlib.pyplot as plt
import numpy as np

# Example matrix
matrix = np.array([
    [0, 1, 2],
    [2, 1, 3],
    [1, 0, 2]
])

# Create a color map
colors = {
    0: 'white',   # No color dot
    1: 'yellow',
    2: 'green',
    3: 'blue'
}

# Create an image from the matrix
fig, ax = plt.subplots()
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        # Draw a circle in the center of each square based on the matrix value
        if matrix[i, j] != 0:
            circle = plt.Circle((j + 0.5, matrix.shape[0] - i - 1 + 0.5), 0.2, color=colors[matrix[i, j]])
            ax.add_patch(circle)

# Add grid lines
for i in range(matrix.shape[0] + 1):
    ax.plot([i, i], [0, matrix.shape[0]], color='black')
for j in range(matrix.shape[1] + 1):
    ax.plot([0, matrix.shape[1]], [j, j], color='black')

# Set limits and turn off axes
ax.set_xlim(0, matrix.shape[1])
ax.set_ylim(0, matrix.shape[0])
ax.set_xticks([])
ax.set_yticks([])

# Display the image
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
