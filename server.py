import asyncio
import os

import websockets

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "5555"))
clients = set()


async def handle_client(websocket):
    clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    if len(clients) == 2:
        websockets.broadcast(clients, "MATCH_START")

    try:
        async for message in websocket:
            if message.startswith("SHOT_HIT:"):
                _, damage = message.split(":", 1)
                for client in clients:
                    if client != websocket:
                        await client.send(f"DAMAGE:{damage}")
            else:
                for client in clients:
                    if client != websocket:
                        await client.send(message)
    finally:
        clients.discard(websocket)
        print(f"Client disconnected: {websocket.remote_address}")


async def main():
    print(f"WebSocket server listening on port {PORT}")
    async with websockets.serve(handle_client, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
