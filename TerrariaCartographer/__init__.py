__all__ = ["TerrariaCartographer"]

from TerraGPS import TerraGPS
import asyncio, os, concurrent.futures, logging, logging.handlers, TerraMapper, os, time, tornado.web, shutil


class TerrariaCartographer:
    class MainHandler(tornado.web.RequestHandler):
        servedTerraGPSOutputImage = ""

        def get(self):
            self.set_header("Content-type", "image/png")
            self.set_header(
                "Content-length", os.path.getsize(self.servedTerraGPSOutputImage)
            )
            with open(self.servedTerraGPSOutputImage, "rb") as f:
                self.write(f.read())
            self.finish()

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

        # Define the path to the world file
        self.worldFileName = worldPath.split("/")[-1]
        if not self.worldFileName.split(".")[1] == "wld":
            self.log.error("World file not a valid world file. Exiting.")
            exit(1)

        # Define the name of the world.
        self.worldName = self.worldFileName.split(".")[0]

        # Define the output file path
        if outputFile is None:
            self.outputFile = f"{self.worldName}.png"
        else:
            # If the output file is defined, use it.
            self.outputFile = outputFile

        # Define the TerraMapper configuration
        self.initTerraMapperConfig()

        # Define the TerraGPS configuration
        self.tshockHost = tshockHost
        self.tshockPort = tshockPort
        self.terraGPSTshockToken = tshockToken
        self.terraGPSInputImage = self.terraMapperOutputImage
        self.terraGPSOutputImage = self.outputFile

        # Define the TerraMapper instance
        self.TerraGPS = TerraGPS(
            tshock_token=self.terraGPSTshockToken,
            tshock_host=self.tshockHost,
            tshock_port=self.tshockPort,
            input_image=self.terraGPSInputImage,
            output_image=self.terraGPSOutputImage,
        )
        # Define the webserver as not started
        self.webserverStarted = False
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
        self.terraMapperOutputImage = f"{self.worldName}_working.png"
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

    def generateWorldMap(self) -> None:
        try:
            while True:
                if os.path.exists(self.terraGPSInputImage):
                    if os.path.getmtime(self.terraMapperWorldPath) > os.path.getmtime(
                        self.terraGPSInputImage
                    ):
                        self.log.warning(
                            "Newer world file detected, regenerating world map..."
                        )
                        TerraMapper.TerraMapper(config=self.TerraMapperConfig)
                else:
                    self.log.warning(
                        "No world map detected, generating a new world map..."
                    )
                    TerraMapper.TerraMapper(config=self.TerraMapperConfig)
        except Exception as errorMsg:
            self.log.error(
                f"Exception encountered while generating the world map: {errorMsg}"
            )
            self.log.warning("Retrying after three seconds...")
            time.sleep(3)
            self.generateWorldMap()

    def generatePlayerMap(self) -> None:
        try:
            while True:
                if os.path.exists(self.terraGPSInputImage):
                    if os.path.exists(self.terraGPSOutputImage):
                        shutil.copy2(
                            self.terraGPSOutputImage,
                            self.terraGPSOutputImage.replace(".png", "_served.png"),
                        )

                    self.TerraGPS.generateMap()
                    time.sleep(3)
                else:
                    self.log.warning(
                        "No world map detected, waiting for a world map to be generated..."
                    )
                    time.sleep(3)
        except Exception as errorMsg:
            self.log.error(
                f"Exception encountered while generating the player map: {errorMsg}"
            )
            self.log.warning("Retrying...")
            self.generatePlayerMap()

    async def startWebserver(self):
        app = self.make_app()
        app.listen(8888)
        await asyncio.Event().wait()
        self.webserverStarted = True

    def make_app(self):
        self.MainHandler.servedTerraGPSOutputImage = self.terraGPSOutputImage.replace(
            ".png", "_served.png"
        )
        return tornado.web.Application(
            [
                (r"/", self.MainHandler),
            ]
        )

    async def run(self):
        try:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                loop.run_in_executor(pool, self.generatePlayerMap)
                loop.run_in_executor(pool, self.generateWorldMap)
                await self.startWebserver()

        except KeyboardInterrupt:
            self.log.warning("Keyboard interrupt detected. Exiting.")
            exit(0)
