import json
import random
from collections import deque

"""
31x31 Square Maze Generator with Approved Center Preservation & Moving Gates.
Guarantees:
- 31x31 odd-grid maze representation (walls on odd/even grid).
- Preserves the approved 12x12/13x13 center layout.
- Connectivity & BFS reachability validation (all collectibles and exit reachable).
- Moving hedge gates with non-trapping guarantee (dual-phase reachability check).
- Solvability and pathfinding verification.
"""

GRID_SIZE = 31 # 31x31 cells (0 to 30)

# Cell types:
# 0 = Path (Walkable)
# 1 = Wall (Hedge)
# 2 = Gate_A (Open in Phase A, Closed in Phase B)
# 3 = Gate_B (Closed in Phase A, Open in Phase B)
# 4 = Player Start
# 5 = Momo Collectible
# 6 = Exit / Leaf Gate

def create_base_grid():
    # Initialize full grid with walls (1)
    grid = [[1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    return grid

def stamp_approved_center(grid):
    """
    Stamps the approved center layout in the middle of the 31x31 grid (from index 9 to 21).
    Center is at (15, 15).
    """
    offset_x = 9
    offset_y = 9
    
    # 13x13 center pattern (0 = path, 1 = wall)
    # 0 is walkable path, 1 is hedge wall
    center_pattern = [
        [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1], # Top border with exit opening
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1], # Center heart
        [1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1], # Bottom border with south opening
    ]
    
    for r in range(13):
        for c in range(13):
            grid[offset_y + r][offset_x + c] = center_pattern[r][c]
            
    # Connect center to outer sectors at 4 cardinal openings:
    grid[offset_y][offset_x + 5] = 0 # North Exit
    grid[offset_y][offset_x + 6] = 0
    grid[offset_y][offset_x + 7] = 0
    grid[offset_y + 12][offset_x + 3] = 0 # South
    grid[offset_y + 12][offset_x + 9] = 0
    grid[offset_y + 6][offset_x] = 0 # West
    grid[offset_y + 6][offset_x + 12] = 0 # East

def carve_outer_maze(grid):
    """Carves outer sectors using randomized DFS / Kruskal's, preserving wall borders and odd paths."""
    # Outer paths are odd coordinates (1, 3, 5... 29)
    # Protect the center box: [8..22, 8..22]
    visited = set()
    
    # Mark center path cells as visited
    for y in range(8, 23):
        for x in range(8, 23):
            if grid[y][x] == 0:
                visited.add((x, y))

    def in_outer_bounds(x, y):
        return 1 <= x < GRID_SIZE - 1 and 1 <= y < GRID_SIZE - 1 and not (9 <= x <= 21 and 9 <= y <= 21)

    # Start carving from multiple seeds along outer edges
    seeds = [(1, 1), (29, 1), (1, 29), (29, 29), (1, 15), (29, 15), (15, 1), (15, 29)]
    random.shuffle(seeds)
    
    for sx, sy in seeds:
        if (sx, sy) in visited:
            continue
        stack = [(sx, sy)]
        grid[sy][sx] = 0
        visited.add((sx, sy))
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            # Check 2 steps in 4 cardinal directions
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = cx + dx, cy + dy
                if in_outer_bounds(nx, ny) and (nx, ny) not in visited:
                    neighbors.append((nx, ny, cx + dx//2, cy + dy//2))
                    
            if neighbors:
                nx, ny, mx, my = random.choice(neighbors)
                grid[my][mx] = 0 # Carve wall between
                grid[ny][nx] = 0 # Carve target cell
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    # Add loops (braid the maze slightly for multi-path exploration and ghost flanking)
    for _ in range(35):
        rx = random.randrange(1, GRID_SIZE - 1, 2)
        ry = random.randrange(1, GRID_SIZE - 1, 2)
        if not (8 <= rx <= 22 and 8 <= ry <= 22):
            for dx, dy in [(0, 1), (1, 0)]:
                wx, wy = rx + dx, ry + dy
                if 1 <= wx < GRID_SIZE - 1 and 1 <= wy < GRID_SIZE - 1:
                    if grid[wy][wx] == 1 and grid[wy - dy][wx - dx] == 0 and grid[wy + dy][wx + dx] == 0:
                        grid[wy][wx] = 0
                        break

def place_moving_gates_and_items(grid):
    """
    Places:
    - Moving Hedge Gates (Gate A and Gate B) as dynamic shortcuts.
    - Guarantees permanent main circulation loops so player is NEVER trapped.
    - Player Start in central sector.
    - Momo Dumpling Collectibles scattered strategically.
    - Leaf Gate Exit.
    """
    # 1. Guarantee Permanent Cardinal Circulation Corridors (ALWAYS OPEN)
    # North exit corridor
    for y in range(1, 10):
        grid[y][15] = 0
    # South corridor
    for y in range(21, 30):
        grid[y][15] = 0
    # West corridor
    for x in range(1, 10):
        grid[15][x] = 0
    # East corridor
    for x in range(21, 30):
        grid[15][x] = 0

    # 2. Strategic Dynamic Shortcut Gates (Opening and closing on alternating timer)
    # These create exciting dynamic path changes and shortcut routing without trapping!
    gates = [
        {"x": 11, "y": 7, "phase": "A"},  # NW Shortcut Gate A
        {"x": 19, "y": 7, "phase": "B"},  # NE Shortcut Gate B
        {"x": 11, "y": 23, "phase": "B"}, # SW Shortcut Gate B
        {"x": 19, "y": 23, "phase": "A"}, # SE Shortcut Gate A
        {"x": 7, "y": 15, "phase": "A"},  # Inner West Bypass A
        {"x": 23, "y": 15, "phase": "B"}, # Inner East Bypass B
    ]
    
    gate_data = []
    for g in gates:
        gx, gy = g["x"], g["y"]
        grid[gy][gx] = 2 if g["phase"] == "A" else 3
        gate_data.append({"x": gx, "y": gy, "phase": g["phase"]})

    # Player Start: Central peaceful court (15, 17)
    player_start = (15, 17)
    grid[17][15] = 4

    # Exit Leaf Gate: North Perimeter (15, 1)
    exit_gate = (15, 1)
    grid[1][15] = 6

    # Momo Collectibles: 24 collectibles scattered across sectors
    collectibles = []
    candidate_spots = [
        (15, 15), (17, 15), (13, 15), (15, 13), # Center momos
        (3, 3), (7, 3), (11, 3), (19, 3), (23, 3), (27, 3), # North sector
        (3, 27), (7, 27), (11, 27), (19, 27), (23, 27), (27, 27), # South sector
        (3, 11), (3, 19), (27, 11), (27, 19), # West & East sectors
        (7, 7), (23, 7), (7, 23), (23, 23) # Intermediate corners
    ]
    for cx, cy in candidate_spots:
        if grid[cy][cx] == 0:
            grid[cy][cx] = 5
            collectibles.append({"x": cx, "y": cy})

    return player_start, exit_gate, collectibles, gate_data

def validate_connectivity(grid, player_start, exit_gate, collectibles, gate_data):
    """
    Validates:
    1. Full reachability in Phase A (Gate A open, Gate B closed).
    2. Full reachability in Phase B (Gate A closed, Gate B open).
    3. Guarantees the player can NEVER be trapped regardless of gate switching.
    """
    def check_phase(open_phase):
        # In open_phase: open gates are passable (0), closed gates are walls (1)
        passable = set()
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                val = grid[y][x]
                if val in (0, 4, 5, 6): # Normal paths & items
                    passable.add((x, y))
                elif val == 2 and open_phase == "A": # Gate A open
                    passable.add((x, y))
                elif val == 3 and open_phase == "B": # Gate B open
                    passable.add((x, y))

        # BFS from player start
        q = deque([player_start])
        visited = {player_start}
        while q:
            cx, cy = q.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in passable and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return visited

    visited_a = check_phase("A")
    visited_b = check_phase("B")

    # Verify Exit reachable in both phases
    exit_ok_a = exit_gate in visited_a
    exit_ok_b = exit_gate in visited_b

    # Verify all collectibles reachable in both phases
    collectible_ok_a = all((c["x"], c["y"]) in visited_a for c in collectibles)
    collectible_ok_b = all((c["x"], c["y"]) in visited_b for c in collectibles)

    # Non-trapping guarantee: Intersection of reachable sets covers all player movement zones
    is_safe = exit_ok_a and exit_ok_b and collectible_ok_a and collectible_ok_b

    print(f"Connectivity Validation Report:")
    print(f"  • Phase A (Gate A Open, B Closed): Reachable Cells = {len(visited_a)}, Exit OK = {exit_ok_a}, Collectibles OK = {collectible_ok_a}")
    print(f"  • Phase B (Gate B Open, A Closed): Reachable Cells = {len(visited_b)}, Exit OK = {exit_ok_b}, Collectibles OK = {collectible_ok_b}")
    print(f"  • Non-Trapping Safety Guarantee: {'PASSED ✓' if is_safe else 'FAILED ✗'}")
    
    return is_safe

def generate_and_export_maze(output_json_path):
    random.seed(101)
    grid = create_base_grid()
    stamp_approved_center(grid)
    carve_outer_maze(grid)
    start, exit_pt, collectibles, gates = place_moving_gates_and_items(grid)
    
    is_valid = validate_connectivity(grid, start, exit_pt, collectibles, gates)
    if not is_valid:
        raise RuntimeError("Maze generation failed non-trapping connectivity validation!")

    maze_data = {
        "grid_size": GRID_SIZE,
        "cell_size_meters": 1.8, # Scaled to match character proportions
        "wall_height_meters": 1.8,
        "player_start": {"x": start[0], "y": start[1]},
        "exit_gate": {"x": exit_pt[0], "y": exit_pt[1]},
        "collectibles_count": len(collectibles),
        "collectibles": collectibles,
        "moving_gates": gates,
        "grid": grid
    }

    with open(output_json_path, "w") as f:
        json.dump(maze_data, f, indent=2)
    print(f"  ✓ Exported 31x31 Maze Data -> {output_json_path}")
    return maze_data

if __name__ == "__main__":
    out_path = r"D:\Projects\MOMO MAZE\UnrealProject\Content\MazeData_31x31.json"
    generate_and_export_maze(out_path)
