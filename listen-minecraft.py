import os
import argparse
import asyncio
import datetime
import aiofiles
import configargparse

async def tcp_echo_client(host, port, chat_history):
    # host = 'minechat.dvmn.org'
    # port = 5000

    try:
        print('starting connection')
        reader, writer = await asyncio.open_connection(host, port)

        while True:
            data = await reader.read(200)
            if not data:
                break
            print(f'Received: {data.decode()!r}')
            async with aiofiles.open(chat_history, "a", encoding='UTF-8') as f:
                await f.write(f'[{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}]: {data.decode()}')

            await asyncio.sleep(1)

    finally:
        print('Closing the connection.')
        writer.close()
        await writer.wait_closed()


async def main(args):
    while True:
        await tcp_echo_client(args.host, args.port, args.history)
        await asyncio.sleep(1)


if __name__ == '__main__':
    parser = configargparse.ArgumentParser(
        description="TCP Chat Listener",
        default_config_files=['.minecraft.config']
    )

    parser.add_argument('--host', type=str, help='Server host', env_var='MINECHAT_HOST', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='Server port', env_var='MINECHAT_PORT', default=5000)
    parser.add_argument('--history', type=str, help='File to save chat history', env_var='MINECHAT_HISTORY',
                        default='minecraft.txt')

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except asyncio.CancelledError:
        print('Connection cancelled.')
    except KeyboardInterrupt:
        print("Program interrupted.")
