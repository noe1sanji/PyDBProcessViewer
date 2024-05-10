import argparse
import json
import os
import sys

import mysql.connector
from mysql.connector import errorcode
from rich.console import Console

from helpers import bar_progress, create_table, get_mysql_conn

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", required=True, help="JSON file with database configuration"
)
parser.add_argument("--refresh-interval", default=10, type=int)
parser.add_argument("--order-by", help="[column] [asc|desc]")
parser.add_argument("--group-by-command", action="store_true")
parser.add_argument("--server-name", type=str, default="MYSQL")
parser.add_argument("--table-highlight", action="store_true")
parser.add_argument("--table-collapse", action="store_true")
parser.add_argument("--hide-sleep", help="Hide 'Sleep' processes", action="store_true")

args = parser.parse_args()

console = Console()

if not os.path.isfile(args.config):
    print(f"File not found: {args.config}")
    sys.exit(1)

with open(args.config, "r") as f:
    json_config = json.load(f)

try:
    config = {
        "host": json_config["host"],
        "user": json_config["username"],
        "password": json_config["password"],
        "db": json_config["database"],
        "port": json_config["port"],
    }
except KeyError as e:
    print(f"Missing configuration key: {e}")
    sys.exit(1)


query = "SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST"

if args.order_by:
    query = f"SELECT * FROM INFORMATION_SCHEMA.PROCESSLIST ORDER BY {args.order_by}"

if args.group_by_command:
    query = f"SELECT COMMAND, COUNT(*) AS TOTAL FROM INFORMATION_SCHEMA.PROCESSLIST GROUP BY COMMAND"

processes = []

while True:
    try:
        with get_mysql_conn(**config) as cnx:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)
            results = cur.fetchall()

            if results is not None:
                total = len(results)

                if args.hide_sleep:
                    sleep_process = len(
                        [item for item in results if item["COMMAND"] == "Sleep"]
                    )
                    results = [item for item in results if item["COMMAND"] != "Sleep"]

                table = create_table(
                    items=results,
                    server_name=args.server_name,
                    table_collapse=args.table_collapse,
                    table_highlight=args.table_highlight,
                )
                os.system("clear")
                console.print(table)

                console.print("")

                if args.hide_sleep:
                    console.print(f"[b]Sleep: {sleep_process}")

                console.print(f"[b]Total: {total}")
                console.print("")

            bar_progress(args.refresh_interval)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            console.log("Wrong username and/or password")
            sys.exit(1)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            console.log("Database does not exist")
            sys.exit(1)
        elif err.errno == errorcode.CR_CONN_HOST_ERROR:
            console.log(str(err))
            bar_progress(10)
    except KeyboardInterrupt:
        exit(0)
