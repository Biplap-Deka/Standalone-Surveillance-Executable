import cv2
import pandas as pd
import os
import sys
import pywhatkit
from ultralytics import YOLO
from datetime import datetime

num = int(input("Enter the number of cameras: "))
end = num+1
camera_sources={}
for i in range(1, end):
    rtsp = input(f"Enter the RTSP URL of Camera {i}: ")
    camera_sources[f"CAM{i:02d}"] = rtsp

whatsapp_nr = input("Enter the WhatsApp number for message alerts: ")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
model = YOLO(resource_path("yolov8x.pt"))

os.makedirs("Snapshots", exist_ok = True)
def send_whatsapp(message):
    try:
        pywhatkit.sendwhatmsg_instantly(
            phone_no = whatsapp_nr,
            message = message,
            wait_time=15,
            tab_close = True)
    except Exception as e:
        print(f"Whatsapp Error: {e}")

incident_df = pd.DataFrame(columns = ["Timestamp","Camera","Violation","Confidence"])

def export_excel():
    time_stamp = datetime.now().strftime("%Y%m%d_%H:%M:%S")
    file_name = f"Surveillance_Report_{time_stamp}.xlsx"
    output_file = os.path.join(os.getcwd(),file_name)
    incident_df.to_excel(output_file, index = False)
    print(f"Report Exported: {output_file}")

camera_objects = {}
for cam_name, cam_url in camera_sources.items():
    camera_objects[cam_name] = cv2.VideoCapture(cam_url)
last_alert = {}
while True:
    for cam_name, cap in camera_objects.items():
        ret, frame = cap.read()
        if not ret:
            continue
        results = model(frame)
        detected = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                label = model.names[cls_id]
                detected.append(label)
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        violation = None
        if "person" in detected and "helmet" not in detected:
            violation = "Helmet Missing"
        if "person" in detected and "vest" not in detected:
            violation = "Safety Vest Missing"
        if "fire" in detected:
            violation = "Fire Detected"
        if "smoke" in detected:
            violation = "Smoke Detected"
        
        if violation:

            current_time = datetime.now().strftime(
                "%Y%m%d_%H:%M:%S"
            )

            if last_alert.get(
                f"{cam_name}_{violation}"
            ) != violation:

                incident_df.loc[
                    len(incident_df)
                ] = [
                    current_time,
                    cam_name,
                    violation,
                    round(confidence, 3)
                ]

                send_whatsapp(
                    f"{violation} in {cam_name} at {current_time}"
                )

                last_alert[
                    f"{cam_name}_{violation}"
                ] = violation

                snapshot_file = (
                    f"Snapshots/{cam_name}_{current_time}.jpg"
                )

                cv2.imwrite(
                    snapshot_file,
                    frame
                )
    cv2.imshow(cam_name, frame)
key = cv2.waitKey(1)
if key == ord("e"):
        export_excel()
if key == 27:
        for cap in camera_objects.values():
                cap.release()
                cv2.destroyAllWindows()
                break
    
