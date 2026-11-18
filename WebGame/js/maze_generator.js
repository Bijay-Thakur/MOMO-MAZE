// Maze Generator & Pathfinding for MOMO MAZE
// Approved 12x12 Living Maze from Concept Sheet + Procedural Campaign Mazes + 31x31 Grand Maze

import { MASTER_MAZE_31X31, CAMPAIGN_LEVELS } from './game_data.js';

// Approved 12x12 Maze Grid from Environment Concept Sheet (Panel 2)
// 1 = Hedge Wall, 0 = Grass Path, 2 = Leaf Gate Exit
export const APPROVED_12X12_MAZE = {
  size: 12,
  cellSize: 1.0,
  name: "The Morning Meadow (Approved 12×12)",
  grid: [
    [1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  // Row 0 (North, Leaf Gate at cols 5,6)
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  // Row 1
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],  // Row 2
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],  // Row 3
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],  // Row 4
    [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],  // Row 5
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1],  // Row 6
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  // Row 7 (Central crossroad)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],  // Row 8
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],  // Row 9
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],  // Row 10 (Bottom path, Player Start at (1, 10))
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   // Row 11 (South boundary)
  ],
  playerStart: { x: 1, y: 10 }, // Bottom-left corridor inside the maze!
  exitGate: { x: 5.5, y: 0 },    // North center Leaf Gate
  collectibles: [
    { x: 1, y: 9 }, // Directly in front of Golumolu!
    { x: 1, y: 7 }, // West corridor south
    { x: 1, y: 5 }, // West corridor mid
    { x: 1, y: 3 }, // West corridor north
    { x: 1, y: 1 }, // Northwest corner
    { x: 4, y: 7 }, // Central crossroad west
    { x: 7, y: 7 }, // Central crossroad east
    { x: 9, y: 7 }, // East crossroad
    { x: 10, y: 7 }, // East corridor mid
    { x: 10, y: 1 }, // Northeast corner
    { x: 3, y: 5 }, // Mid pathway
    { x: 6, y: 9 }  // South pathway
  ],
  movingGates: [],
  ghosts: [
    { type: 'follower', x: 2, y: 3 },
    { type: 'cutter', x: 9, y: 3 },
    { type: 'wanderer', x: 2, y: 9 }
  ],
  isBeautyMaster: true
};

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
      isGrand31: true,
      ghosts: [
        { type: 'follower', x: 11, y: 15 },
        { type: 'cutter', x: 19, y: 15 },
        { type: 'wanderer', x: 15, y: 25 }
      ]
    };
  }

  static generateCampaignLevel(levelConfig) {
    // Level 1 uses the 12x12 Approved Concept Maze!
    if (levelConfig.level_id === 1) {
      return JSON.parse(JSON.stringify(APPROVED_12X12_MAZE));
    }

    const size = levelConfig.grid_size || 15;
    const targetMomos = levelConfig.target_momos || 8;
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
        const [nx, ny, dx, dy] = neighbors[Math.floor(Math.random() * neighbors.length)];
        grid[cy + dy / 2][cx + dx / 2] = 0;
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

    // Player starts safely inside the bottom-left corridor
    const playerStart = { x: 1, y: size - 2 };
    // Exit gate at top-right corridor
    const exitGate = { x: size - 2, y: 1 };
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
      const shuffledPaths = [...pathCells].sort(() => 0.5 - Math.random());
      const gateCount = Math.min(6, Math.floor(pathCells.length / 8));
      for (let i = 0; i < gateCount; i++) {
        const pt = shuffledPaths[i];
        const phase = i % 2 === 0 ? 'A' : 'B';
        grid[pt.y][pt.x] = phase === 'A' ? 2 : 3;
        movingGates.push({ x: pt.x, y: pt.y, phase });
      }
    }

    // Place Momo dumplings only inside open corridor cells
    const remainingOpenCells = pathCells.filter(pt => grid[pt.y][pt.x] === 0);
    const shuffledForMomos = [...remainingOpenCells].sort(() => 0.5 - Math.random());
    const count = Math.min(targetMomos, shuffledForMomos.length);
    const collectibles = shuffledForMomos.slice(0, count).map(p => ({ x: p.x, y: p.y }));

    // Ghosts
    const ghosts = [
      { type: 'follower', x: size - 3, y: size - 3 }
    ];
    if (levelConfig.level_id >= 3) {
      ghosts.push({ type: 'cutter', x: size - 3, y: 2 });
    }
    if (levelConfig.level_id >= 6) {
      ghosts.push({ type: 'wanderer', x: 2, y: size - 3 });
    }

    return {
      size,
      grid,
      playerStart,
      exitGate,
      collectibles,
      movingGates,
      ghosts,
      isBeautyMaster: false
    };
  }

  // BFS Pathfinding on 2D Grid
  static findPath(grid, size, start, target, activePhase = 'A') {
    const queue = [[start]];
    const visited = new Set([`${start.x},${start.y}`]);

    const isWalkable = (x, y) => {
      if (x < 0 || x >= size || y < 0 || y >= size) return false;
      const cell = grid[y][x];
      if (cell === 1) return false; // Wall
      if (cell === 2 && activePhase === 'A') return false; // Gate A closed in Phase A
      if (cell === 3 && activePhase === 'B') return false; // Gate B closed in Phase B
      return true;
    };

    while (queue.length > 0) {
      const path = queue.shift();
      const curr = path[path.length - 1];

      if (curr.x === target.x && curr.y === target.y) {
        return path;
      }

      const dirs = [[0, -1], [0, 1], [-1, 0], [1, 0]];
      for (const [dx, dy] of dirs) {
        const nx = curr.x + dx;
        const ny = curr.y + dy;
        const key = `${nx},${ny}`;

        if (!visited.has(key) && isWalkable(nx, ny)) {
          visited.add(key);
          queue.push([...path, { x: nx, y: ny }]);
        }
      }
    }

    return []; // No path found
  }
}
