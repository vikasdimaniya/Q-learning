import custom_env_multi_agent

env = custom_env_multi_agent.MultiAgentEnv()

obs, _ = env.reset()
done = False

try:
    while not done:
        actions = [env.action_space.sample() for _ in range(len(env.simmap.agents))]
        obs, reward, done, truncated, info = env.step(actions)
        env.render()
finally:
    env.close()