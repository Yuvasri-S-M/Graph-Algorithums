import tkinter as tk
from tkinter import messagebox, ttk
from collections import defaultdict
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Algorithms")

        self.graph = defaultdict(list)  
        self.nodes = set()

        input_frame = tk.Frame(root)
        input_frame.grid(row=0, column=0, sticky="w", padx=6, pady=6)

        tk.Label(input_frame, text="Source").grid(row=0, column=0)
        tk.Label(input_frame, text="Destination").grid(row=0, column=1)
        tk.Label(input_frame, text="Weight").grid(row=0, column=2)

        self.src_entry = tk.Entry(input_frame, width=8)
        self.dst_entry = tk.Entry(input_frame, width=8)
        self.wt_entry = tk.Entry(input_frame, width=6)

        self.src_entry.grid(row=1, column=0, padx=2)
        self.dst_entry.grid(row=1, column=1, padx=2)
        self.wt_entry.grid(row=1, column=2, padx=2)

        tk.Button(input_frame, text="Add Edge", command=self.add_edge).grid(row=1, column=3, padx=6)
        tk.Button(input_frame, text="Clear Graph", command=self.clear_graph).grid(row=1, column=4, padx=6)

        algo_frame = tk.Frame(root)
        algo_frame.grid(row=1, column=0, sticky="w", padx=6)
        self.algorithm = tk.StringVar(value="BFS")
        tk.OptionMenu(algo_frame, self.algorithm, "BFS", "DFS", "Kruskal", "Prim").grid(row=0, column=0, padx=2)

        tk.Label(algo_frame, text="Start Node:").grid(row=0, column=1, padx=(8,2))
        self.start_node_var = tk.StringVar(value="")
        self.start_node_cb = ttk.Combobox(algo_frame, textvariable=self.start_node_var, values=[], width=8)
        self.start_node_cb.grid(row=0, column=2, padx=2)

        tk.Button(algo_frame, text="Run", command=self.run_algorithm).grid(row=0, column=3, padx=6)

        display_frame = tk.Frame(root)
        display_frame.grid(row=2, column=0, padx=6, pady=6)

        self.output = tk.Text(display_frame, height=8, width=50)
        self.output.grid(row=0, column=0, sticky="nw")

        self.fig, self.ax = plt.subplots(figsize=(5,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=display_frame)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=8)
        plt.tight_layout()

        self.pos = None  

    def add_edge(self):
        u = self.src_entry.get().strip()
        v = self.dst_entry.get().strip()
        if not u or not v:
            messagebox.showerror("Input error", "Source and Destination cannot be empty")
            return
        try:
            w = int(self.wt_entry.get().strip()) if self.wt_entry.get().strip() else 1
        except ValueError:
            messagebox.showerror("Input error", "Weight must be an integer")
            return

        self.graph[u].append((v, w))
        self.graph[v].append((u, w))
        self.nodes.update([u, v])

        self.output.insert(tk.END, f"Added edge {u} --({w})-- {v}\n")
        self.src_entry.delete(0, tk.END)
        self.dst_entry.delete(0, tk.END)
        self.wt_entry.delete(0, tk.END)
        self.update_start_combobox()
        self.draw_graph()  

    def clear_graph(self):
        self.graph.clear()
        self.nodes.clear()
        self.output.delete("1.0", tk.END)
        self.update_start_combobox()
        self.pos = None
        self.ax.clear()
        self.canvas.draw()

    def update_start_combobox(self):
        vals = sorted(list(self.nodes))
        self.start_node_cb['values'] = vals
        if vals:
            self.start_node_var.set(vals[0])
        else:
            self.start_node_var.set("")

    def run_algorithm(self):
        algo = self.algorithm.get()
        start = self.start_node_var.get() if self.start_node_var.get() else (next(iter(self.nodes)) if self.nodes else None)
        if not start:
            messagebox.showerror("Error", "No graph defined or no start node selected")
            return

        self.output.insert(tk.END, f"\nRunning {algo} from {start}...\n")

        if algo == "BFS":
            order = self.bfs(start)
            self.output.insert(tk.END, f"BFS order: {' -> '.join(order)}\n")
            self.draw_graph(highlight_nodes=order, highlight_edges=None)

        elif algo == "DFS":
            order = self.dfs(start)
            self.output.insert(tk.END, f"DFS order: {' -> '.join(order)}\n")
            self.draw_graph(highlight_nodes=order, highlight_edges=None)

        elif algo == "Kruskal":
            mst = self.kruskal()
            self.output.insert(tk.END, f"Kruskal MST edges: {mst}\n")
            # edges are tuples (u, v, w)
            highlight = [(u, v) for u, v, w in mst]
            self.draw_graph(highlight_nodes=None, highlight_edges=highlight, edge_label=True)

        elif algo == "Prim":
            mst = self.prim(start)
            self.output.insert(tk.END, f"Prim MST edges: {mst}\n")
            highlight = [(u, v) for u, v, w in mst]
            self.draw_graph(highlight_nodes=None, highlight_edges=highlight, edge_label=True)

        else:
            self.output.insert(tk.END, "Algorithm not implemented\n")

    def bfs(self, start):
        visited, queue, order = set(), [start], []
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neigh, _ in self.graph[node]:
                    if neigh not in visited and neigh not in queue:
                        queue.append(neigh)
        for n in sorted(self.nodes):
            if n not in visited:
                order.append(n)
        return order

    def dfs(self, start):
        visited, stack, order = set(), [start], []
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neigh, _ in reversed(self.graph[node]):
                    if neigh not in visited:
                        stack.append(neigh)
        for n in sorted(self.nodes):
            if n not in visited:
                order.append(n)
        return order

    def kruskal(self):
        parent = {}
        rank = {}

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u, v):
            ru, rv = find(u), find(v)
            if ru == rv:
                return False
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            elif rank[ru] > rank[rv]:
                parent[rv] = ru
            else:
                parent[rv] = ru
                rank[ru] += 1
            return True

        edges = []
        seen = set()
        for u in self.graph:
            for v, w in self.graph[u]:
                key = tuple(sorted((u, v)) + [w]) if isinstance(w, int) else tuple(sorted((u, v)))
                if (u, v) not in seen and (v, u) not in seen:
                    edges.append((u, v, w))
                    seen.add((u, v))
                    seen.add((v, u))

        edges.sort(key=lambda x: x[2])

        for node in self.nodes:
            parent[node] = node
            rank[node] = 0

        mst = []
        for u, v, w in edges:
            if union(u, v):
                mst.append((u, v, w))
        return mst

    def prim(self, start):
        visited = set()
        edges = [(0, start, None)]
        mst = []
        while edges:
            w, u, prev = heapq.heappop(edges)
            if u in visited:
                continue
            visited.add(u)
            if prev is not None:
                mst.append((prev, u, w))
            for v, wt in self.graph[u]:
                if v not in visited:
                    heapq.heappush(edges, (wt, v, u))
        return mst

    def build_networkx_graph(self):
        G = nx.Graph()
        for u in self.graph:
            for v, w in self.graph[u]:
                G.add_edge(u, v, weight=w)
        for n in self.nodes:
            if n not in G:
                G.add_node(n)
        return G

    def draw_graph(self, highlight_nodes=None, highlight_edges=None, edge_label=False):
      
        G = self.build_networkx_graph()
        self.ax.clear()
        if self.pos is None:
            self.pos = nx.spring_layout(G, seed=42)
        else:
            try:
                self.pos = nx.spring_layout(G, pos=self.pos, seed=42)
            except Exception:
                self.pos = nx.spring_layout(G, seed=42)

        node_colors = []
        labels = {n: str(n) for n in G.nodes()}
        if highlight_nodes:
            highlight_set = set(highlight_nodes)
            order_idx = {n: i+1 for i, n in enumerate(highlight_nodes)}
            for n in G.nodes():
                if n in highlight_set:
                    node_colors.append('lightgreen')
                    labels[n] = f"{n}\n#{order_idx[n]}"
                else:
                    node_colors.append('lightblue')
        else:
            node_colors = ['lightblue' for _ in G.nodes()]

        all_edges = list(G.edges())
        default_edge_color = []
        width = []
        highlight_set_edges = set()
        if highlight_edges:
            for a, b in highlight_edges:
                if (a, b) in G.edges() or (b, a) in G.edges():
                    highlight_set_edges.add(tuple(sorted((a, b))))

        for a, b in all_edges:
            if tuple(sorted((a, b))) in highlight_set_edges:
                default_edge_color.append('red')
                width.append(2.5)
            else:
                default_edge_color.append('gray')
                width.append(1.0)

        nx.draw_networkx_nodes(G, self.pos, node_color=node_colors, node_size=700, ax=self.ax)
        nx.draw_networkx_labels(G, self.pos, labels=labels, font_size=8, ax=self.ax)
        nx.draw_networkx_edges(G, self.pos, edgelist=all_edges, edge_color=default_edge_color, width=width, ax=self.ax)

        if edge_label:
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, font_size=7, ax=self.ax)

        self.ax.set_axis_off()
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
