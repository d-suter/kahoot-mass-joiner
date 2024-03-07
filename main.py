import json
import random
import threading
import time
import uuid
import logging
from websocket import create_connection
import base64
import re
import py_mini_racer
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _shiftBits(solution, sessionToken):
    decodedToken = base64.b64decode(sessionToken).decode('utf-8', 'strict')
    solChars = [ord(s) for s in solution]
    sessChars = [ord(s) for s in decodedToken]
    return "".join([chr(sessChars[i] ^ solChars[i % len(solChars)]) for i in range(len(sessChars))])

def solveChallenge(text, sessionToken):
    text = text.replace('\t', '', -1).encode('ascii', 'ignore').decode('utf-8')
    text = re.split("[{};]", text)
    replaceFunction = "return message.replace(/./g, function(char, position) {"
    rebuilt = [text[1] + "{", text[2] + ";", replaceFunction, text[7] + ";})};", text[0]]

    jsEngine = py_mini_racer.MiniRacer()
    solution = jsEngine.eval("".join(rebuilt))

    return _shiftBits(solution, sessionToken)

def join_game(game_id, player_name):
    try:
        l_data = random.randint(100, 999)
        o_data = random.randint(-999, -100)

        generated_uuid = str(uuid.uuid4())
        cookies = {
            'generated_uuid': generated_uuid,
            'player': 'active',
        }

        headers = {
            'authority': 'kahoot.it',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'tr-TR,tr;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://kahoot.it/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        response = requests.get(f'https://kahoot.it/reserve/session/{game_id}/?{time.time()}', cookies=cookies, headers=headers)
        session_token = response.headers["X-Kahoot-Session-Token"]
        challenge_text = response.json()["challenge"]
        wss_connection = solveChallenge(challenge_text, session_token)

        ws = create_connection(f"wss://kahoot.it/cometd/{game_id}/{wss_connection}")
        ws.send(json.dumps([{"id": "1", "version": "1.0", "minimumVersion": "1.0", "channel": "/meta/handshake",
                             "supportedConnectionTypes": ["websocket", "long-polling", "callback-polling"],
                             "advice": {"timeout": 60000, "interval": 0},
                             "ext": {"ack": True, "timesync": {"tc": str(time.time()), "l": 0, "o": 0}}}]))
        clientId = json.loads(ws.recv())[0]["clientId"]
        ws.send(json.dumps([{"id": "2", "channel": "/meta/connect", "connectionType": "websocket",
                             "advice": {"timeout": 0}, "clientId": clientId,
                             "ext": {"ack": 0, "timesync": {"tc": str(time.time()), "l": l_data, "o": o_data}}}]))
        ws.recv()
        ws.send(json.dumps([{"id": "3", "channel": "/meta/connect", "connectionType": "websocket", "clientId": clientId,
                             "ext": {"ack": 1, "timesync": {"tc": str(time.time()), "l": l_data, "o": o_data}}}]))
        while True:
            x = json.dumps([{"id": "4", "channel": "/service/controller",
                             "data": {"type": "login", "gameid": game_id, "host": "kahoot.it",
                                      "name": player_name, "content": "{\"device\":{\"userAgent\":\"Mozilla/5.0 "
                                                                        "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                                        "(KHTML, like Gecko) Chrome/120.0.0.0 "
                                                                        "Safari/537.36\",\"screen\":{\"width\":920,"
                                                                        "\"height\":974}}}"},
                             "clientId": clientId, "ext": {}}])
            ws.send(x)
            findit = ws.recv()
            if '"loginResponse","cid":' in findit:
                logging.info(findit)
                break
        ws.send(json.dumps([{"id": "5", "channel": "/service/controller",
                             "data": {"id": 16, "type": "message", "gameid": game_id, "host": "kahoot.it",
                                      "content": "{\"usingNamerator\":false}"}, "clientId": clientId, "ext": {}}]))
        ws.send(json.dumps([{"id": "6", "channel": "/meta/connect", "connectionType": "websocket", "clientId": clientId,
                             "ext": {"ack": 2, "timesync": {"tc": str(time.time()), "l": l_data, "o": o_data}}}]))
        a = 2
        b = 6
        while True:
            a += 1
            b += 1
            ws.send(json.dumps([{"id": b, "channel": "/meta/connect", "connectionType": "websocket",
                                 "clientId": clientId, "ext": {"ack": a,
                                                                "timesync": {"tc": str(time.time()), "l": l_data,
                                                                             "o": o_data}}}]))
            ws.recv()
    except Exception as e:
        logging.error(f"Error: {e}, most likely cause of speed")


def start_joining_threads(game_id, nick_start):
    for _ in range(100):
        threading.Thread(target=join_game, args=(game_id, f"{nick_start}{random.randint(100000, 999999)}")).start()
        time.sleep(0.01)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Kahoot mass joiner')
    parser.add_argument('--game_id', required=True, help='Game ID')
    parser.add_argument('--nick_start', required=True, help='Nickname prefix')
    args = parser.parse_args()

    start_joining_threads(args.game_id, args.nick_start)
