import json
import os
import argparse
import asyncio
import datetime
import aiofiles
import configargparse

async def tcp_echo_client(host, port, chat_history, hash):
    # host = 'minechat.dvmn.org'
    # port = 5000

    message = 'message test'

    try:
        print('starting connection')
        reader, _ = await asyncio.open_connection(host, port)

        while True:

            data = await reader.read(200)
            if not data:
                break
            print(data.decode(), end='')
            async with aiofiles.open(chat_history, "a", encoding='UTF-8') as f:
                await f.write(f'[{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}]: {data.decode()}')

            await asyncio.sleep(1)

    finally:
        print('Closing the connection.')
        # writer_post.close()
        # await writer_post.wait_closed()


async def main(args):
    # while True:
    await tcp_echo_client(args.host, args.port, args.history, args.hash)
        # await asyncio.sleep(1)


if __name__ == '__main__':

    test_hash = '34b3131a-7278-11ef-abed-0242ac110002'

    parser = configargparse.ArgumentParser(
        description="TCP Chat Listener",
        default_config_files=['.minecraft.config']
    )

    parser.add_argument('--host', type=str, help='Server host', env_var='MINECHAT_HOST', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='Server port', env_var='MINECHAT_PORT', default=5000)
    parser.add_argument('--history', type=str, help='File to save chat history', env_var='MINECHAT_HISTORY',
                        default='minecraft.txt')
    parser.add_argument('--hash', type=str, help='Hash', env_var='MINECHAT_HASH', default='')

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except asyncio.CancelledError:
        print('Connection cancelled.')
    except KeyboardInterrupt:
        print("Program interrupted.")
