# Connect Four Game

## NOTE 
As of 10/20/24 23:00 MST work for sprint 2 has not been uploaded, I went on a very big rabbit hole today that has resulted in non functioning code, I will continue on tomorrow.  
This is a simple Connect Four game implemented using Python and sockets.

**How to play:** (To be implemented)
1. **Start the server:** `./server.py <host> <port>`
2. **Connect clients:** `./client.py <host> <port> <action>` *(current only action is "join")*
3. **Play the game:** Players take turns entering their moves. The first player to get four in a row wins!

**Technologies used:**
* Python
* Sockets

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
