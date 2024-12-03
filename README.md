# Connect Four Game
This is a simple Connect Four game implemented using Python and sockets.

**How to play:** 
1. **Start the server:** `./server.py -p <port>` (`./server.py -h` for help)
2. **Connect clients:** `./client.py -i <host> -p <port>` (`./client.py -h` for help)
3. **In the Menu:** Upon launching the client you will be loaded into a menu. Here you can create and join lobbies. 
4. **In the Lobby:** Once in the lobby you can view the players in the lobby and change yourname using the shown commands. When 2 players have joined you may start the game. 
5. **In the Game:** Once in the game players will enter alternating `move <column>` comands to drop their chip into a column. The first player to get 4 in a row wins! After winning players will return to the lobby where they can play again and view the win counts. 

**Security/Risk Evaluation:**

The game has some security concerns that can be improved. Right now, the messages between the client and server are not encrypted, so anyone could potentially intercept them. In the future, using encryption like SSL/TLS could protect the data. The server is also at risk of being overloaded if someone intentionally creates too many lobbies or sends too much data. Adding limits to how many connections or actions are allowed could help. There’s no way to check who is connecting to the server, meaning anyone can join and take actions they shouldn’t. Adding user authentication could fix this. If two players try to do something at the same time, like make a move, it might cause problems because the server doesn’t manage those conflicts well. Using locks or other controls could prevent this. Finally, the server doesn’t handle unexpected disconnections or too much activity very well, which might cause crashes. Adding better ways to manage resources and timeouts for inactive players could make it more stable.

**Technologies used:**
* Python
* Sockets
* Threading

**Additional resources:**
* [Link to Python documentation](https://docs.python.org/3/)
* [Link to sockets tutorial](https://realpython.com/python-sockets/)


# Statement of Work for Multiplayer Connect Four Game

## Project Title:  
**Multiplayer Connect Four Game**

## Team:  
**Travis Barkley** (Solo Developer)

## Project Objective:  
To develop a Python-based multiplayer Connect Four game using client-server architecture to teach and apply fundamental concepts of networking and socket programming.

## Scope:  
**Inclusions**:
- Implement client-server architecture.
- Game logic (alternating turns, determining winner, handling draw conditions).
- Multiplayer capability with at least two clients.
- Error handling for network failures, invalid input, etc.

**Exclusions**:
- No advanced graphical interfaces.
- No AI opponents.

## Deliverables:
- Working client and server code.
- Documentation.
- Brief user instruction guide.
- Finished game product.

## Timeline:
- **Sprint 0**: Setup tools, submit SOW (Sept 08 - Sept 22).
- **Sprint 1**: Socket programming, TCP client-server (Sept 22 - Oct 06).
- **Sprint 2**: Develop game message protocol, manage client connections (Oct 06 - Oct 20).
- **Sprint 3**: Multiplayer functionality, synchronize state across clients (Oct 20 - Nov 03).
- **Sprint 4**: Game play, game state (Nov 03 - Nov 17).
- **Sprint 5**: Implement error handling and testing (Nov 17 - Dec 6).

## Task Breakdown:  
Tasks will follow the sprint breakdown and will be adjusted later with more detailed future planning.

## Technical Requirements:  
**Hardware**:  
Basic Linux servers or personal computers running Linux environments. Standard networking setup (DNS, IP addressing, TCP ports), and testing in a local environment on Linux terminals.

**Software**:  
Python, socket library, threading, Git, and VS Code as the IDE.

## Assumptions:
1. Stable network connectivity will be available for both server and clients during testing and deployment.
2. Necessary development resources (Linux environments, Python libraries, and hardware) will be available throughout the project.
3. Python libraries and tools (e.g., socket, threading) will remain compatible with the latest Python version.
4. Users will have basic knowledge of operating command-line interfaces (CLI).
5. No significant delays (e.g., hardware failures or personal interruptions) will impact the project timeline.

## Roles and Responsibilities:  
Travis Barkley will be responsible for all aspects of development, testing, and project management.

## Communication Plan:  
Travis will manage the project solo, conducting proper code reviews before approving pull requests and after each sprint to resolve any issues.
