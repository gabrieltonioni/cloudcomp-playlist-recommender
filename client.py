import argparse
import subprocess
import json
import time


def sync_app(app_name):
    cmd = ["argocd", "app", "sync", app_name]
    subprocess.run(cmd)

def read_model_date(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data["model_date"]

def monitor_file(filename, ip_address, dataset_url):
    songs = ["HUMBLE.", "T-Shirt", "XO TOUR Llif3"]
    send_request(songs, ip_address)
    last_model_date = read_model_date(filename)

    script = "cloudcomp-playlist-recommender/update_dataset_and_push.sh"
    args = [dataset_url]
    subprocess.run(["/bin/bash", "-c", script] + args)

    start_time = time.time()
    # sync_app("gabrielduarte-playlist-recommender")
    while True:
        current_model_date = read_model_date(filename)
        if current_model_date != last_model_date:
            break
        send_request(songs, args.ip)
    end_time = time.time()
    print(f"The script ran for {end_time - start_time} seconds.")

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
    parser = argparse.ArgumentParser(description="Send a request to the playlists-recommender service.")
    parser.add_argument("--ip", type=str, required=True, help="The IP address of the playlists-recommender service.")
    parser.add_argument("--dsurl", type=str, required=False, help="New dataset url")
    args = parser.parse_args()

    if(args.dsurl):
        monitor_file("response.out", args.ip, args.dsurl)
    else:
        songs = ["HUMBLE.", "T-Shirt", "XO TOUR Llif3"]
        send_request(songs, args.ip)