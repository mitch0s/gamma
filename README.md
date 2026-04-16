<p align="center" width="100%">
<img width="30%" src="https://i.ibb.co/8K4c6Mc/ezgif-2-b1c4d759f1.png">
</p>

# Gamma
### Asynchronous Reverse Proxy for Minecraft Networks

*It's back! Gamma is now under active development, focusing mainly on an async reimplementation of the core proxy. You can see the latest developments on the [development branch](https://github.com/mitch0s/gamma/tree/development). You may also want to join the [Discord Server!](https://discord.gg/NPyG3gAVtC)!*

Gamma is a reverse proxy for Minecraft networks implemented in Python using asyncio. Gamma supports relaying traffic between multiple client connections to multiple servers. Players are proxied to the respective server depending on the hostname included in the first connection packet.


## Features
| Status | Feature | Description |
| :----: | ------- | ----------- |
| ✅ | Asynchronous&nbsp;I/O    |  Gamma is written around asynchronous network communication, which brings a multitude of benefits such as lower memory usage. |
| ✅ | Multiple&nbsp;Players    |  Gamma supports multiple simultaneous player (client) connections. |
| ✅ | Multiple&nbsp;Backends   |  Gamma supports multiple configured backends (Minecraft servers). |
| ✅ | Packet&nbsp;Pipeline     |  Gamma allows users to easily implement PacketHandler subclasses and register them in the packet pipeline of any Connection object. |
| ✅ | Packet&nbsp;Pipeline     |  Gamma allows users to easily implement PacketHandler subclasses and register them in the packet pipeline of any Connection object. |
| ✅ | Config&nbsp;Manager      |  Backend configuration management has not been implemented in the async rewrite just yet. |
| 🚧 | Proxy&nbsp;Protocol      |  Support for sending client addresses to upstream server using the `PROXY TCP4` header has not been implemented in the async rewrite just yet. |
| ❌ | Terminal&nbsp;Interface  |  Terminal interface using the [Textual](https://github.com/textualize/textual) package that displays per-player or global connection information. |
| ❌ | Docker Support           |  Docker containerization config (dockerfile)  |
| ❌ | Crosstalk                |  Peer discovery and communication mechanism allowing your distributed Gamma instances discover and communicate player + network information with each-other.  |

## Installation
| Step | Description | Command |
| :-: | --- | --- |
| 1 | Clone repo | `git clone https://github.com/mitch0s/gamma/` |
| 2 | Change directory to 'gamma/' | `cd gamma/` |
| 3 | Create Python Virtual Environment (venv) | `python -m venv venv` |
| 4 | Activate Virtual Environment | `./venv/Scripts/activate` (_Note: activation command different on MacOS/Linux_) |
| 5 | Install Package Requirements | `pip install -r requirements.txt` |
| 6 | Change directory to 'src/' | `cd src/` |
| 7 | Start Gamma | `python main.py` |
| 8 | Done | Gamma should now running in the same terminal. |

## How Does Gamma Work?
<img width="1502" height="484" alt="image" src="https://github.com/user-attachments/assets/28ed9db7-94ba-40b9-90b5-d6adc11a2f9e" />

1. Minecraft client (client) sends DNS request to resolve _some_ hostname.
2. DNS server resolves and returns an IPv4 address to the client. This address points to a machine running Gamma.
3. Client connects to the machine running Gamma, and sends a handshake packet that includes the user-entered hostname ('server.com').
4. While no upstream connection is established, Gamma buffers packets from the client and scans them for the hostname (and later username).
5. Once the hostname is extracted, Gamma requests a config for the specified hostname.
    1. _If no config for the hostname is found, Gamma responds with an "invalid hostname" MOTD/Disconnect message, and closes the connection._
6. ConnectionRelay reads the hostname config and opens a connection to the specified host:port (+some other logic depending on config).
7. The buffered handshake packets received from client earlier are forwarded to upstream server.
8. ConnectionRelay enters 'forwarding' mode, and directly passes packets between upstream and downstream until one of the connections are closed.
    1. _Packets are passed through PacketHandler instances registered with the Connection instance being read from before being forwarded._

## More documentation coming soon!
  
  
### Similar Projects
Gamma is partly inspired by [infrared](https://github.com/haveachin/infrared).
