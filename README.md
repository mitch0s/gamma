<p align="center" width="100%">
    <img width="30%" src="https://i.ibb.co/8K4c6Mc/ezgif-2-b1c4d759f1.png">
</p>

# Gamma
### A Minecraft proxy implemented in Python

Gamma is a reverse-TCP proxy for Minecraft networks implemented in Python using the `Socket` package.

### Features
- Multiple Players
  - The proxy supports multiple player connections simultaneously
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
