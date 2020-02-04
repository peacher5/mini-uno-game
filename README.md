## Mini UNO Terminal Game

> Protocol Design Project @ Computer Science, Kasetsart University

### Screenshots

<p align="center">
    <img src="../assets/wait.png?raw=true" alt="Screenshot 1" height="360" />
</p>

<p align="center">
    <img src="../assets/player_turn.png?raw=true" alt="Screenshot 2" height="360" />
</p>

<p align="center">
    <img src="../assets/opponent_turn.png?raw=true" alt="Screenshot 3" height="360" />
</p>

### Notes

- Python 3.6+ is required
- Minimum ternimal size is 73x19
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
