import requests
import xmltodict
import json
from slackclient import SlackClient
import os
import sqlite3
import settings


def send_lines(lines):
    token = os.environ['SLACK_TOKEN']
    sc = SlackClient(token)
    print sc.api_call("api.test")
    print sc.api_call("channels.info", channel="researchbotdev")
    for line in lines:
        print sc.api_call(
            "chat.postMessage",
            channel="#researchbotdev",
            text=":tada: NEW PAPER :tada:\n" + line,
            username='researchbot',
            icon_emoji=':robot_face:'
        )

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def pull_papers(phrase, url=settings.DEFAULT_URL):
    data = requests.get(url.format(phrase=phrase))
    docs = xmltodict.parse(data.content)['feed']['entry']
    titles = {doc['title'] for doc in docs}
    return titles


def filter_unsent_titles(titles):
    conn = sqlite3.connect(settings.DB_NAME)
    unsent = []
    for title in titles:
        res = conn.execute(
            "SELECT title FROM papers WHERE title = ?", (title,))
        if not len(res.fetchall()):
            unsent.append(title)
    return unsent


def record_sent_titles(titles):
    conn = sqlite3.connect(settings.DB_NAME)
    for title in titles:
        conn.execute("INSERT into papers values (?)", (title,))
        conn.commit()


def pull_titles():
    titles = ([]
        + list(pull_papers('TCGA'))
        + list(pull_papers('bioinformatics'))
    )
    titles = filter_unsent_titles(titles)
    record_sent_titles(titles)
    send_lines(titles)

if __name__ == '__main__':
    pull_titles()
