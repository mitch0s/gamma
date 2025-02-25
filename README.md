<p align="center" width="100%">
<img width="30%" src="https://i.ibb.co/8K4c6Mc/ezgif-2-b1c4d759f1.png">
</p>

# Gamma
### A Minecraft proxy implemented in Python

*Note: this project is not actively maintained which may lead to issues and bugs.*

Gamma is a reverse-TCP proxy for Minecraft networks implemented in Python using the `socket` package. Gamma supports multiple client connections to multiple servers. Players are proxied to the respective server depending on the hostname included in the first connection packet.

Join our [Discord Server!](https://discord.gg/NPyG3gAVtC)!

### Features
- Proxy Protocol
  - Gamma supports sending the `proxy protocol v1` heading to the server to forward player IPs
- Multiple Players
  - Gamma supports multiple player connections simultaneously
- Multiple Servers
  - Gamma supports proxying players to different servers depending on the hostname that they include in their server list
- Highly Customisable
  - In the `Connection` class, there are functions that get called when events happen. Here are a list of the current events that are triggered
    - `on_player_ping`
    - `on_invalid_hostname_ping`
    - `on_player_connect`
    - `on_player_disconnect`
    - `on_server_offline`

- Additionally to all of this, we also have a bandwidth counter, `self.conn_bandwidth` which counts the total amount of bytes sent and received from the `upstream` (server) or the `downstream` (player) connection. 



### Similar Projects
I would have to say that the biggest inspiration for this project would have to be [infrared](https://github.com/haveachin/infrared) by [haveachin](https://github.com/haveachin)

### Notes
- Proxy Protocol
  - Please be aware that when `proxy-protocol` is enabled, the server that the players will be proxied to has to be able to understand and read the proxy protocol header. Without this, the server can't understand the packet and drops it. If you're using `Waterfall`, you can turn set `proxy-protocol: true` in config.yml. Other server types normally have plugins to parse this kind of data.
  
  
### Getting Started
1. Clone the repo in whatever environment you wish
2. Install the following requirements: `requests`, `json`
3. In the same directory as the `main.py` file, run `python3 main.py` and watch the magic happen!
4. Give yourself a pat on the back :) 


### The Connection Object

|           Variable           |     Type      |                                               Description                                               |
|:----------------------------:|:-------------:|:-------------------------------------------------------------------------------------------------------:|
|      self.upstream_conn      | Socket Object |           The Socket object that contains the connection between the `server` and the `proxy`           |
|     self.downstream_conn     | Socket Object |           The Socket object that contains the connection between the `player` and the `proxy`           |
|   self.downstream_address    |     Tuple     |          A tuple that contains the `players` ip and port in the format `(ip: str, port: int)`           |
|       self.conn_alive        |    Boolean    | Determines whether the connection is active or disconnected, `True = Connected`, `False = Disconnected` |
|  self.upstream_packet_count  |    Integer    |                    The total number of packets transferred, from `Server` to `Gamma`                    |
| self.downstream_packet_count |    Integer    |                    The total number of packets transferred from `Player` to `Gamma`                     |
|     self.downstream_bandwidth      |    Integer    |         The total amount of bytes proxied from the `downstream` connection         |
|     self.upstream_bandwidth      |    Integer    |         The total amount of bytes proxied from the `upstream` connection         |
|      self.conn_hostname      |    String     |                  The hostname that the player has connected to from their server list                   |
|     self.player_username     |    String     |              The username of the proxied player, can be None if a username isn't detected               |
