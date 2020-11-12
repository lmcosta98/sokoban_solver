import asyncio
import getpass
import json
import os
import pprint
import random

import websockets

from consts import Tiles
from mapa import Map


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        # You can create your own map representation or use the game representation:
        mapa = Map(game_properties["map"])
        #print(mapa)

        keys = ["w","a", "s", "d"]

        while True:
            try:
                # receive game state, this must be called timely or the game will get out of sync with the server
                state = json.loads(await websocket.recv())
<<<<<<< HEAD
                pprint.pprint(state)
                print(Map(f"levels/{state['level']}.xsb"))
                # goals vazios
                #print(mapa.empty_goals)

                # todos os goals do mapa
=======
                print("###### STATE ######\n")
                pprint.pprint(state)
                #print(Map(f"levels/{state['level']}.xsb"))
                # goals vazios
                print("\n###### EMPTY GOALS ######\n")
                print(mapa.empty_goals)

                # todos os goals do mapa
                print("\n###### GOALS ######\n")
>>>>>>> upstream/master
                print(mapa.filter_tiles([Tiles.GOAL, Tiles.BOX_ON_GOAL]))

                key = random.choice(keys)

                # send key command to server - you must implement this send in the AI agent
                await websocket.send(json.dumps({"cmd": "key", "key": key}))


            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
