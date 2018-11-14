import requests

if __name__ == "__main__":
    r = requests.get('http://fortune.com/fortune500/list/', auth=())
    status = r.status_code
    
    if status == 200:
        print(
            r.text[:300]
        )