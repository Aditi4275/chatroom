import asyncio
import os

PORT = 4000

clients = {}  


async def broadcast(message, exclude_writer=None):
    to_remove = []
    for user, writer in clients.items():
        if writer is exclude_writer:
            continue
        try:
            writer.write(message.encode())
            await writer.drain()
        except Exception:
            to_remove.append(user)
    for user in to_remove:
        await remove_client(user)


async def remove_client(username):
    writer = clients.pop(username, None)
    if writer:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        await broadcast(f"INFO {username} disconnected\n")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peername = writer.get_extra_info('peername')
    username = None
    try:
        data = await reader.readline()
        if not data:
            writer.close()
            await writer.wait_closed()
            return
        login_line = data.decode().strip()
        if not login_line.startswith("LOGIN "):
            writer.write("ERR Invalid login\n".encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        username = login_line[6:].strip()
        if not username:
            writer.write("ERR Invalid username\n".encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        if username in clients:
            writer.write("ERR username-taken\n".encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        clients[username] = writer
        writer.write("OK\n".encode())
        await writer.drain()

        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            if message == "WHO":
                for user in clients:
                    writer.write(f"USER {user}\n".encode())
                await writer.drain()
            if message.startswith("MSG "):
                text = message[4:].strip()
                if text:
                    await broadcast(f"MSG {username} {text}\n", exclude_writer=writer)
            else:
                pass

    except Exception as e:
        print(f"Error from {peername}: {e}")
    finally:
        if username:
            await remove_client(username)


async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', PORT)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
