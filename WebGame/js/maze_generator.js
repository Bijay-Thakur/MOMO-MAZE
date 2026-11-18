// Maze Generator & Pathfinding for MOMO MAZE
// Supports custom sizes, moving gates, collectibles, and BFS navigation for AI

import { MASTER_MAZE_31X31, CAMPAIGN_LEVELS } from './game_data.js';

export class MazeGenerator {
  static getLevelConfig(levelId) {
    const found = CAMPAIGN_LEVELS.find(l => l.level_id === levelId);
    return found || CAMPAIGN_LEVELS[0];
  }

  static getMaster31x31Maze() {
    const data = MASTER_MAZE_31X31;
    return {
      size: data.grid_size,
      grid: JSON.parse(JSON.stringify(data.grid)),
      playerStart: { x: data.player_start.x, y: data.player_start.y },
      exitGate: { x: data.exit_gate.x, y: data.exit_gate.y },
      collectibles: JSON.parse(JSON.stringify(data.collectibles)),
      movingGates: JSON.parse(JSON.stringify(data.moving_gates || [])),
      isGrand31: true
    };
  }

  static generateCampaignLevel(levelConfig) {
    const size = levelConfig.grid_size || 15;
    const targetMomos = levelConfig.target_momos || 6;
    const hasMovingGates = !!levelConfig.has_moving_gates;

    // Grid: 1 = Wall, 0 = Path, 2 = Gate_A, 3 = Gate_B
    const grid = Array.from({ length: size }, () => Array(size).fill(1));

    // Carve maze with DFS from (1, 1)
    const stack = [[1, 1]];
    grid[1][1] = 0;
    const visited = new Set(['1,1']);

    while (stack.length > 0) {
      const [cx, cy] = stack[stack.length - 1];
      const neighbors = [];
      const dirs = [
        [0, -2], [0, 2], [-2, 0], [2, 0]
      ];

      for (const [dx, dy] of dirs) {
        const nx = cx + dx;
        const ny = cy + dy;
        if (nx > 0 && nx < size - 1 && ny > 0 && ny < size - 1 && !visited.has(`${nx},${ny}`)) {
          neighbors.push([nx, ny, dx, dy]);
        }
      }

      if (neighbors.length > 0) {
        // Pick random neighbor
        const [nx, ny, dx, dy] = neighbors[Math.floor(Math.random() * neighbors.length)];
        grid[cy + dy / 2][cx + dx / 2] = 0; // Carve wall between
        grid[ny][nx] = 0;
        visited.add(`${nx},${ny}`);
        stack.push([nx, ny]);
      } else {
        stack.pop();
      }
    }

    // Add extra pathway loops for cozy exploration and multiple routes
    const loopFactor = Math.floor(size * 0.7);
    for (let i = 0; i < loopFactor; i++) {
      const rx = 1 + Math.floor(Math.random() * (size - 2));
      const ry = 1 + Math.floor(Math.random() * (size - 2));
      if (grid[ry][rx] === 1) {
        // Only remove wall if it joins two separate paths
        let adjacentPaths = 0;
        if (grid[ry - 1]?.[rx] === 0) adjacentPaths++;
        if (grid[ry + 1]?.[rx] === 0) adjacentPaths++;
        if (grid[ry]?.[rx - 1] === 0) adjacentPaths++;
        if (grid[ry]?.[rx + 1] === 0) adjacentPaths++;
        if (adjacentPaths === 2) {
          grid[ry][rx] = 0;
        }
      }
    }

    const playerStart = { x: 1, y: 1 };
    const exitGate = { x: size - 2, y: size - 2 };
    grid[playerStart.y][playerStart.x] = 0;
    grid[exitGate.y][exitGate.x] = 0;

    // Collect all open walkable cells
    const pathCells = [];
    for (let y = 1; y < size - 1; y++) {
      for (let x = 1; x < size - 1; x++) {
        if (grid[y][x] === 0 && !(x === playerStart.x && y === playerStart.y) && !(x === exitGate.x && y === exitGate.y)) {
          pathCells.push({ x, y });
        }
      }
    }

    // Place Moving Gates if enabled
    const movingGates = [];
    if (hasMovingGates && pathCells.length > 20) {
      const gateCount = Math.min(6, Math.max(2, Math.floor(size / 6)));
      // Find choke points (cells with 2 wall neighbors opposite)
      for (let i = 0; i < pathCells.length && movingGates.length < gateCount; i++) {
        const idx = Math.floor(Math.random() * pathCells.length);
        const { x, y } = pathCells[idx];
        const isHorizontalChoke = grid[y][x - 1] === 1 && grid[y][x + 1] === 1 && grid[y - 1][x] === 0 && grid[y + 1][x] === 0;
        const isVerticalChoke = grid[y - 1][x] === 1 && grid[y + 1][x] === 1 && grid[y][x - 1] === 0 && grid[y][x + 1] === 0;

        if ((isHorizontalChoke || isVerticalChoke) && !movingGates.some(g => Math.hypot(g.x - x, g.y - y) < 4)) {
          const phase = movingGates.length % 2 === 0 ? 'A' : 'B';
          grid[y][x] = phase === 'A' ? 2 : 3;
          movingGates.push({ x, y, phase });
          pathCells.splice(idx, 1);
        }
      }
    }

    // Distribute Momo collectibles evenly along paths
    const collectibles = [];
    const needed = Math.min(targetMomos, pathCells.length);
    // Shuffle pathCells
    for (let i = pathCells.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pathCells[i], pathCells[j]] = [pathCells[j], pathCells[i]];
    }

    for (let i = 0; i < needed; i++) {
      collectibles.push({ x: pathCells[i].x, y: pathCells[i].y });
    }

    return {
      size,
      grid,
      playerStart,
      exitGate,
      collectibles,
      movingGates,
      isGrand31: false
    };
  }

  // Pathfinding (BFS) from (startX, startY) to (targetX, targetY)
  // Considers moving gates state (activePhase: 'A' | 'B')
  static findPath(grid, size, start, target, activePhase = 'A') {
    if (!start || !target) return [];
    const queue = [[start.x, start.y]];
    const parent = new Map();
    const visited = new Set([`${start.x},${start.y}`]);

    let found = false;

    while (queue.length > 0) {
      const [cx, cy] = queue.shift();
      if (cx === target.x && cy === target.y) {
        found = true;
        break;
      }

      const dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]];
      for (const [dx, dy] of dirs) {
        const nx = cx + dx;
        const ny = cy + dy;
        const key = `${nx},${ny}`;

        if (nx >= 0 && nx < size && ny >= 0 && ny < size && !visited.has(key)) {
          const cell = grid[ny][nx];
          // 0 is path
          // 2 is Gate A (walkable if activePhase === 'B', blocked if activePhase === 'A')
          // 3 is Gate B (walkable if activePhase === 'A', blocked if activePhase === 'B')
          let isWalkable = cell === 0;
          if (cell === 2 && activePhase === 'B') isWalkable = true;
          if (cell === 3 && activePhase === 'A') isWalkable = true;

          if (isWalkable) {
            visited.add(key);
            parent.set(key, [cx, cy]);
            queue.push([nx, ny]);
          }
        }
      }
    }

    if (!found) return [];

    // Reconstruct path
    const path = [];
    let curr = [target.x, target.y];
    while (curr) {
      path.unshift({ x: curr[0], y: curr[1] });
      const p = parent.get(`${curr[0]},${curr[1]}`);
      if (!p) break;
      curr = p;
    }
    return path;
  }
}
