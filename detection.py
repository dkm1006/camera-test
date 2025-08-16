from dataclasses import dataclass

from transformers import pipeline

from config import DETECTION_MODEL, LABELS


@dataclass
class Centroid:
    x: int
    y: int


@dataclass
class BoundingBox:
    xmin: int
    xmax: int
    ymin: int
    ymax: int

    @property
    def centroid(self) -> Centroid:
        return Centroid(
            x=(self.xmax + self.xmin) // 2,
            y=(self.ymax - self.ymin) // 2
        )


@dataclass
class Detection:
    label: str
    score: float
    bbox: BoundingBox
    centroid: Centroid


class ObjectDetector:
    def __init__(self, model:str=DETECTION_MODEL, labels:set=LABELS, threshold:float=0.5):
        self._pipe = pipeline('object-detection', model=DETECTION_MODEL)
        self.labels = labels
        self._threshold

    def detect(self, image:'PIL.Image') -> list[Detection]:
        detections = self._pipe(image)
        filtered_detections = [
            self._transform_detection(detection)
            for detection in detections
            if detection['label'] in self.labels
        ]
        return filtered_detections
    
    def _transform_detection(self, detection_dict:dict) -> Detection:
        label = detection_dict.pop('label')
        score = detection_dict.pop('score')
        bbox = BoundingBox(**detection_dict)
        centroid = bbox.centroid
        return Detection(label=label, score=score, bbox=bbox, centroid=centroid)
