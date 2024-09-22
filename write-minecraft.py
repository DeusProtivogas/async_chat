import json
import os
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

async def handle_bad_hash(reader, writer):
    logging.info('Registering new user...')

    username = input("Enter your username: ")
    writer.write(f'{username}\n'.encode())
    await writer.drain()

    response = await reader.read(400)
    user_data = response.decode().split("\n")[0]
    logging.info(response.decode())

    account_data = json.loads(user_data)
    await save_account(account_data)

    logging.info(f'New account created: {account_data["nickname"]}, hash: {account_data["account_hash"]}')

async def register_user(reader, writer):
    logging.info('Registering new user...')

    response = await reader.read(400)
    logging.info(f'Received: {response.decode()}')
    writer.write(f'\n'.encode())
    await writer.drain()

    response = await reader.read(400)
    logging.info(f'New received: {response.decode()}')
    username = input("Enter your username: ")
    writer.write(f'{username}\n'.encode())
    await writer.drain()

    response = await reader.read(400)
    user_data = response.decode().split("\n")[0]
    logging.info(response.decode())

    account_data = json.loads(user_data)
    await save_account(account_data)

    logging.info(f'New account created: {account_data["nickname"]}, hash: {account_data["account_hash"]}')


async def authenticate_user(reader, writer, account):
    logging.info(f'Authenticating with hash: {account["account_hash"]}')

    _ = await reader.read(200)
    writer.write(f'{account["account_hash"]}\n'.encode())
    await writer.drain()

    data = await reader.read(200)
    logging.info(data.decode())

    if account["account_hash"] and json.loads(data.decode().split('\n')[0]) is None:
        logging.info('Incorrect hash. Check it, or create an account')
        return False
    return True


async def connection_handler(host, port):
    reader, writer = await asyncio.open_connection(host, port)

    try:
        account = await load_account()
        if not account:
            logging.info('No existing account found, starting registration')
            await register_user(reader, writer)

            writer.close()
            await writer.wait_closed()
            reader, writer = await asyncio.open_connection(host, port)
            account = await load_account()

        if not await authenticate_user(reader, writer, account):
            create_account = input("Do you want to register a new account? (y/n): ").strip().lower()
            if create_account == 'y':
                await handle_bad_hash(reader, writer)
            else:
                logging.info('Exiting program...')
                return

        await send_message(reader, writer)
    except Exception as e:
        logging.error('An error occurred: %s', e)
    finally:
        writer.close()
        await writer.wait_closed()
        logging.info('Connection closed.')


async def send_message(reader, writer):
    logging.info("You can start sending messages.")
    while True:
        message = input()
        writer.write(f'{message}\n'.encode())
        await writer.drain()
        await asyncio.sleep(1)


async def main(args):
    await connection_handler(args.host, args.port)


if __name__ == '__main__':
    ACCOUNT_FILE = 'account.json'
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
