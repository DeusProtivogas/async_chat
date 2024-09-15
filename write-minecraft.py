import json
import os
import argparse
import asyncio
import datetime
import aiofiles
import configargparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tcp_client.log"),
        logging.StreamHandler()
    ]
)


async def send_message(host, port, chat_history):

    try:
        logging.info('Starting connection to %s:%s', host, port)
        # reader, _ = await asyncio.open_connection(host, port)
        reader_post, writer_post = await asyncio.open_connection(host, port)

        data = await reader_post.read(200)
        logging.info('Received data: %s', data.decode().strip())

        user_hash = input()
        writer_post.write(f'{user_hash}\n'.encode())
        await writer_post.drain()
        # writer_post.close()
        # await writer_post.wait_closed()

        test_data = await reader_post.read(200)
        logging.info(test_data.decode())

        # print(test_data)
        if user_hash and json.loads(test_data.decode()[:4]) is None:
            logging.info('Incorrect hash. Check it, or create an account')
            user_hash = None

        if not user_hash:
            username = input()

            writer_post.write(f'{username}\n'.encode())
            await writer_post.drain()
            response = await reader_post.read(400)
            logging.info(response.decode())


        while True:

            message = input()
            writer_post.write(f'{message}\n'.encode())

            await asyncio.sleep(1)
    except Exception as e:
        logging.error('An error occurred: %s', e)

    finally:
        logging.info('Closing the connection.')


async def main(args):
# while True:
    await send_message(args.host, args.port, args.history)
        # await asyncio.sleep(1)


if __name__ == '__main__':

    test_hash = '34b3131a-7278-11ef-abed-0242ac110002'

    parser = configargparse.ArgumentParser(
        description="TCP Chat Poster",
        default_config_files=['.minecraft_write.config']
    )

    parser.add_argument('--host', type=str, help='Server host', env_var='MINECHAT_HOST', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='Server port', env_var='MINECHAT_WRITE_PORT', default=5050)
    parser.add_argument('--history', type=str, help='File to save chat history', env_var='MINECHAT_HISTORY',
                        default='minecraft.txt')
    # parser.add_argument('--hash', type=str, help='Hash', env_var='MINECHAT_HASH', default=test_hash)

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except asyncio.CancelledError:
        logging.warning('Connection cancelled.')
    except KeyboardInterrupt:
        logging.info("Program interrupted.")