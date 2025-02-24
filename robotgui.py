import tkinter as tk
from tkinter import messagebox
from queue import PriorityQueue
import time

class RobotPathfinding:
    def __init__(self, grid, start, target):
        self.grid = grid
        self.start = start
        self.target = target
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

    def is_valid(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols and self.grid[x][y] == 0

    def heuristic(self, x, y):
        return abs(x - self.target[0]) + abs(y - self.target[1])

    def find_path(self):
        pq = PriorityQueue()
        g_cost = [[float('inf')] * self.cols for _ in range(self.rows)]
        g_cost[self.start[0]][self.start[1]] = 0
        pq.put((0, self.start))
        parent = {}

        while not pq.empty():
            _, current = pq.get()
            if current == self.target:
                return self.reconstruct_path(parent)

            for dx, dy in self.directions:
                nx, ny = current[0] + dx, current[1] + dy
                if self.is_valid(nx, ny):
                    new_g = g_cost[current[0]][current[1]] + 1
                    if new_g < g_cost[nx][ny]:
                        g_cost[nx][ny] = new_g
                        f = new_g + self.heuristic(nx, ny)
                        pq.put((f, (nx, ny)))
                        parent[(nx, ny)] = current

        return []

    def reconstruct_path(self, parent):
        path = []
        current = self.target
        while current != self.start:
            path.append(current)
            current = parent[current]
        path.append(self.start)
        path.reverse()
        return path


class PathfindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Robot Pathfinding")
        self.root.configure(bg='#f0f8ff')  # Light background color
        
        self.grid = []
        self.rows = 5
        self.cols = 5
        self.start = (0, 0)
        self.target = (4, 4)
        self.cell_size = 50

        self.create_widgets()
        self.obstacle_mode = False

    def create_widgets(self):
        # Input fields for rows, cols, start, target
        self.input_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Rows:", bg='#f0f8ff').grid(row=0, column=0)
        self.rows_entry = tk.Entry(self.input_frame)
        self.rows_entry.grid(row=0, column=1)
        self.rows_entry.insert(0, "5")

        tk.Label(self.input_frame, text="Cols:", bg='#f0f8ff').grid(row=1, column=0)
        self.cols_entry = tk.Entry(self.input_frame)
        self.cols_entry.grid(row=1, column=1)
        self.cols_entry.insert(0, "5")

        tk.Label(self.input_frame, text="Start (x, y):", bg='#f0f8ff').grid(row=2, column=0)
        self.start_entry = tk.Entry(self.input_frame)
        self.start_entry.grid(row=2, column=1)
        self.start_entry.insert(0, "0,0")

        tk.Label(self.input_frame, text="Target (x, y):", bg='#f0f8ff').grid(row=3, column=0)
        self.target_entry = tk.Entry(self.input_frame)
        self.target_entry.grid(row=3, column=1)
        self.target_entry.insert(0, "4,4")

        tk.Button(self.input_frame, text="Generate Grid", command=self.generate_grid).grid(row=4, column=0, columnspan=2)

        # Canvas for displaying grid
        self.canvas = tk.Canvas(self.root, bg='#e0f7fa')  # Light blue background
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Buttons for setting obstacles and finding path
        self.action_frame = tk.Frame(self.root, bg='#f0f8ff')
        self.action_frame.pack(pady=10)

        tk.Button(self.action_frame, text="Set Obstacles", command=self.toggle_obstacle_mode).pack(side=tk.LEFT, padx=5)
        tk.Button(self.action_frame, text="Find Path", command=self.find_path).pack(side=tk.LEFT, padx=5)

    def generate_grid(self):
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())
            start = tuple(map(int, self.start_entry.get().split(',')))
            target = tuple(map(int, self.target_entry.get().split(',')))

            if not (0 <= start[0] < self.rows and 0 <= start[1] < self.cols):
                raise ValueError("Start position out of bounds")
            if not (0 <= target[0] < self.rows and 0 <= target[1] < self.cols):
                raise ValueError("Target position out of bounds")

            self.start = start
            self.target = target
            self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

            self.draw_grid()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def draw_grid(self, path=None, robot_position=None):
        self.canvas.delete("all")
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # Resize the canvas to fit the grid dimensions
        canvas_width = max(grid_width, 500)
        canvas_height = max(grid_height, 500)
        self.canvas.config(width=canvas_width, height=canvas_height)

        # Calculate offsets to center the grid
        x_offset = (canvas_width - grid_width) // 2
        y_offset = (canvas_height - grid_height) // 2

        for i in range(self.rows):
            for j in range(self.cols):
                x1, y1 = x_offset + j * self.cell_size, y_offset + i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = "white"
                if self.grid[i][j] == 1:
                    color = "black"
                if path and (i, j) in path:
                    color = "blue"
                if robot_position == (i, j):
                    color = "yellow"
                if (i, j) == self.start:
                    color = "green"
                if (i, j) == self.target:
                    color = "red"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#add8e6")  # Light blue outline

    def toggle_obstacle_mode(self):
        if self.obstacle_mode:
            self.canvas.unbind("<Button-1>")
            self.obstacle_mode = False
        else:
            self.canvas.bind("<Button-1>", self.mark_obstacle)
            self.obstacle_mode = True

    def mark_obstacle(self, event):
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        x_offset = (self.canvas.winfo_width() - grid_width) // 2
        y_offset = (self.canvas.winfo_height() - grid_height) // 2

        x, y = (event.y - y_offset) // self.cell_size, (event.x - x_offset) // self.cell_size
        if 0 <= x < self.rows and 0 <= y < self.cols and (x, y) != self.start and (x, y) != self.target:
            self.grid[x][y] = 1 if self.grid[x][y] == 0 else 0
            self.draw_grid()

    def find_path(self):
        if not self.grid:
            messagebox.showerror("Error", "Generate the grid first!")
            return

        robot = RobotPathfinding(self.grid, self.start, self.target)
        path = robot.find_path()

        if path:
            self.simulate_robot_movement(path)
        else:
            self.draw_grid()
            messagebox.showerror("No Path", "No path could be found.")

    def simulate_robot_movement(self, path):
        for position in path:
            self.draw_grid(path=path, robot_position=position)
            self.root.update()
            time.sleep(0.5)  # Pause to simulate movement

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingApp(root)
    root.mainloop()
