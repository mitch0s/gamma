import asyncio
from gamma.net.player_connection import PlayerConnection
from gamma.net.server_connection import ServerConnection
from gamma.net.connection_relay import ConnectionRelay
from gamma.response.invalid_hostname_motd import invalid_hostname_motd


async def handle_player(reader, writer):
    player_conn = PlayerConnection(reader, writer)
    server_conn = ServerConnection(host='localhost', port=25560)
    relay = ConnectionRelay(downstream=player_conn, upstream=server_conn)
    await relay.start()


async def main():
    server = await asyncio.start_server(handle_player, '0.0.0.0', 25565)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())