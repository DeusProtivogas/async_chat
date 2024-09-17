import json
import os
import argparse
import asyncio
import datetime
import aiofiles
import configargparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tcp_client.log"),
        logging.StreamHandler()
    ]
)


async def tcp_echo_client(host, port, chat_history):
    try:
        logging.info('Starting connection to %s:%s', host, port)
        reader, writer = await asyncio.open_connection(host, port)

        while True:

            data = await reader.read(200)
            if not data:
                break

            logging.info('Received data: %s', data.decode().strip())
            async with aiofiles.open(chat_history, "a", encoding='UTF-8') as f:
                await f.write(f'[{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}]: {data.decode()}')

            await asyncio.sleep(1)

    except Exception as e:
        logging.error('An error occurred: %s', e)

    finally:
        writer.close()
        await writer.wait_closed()
        logging.info('Closing the connection.')


async def main(args):
    await tcp_echo_client(args.host, args.port, args.history)


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
        logging.warning('Connection cancelled.')
    except KeyboardInterrupt:
        logging.info("Program interrupted.")
