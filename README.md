### Get all images from exposed Twonky servers in one .html file 

#### Just a code i'm using to investigate interesting servers from my scanner-bot

1. `~$ shodan download twonky.json.gz port:9000 Twonky`
2. `~$ shodan parse --fields ip_str,port --separator ":" >> ips.txt`
3. `~$ python3 tw2html.py`
