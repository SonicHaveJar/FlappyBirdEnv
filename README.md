# Flappy Bird Env

Flappy Bird clone in python, ready to be used as a RL environment.

```
env = FlappyEnv()

obs = env.reset()

done = False
while not done:
    obs, reward, done = env.step(action)
```

Run ``` python env.py``` to play the game, or you can import ``` FlappyEnv ``` into your script.

## Gameplay
![Gif](gameplay.gif)