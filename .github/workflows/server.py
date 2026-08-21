import asyncio
import websockets

SERVER_IP = '127.0.0.1'
PORT = 5555

clients = set()

async def handle_client(websocket):
    print(f"New connection secured from client: {websocket.remote_address}")
    clients.add(websocket)

    # Check if a pair of distinct game processes have completed handshake sequence
    if len(clients) == 2:
        print("Required active player count achieved. Directing client game-state modification...")
        # Send match start signal to all connected clients
        websockets.broadcast(clients, "MATCH_START")

    try:
        async for message in websocket:
            # Catch inbound bullet confirmation vectors and proxy damage onto the opposite network target
            if message.startswith("SHOT_HIT:"):
                try:
                    _, dmg = message.split(":")
                    damage_packet = f"DAMAGE:{dmg}"
                    # Route damage exclusively to the alternate socket connection
                    for c in clients:
                        if c != websocket:
                            await c.send(damage_packet)
                except Exception:
                    pass
            else:
                # Basic execution path: forward client transformation coordinates (MOVE:)
                for c in clients:
                    if c != websocket:
                        await c.send(message)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print(f"Connection terminated/dropped by client address: {websocket.remote_address}")
        clients.discard(websocket)

async def main():
    print(f"Matchmaking WebSocket server listening on port {PORT}...")
    async with websockets.serve(handle_client, SERVER_IP, PORT):
        await asyncio.Future()  # Keep server running perpetually

if __name__ == "__main__":
    asyncio.run(main())