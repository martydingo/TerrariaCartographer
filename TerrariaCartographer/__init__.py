from TerraGPS import TerraGPS
import asyncio, argparse, os, concurrent.futures, logging, logging.handlers, TerraMapper, os


class TerrariaCartographer:
    def __init__(
        self,
        worldPath,
        tshockToken,
        outputFile=None,
        tshockHost="localhost",
        tshockPort=7878,
    ) -> None:
        # Initialize logging
        self.initLogging()

        # Define the world path
        self.terraMapperWorldPath = worldPath

        # Define the name of the world.
        self.worldFileName = worldPath.split("/")[-1]
        if not self.worldFileName.split(".")[1] == "wld":
            self.log.error("World file not a valid world file. Exiting.")
            exit(1)

        self.worldName = self.worldFileName.split(".")[0]

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
            # If the output file is defined, use it.
            self.outputFile = outputFile

        # Define the TerraMapper configuration
        self.initTerraMapperConfig()

        # Define the TerraGPS configuration
        self.initTerraGPSConfig()

        # Define the TerraMapper instance
        self.TerraGPS = TerraGPS(
            tshock_host=self.tshockHost,
            tshock_token=self.terraGPSTshockToken,
            input_image=self.terraGPSInputImage,
            output_image=self.terraGPSOutputImage,
        )

        # If the world exists..
        if os.path.exists(self.terraMapperWorldPath):
            # Run the program
            asyncio.run(self.run())
        else:
            # Otherwise, exit.
            self.log.error("World file not found. Exiting.")
            exit(1)

    def initLogging(self):
        # Initialize the logger and set the level to DEBUG
        self.log = logging.getLogger("TerrariaCartographer")

        # Set the format for the logging output
        logFormatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Set the handler to output to STDOUT
        stdoutStreamHandler = logging.StreamHandler()
        stdoutStreamHandler.setFormatter(logFormatter)

        # Set the handler to output to syslog
        syslogStreamHandler = logging.handlers.SysLogHandler()
        syslogStreamHandler.setFormatter(logFormatter)

        # Set the logging level to DEBUG
        self.log.setLevel(logging.DEBUG)

        # Add the handlers to the logger
        self.log.addHandler(stdoutStreamHandler)
        self.log.addHandler(syslogStreamHandler)

        # Log a message that logging has been initialized
        self.log.debug("Logging Initialized")

    def initTerraMapperConfig(self) -> None:
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
            self.log.info("Checking if world map needs to be generated...")
            if os.path.exists(self.terraGPSInputImage):
                if os.path.getmtime(self.terraMapperWorldPath) > os.path.getmtime(
                    self.terraGPSInputImage
                ):
                    TerraMapper.TerraMapper(config=self.TerraMapperConfig)
            else:
                TerraMapper.TerraMapper(config=self.TerraMapperConfig)

    def generatePlayerMap(self) -> None:
        while True:
            self.log.info("Checking if player map needs to be generated...")
            if os.path.exists(self.terraGPSInputImage):
                self.TerraGPS.generateMap()

    async def run(self):
        try:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                loop.run_in_executor(pool, self.generatePlayerMap)
                loop.run_in_executor(pool, self.generateWorldMap)
        except KeyboardInterrupt:
            self.log.warning("Keyboard interrupt detected. Exiting.")
            exit(0)


if __name__ == "__main__":
    preArgs = argparse.ArgumentParser(
        prog="TerrariaCartographer",
        description="A simple class to get the position of a player in Terraria via the Terraria API and paint it onto the world image",
    )
    preArgs.add_argument(
        "-f",
        "--worldFile",
        help="The path of the world to generate a map for",
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
        worldPath=args.worldFile,
        tshockHost=args.host,
        tshockToken=args.token,
        outputFile=args.output,
    )
