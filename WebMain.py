from time import sleep
from flask_cors import CORS
from flask import Flask, jsonify, request, redirect, url_for
import Common
import threading
from liveDownloader import run as RUN

app = Flask("liveStatus")
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)
# url_for('static', filename='index.html')
# url_for('static', filename='index.js')


@app.route("/")
def index():
    return redirect("/static/index.html")

@app.route("/config", methods=["GET"])
def readConfig():
    config = Common.config.copy()
    config.pop("b_p")
    config.pop("mtd")
    config.pop("del")
    config.pop("mv")
    return jsonify(config)


@app.route("/config", methods=["POST"])
def writeConfig():
    # TODO : 完善
    Common.reloadConfig()
    return jsonify({"message":"ok","code":200,"status":0,"data":request.form})


@app.route("/encode/insert", methods=["POST"])
def insertEncode():
    if "filename" in request.form:
        Common.encodeQueue.put(request.form["filename"])
        return jsonify({"message":"ok","code":200,"status":0})


@app.route("/upload/insert", methods=["POST"])
def insertUpload():
    if "filename" in request.form:
        Common.uploadQueue.put(request.form["filename"])
        return jsonify({"message":"ok","code":200,"status":0})


@app.route("/upload/finish", methods=["POST"])
def finishUpload():
    Common.uploadQueue.put(True)
    return jsonify({"message":"ok","code":200,"status":0})


@app.route("/stats", methods=["GET"])
def getAllStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
        "encode": Common.encodeStatus,
        "upload": Common.uploadStatus,
        "error": Common.errors,
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        }
    }})


@app.route("/stats/broadcast", methods=["GET"])
def geBroadcastStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "broadcast": {
            "broadcaster": Common.broadcaster.__str__(),
            "isBroadcasting": Common.isBroadcasting,
            "streamUrl": Common.streamUrl,
            "updateTime": Common.updateTime
        }
    }})


@app.route("/stats/download", methods=["GET"])
def geDownloadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "download":Common.downloadStatus,
    }})


@app.route("/stats/encode", methods=["GET"])
def getEncodeStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "encode": Common.encodeStatus,
    }})


@app.route("/stats/upload", methods=["GET"])
def getUploadStats():
    return jsonify({"message":"ok","code":200,"status":0,"data":{
        "upload": Common.uploadStatus,
    }})


def SubThread():
    t = threading.Thread(target=RUN, args=(Common.config['l_u'],))
    t.setDaemon(True)
    t.start()
    while True:
        if t.is_alive():
            sleep(240)
        else:
            t = threading.Thread(target=RUN, args=(Common.config['l_u'],))
            t.setDaemon(True)
            t.start()


p = threading.Thread(target = SubThread)
p.setDaemon(True)
p.start()
