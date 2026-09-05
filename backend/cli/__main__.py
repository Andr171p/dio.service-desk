import argparse
import asyncio
import logging
import sys

from .commands import create_super_admin, create_s3_buckets


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Bootstrap utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("create-super-admin", help="Создать супер администратора")
    subparsers.add_parser("create-s3-buckets", help="Инициализация S3 хранилища")

    args = parser.parse_args()

    if args.command == "create-super-admin":
        asyncio.run(create_super_admin.main())

    elif args.command == "create-s3-buckets":
        asyncio.run(create_s3_buckets.main())

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
