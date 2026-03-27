import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

# =========================================================
# CORELAP Module
# =========================================================
class CorelapGUI:
    def __init__(self, parent):
        
        self.window = tk.Toplevel(parent)
        self.window.title("CORELAP Layout Generator")
        self.window.geometry("1100x920")

        # ---------------- Variables ----------------
        self.num_depts_var = tk.IntVar(value=9)
        self.partial_adj_var = tk.DoubleVar(value=0.5)

        # default weights
        self.rels = ['A', 'E', 'I', 'O', 'U', 'X']
        self.weights = {
            'A': tk.IntVar(value=125),
            'E': tk.IntVar(value=25),
            'I': tk.IntVar(value=5),
            'O': tk.IntVar(value=1),
            'U': tk.IntVar(value=0),
            'X': tk.IntVar(value=-125)
        }
        
        self.cutoffs = {
            'A': tk.DoubleVar(value=100.0),
            'E': tk.DoubleVar(value=80.0),
            'I': tk.DoubleVar(value=60.0),
            'O': tk.DoubleVar(value=40.0),
            'U': tk.DoubleVar(value=20.0),
            'X': tk.DoubleVar(value=0.0)
        }

        self.rel_entries = {}
        self.setup_ui()

    # =========================================================
    # UI
    # =========================================================
    def setup_ui(self):
        top_frame = ttk.LabelFrame(self.window, text="Configuration & Parameters", padding=(10, 10))
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        param_frame = ttk.Frame(top_frame)
        param_frame.grid(row=0, column=0, rowspan=2, sticky=tk.N)

        ttk.Label(param_frame, text="Number of Departments:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(param_frame, textvariable=self.num_depts_var, width=8).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(param_frame, text="Partial Adjacency Factor (α):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(param_frame, textvariable=self.partial_adj_var, width=8).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        def_frame = ttk.LabelFrame(top_frame, text="REL Weights & Cutoffs", padding=(5, 5))
        def_frame.grid(row=0, column=1, rowspan=2, padx=20, sticky=tk.W)

        ttk.Label(def_frame, text="REL:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(def_frame, text="Weight:", font=('Arial', 9, 'bold')).grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(def_frame, text="Cutoff:", font=('Arial', 9, 'bold')).grid(row=2, column=0, padx=5, pady=2)

        for idx, rel in enumerate(self.rels):
            ttk.Label(def_frame, text=rel, font=('Arial', 9, 'bold')).grid(row=0, column=idx + 1, padx=5)
            ttk.Entry(def_frame, textvariable=self.weights[rel], width=6).grid(row=1, column=idx + 1, padx=2)
            ttk.Entry(def_frame, textvariable=self.cutoffs[rel], width=6).grid(row=2, column=idx + 1, padx=2)

        ttk.Button(top_frame, text="Create REL Table", command=self.create_table).grid(row=0, column=2, rowspan=2, padx=20)

        self.mid_frame = ttk.LabelFrame(
            self.window,
            text="REL Chart Input (select a cell and Ctrl+V to paste upper-triangular values from Excel)",
            padding=(10, 10)
        )
        self.mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=5)

        self.bottom_frame = ttk.LabelFrame(self.window, text="Execution & Results", padding=(10, 10))
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.run_btn = ttk.Button(self.bottom_frame, text="Run CORELAP", command=self.run_algorithm, state=tk.DISABLED)
        self.run_btn.pack(side=tk.TOP, pady=5)

        self.notebook = ttk.Notebook(self.bottom_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tab_layout = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_layout, text="Final Layout")
        self.canvas = tk.Canvas(self.tab_layout, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.tab_cv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cv, text="Numerical CV Matrix")

        self.tab_dist = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dist, text="Distance Matrix")

        self.tab_steps = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_steps, text="Selection / Placement Steps")

    def create_table(self):
        for widget in self.mid_frame.winfo_children():
            widget.destroy()
        self.rel_entries.clear()

        try:
            n = self.num_depts_var.get()
            if n < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number of departments (>= 2).")
            return

        for i in range(n):
            ttk.Label(self.mid_frame, text=f"D{i + 1}", font=('Arial', 9, 'bold')).grid(row=0, column=i + 1, padx=5, pady=2)
            ttk.Label(self.mid_frame, text=f"D{i + 1}", font=('Arial', 9, 'bold')).grid(row=i + 1, column=0, padx=5, pady=2)

        for i in range(n):
            for j in range(n):
                if i < j:
                    ent = ttk.Entry(self.mid_frame, width=4, justify='center')
                    ent.insert(0, "U")
                    ent.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                    ent.bind('<Control-v>', self.paste_from_excel)
                    ent.bind('<Command-v>', self.paste_from_excel)
                    self.rel_entries[(i, j)] = ent
                elif i == j:
                    ttk.Label(self.mid_frame, text="-").grid(row=i + 1, column=j + 1)

        self.run_btn.config(state=tk.NORMAL)

    def paste_from_excel(self, event):
        try:
            clipboard = self.window.clipboard_get()
        except tk.TclError:
            return 'break'

        rows = clipboard.strip().split('\n')
        caller = event.widget
        start_i, start_j = 0, 1

        for (i, j), ent in self.rel_entries.items():
            if ent == caller:
                start_i, start_j = i, j
                break

        for r_idx, row in enumerate(rows):
            cols = row.strip().split('\t')
            for c_idx, val in enumerate(cols):
                target_i = start_i + r_idx
                target_j = start_j + c_idx
                if (target_i, target_j) in self.rel_entries:
                    ent = self.rel_entries[(target_i, target_j)]
                    ent.delete(0, tk.END)
                    clean_val = val.strip().upper()
                    if clean_val:
                        ent.insert(0, clean_val)

        return 'break'

    # =========================================================
    # Data preparation
    # =========================================================
    def build_rel_matrix(self, n):
        rel_matrix = {}
        valid = set(self.weights.keys())

        for (i, j), ent in self.rel_entries.items():
            val = ent.get().strip().upper()
            if val not in valid:
                raise ValueError(f"Invalid REL value '{val}'. Use only A, E, I, O, U, X.")
            rel_matrix[(i, j)] = val
            rel_matrix[(j, i)] = val

        return rel_matrix

    def build_cv_and_tcr(self, n, rel_matrix, weight_map):
        cv_matrix = [[0] * n for _ in range(n)]
        tcr = {i: 0 for i in range(n)}
        count_A = {i: 0 for i in range(n)}

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                rel = rel_matrix[(i, j)]
                w = weight_map[rel]
                cv_matrix[i][j] = w
                tcr[i] += abs(w)  # lecture rule
                if rel == 'A':
                    count_A[i] += 1

        return cv_matrix, tcr, count_A

    # =========================================================
    # Department selection logic
    # =========================================================
    def select_first_department(self, departments, tcr, count_A):
        return min(departments, key=lambda d: (-tcr[d], -count_A[d], d))

    def choose_reserved_x_departments(self, chosen_dept, candidates, rel_matrix, tcr):
        x_candidates = [d for d in candidates if rel_matrix[(d, chosen_dept)] == 'X']
        return sorted(x_candidates, key=lambda d: (tcr[d], d))

    def best_rel_rank_to_placed(self, dept, placed, rel_matrix):
        rank = {'A': 5, 'E': 4, 'I': 3, 'O': 2, 'U': 1, 'X': 0}
        best_rank = -1
        best_letter = None
        for p in placed:
            rel = rel_matrix[(dept, p)]
            if rank[rel] > best_rank:
                best_rank = rank[rel]
                best_letter = rel
        return best_rank, best_letter

    def select_next_department(self, active_candidates, placed, rel_matrix, tcr):
        best_dept = None
        best_key = None
        best_letter = None

        for d in active_candidates:
            best_rank, rel_letter = self.best_rel_rank_to_placed(d, placed, rel_matrix)
            key = (best_rank, tcr[d], -d) 

            if best_key is None or key > best_key:
                best_key = key
                best_dept = d
                best_letter = rel_letter

        return best_dept, best_letter

    # =========================================================
    # Placement logic
    # =========================================================
    def get_all_open_spots(self, layout):
        directions8 = [
            (-1, 0),  # 1 west
            (-1, -1), # 2 southwest
            (0, -1),  # 3 south
            (1, -1),  # 4 southeast
            (1, 0),   # 5 east
            (1, 1),   # 6 northeast
            (0, 1),   # 7 north
            (-1, 1)   # 8 northwest
        ]

        open_spots = set()
        occupied = set(layout.keys())

        for (x, y) in occupied:
            for dx, dy in directions8:
                s = (x + dx, y + dy)
                if s not in occupied:
                    open_spots.add(s)

        return open_spots

    def get_candidate_boundary_spots(self, layout):
        occupied = set(layout.keys())
        open_spots = self.get_all_open_spots(layout)

        candidates = []
        for s in open_spots:
            x, y = s
            touches = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    if (x + dx, y + dy) in occupied:
                        touches = True
                        break
                if touches:
                    break
            if touches:
                candidates.append(s)

        return candidates

    def boundary_order_from_west(self, layout):
        candidates = self.get_candidate_boundary_spots(layout)
        if not candidates:
            return []

        occupied = set(layout.keys())
        xs = [x for x, _ in occupied]
        ys = [y for _, y in occupied]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        min_x = min(x for x, _ in candidates)
        west_candidates = [p for p in candidates if p[0] == min_x]
        start = min(west_candidates, key=lambda p: (abs(p[1] - cy), -p[1]))

        def lecture_angle(p):
            dx = p[0] - cx
            dy = p[1] - cy
            ang = math.atan2(-dy, dx)  
            ang = (ang - math.pi) % (2 * math.pi)
            return ang

        ordered = sorted(candidates, key=lambda p: (
            (lecture_angle(p) - lecture_angle(start)) % (2 * math.pi),
            (p[0] - cx) ** 2 + (p[1] - cy) ** 2,
            p[0],
            p[1]
        ))

        return ordered

    def evaluate_wp(self, dept, spot, layout, rel_matrix, weight_map, alpha):
        wp = 0.0
        for (x, y), other_dept in layout.items():
            dx = spot[0] - x
            dy = spot[1] - y

            if abs(dx) + abs(dy) == 1:
                wp += weight_map[rel_matrix[(dept, other_dept)]]
            elif abs(dx) == 1 and abs(dy) == 1:
                wp += alpha * weight_map[rel_matrix[(dept, other_dept)]]

        return wp

    def place_department(self, dept, layout, rel_matrix, weight_map, alpha):
        ordered_spots = self.boundary_order_from_west(layout)
        best_spot = None
        best_wp = None

        for spot in ordered_spots:
            wp = self.evaluate_wp(dept, spot, layout, rel_matrix, weight_map, alpha)
            if best_wp is None or wp > best_wp:
                best_wp = wp
                best_spot = spot

        return best_spot, best_wp, ordered_spots

    # =========================================================
    #  CORELAP
    # =========================================================
    def corelap(self, n, rel_matrix, weight_map, tcr, count_A, alpha):
        all_depts = list(range(n))
        steps = []

        first = self.select_first_department(all_depts, tcr, count_A)

        placed_sequence = [first]
        layout = {(0, 0): first}
        placed = [first]
        remaining = set(all_depts) - {first}

        steps.append({
            "step": 1,
            "dept": first,
            "selection_reason": f"First department: largest TCR = {tcr[first]}",
            "placement_reason": "Placed at position 0",
            "position": (0, 0),
            "wp": "-"
        })

        reserved_last = self.choose_reserved_x_departments(first, remaining, rel_matrix, tcr)
        for d in reserved_last:
            remaining.remove(d)

        reserved_next_last = []

        if remaining:
            second, rel_letter = self.select_next_department(remaining, placed, rel_matrix, tcr)
            spot, wp, ordered_spots = self.place_department(second, layout, rel_matrix, weight_map, alpha)

            layout[spot] = second
            placed.append(second)
            placed_sequence.append(second)
            remaining.remove(second)

            steps.append({
                "step": 2,
                "dept": second,
                "selection_reason": f"Strongest relation to placed set = {rel_letter}; tie broken by largest TCR",
                "placement_reason": "Placed using western-edge boundary scan",
                "position": spot,
                "wp": f"{wp:.2f}"
            })

            reserved_next_last = self.choose_reserved_x_departments(second, remaining, rel_matrix, tcr)
            for d in reserved_next_last:
                remaining.remove(d)

            reserved_next_last = [d for d in reserved_next_last if d not in reserved_last]

        step_counter = len(placed_sequence) + 1
        while remaining:
            nxt, rel_letter = self.select_next_department(remaining, placed, rel_matrix, tcr)
            spot, wp, ordered_spots = self.place_department(nxt, layout, rel_matrix, weight_map, alpha)

            layout[spot] = nxt
            placed.append(nxt)
            placed_sequence.append(nxt)
            remaining.remove(nxt)

            steps.append({
                "step": step_counter,
                "dept": nxt,
                "selection_reason": f"Strongest relation to placed set = {rel_letter}; tie broken by largest TCR",
                "placement_reason": "Placed using western-edge boundary scan",
                "position": spot,
                "wp": f"{wp:.2f}"
            })
            step_counter += 1

        for d in reserved_next_last:
            spot, wp, ordered_spots = self.place_department(d, layout, rel_matrix, weight_map, alpha)
            layout[spot] = d
            placed.append(d)
            placed_sequence.append(d)

            steps.append({
                "step": step_counter,
                "dept": d,
                "selection_reason": "Reserved near the end due to X relationship with second department",
                "placement_reason": "Placed after normal candidates",
                "position": spot,
                "wp": f"{wp:.2f}"
            })
            step_counter += 1

        for d in reserved_last:
            spot, wp, ordered_spots = self.place_department(d, layout, rel_matrix, weight_map, alpha)
            layout[spot] = d
            placed.append(d)
            placed_sequence.append(d)

            steps.append({
                "step": step_counter,
                "dept": d,
                "selection_reason": "Reserved for the end due to X relationship with first department",
                "placement_reason": "Placed last",
                "position": spot,
                "wp": f"{wp:.2f}"
            })
            step_counter += 1

        return layout, placed_sequence, steps

    # =========================================================
    # Distance matrix
    # =========================================================
    def build_distance_matrix(self, n, layout):
        dist_matrix = [[0] * n for _ in range(n)]
        dept_coords = {dept: coord for coord, dept in layout.items()}

        for i in range(n):
            for j in range(n):
                if i != j:
                    xi, yi = dept_coords[i]
                    xj, yj = dept_coords[j]
                    dist_matrix[i][j] = abs(xi - xj) + abs(yi - yj)

        return dist_matrix

    # =========================================================
    # Run
    # =========================================================
    def run_algorithm(self):
        try:
            n = self.num_depts_var.get()
            if n < 2:
                raise ValueError("Number of departments must be at least 2.")

            alpha = self.partial_adj_var.get()
            weight_map = {k: v.get() for k, v in self.weights.items()}

            rel_matrix = self.build_rel_matrix(n)
            cv_matrix, tcr, count_A = self.build_cv_and_tcr(n, rel_matrix, weight_map)

            self.build_data_table(
                self.tab_cv,
                cv_matrix,
                n,
                title="Closeness Values (CV)",
                include_tcr=tcr,
                include_a_count=count_A
            )

            layout, placed_sequence, steps = self.corelap(
                n=n,
                rel_matrix=rel_matrix,
                weight_map=weight_map,
                tcr=tcr,
                count_A=count_A,
                alpha=alpha
            )

            dist_matrix = self.build_distance_matrix(n, layout)
            
            # --- CALCULATE LAYOUT SCORE ---
            
            layout_score = 0
            for i in range(n):
                for j in range(n):
                    if i != j:
                        layout_score += cv_matrix[i][j] * dist_matrix[i][j]

            self.draw_layout(layout, layout_score)

            self.build_data_table(
                self.tab_dist,
                dist_matrix,
                n,
                title="Rectilinear Distances Between Departments"
            )

            self.build_steps_table(steps)

            seq_text = " → ".join([f"D{d + 1}" for d in placed_sequence])
            messagebox.showinfo("CORELAP Completed", f"Placement sequence:\n{seq_text}\n\nTotal Layout Score: {layout_score}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================================================
    # Tables
    # =========================================================
    def build_data_table(self, parent_frame, data_matrix, n, title, include_tcr=None, include_a_count=None):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ttk.Label(parent_frame, text=title, font=('Arial', 12, 'bold')).pack(pady=10)

        tree_frame = ttk.Frame(parent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cols = ["Dept"] + [f"D{i + 1}" for i in range(n)]
        if include_a_count is not None:
            cols.append("No. of A")
        if include_tcr is not None:
            cols.append("TCR")

        tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=n)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=75, anchor=tk.CENTER)

        for i in range(n):
            row_data = [f"D{i + 1}"]
            for j in range(n):
                row_data.append("-" if i == j else data_matrix[i][j])

            if include_a_count is not None:
                row_data.append(include_a_count[i])
            if include_tcr is not None:
                row_data.append(tcr_value if False else include_tcr[i])

            tree.insert("", tk.END, values=row_data)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    def build_steps_table(self, steps):
        for widget in self.tab_steps.winfo_children():
            widget.destroy()

        ttk.Label(self.tab_steps, text="Selection / Placement Steps", font=('Arial', 12, 'bold')).pack(pady=10)

        cols = ("Step", "Department", "Selection Reason", "Placement Reason", "Position", "WP")
        tree = ttk.Treeview(self.tab_steps, columns=cols, show='headings', height=14)

        widths = {
            "Step": 60,
            "Department": 100,
            "Selection Reason": 360,
            "Placement Reason": 250,
            "Position": 100,
            "WP": 80
        }

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col], anchor=tk.CENTER)

        for s in steps:
            tree.insert(
                "",
                tk.END,
                values=(
                    s["step"],
                    f"D{s['dept'] + 1}",
                    s["selection_reason"],
                    s["placement_reason"],
                    str(s["position"]),
                    s["wp"]
                )
            )

        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # =========================================================
    # Layout drawing
    # =========================================================
    def draw_layout(self, layout, layout_score=None):
        self.canvas.delete("all")
        if not layout:
            return

        min_x = min(x for x, y in layout.keys())
        max_x = max(x for x, y in layout.keys())
        min_y = min(y for x, y in layout.keys())
        max_y = max(y for x, y in layout.keys())

        grid_cols = max_x - min_x + 1
        grid_rows = max_y - min_y + 1

        self.window.update_idletasks() 
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1:
            canvas_w, canvas_h = 800, 500

        cell_size = min(canvas_w / (grid_cols + 2), canvas_h / (grid_rows + 2))
        offset_x = (canvas_w - (grid_cols * cell_size)) / 2
        offset_y = (canvas_h - (grid_rows * cell_size)) / 2

        # Display the Score at the top
        if layout_score is not None:
            self.canvas.create_text(
                canvas_w / 2, 20, 
                text=f"Total Layout Score: {layout_score}", 
                font=("Arial", 14, "bold"), 
                fill="darkgreen"
            )

        for (x, y), dept in layout.items():
            cx = offset_x + (x - min_x) * cell_size
            cy = offset_y + (y - min_y) * cell_size

            self.canvas.create_rectangle(
                cx, cy, cx + cell_size, cy + cell_size,
                fill="#e1f5fe", outline="#0277bd", width=2
            )
            self.canvas.create_text(
                cx + cell_size / 2,
                cy + cell_size / 2,
                text=f"D{dept + 1}",
                font=("Arial", 15, "bold"),
                fill="#01579b"
            )







# =========================================================
# CRAFT Module
# =========================================================
class CraftGUI:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("CRAFT Layout Optimization")
        self.window.geometry("1300x950")
        self.grid_cells = {}
        self.final_grid_cells = {}
        self.score_mode = tk.StringVar(value="Directed From-To")
        
        # Craft Setup Variables
        self.proj_name = tk.StringVar(value="Production")
        self.num_depts = tk.IntVar(value=10)
        self.num_fixed = tk.IntVar(value=5)                   
        self.random_problem = tk.BooleanVar(value=True)
        
        # Facility & Calculation Variables
        self.scale_unit = tk.StringVar(value="m")             
        self.scale_val = tk.DoubleVar(value=1.0)              
        
        self.plant_length_unit = tk.DoubleVar(value=10.0)     
        self.plant_width_unit = tk.DoubleVar(value=10.0)      
        
        self.plant_length_cells = tk.IntVar(value=10)
        self.plant_width_cells = tk.IntVar(value=10)
        self.plant_area_unit = tk.DoubleVar(value=100.0)
        self.plant_area_cells = tk.IntVar(value=100)
        
        self.dept_width = tk.IntVar(value=5)                  
        self.dist_measure = tk.StringVar(value="Rectilinear")
        self.initial_solution = tk.StringVar(value="Sequential") 
        self.solution_method = tk.StringVar(value="Traditional Craft") 
        self.show_flows_var = tk.BooleanVar(value=False)
        
        # Data Dictionaries
        self.flow_entries = {}
        self.cost_entries = {}
        self.dept_info_entries = {}
        self.fixed_pos_entries = {}
        self.fixed_cost_entries = {}
        self.layout_entries = {}
        self.grid_cells = {}
        self.final_grid_cells = {}
        
        # Pastel Colors
        self.colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", 
                       "#E6B3FF", "#FFB3E6", "#E2F0CB", "#FFC8A2", "#D4F0F0", 
                       "#F3B0C3", "#C6D8FF"]

        self.scale_val.trace_add("write", self.update_calculations)
        self.plant_length_unit.trace_add("write", self.update_calculations)
        self.plant_width_unit.trace_add("write", self.update_calculations)

        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_setup = ttk.Frame(self.notebook)
        self.tab_data = ttk.Frame(self.notebook)
        self.tab_layout = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_setup, text="1. Setup & Facility Info")
        self.notebook.add(self.tab_data, text="2. Data Matrices & Initial Grid")
        self.notebook.add(self.tab_layout, text="3. Execution & Layout")

        self.build_setup_tab()
        self.build_data_tab()
        self.build_layout_tab()

    def build_setup_tab(self):
        f1 = ttk.LabelFrame(self.tab_setup, text="New Layout Problem", padding=10)
        f1.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(f1, text="Problem Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(f1, textvariable=self.proj_name).grid(row=0, column=1, pady=2)
        
        ttk.Label(f1, text="Number of Depts:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(f1, textvariable=self.num_depts).grid(row=1, column=1, pady=2)
        
        ttk.Label(f1, text="Number of Fixed Points:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(f1, textvariable=self.num_fixed).grid(row=2, column=1, pady=2)

        ttk.Label(f1, text="Scale Unit (m, ft, etc.):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(f1, textvariable=self.scale_unit).grid(row=3, column=1, pady=2)
        
        ttk.Checkbutton(f1, text="Make Random Problem", variable=self.random_problem).grid(row=0, column=2, rowspan=4, padx=40)

        f2 = ttk.LabelFrame(self.tab_setup, text="Define Facility & Parameters", padding=10)
        f2.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(f2, text="Distance Measure:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(f2, textvariable=self.dist_measure, values=["Rectilinear", "Euclidean"], width=13).grid(row=0, column=1, pady=2)

        ttk.Label(f2, text="Score Convention:").grid(row=0, column=5, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Combobox(
            f2,
            textvariable=self.score_mode,
            values=["Directed From-To", "Upper Triangle Only"],
            width=18,
            state="readonly"
        ).grid(row=0, column=6, pady=2, padx=5)
        
        ttk.Label(f2, text="Initial Solution:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(
                f2,
                textvariable=self.initial_solution,
                values=["Sequential", "Random", "Leave Blank"],
                width=13
            ).grid(row=1, column=1, pady=2)

        ttk.Label(f2, text="Solution Method:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(f2, textvariable=self.solution_method, values=["Opt. Sequence", "Traditional Craft"], width=13).grid(row=2, column=1, pady=2)

        ttk.Label(f2, text="Plant Length (units):").grid(row=0, column=3, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Entry(f2, textvariable=self.plant_length_unit, width=10).grid(row=0, column=4, pady=2, padx=5)
        
        ttk.Label(f2, text="Plant Width (units):").grid(row=1, column=3, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Entry(f2, textvariable=self.plant_width_unit, width=10).grid(row=1, column=4, pady=2, padx=5)

        ttk.Label(f2, text="Dept. Width (cells):").grid(row=2, column=3, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Entry(f2, textvariable=self.dept_width, width=10).grid(row=2, column=4, pady=2, padx=5)

        ttk.Button(f2, text="Generate Data Grids ->", command=self.generate_data_grids).grid(row=0, column=5, rowspan=4, padx=40)

    def build_data_tab(self):
        self.data_canvas = tk.Canvas(self.tab_data)
        scroll_y = ttk.Scrollbar(self.tab_data, orient="vertical", command=self.data_canvas.yview)
        scroll_x = ttk.Scrollbar(self.tab_data, orient="horizontal", command=self.data_canvas.xview)
        self.scroll_frame = ttk.Frame(self.data_canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all")))
        self.data_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.data_canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.data_canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.fac_frame = ttk.LabelFrame(self.scroll_frame, text="Facility Information", padding=10)
        self.fac_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.dept_frame = ttk.LabelFrame(self.scroll_frame, text="Department Information", padding=10)
        self.dept_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        self.initial_layout_frame = ttk.LabelFrame(self.scroll_frame, text="Initial Layout Grid (Manual Constraints)", padding=10)
        self.initial_layout_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

        self.row3_frame = ttk.Frame(self.scroll_frame)
        self.row3_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nw")
        
        self.flow_frame = ttk.LabelFrame(self.row3_frame, text="Flow Matrix", padding=10)
        self.flow_frame.pack(side=tk.LEFT, padx=(0, 20), anchor="nw")
        
        self.fixed_pos_frame = ttk.LabelFrame(self.row3_frame, text="Fixed Points", padding=10)
        self.fixed_pos_frame.pack(side=tk.LEFT, anchor="nw")

        self.row4_frame = ttk.Frame(self.scroll_frame)
        self.row4_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nw")
        
        self.cost_frame = ttk.LabelFrame(self.row4_frame, text="Cost Matrix (Default = 1)", padding=10)
        self.cost_frame.pack(side=tk.LEFT, padx=(0, 20), anchor="nw")
        
        self.fixed_cost_frame = ttk.LabelFrame(self.row4_frame, text="Fixed Point Costs", padding=10)
        self.fixed_cost_frame.pack(side=tk.LEFT, anchor="nw")

    def update_calculations(self, *args):
        try:
            scale = self.scale_val.get()
            if scale <= 0: scale = 1.0 
            
            l_unit = self.plant_length_unit.get()
            w_unit = self.plant_width_unit.get()
            
            l_cells = math.ceil(l_unit / scale)
            w_cells = math.ceil(w_unit / scale)
            
            self.plant_length_cells.set(l_cells)
            self.plant_width_cells.set(w_cells)
            self.plant_area_unit.set(round(l_unit * w_unit, 2))
            self.plant_area_cells.set(l_cells * w_cells)
            
            for i, data in self.dept_info_entries.items():
                area = data['area'].get()
                cells = math.ceil(area / (scale**2))
                data['cells'].set(cells)
        except tk.TclError: pass 

    def generate_data_grids(self):
        n = self.num_depts.get()
        m = self.num_fixed.get()
        is_random = self.random_problem.get()
        unit = self.scale_unit.get() or "unit"
        
        for w in self.fac_frame.winfo_children(): w.destroy()
        for w in self.dept_frame.winfo_children(): w.destroy()
        for w in self.flow_frame.winfo_children(): w.destroy()
        for w in self.cost_frame.winfo_children(): w.destroy()
        for w in self.fixed_pos_frame.winfo_children(): w.destroy()
        for w in self.fixed_cost_frame.winfo_children(): w.destroy()
        for w in self.initial_layout_frame.winfo_children(): w.destroy()
        
        self.fixed_pos_entries.clear()
        self.fixed_cost_entries.clear()
        self.layout_entries.clear()

        # 1. Facility Info
        ttk.Label(self.fac_frame, text=f"Scale-{unit}/unit", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        s_ent = ttk.Entry(self.fac_frame, textvariable=self.scale_val, width=8)
        s_ent.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.fac_frame, text="Cells", font=('Arial', 9, 'bold'), foreground="blue").grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(self.fac_frame, text=f"Length-{unit}").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.fac_frame, textvariable=self.plant_length_unit, width=8).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.fac_frame, textvariable=self.plant_length_cells, foreground="blue").grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(self.fac_frame, text=f"Width-{unit}").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.fac_frame, textvariable=self.plant_width_unit, width=8).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(self.fac_frame, textvariable=self.plant_width_cells, foreground="blue").grid(row=2, column=2, padx=5, pady=2)
        
        ttk.Label(self.fac_frame, text=f"Area-sq.{unit}").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.fac_frame, textvariable=self.plant_area_unit).grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(self.fac_frame, textvariable=self.plant_area_cells, foreground="blue").grid(row=3, column=2, padx=5, pady=2)
        
        # 2. Dept Info
        headers = ["Name", "F/V", "Area", "Cells"]
        for col, h in enumerate(headers):
            ttk.Label(self.dept_frame, text=h, font=('Arial', 9, 'bold')).grid(row=0, column=col, padx=5)
            
        self.dept_info_entries.clear()
        for i in range(n):
            ttk.Label(self.dept_frame, text=f"D {i+1}").grid(row=i+1, column=0)
            fv_var = tk.StringVar(value="V")
            ttk.Combobox(self.dept_frame, textvariable=fv_var, values=["V", "F"], width=3, state="readonly").grid(row=i+1, column=1)
            
            area_var = tk.DoubleVar(value=0.0)
            if is_random: area_var.set(round(random.uniform(10.0, 50.0), 1))
            ttk.Entry(self.dept_frame, textvariable=area_var, width=8).grid(row=i+1, column=2)
            
            cells_var = tk.IntVar(value=0)
            ttk.Label(self.dept_frame, textvariable=cells_var, width=8, foreground="blue").grid(row=i+1, column=3)
            
            self.dept_info_entries[i] = {'fv': fv_var, 'area': area_var, 'cells': cells_var}
            area_var.trace_add("write", self.update_calculations)

        self.update_calculations()

        # Manual Grid
        rows = self.plant_length_cells.get()
        cols = self.plant_width_cells.get()
        ttk.Label(
            self.initial_layout_frame,
            text="(Type Dept. Numbers here to force initial positions. 0 = empty)",
            foreground="gray"
        ).grid(row=0, column=0, columnspan=cols, pady=5, sticky="w")

        ttk.Button(
            self.initial_layout_frame,
            text="Clear Grid",
            command=self.clear_initial_layout_grid
        ).grid(row=0, column=cols, columnspan=2, padx=10, pady=5, sticky="e")
        for c in range(cols): ttk.Label(self.initial_layout_frame, text=str(c+1)).grid(row=1, column=c+1)
        for r in range(rows):
            ttk.Label(self.initial_layout_frame, text=str(r+1)).grid(row=r+2, column=0, padx=5)
            for c in range(cols):
                ent = ttk.Entry(self.initial_layout_frame, width=3, justify='center')
                ent.insert(0, "0")
                ent.grid(row=r+2, column=c+1, padx=1, pady=1)
                self.layout_entries[(r, c)] = ent

        # 3. Matrices
        ttk.Label(self.flow_frame, text="TO ->", foreground="red").grid(row=0, column=0, columnspan=n)
        ttk.Label(self.cost_frame, text="TO ->", foreground="red").grid(row=0, column=0, columnspan=n)
        for i in range(n):
            ttk.Label(self.flow_frame, text=f"D {i+1}", foreground="red").grid(row=i+1, column=0, padx=5)
            ttk.Label(self.cost_frame, text=f"D {i+1}", foreground="red").grid(row=i+1, column=0, padx=5)
            for j in range(n):
                f_ent = ttk.Entry(self.flow_frame, width=5)
                if i == j: f_ent.insert(0, "0")
                else: f_ent.insert(0, str(random.randint(0, 20)) if is_random else "")
                f_ent.grid(row=i+1, column=j+1, padx=2, pady=2)
                self.flow_entries[(i,j)] = f_ent
                
                c_ent = ttk.Entry(self.cost_frame, width=5)
                c_ent.insert(0, "0" if i==j else "1")
                c_ent.grid(row=i+1, column=j+1, padx=2, pady=2)
                self.cost_entries[(i,j)] = c_ent

        # 4. Fixed Points
        if m > 0:
            self.fixed_pos_frame.pack(side=tk.LEFT, anchor="nw")
            self.fixed_cost_frame.pack(side=tk.LEFT, anchor="nw")
            for col in range(m): ttk.Label(self.fixed_pos_frame, text=str(col+1)).grid(row=0, column=col+1, padx=5)
            ttk.Label(self.fixed_pos_frame, text="x-Prop.", foreground="red").grid(row=1, column=0, padx=5, sticky=tk.E)
            ttk.Label(self.fixed_pos_frame, text="y-Prop.", foreground="red").grid(row=2, column=0, padx=5, sticky=tk.E)
            for col in range(m):
                x_ent = ttk.Entry(self.fixed_pos_frame, width=5)
                x_ent.insert(0, str(random.randint(0, cols)) if is_random else "0")
                x_ent.grid(row=1, column=col+1, padx=2, pady=2)
                self.fixed_pos_entries[('x', col)] = x_ent
                
                y_ent = ttk.Entry(self.fixed_pos_frame, width=5)
                y_ent.insert(0, str(random.randint(0, rows)) if is_random else "0")
                y_ent.grid(row=2, column=col+1, padx=2, pady=2)
                self.fixed_pos_entries[('y', col)] = y_ent

            for col in range(m): ttk.Label(self.fixed_cost_frame, text=str(col+1)).grid(row=0, column=col+1, padx=5)
            for i in range(n):
                ttk.Label(self.fixed_cost_frame, text=f"D {i+1}").grid(row=i+1, column=0, padx=5)
                for j in range(m):
                    fc_ent = ttk.Entry(self.fixed_cost_frame, width=5)
                    fc_ent.insert(0, "0")
                    fc_ent.grid(row=i+1, column=j+1, padx=2, pady=2)
                    self.fixed_cost_entries[(i, j)] = fc_ent
        else:
            self.fixed_pos_frame.pack_forget()
            self.fixed_cost_frame.pack_forget()

        self.notebook.select(self.tab_data)

    def build_layout_tab(self):
        left_panel = ttk.Frame(self.tab_layout, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame,
            text="Generate Random Layout",
            command=self.generate_random_layout_to_grid
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Draw Manual Grid",
            command=self.process_and_draw_manual_grid
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Solve (CRAFT Iterations)",
            command=self.solve_craft
        ).grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        ttk.Checkbutton(
            btn_frame,
            text="Show Flows",
            variable=self.show_flows_var,
            command=self.redraw_layout_canvases
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.stats_tree = ttk.Treeview(
            left_panel,
            columns=("Dept", "Centroid X", "Centroid Y", "Inflow", "Outflow"),
            show='headings',
            height=8
        )
        for col in self.stats_tree["columns"]:
            self.stats_tree.heading(col, text=col)
            width = 60 if "flow" in col.lower() else 70
            self.stats_tree.column(col, width=width, anchor=tk.CENTER)
        self.stats_tree.pack(fill=tk.BOTH, expand=False)

        ttk.Label(left_panel, text="Iteration Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 2))
        self.log_text = tk.Text(left_panel, height=15, width=45, bg="#f4f4f4")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        right_panel = ttk.Frame(self.tab_layout)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        frame_initial = ttk.LabelFrame(right_panel, text="Initial Layout")
        frame_initial.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        self.canvas_initial = tk.Canvas(frame_initial, bg="white")
        self.canvas_initial.pack(fill=tk.BOTH, expand=True)

        frame_final = ttk.LabelFrame(right_panel, text="Final Optimized Layout")
        frame_final.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5, 0))
        self.canvas_final = tk.Canvas(frame_final, bg="white")
        self.canvas_final.pack(fill=tk.BOTH, expand=True)


    def generate_random_layout_to_grid(self):
        self.initial_solution.set("Random")
        self.process_and_draw_manual_grid()


    def clear_initial_layout_grid(self):
        rows = self.plant_length_cells.get()
        cols = self.plant_width_cells.get()

        for r in range(rows):
            for c in range(cols):
                self.layout_entries[(r, c)].delete(0, tk.END)
                self.layout_entries[(r, c)].insert(0, "0")


    def redraw_layout_canvases(self):
        if self.grid_cells:
            self.draw_grid_on_canvas(self.canvas_initial, self.grid_cells, update_stats=False)

        if self.final_grid_cells:
            self.draw_grid_on_canvas(self.canvas_final, self.final_grid_cells, update_stats=False)


    def get_required_cells(self, dept_id):
        dept_data = self.dept_info_entries.get(dept_id)
        if dept_data and 'cells' in dept_data:
            try:
                return int(dept_data['cells'].get())
            except (ValueError, TypeError):
                return 0
        return 0


    def get_aisle_cell_order(self):
        rows = self.plant_length_cells.get()
        cols = self.plant_width_cells.get()

        try:
            aisle_w = int(self.dept_width.get())
        except (ValueError, TypeError):
            aisle_w = 1

        if aisle_w <= 0:
            aisle_w = 1

        order = []
        aisle_index = 0

        for start_col in range(0, cols, aisle_w):
            end_col = min(start_col + aisle_w, cols)

            if aisle_index % 2 == 0:
                row_range = range(rows)
            else:
                row_range = range(rows - 1, -1, -1)

            for r in row_range:
                for c in range(start_col, end_col):
                    order.append((r, c))

            aisle_index += 1

        return order


    def fill_grid_from_sequence(self, dept_sequence):
        rows = self.plant_length_cells.get()
        cols = self.plant_width_cells.get()

        for r in range(rows):
            for c in range(cols):
                self.layout_entries[(r, c)].delete(0, tk.END)
                self.layout_entries[(r, c)].insert(0, "0")

        cell_order = self.get_aisle_cell_order()
        idx = 0

        for d in dept_sequence:
            need = self.get_required_cells(d)
            for _ in range(need):
                if idx >= len(cell_order):
                    return
                r, c = cell_order[idx]
                self.layout_entries[(r, c)].delete(0, tk.END)
                self.layout_entries[(r, c)].insert(0, str(d + 1))
                idx += 1


    def build_sequential_initial_layout(self):
        n = self.num_depts.get()
        seq = list(range(n))
        self.fill_grid_from_sequence(seq)


    def build_random_initial_layout(self):
        n = self.num_depts.get()
        seq = list(range(n))
        random.shuffle(seq)
        self.fill_grid_from_sequence(seq)


    def process_and_draw_manual_grid(self):
        n = self.num_depts.get()
        rows = self.plant_length_cells.get()
        cols = self.plant_width_cells.get()

        mode = self.initial_solution.get().strip()

        if mode == "Sequential":
            self.build_sequential_initial_layout()
        elif mode == "Random":
            self.build_random_initial_layout()
        
        self.grid_cells.clear()
        placed_counts = {i: 0 for i in range(n)}

        for r in range(rows):
            for c in range(cols):
                val = self.layout_entries[(r, c)].get().strip()
                try:
                    d = int(val) - 1
                    if 0 <= d < n:
                        self.grid_cells[(r, c)] = d
                        placed_counts[d] += 1
                except ValueError:
                    pass

        missing = []
        extra = []
        for i in range(n):
            req = self.get_required_cells(i)
            if placed_counts[i] < req:
                missing.append(f"D{i+1}: need {req}, found {placed_counts[i]}")
            elif placed_counts[i] > req:
                extra.append(f"D{i+1}: need {req}, found {placed_counts[i]}")

        if missing or extra:
            msg = []
            if missing:
                msg.append("Missing cells:\n" + "\n".join(missing))
            if extra:
                msg.append("Extra cells:\n" + "\n".join(extra))
            messagebox.showwarning("Layout / Area Mismatch", "\n\n".join(msg))

        self.final_grid_cells = {}
        if hasattr(self, "canvas_final"):
            self.canvas_final.delete("all")

        self.draw_grid_on_canvas(self.canvas_initial, self.grid_cells, update_stats=True)

        centroids = self.get_centroids_from_grid(self.grid_cells)
        initial_cost = self.calculate_cost(centroids) if centroids else 0.0

        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Initial Layout Cost: ${initial_cost:,.2f}\n")
        self.log_text.insert(tk.END, "-" * 40 + "\n")


    def draw_grid_on_canvas(self, canvas, grid_dict, update_stats=False):
        canvas.delete("all")
        cols = self.plant_width_cells.get()
        rows = self.plant_length_cells.get()
        n = self.num_depts.get()
        m = self.num_fixed.get()

        self.window.update_idletasks()
        cw, ch = canvas.winfo_width(), canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 500, 250

        cell_size = min(cw // (cols + 2), ch // (rows + 2))
        if cell_size < 10:
            cell_size = 20

        offset_x = (cw - (cols * cell_size)) / 2
        offset_y = (ch - (rows * cell_size)) / 2

        dept_cells = {i: [] for i in range(n)}

        if update_stats:
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)

        for (r, c), dept_id in grid_dict.items():
            dept_cells[dept_id].append((r, c))

            x1 = offset_x + c * cell_size
            y1 = offset_y + r * cell_size

            color = self.colors[dept_id % len(self.colors)]
            canvas.create_rectangle(
                x1, y1, x1 + cell_size, y1 + cell_size,
                fill=color, outline="gray"
            )
            canvas.create_text(
                x1 + cell_size / 2,
                y1 + cell_size / 2,
                text=str(dept_id + 1),
                fill="black",
                font=("Arial", 14, "bold")
            )

        centroids = {}
        for dept_id, assigned in dept_cells.items():
            if assigned:
                cx = sum(c + 0.5 for r, c in assigned) / len(assigned)
                cy = sum(r + 0.5 for r, c in assigned) / len(assigned)
                centroids[dept_id] = (cx, cy)

        for k in range(m):
            try:
                x_prop = float(self.fixed_pos_entries[('x', k)].get())
                y_prop = float(self.fixed_pos_entries[('y', k)].get())
            except ValueError:
                continue

            fx = x_prop * cols
            fy = y_prop * rows

            px = offset_x + fx * cell_size
            py = offset_y + fy * cell_size

            canvas.create_oval(
                px - 8, py - 8, px + 8, py + 8,
                fill="black", outline="red", width=2
            )
            canvas.create_text(
                px, py - 16,
                text=f"FP{k+1}",
                fill="black",
                font=("Arial", 10, "bold")
            )

        if self.show_flows_var.get():
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    if i not in centroids or j not in centroids:
                        continue

                    try:
                        f = float(self.flow_entries[(i, j)].get())
                    except ValueError:
                        continue

                    if f == 0:
                        continue

                    xi, yi = centroids[i]
                    xj, yj = centroids[j]

                    x1 = offset_x + xi * cell_size
                    y1 = offset_y + yi * cell_size
                    x2 = offset_x + xj * cell_size
                    y2 = offset_y + yj * cell_size

                    canvas.create_line(
                        x1, y1, x2, y2,
                        fill="red",
                        width=2,
                        arrow=tk.LAST
                    )

                    mx = (x1 + x2) / 2
                    my = (y1 + y2) / 2
                    label = str(int(f)) if float(f).is_integer() else f"{f:.1f}"

                    canvas.create_text(
                        mx, my - 8,
                        text=label,
                        fill="darkred",
                        font=("Arial", 9, "bold")
                    )

        if update_stats:
            for dept_id in range(n):
                if dept_id in centroids:
                    cx, cy = centroids[dept_id]

                    inflow = 0.0
                    outflow = 0.0
                    for j in range(n):
                        try:
                            outflow += float(self.flow_entries[(dept_id, j)].get())
                        except ValueError:
                            pass
                        try:
                            inflow += float(self.flow_entries[(j, dept_id)].get())
                        except ValueError:
                            pass

                    self.stats_tree.insert(
                        "",
                        tk.END,
                        values=(
                            f"D{dept_id + 1}",
                            f"{cx:.2f}",
                            f"{cy:.2f}",
                            f"{inflow:.1f}",
                            f"{outflow:.1f}",
                        )
                    )


    def get_centroids_from_grid(self, grid_dict):
        dept_cells = {}
        for (r, c), d in grid_dict.items():
            dept_cells.setdefault(d, []).append((r, c))

        centroids = {}
        for d, cells in dept_cells.items():
            cx = sum(c + 0.5 for r, c in cells) / len(cells)
            cy = sum(r + 0.5 for r, c in cells) / len(cells)
            centroids[d] = (cx, cy)

        return centroids


    def calculate_cost(self, centroids):
        cost = 0.0
        n = self.num_depts.get()
        m = self.num_fixed.get()
        measure = self.dist_measure.get()

        try:
            scale = float(self.scale_val.get())
        except ValueError:
            scale = 1.0

        cols = self.plant_width_cells.get()
        rows = self.plant_length_cells.get()

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if i not in centroids or j not in centroids:
                    continue

                try:
                    f = float(self.flow_entries[(i, j)].get())
                    c = float(self.cost_entries[(i, j)].get())
                except ValueError:
                    continue

                if f == 0 or c == 0:
                    continue

                xi, yi = centroids[i]
                xj, yj = centroids[j]

                if measure == "Rectilinear":
                    dist = abs(xi - xj) + abs(yi - yj)
                else:
                    dist = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)

                cost += f * c * dist * scale

        if m > 0:
            for i in range(n):
                if i not in centroids:
                    continue

                xi, yi = centroids[i]

                for k in range(m):
                    try:
                        fc = float(self.fixed_cost_entries[(i, k)].get())
                    except ValueError:
                        continue

                    if fc == 0:
                        continue

                    try:
                        x_prop = float(self.fixed_pos_entries[('x', k)].get())
                        y_prop = float(self.fixed_pos_entries[('y', k)].get())
                    except ValueError:
                        continue

                    fx = x_prop * cols
                    fy = y_prop * rows

                    if measure == "Rectilinear":
                        dist = abs(xi - fx) + abs(yi - fy)
                    else:
                        dist = math.sqrt((xi - fx) ** 2 + (yi - fy) ** 2)

                    cost += fc * dist * scale

        return cost


    def get_variable_departments(self, centroids):
        n = self.num_depts.get()
        return [
            i for i in range(n)
            if self.dept_info_entries[i]['fv'].get() == "V" and i in centroids
        ]


    def get_department_priority_scores(self, dept_list):
        scores = {}
        for i in dept_list:
            score = 0.0

            for j in dept_list:
                if i == j:
                    continue
                try:
                    fij = float(self.flow_entries[(i, j)].get())
                except ValueError:
                    fij = 0.0
                try:
                    fji = float(self.flow_entries[(j, i)].get())
                except ValueError:
                    fji = 0.0
                try:
                    cij = float(self.cost_entries[(i, j)].get())
                except ValueError:
                    cij = 0.0
                try:
                    cji = float(self.cost_entries[(j, i)].get())
                except ValueError:
                    cji = 0.0

                score += fij * cij + fji * cji

            for k in range(self.num_fixed.get()):
                try:
                    fc = float(self.fixed_cost_entries[(i, k)].get())
                except ValueError:
                    fc = 0.0
                score += fc

            scores[i] = score

        return scores


    def get_opt_sequence_pairs(self, dept_list):
        scores = self.get_department_priority_scores(dept_list)
        ordered = sorted(dept_list, key=lambda d: scores[d], reverse=True)

        pairs = []
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                pairs.append((ordered[i], ordered[j]))

        return pairs, scores


    def get_dept_cells(self, grid_dict, dept_id):
        return [pos for pos, d in grid_dict.items() if d == dept_id]


    def are_equal_area(self, grid_dict, d1, d2):
        return len(self.get_dept_cells(grid_dict, d1)) == len(self.get_dept_cells(grid_dict, d2))


    def are_adjacent(self, grid_dict, d1, d2):
        cells1 = set(self.get_dept_cells(grid_dict, d1))
        cells2 = set(self.get_dept_cells(grid_dict, d2))

        for r, c in cells1:
            if (r - 1, c) in cells2 or (r + 1, c) in cells2 or (r, c - 1) in cells2 or (r, c + 1) in cells2:
                return True
        return False


    def get_candidate_pairs(self, grid_dict, dept_list, ordered_pairs=None):
        if ordered_pairs is None:
            ordered_pairs = []
            for i in range(len(dept_list)):
                for j in range(i + 1, len(dept_list)):
                    ordered_pairs.append((dept_list[i], dept_list[j]))

        eligible = []
        for d1, d2 in ordered_pairs:
            if self.are_equal_area(grid_dict, d1, d2) or self.are_adjacent(grid_dict, d1, d2):
                eligible.append((d1, d2))

        return eligible


    def estimate_cost_by_centroid_swap(self, centroids, d1, d2):
        if d1 not in centroids or d2 not in centroids:
            return None

        est = dict(centroids)
        est[d1], est[d2] = est[d2], est[d1]
        return self.calculate_cost(est)


    def perform_spatial_swap(self, grid_dict, d1, d2):
        temp_grid = grid_dict.copy()

        cells_d1 = [pos for pos, d in temp_grid.items() if d == d1]
        cells_d2 = [pos for pos, d in temp_grid.items() if d == d2]

        if not cells_d1 or not cells_d2:
            return None

        if len(cells_d1) == len(cells_d2):
            for pos in cells_d1:
                temp_grid[pos] = d2
            for pos in cells_d2:
                temp_grid[pos] = d1
            return temp_grid

        combined = cells_d1 + cells_d2
        n1 = len(cells_d1)
        n2 = len(cells_d2)

        c1x = sum(c + 0.5 for r, c in cells_d1) / n1
        c1y = sum(r + 0.5 for r, c in cells_d1) / n1
        c2x = sum(c + 0.5 for r, c in cells_d2) / n2
        c2y = sum(r + 0.5 for r, c in cells_d2) / n2

        ranked_for_d1 = sorted(
            combined,
            key=lambda pos: (
                (pos[1] + 0.5 - c2x) ** 2 + (pos[0] + 0.5 - c2y) ** 2,
                pos[0],
                pos[1]
            )
        )

        d1_new = set(ranked_for_d1[:n1])
        d2_new = set(combined) - d1_new

        for pos in d1_new:
            temp_grid[pos] = d1
        for pos in d2_new:
            temp_grid[pos] = d2

        return temp_grid


    def run_traditional_craft(self, current_grid, current_cost, var_depts):
        iteration = 1

        while True:
            current_centroids = self.get_centroids_from_grid(current_grid)
            candidate_pairs = self.get_candidate_pairs(current_grid, var_depts)

            best_pair = None
            best_est_cost = current_cost

            for d1, d2 in candidate_pairs:
                est_cost = self.estimate_cost_by_centroid_swap(current_centroids, d1, d2)
                if est_cost is None:
                    continue
                if est_cost < best_est_cost:
                    best_est_cost = est_cost
                    best_pair = (d1, d2)

            if best_pair is None:
                break

            d1, d2 = best_pair

            self.log_text.insert(
                tk.END,
                f"Iter {iteration}: Best estimated swap = D{d1+1} & D{d2+1}\n"
                f" -> Estimated Cost: ${best_est_cost:,.2f}\n"
            )

            trial_grid = self.perform_spatial_swap(current_grid, d1, d2)
            if trial_grid is None:
                break

            actual_cost = self.calculate_cost(self.get_centroids_from_grid(trial_grid))

            self.log_text.insert(
                tk.END,
                f" -> Actual Cost After Swap: ${actual_cost:,.2f}\n"
            )

            if actual_cost >= current_cost - 0.01:
                self.log_text.insert(
                    tk.END,
                    " -> Actual switch did not improve the layout. Terminating.\n\n"
                )
                break

            old_cost = current_cost
            current_grid = trial_grid
            current_cost = actual_cost

            self.log_text.insert(
                tk.END,
                f" -> Accepted. Savings: ${old_cost - current_cost:,.2f}\n\n"
            )
            self.log_text.see(tk.END)
            self.window.update_idletasks()

            iteration += 1

        return current_grid, current_cost


    def run_opt_sequence_craft(self, current_grid, current_cost, var_depts):
        iteration = 1

        while True:
            current_centroids = self.get_centroids_from_grid(current_grid)
            pair_list, scores = self.get_opt_sequence_pairs(var_depts)
            candidate_pairs = self.get_candidate_pairs(current_grid, var_depts, pair_list)

            self.log_text.insert(tk.END, "\nOpt. Sequence ranking:\n")
            for d in sorted(var_depts, key=lambda x: scores[x], reverse=True):
                self.log_text.insert(
                    tk.END,
                    f" D{d+1} -> priority score = {scores[d]:,.2f}\n"
                )

            improved = False

            for d1, d2 in candidate_pairs:
                est_cost = self.estimate_cost_by_centroid_swap(current_centroids, d1, d2)
                if est_cost is None or est_cost >= current_cost - 0.01:
                    continue

                self.log_text.insert(
                    tk.END,
                    f"Iter {iteration}: Tested D{d1+1} & D{d2+1}"
                    f" -> Estimated Cost = ${est_cost:,.2f}\n"
                )

                trial_grid = self.perform_spatial_swap(current_grid, d1, d2)
                if trial_grid is None:
                    continue

                actual_cost = self.calculate_cost(self.get_centroids_from_grid(trial_grid))
                self.log_text.insert(
                    tk.END,
                    f" -> Actual Cost = ${actual_cost:,.2f}\n"
                )

                if actual_cost < current_cost - 0.01:
                    old_cost = current_cost
                    current_grid = trial_grid
                    current_cost = actual_cost

                    self.log_text.insert(
                        tk.END,
                        f" Accepted swap D{d1+1} & D{d2+1}\n"
                        f" Savings = ${old_cost - current_cost:,.2f}\n\n"
                    )

                    improved = True
                    iteration += 1
                    self.log_text.see(tk.END)
                    self.window.update_idletasks()
                    break
                else:
                    self.log_text.insert(
                        tk.END,
                        " Rejected: actual switch did not improve.\n\n"
                    )

            if not improved:
                break

        return current_grid, current_cost


    def solve_craft(self):
        if not self.grid_cells:
            messagebox.showwarning("Warning", "Please draw an Initial Layout first!")
            return

        current_grid = self.grid_cells.copy()
        centroids = self.get_centroids_from_grid(current_grid)
        current_cost = self.calculate_cost(centroids)

        var_depts = self.get_variable_departments(centroids)

        if len(var_depts) < 2:
            messagebox.showwarning("Warning", "Not enough variable departments to perform swaps.")
            return

        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, f"Initial Cost: ${current_cost:,.2f}\n")
        self.log_text.insert(tk.END, "-" * 40 + "\n")

        method = self.solution_method.get().strip()

        if method == "Opt. Sequence":
            self.log_text.insert(tk.END, "Running CRAFT - Opt. Sequence mode.\n\n")
            current_grid, current_cost = self.run_opt_sequence_craft(current_grid, current_cost, var_depts)
        else:
            self.log_text.insert(tk.END, "Running CRAFT - Traditional Craft mode.\n\n")
            current_grid, current_cost = self.run_traditional_craft(current_grid, current_cost, var_depts)

        self.log_text.insert(tk.END, "-" * 40 + "\n")
        self.log_text.insert(tk.END, f"FINAL SCORE (Z): ${current_cost:,.2f}\n")
        self.log_text.see(tk.END)

        self.final_grid_cells = current_grid.copy()
        self.draw_grid_on_canvas(self.canvas_final, self.final_grid_cells, update_stats=False)




# =========================================================
# Main Menu
# =========================================================
class FacilityLayoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Facility Layout Planning Suite")
        self.root.geometry("400x300")
        
        ttk.Label(root, text="Select Layout Algorithm", font=('Arial', 16, 'bold')).pack(pady=30)
        
        btn_corelap = ttk.Button(root, text="Launch CORELAP", command=self.open_corelap, width=25)
        btn_corelap.pack(pady=10)
        
        btn_craft = ttk.Button(root, text="Launch CRAFT", command=self.open_craft, width=25)
        btn_craft.pack(pady=10)

    def open_corelap(self):
        
        CorelapGUI(self.root)

    def open_craft(self):
        CraftGUI(self.root)



if __name__ == "__main__":
    root = tk.Tk()
    app = FacilityLayoutApp(root)
    root.mainloop()