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

async def load_account():
    if os.path.exists(ACCOUNT_FILE):
        async with aiofiles.open(ACCOUNT_FILE, 'r') as f:
            content = await f.read()
            return json.loads(content)
    return None


async def save_account(account_data):
    async with aiofiles.open(ACCOUNT_FILE, 'w') as f:
        await f.write(json.dumps(account_data))


async def register_user(host, port):
    try:
        logging.info('Registering new user...')
        reader, writer = await asyncio.open_connection(host, port)

        response = await reader.read(400)
        logging.info(f'Received: {response.decode()}')
        writer.write(f'\n'.encode())
        await writer.drain()

        response = await reader.read(400)
        logging.info(f'New received: {response.decode()}')
        username = input()
        writer.write(f'{username}\n'.encode())
        await writer.drain()

        response = await reader.read(400)
        user_data = response.decode().split("\n")[0]
        logging.info(f'New new received: {user_data}')

        account_data = json.loads(user_data)
        await save_account(account_data)

        logging.info(f'New account created: {account_data["nickname"]}, hash: {account_data["account_hash"]}')

    finally:
        writer.close()
        await writer.wait_closed()

async def register_account(host, port):
    reader_post, writer_post = await asyncio.open_connection(host, port)
    await register_user(host, port)
    account = await load_account()

    response = await reader_post.read(400)
    logging.info(f'Received: {response.decode()}')
    user_hash = account['account_hash']
    logging.info(f'Retrying authentication with new hash: {user_hash}')

    writer_post.write(f'{user_hash}\n'.encode())
    await writer_post.drain()
    test_data = await reader_post.read(200)

    logging.info(test_data.decode())
    return reader_post, writer_post

async def login(host, port):
    account = await load_account()

    if not account:
        logging.info('No existing account found, starting registration')
        await register_user(host, port)
        account = await load_account()

    user_hash = account['account_hash']
    logging.info(f'Authenticating with hash: {user_hash}')

    logging.info('Starting connection to %s:%s', host, port)
    reader_post, writer_post = await asyncio.open_connection(host, port)

    _ = await reader_post.read(200)

    writer_post.write(f'{user_hash}\n'.encode())
    await writer_post.drain()

    data = await reader_post.read(200)
    logging.info(data.decode())

    if user_hash and json.loads(data.decode().split('\n')[0]) is None:
        logging.info('Incorrect hash. Check it, or create an account')

        create_account = input("Do you want to register a new account? (y/n): ").strip().lower()

        if create_account == 'y':
            writer_post.close()
            await writer_post.wait_closed()
            reader_post, writer_post = await register_account(host, port)
        else:
            logging.info('Exiting program...')
            return
    return writer_post


async def send_message(host, port):

    try:
        writer_post = await login(host, port)

        while True:

            message = input()
            writer_post.write(f'{message}\n'.encode())

            await asyncio.sleep(1)
    except Exception as e:
        logging.error('An error occurred: %s', e)

    finally:
        writer_post.close()
        await writer_post.wait_closed()
        logging.info('Closing the connection.')


async def main(args):
    await send_message(args.host, args.port)


if __name__ == '__main__':

    ACCOUNT_FILE = 'account.json'

    test_hash = '34b3131a-7278-11ef-abed-0242ac110002'

    parser = configargparse.ArgumentParser(
        description="TCP Chat Poster",
        default_config_files=['.minecraft_write.config']
    )

    parser.add_argument('--host', type=str, help='Server host', env_var='MINECHAT_HOST', default='minechat.dvmn.org')
    parser.add_argument('--port', type=int, help='Server port', env_var='MINECHAT_WRITE_PORT', default=5050)
    parser.add_argument('--history', type=str, help='File to save chat history', env_var='MINECHAT_HISTORY',
                        default='minecraft.txt')

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except asyncio.CancelledError:
        logging.warning('Connection cancelled.')
    except KeyboardInterrupt:
        logging.info("Program interrupted.")