<p align="center" width="100%">
    <img width="30%" src="https://i.ibb.co/8K4c6Mc/ezgif-2-b1c4d759f1.png">
</p>

# Gamma
### A Minecraft proxy implemented in Python

Gamma is a reverse-TCP proxy for Minecraft networks implemented in Python using the `Socket` package. Gamma supports multiple client connections to multiple servers. Players are proxied to the respective server depending on the hostname included in the first connection packet.

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
    - `on_player_join`
    - `on_player_leave`

- Additionally to all of this, we also have a bandwidth counter, `self.conn_bandwidth` which counts the total amount of bytes sent and received from the `upstream` (server) or the `downstream` (player) connection. 



### Similar Projects
I would have to say that the biggest inspiration for this project would have to be [infrared](https://github.com/haveachin/infrared) by [haveachin](https://github.com/haveachin)

### Notes
- Proxy Protocol
  - Please be aware that when `proxy-protocol` is enabled, the server that the players will be proxied to has to be able to understand and read the proxy protocol header. Without this, the server can't understand the packet and drops it. If you're using `Waterfall`, you can turn set `proxy-protocol: true` in config.yml. Other server types normally have plugins to parse this kind of data.
