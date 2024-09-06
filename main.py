import asyncio


async def tcp_echo_client():
    host = 'minechat.dvmn.org'
    port = 5000

    try:
        print('starting connection')
        reader, writer = await asyncio.open_connection(host, port)

        while True:
            data = await reader.read(200)
            if not data:
                break
            print(f'Received: {data.decode()!r}')
            await asyncio.sleep(1)

    finally:
        print('Closing the connection.')
        writer.close()
        await writer.wait_closed()


async def main():
    while True:
        await tcp_echo_client()
        await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        print('Connection cancelled.')
    except KeyboardInterrupt:
        print("Program interrupted.")
