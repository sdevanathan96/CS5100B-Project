import time
import platform

from src.environments.custom_environments.complex_gridworld_environment import ComplexGridworld, Square, Item
from src.agent.base_agent import Agent
from src.agent.prompts import PromptLoader
from dotenv import load_dotenv
from src.gui.gui import GUI
from src.agent.actions import Action, format_actions

# Load the GROQ API KEY from a .env file
load_dotenv("../.env")


# Define the simulation logic in a function
def run_simulation(env, target_position, gui):
    # Initial observation of the agent's position
    print("Starting Gridworld Simulation...\n")
    agent_reached_target = False

    # Define the maximum number of episodes (steps)
    max_episodes = 10

    for episode in range(max_episodes):
        time.sleep(1)
        print("=" * 20 + f" Episode {episode + 1} of {max_episodes} " + "=" * 20 + "\n")
        for agent_id, agent in env.agents.items():
            observation = env.get_agent_position(agent_id)
            agent.observation = f"Your current position is: {observation}"

        for agent_id, agent in env.agents.items():
            if agent.termination_condition:
                break
            print(f"Agent {agent_id} Observation: {agent.observation}")

            # Agent makes a decision based on the current observation
            action = agent.step(agent.observation)

            # Extract the action name from the agent's response
            action_name = action.get("action_name", "invalid")
            print(f"Agent {agent_id} Action: {action_name}")
            print(f"Rationale: {action.get('rationale', 'No rationale provided.')}\n")

            # Execute the action in the environment
            agent.observation = env.step(agent.id, action_name)

            # Get the agent's current position
            agents_position = env.get_agent_position(agent_id)
            print(f"Agent {agent_id} Current Position: {agents_position}\n")

            # Check if the agent has reached the target position
            if agents_position == target_position:
                agent.termination_condition = True
                print(f"Agent {agent_id} has reached the target position {target_position}!")

        print("\n" + "=" * 50 + "\n")

        if agent_reached_target:
            time.sleep(1)
            break

    # Final summary
    if agent_reached_target:
        print("Simulation Complete: The agent successfully reached the target position!")
    else:
        print("Simulation Complete: The agent did not reach the target position within the maximum number of episodes.")

    # Stop the GUI when the simulation ends
    gui.is_running = False


if __name__ == '__main__':
    # Define start positions for multiple agents

    prompts = PromptLoader()

    system_prompt = prompts.load_prompt("gridworld_system_prompt")

    actions = [
        Action(name="north", description="Move one step upward on the grid."),
        Action(name="south", description="Move one step downward on the grid."),
        Action(name="west", description="Move one step to the left on the grid."),
        Action(name="east", description="Move one step to the right on the grid.")
    ]

    # Printing the formatted actions using the new function
    actions_description = format_actions(actions)

    output_instruction_text = """
    You are required to respond in JSON format only.

    Your response must include the following keys:
    1. **action_name**: The name of the action you intend to perform.
    2. **action_parameters**: Any specific parameters related to the action, such as step count or target position. If there are no parameters, use an empty dictionary.
    3. **rationale**: A brief explanation of why this action was chosen, considering the current state and objectives.

    Here is an example of the expected format:

    {
      "action_name": "north",
      "action_parameters": {"steps": 1},
      "rationale": "Moving up to get closer to the target position."
    }

    Remember, you must always output a JSON response following this structure.
    """

    target_position = (4, 4)
    agent_name = "Llama-agent-v1"

    variables = {
        "name": agent_name,
        "goal": f"Reach the target position at {target_position}.",
        "actions": actions_description,
    }

    system_prompt.set_variables(variables)

    system_prompt_str = str(system_prompt)
    system_prompt_str += output_instruction_text

    agent_one = Agent(
        agent_id=0,
        name=agent_name,
        action_space=[], # doesn't do anything currently
        system_prompt=system_prompt_str,
        start_position=(0, 0),
        color=(0, 0, 0)
    )

    agent_two = Agent(
        agent_id=1,
        name=agent_name + "2",
        action_space=[], # doesn't do anything currently
        system_prompt=system_prompt_str,
        start_position=(2, 2),
        color=(0, 0, 0)
    )

    agents = {
        agent_one.id: agent_one,
        agent_two.id: agent_two
    }

    # Initialize the gridworld environment
    env = ComplexGridworld(
        grid_size=(10, 10),
        agents=agents
    )

    env[target_position[0], target_position[1]] = Square(
        items=[
            Item(
                item_type="target",
                color=(0, 0, 100),
                shape="circle"
            )
        ]
    )

    gui = GUI(env, agents)

    gui.run(run_simulation, target_position)

