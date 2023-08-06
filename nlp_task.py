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
    ids = []
    return ids