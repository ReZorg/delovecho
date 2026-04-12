#!/usr/bin/env python3

import argparse
import asyncio
import logging
import sys

from deltachat_rpc_client import Rpc

async def setup_account(rpc, addr, password):
    """Sets up and configures a new Delta Chat account."""
    account_id = await rpc.add_account()
    logging.info(f"Added account with ID: {account_id}")

    config = {
        "addr": addr,
        "mail_pw": password,
        "bot": "1",
        "displayname": "Deltecho Bot",
        "e2ee_enabled": "1",
    }
    await rpc.batch_set_config(account_id, config)
    logging.info(f"Set initial config for account {account_id}")

    await rpc.configure(account_id)
    logging.info(f"Configured account {account_id}, checking connection...")

    accounts = await rpc.get_all_accounts()
    logging.info(f"All accounts: {accounts}")

    qr_code = await rpc.get_chat_securejoin_qr_code(account_id)
    print(f"\nInvite QR Code URL:\n{qr_code}\n")

    return account_id

async def main():
    parser = argparse.ArgumentParser(description="DeltaChat Bot Setup Script")
    parser.add_argument("--addr", required=True, help="Email address for the bot")
    parser.add_argument("--password", required=True, help="Email password for the bot")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async with Rpc() as rpc:
        try:
            await setup_account(rpc, args.addr, args.password)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
