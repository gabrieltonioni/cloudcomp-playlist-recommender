import argparse
import subprocess
import json

def send_request(songs, ip_address):
    url = f"http://{ip_address}:32184/api/recommend"
    headers = ["Content-Type: application/json"]
    data = json.dumps({"songs": songs})

    cmd = [
        "wget", "--server-response",
        "--output-document", "response.out",
        "--header", *headers,
        "--post-data", data,
        url
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send a request to the playlists-recommender service.')
    parser.add_argument('--ip', type=str, required=True, help='The IP address of the playlists-recommender service.')
    args = parser.parse_args()

    songs = ["HUMBLE.", "T-Shirt", "XO TOUR Llif3"]
    send_request(songs, args.ip)
