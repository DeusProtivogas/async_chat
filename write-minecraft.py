import json
import os
import argparse
import asyncio
import datetime
import aiofiles
import configargparse


async def send_message(host, port, chat_history):

    try:
        print('starting connection with sender')
        # reader, _ = await asyncio.open_connection(host, port)
        reader_post, writer_post = await asyncio.open_connection(host, 5050)

        test_data = await reader_post.read(200)
        print(test_data.decode())

        hash = input()

        writer_post.write(f'{hash}\n'.encode())
        await writer_post.drain()
        # writer_post.close()
        # await writer_post.wait_closed()

        test_data = await reader_post.read(200)
        print(test_data.decode())

        if not hash:
            username = input()

            writer_post.write(f'{username}\n'.encode())
            await writer_post.drain()
            response = await reader_post.read(200)
            print(response.decode())

        while True:

            message = input()
            writer_post.write(f'{message}\n'.encode())

            await asyncio.sleep(1)
    except Exception as e:
        print(e)

    finally:
        print('Closing the connection.')
        # writer_post.close()
        # await writer_post.wait_closed()


async def main(args):
# while True:
    await send_message(args.host, args.port, args.history)
        # await asyncio.sleep(1)


if __name__ == '__main__':

    test_hash = '34b3131a-7278-11ef-abed-0242ac110002'

    parser = configargparse.ArgumentParser(
        description="TCP Chat Poster",
        default_config_files=['.minecraft.config']
    )

    parser.add_argument('--host', type=str, help='Server host', env_var='MINECHAT_HOST', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='Server port', env_var='MINECHAT_PORT', default=5000)
    parser.add_argument('--history', type=str, help='File to save chat history', env_var='MINECHAT_HISTORY',
                        default='minecraft.txt')
    # parser.add_argument('--hash', type=str, help='Hash', env_var='MINECHAT_HASH', default=test_hash)

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except asyncio.CancelledError:
        print('Connection cancelled.')
    except KeyboardInterrupt:
        print("Program interrupted.")