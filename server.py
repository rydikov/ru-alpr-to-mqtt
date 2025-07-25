import cv2
import logging
import numpy as np
import os
import paho.mqtt.publish as publish
import json
import time

from fast_alpr import ALPR

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger(__name__)

WHITE_COLOR = (255, 255, 255)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alpr = ALPR(
    detector_model=os.environ.get('DETECTOR_MODEL', "yolo-v9-t-512-license-plate-end2end"),
    ocr_model=os.environ.get('OCR_MODEL', "cct-s-v1-global-model"),
)


@app.post("/alpr")
async def upload_file(file: UploadFile = File(...)):

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    response = []

    try:
        nparr = np.fromstring(await file.read(), np.uint8)
        img_np = cv2.imdecode(nparr, flags=1)

        alpr_results = alpr.predict(img_np)

        for result in alpr_results:

            coords = result.detection.bounding_box

            label = f"{result.ocr.text} ({result.ocr.confidence:.2f})"
            label_position = (coords.x1, coords.y1 - 7)

            cv2.rectangle(img_np, (coords.x1, coords.y1), (coords.x2, coords.y2), WHITE_COLOR, 1)
            cv2.putText(img_np, label, label_position, cv2.FONT_HERSHEY_COMPLEX, 0.4, WHITE_COLOR, 1)

            response.append({
                'license_plate': result.ocr.text,
                'confidence': result.ocr.confidence
            })

        if response:
            cv2.imwrite(file_location, img_np)

        try:
            publish.single(
                topic="license-plate-detector/meta",
                payload=json.dumps({'result': response, 'timestamp': time.time()}),
                hostname=os.environ.get('MQTT_HOSTNAME', 'host.docker.internal'),
                port=int(os.environ.get('MQTT_PORT', 1880)),
            )
        except ConnectionRefusedError as e:
            logger.error(f"MQTT server is not available: {e}")
        except TimeoutError as e:
            logger.error(f"MQTT server is not available: {e}")

        return JSONResponse({
            'result': response
        })

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get('APP_PORT', 8000)))
