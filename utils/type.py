from typing import Any, Dict, NamedTuple

from models.note_prediction import NotePredictionModel


StateDict = Dict[str, Any]
NotePredictionCheckpoint = NamedTuple('NotePredictionCheckpoint', [('epoch', int), ('modeldict', StateDict), ('optimizerdict', StateDict), ('loss', float)])