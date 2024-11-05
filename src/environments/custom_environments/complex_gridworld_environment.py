import numpy as np
from typing import Tuple, Dict, List


class Item:
    def __init__(self, item_type: str, color: Tuple[int, int, int], shape: str):
        self.item_type = item_type
        self.color = color
        self.shape = shape

    def __repr__(self):
        return f"Item(type={self.item_type}, color={self.color}, shape={self.shape})"


class Square:
    def __init__(self, obstacle: bool = False, items: List[Item] = None):
        self.obstacle = obstacle
        self.agent_id = None
        self.items = items if items else []

    def is_empty(self):
        return not self.obstacle and self.agent_id is None and not self.items

    def has_items(self):
        return bool(self.items)

    def pick_up_item(self):
        return self.items.pop() if self.items else None


class ComplexGridworld:
    def __init__(
            self,
            grid_size: Tuple[int, int] = (10, 10),
            start_positions: Dict[int, Tuple[int, int]] = None,
            obstacles: List[Tuple[int, int]] = None,
            items: Dict[Tuple[int, int], List[Item]] = None
    ):

        self.grid_size = grid_size
        self.grid = [[Square() for _ in range(grid_size[1])] for _ in range(grid_size[0])]
        self.start_positions = start_positions if start_positions else {0: (0, 0)}
        self.agent_positions = self.start_positions.copy()
        self.agents = set(self.start_positions.keys())

        # Place obstacles
        if obstacles:
            for (row, col) in obstacles:
                self.grid[row][col].obstacle = True

        # Place items
        if items:
            for (row, col), item_list in items.items():
                self.grid[row][col].items.extend(item_list)

        # Place agents in their starting positions
        for agent_id, pos in self.agent_positions.items():
            self.grid[pos[0]][pos[1]].agent_id = agent_id

    def __getitem__(self, key):
        """Support both single index and tuple index access."""
        if isinstance(key, tuple):
            row, col = key
            return self.grid[row][col]
        return self.grid[key]

    def __setitem__(self, key, value):
        """Support both single index and tuple index assignment."""
        if isinstance(key, tuple):
            row, col = key
            self.grid[row][col] = value
        else:
            self.grid[key] = value

    def reset(self):
        """Resets the environment to its initial state."""
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                self.grid[row][col].agent_id = None

        self.agent_positions = self.start_positions.copy()
        for agent_id, pos in self.agent_positions.items():
            self.grid[pos[0]][pos[1]].agent_id = agent_id
        return self.agent_positions

    def step(self, agent_id: int, action: str) ->  str:
        """Execute a step for the specified agent."""
        if agent_id not in self.agent_positions:
            return f"Agent ID {agent_id} not found in the environment."

        if action not in ['north', 'south', 'east', 'west']:
            return f"Invalid action: '{action}'. Valid actions are ['north', 'south', 'east', 'west']."

        current_pos = self.agent_positions[agent_id]
        row, col = current_pos

        new_row, new_col = row, col
        if action == 'north':
            new_row = min(self.grid_size[0] - 1, row + 1)
        elif action == 'south':
            new_row = max(0, row - 1)
        elif action == 'east':
            new_col = min(self.grid_size[1] - 1, col + 1)
        elif action == 'west':
            new_col = max(0, col - 1)

        # Check if the new position is different from the current position
        if (new_row, new_col) == (row, col):
            return f"Agent {agent_id} tried to move '{action}', but it cannot move further in that direction."

        target_square = self.grid[new_row][new_col]
        if target_square.obstacle:
            return "Cannot move into obstacle."

        # Update grid and agent's position
        self.grid[row][col].agent_id = None
        self.agent_positions[agent_id] = (new_row, new_col)
        self.grid[new_row][new_col].agent_id = agent_id

        return f"Agent {agent_id} moved '{action}' from {current_pos} to {(new_row, new_col)}."

    def get_agent_position(self, agent_id: int):
        """Get the position of a specific agent."""
        return self.agent_positions.get(agent_id, None)

    def get_all_agent_positions(self) -> Dict[int, Tuple[int, int]]:
        """Get positions of all agents."""
        return self.agent_positions.copy()