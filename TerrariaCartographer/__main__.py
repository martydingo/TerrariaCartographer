#!/usr/bin/env python3

import argparse
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from TerrariaCartographer import TerrariaCartographer

if __name__ == "__main__":
    preArgs = argparse.ArgumentParser(
        prog="TerrariaCartographer",
        description="A simple class to get the position of a player in Terraria via the Terraria API and paint it onto the world image",
    )
    preArgs.add_argument(
        "-f",
        "--worldFile",
        help="The path of the world to generate a map for",
        required=True,
    )
    preArgs.add_argument(
        "-H", "--host", help="The host of the Terraria server", required=True
    )
    preArgs.add_argument(
        "-t", "--token", help="The token of the Terraria server", required=True
    )
    preArgs.add_argument(
        "-o",
        "--output",
        help="The path where the output image will be placed",
        required=True,
    )

    args = preArgs.parse_args()
    terrariaCartographer = TerrariaCartographer(
        worldPath=args.worldFile,
        tshockHost=args.host,
        tshockToken=args.token,
        outputFile=args.output,
    )
