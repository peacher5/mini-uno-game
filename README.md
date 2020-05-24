## Mini UNO Terminal Game

> Protocol Design Project @ Computer Science, Kasetsart University

### Screenshots

<p align="center">
    <img src="../assets/wait.png?raw=true" alt="Welcome screenshot" width="618" />
</p>

<p align="center">
    <img src="../assets/player_turn.png?raw=true" alt="Player turn screenshot" width="618" />
</p>

<p align="center">
    <img src="../assets/opponent_turn.png?raw=true" alt="Opponent turn screenshot" width="618" />
</p>

### Notes

- Python 3.6+ is required
- Minimum terminal size is 73x19
- Tested on macOS Catalina (iTerm) & Windows 10 (CMD, PowerShell)

### Starting a server

```sh
$ python3 server.py
```

### Running a client

#### Localhost server

```sh
$ python3 client.py
```

#### Any server

```sh
$ python3 client.py 158.108.30.234
```
