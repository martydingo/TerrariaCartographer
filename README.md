# TerrariaCartographer

## Overview
A tool that reads Terraria world files, and polls tShock APIs, to produce a 'live' world map complete with player locations.

## Usage
```
python3 -m TerrariaCartographer.__init__ -f /root/.local/Terraria/worlds/world.wld -H 127.0.0.1 -t tShockExampleRestApiKey -o outputImage.png
```