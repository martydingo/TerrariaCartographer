import asyncio, argparse, os
import concurrent.futures
import TerraMapper
from TerraGPS import TerraGPS
import os


class TerrariaCartographer:
    def __init__(
        self,
        worldName,
        tshockToken,
        outputFile=None,
        tshockHost="localhost",
        tshockPort=7878,
    ) -> None:
        # Define the name of the world. This is used as a pin for inputs/outputs.
        self.worldName = worldName.replace(" ", "_")

        # Define the token to use when fetching player positions from the tShock API
        self.tshockToken = tshockToken

        # Define the host to use when fetching player positions from the tShock API
        self.tshockHost = tshockHost

        # Define the output file path
        if outputFile is None:
            self.outputFile = (
                f"/root/TerrariaCartographer/TerrariaCartographer/{self.worldName}.png"
            )
        else:
            self.outputFile = outputFile

        # Define the TerraMapper configuration
        self.initTerraMapperConfig()

        # Define the TerraGPS configuration
        self.initTerraGPSConfig()
        self.TerraGPS = TerraGPS(
            tshock_host=self.tshockHost,
            tshock_token=self.terraGPSTshockToken,
            input_image=self.terraGPSInputImage,
            output_image=self.terraGPSOutputImage,
        )

        asyncio.run(self.run())

    async def run(self):
        try:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                loop.run_in_executor(pool, self.generatePlayerMap)
                loop.run_in_executor(pool, self.generateWorldMap)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting.")
            exit(0)

    def initTerraMapperConfig(self) -> None:
        self.terraMapperWorldPath = (
            # f"/root/.local/share/Terraria/Worlds/{self.worldName}.wld"
            f"/root/TerrariaCartographer/TerrariaCartographer/{self.worldName}.wld"
        )
        self.terraMapperOutputImage = f"/root/TerrariaCartographer/TerrariaCartographer/{self.worldName}_working.png"
        self.TerraMapperConfig = {
            "draw": {
                "background": True,
                "blocks": True,
                "walls": True,
                "liquids": True,
                "wires": True,
                "paint": True,
                "min_x": 0,
                "min_y": 0,
                "region_width": 0,
                "region_height": 0,
            },
            "output": {"file_path": self.terraMapperOutputImage},
            "world": {
                "file_path": self.terraMapperWorldPath,
            },
            "deep_zoom": {"enabled": False},
        }

    def initTerraGPSConfig(self) -> None:
        self.terraGPSTshockToken = self.tshockToken
        self.terraGPSInputImage = self.terraMapperOutputImage
        self.terraGPSOutputImage = self.outputFile

    def generateWorldMap(self) -> None:
        while True:
            print("Checking if world map needs to be generated...")
            if os.path.exists(self.terraGPSInputImage):
                if os.path.getmtime(self.terraMapperWorldPath) > os.path.getmtime(
                    self.terraGPSInputImage
                ):
                    TerraMapper.TerraMapper(config=self.TerraMapperConfig)
            else:
                TerraMapper.TerraMapper(config=self.TerraMapperConfig)

    def generatePlayerMap(self) -> None:
        while True:
            print("Checking if player map needs to be generated...")
            if os.path.exists(self.terraGPSInputImage):
                self.TerraGPS.generateMap()


if __name__ == "__main__":
    preArgs = argparse.ArgumentParser(
        prog="TerrariaCartographer",
        description="A simple class to get the position of a player in Terraria via the Terraria API and paint it onto the world image",
    )
    preArgs.add_argument(
        "-w",
        "--world",
        help="The name of the world to generate a map for",
    )
    preArgs.add_argument(
        "-H",
        "--host",
        help="The host of the Terraria server",
    )
    preArgs.add_argument(
        "-t",
        "--token",
        help="The token of the Terraria server",
    )
    preArgs.add_argument(
        "-o",
        "--output",
        help="The path where the output image will be placed",
    )

    args = preArgs.parse_args()
    terrariaCartographer = TerrariaCartographer(
        worldName=args.world,
        tshockHost=args.host,
        tshockToken=args.token,
        outputFile=args.output,
    )
