import requests
from urllib.parse import urljoin
from fe.access.auth import Auth
import json


class Searcher:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "searcher/")
        self.user_id = user_id
        self.password = password
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def search(self, store_id: str, keyword: str):
        json = {
            "user_id": self.user_id,
            "store_id": store_id,
            "keyword": keyword
        }
        url = urljoin(self.url_prefix, "search")
        headers = {"token": self.token, "Content-Type": "application/json"}

        #json_str = json.dumps(json_)
        #print(json_str)
        print(url)
        r = requests.post(url, headers=headers, json=json)
        print(r)
        response_json = r.json()
        return r.status_code, response_json.get("pagenum"), response_json.get("row"), response_json.get("show")
        #print(r)
        #return r.status_code

    def show_pages(self, page, content):
        json = {
            "user_id": self.user_id,
            "page": int(page),
            "content": content
        }
        url = urljoin(self.url_prefix, "show_pages")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("pagenum"), response_json.get("row"), response_json.get("show")
