# STEP 1: Import the necessary modules.
from mediapipe.tasks import python
from mediapipe.tasks.python import text


async def detect_language(input_text):
    # STEP 2: Create a LanguageDetector object.
    base_options = python.BaseOptions(model_asset_path="./models/detector.tflite")
    options = text.LanguageDetectorOptions(base_options=base_options)
    detector = text.LanguageDetector.create_from_options(options)

    # STEP 3: Get the language detection result for the input text.
    detection_result = detector.detect(input_text)

    # print(detection_result)
    # STEP 4: Process the detection result and return the language code.
    for detection in detection_result.detections:
        return detection.language_code

async def recommend_insurances(questions):
    #개발중입니다.
    ids = ["6d63fb72-fe0a-4a45-8e16-5b61dbf586c1", "819d6360-9ed2-4bfe-a0c3-dfdabfa62924", "7307918d-c580-43f5-8c12-19d514a49937", "b655dbd0-32bf-48a2-a938-ae812d18886b"]
    return ids