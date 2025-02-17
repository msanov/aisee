import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from huggingface_hub import snapshot_download

from aisee import VisionClassifier

TEST_PATH = Path(__file__).resolve().parent
if not Path(TEST_PATH, "resources").exists():
    snapshot_download(
        repo_id="IIC/aisee_resources", local_dir=f"{TEST_PATH}/resources/",
    )

SINGLE_LABEL_DATAFRAME = pd.DataFrame(
    [
        (f"{TEST_PATH}/resources/images/train/cat/cat1.jpg", "cat", "train"),
        (f"{TEST_PATH}/resources/images/train/cat/cat2.jpg", "cat", "train"),
        (f"{TEST_PATH}/resources/images/val/cat/cat3.jpg", "cat", "val"),
        (f"{TEST_PATH}/resources/images/train/dog/dog1.jpg", "dog", "train"),
        (f"{TEST_PATH}/resources/images/train/dog/dog2.jpg", "dog", "train"),
        (f"{TEST_PATH}/resources/images/val/dog/dog3.jpg", "dog", "val"),
    ],
    columns=["path", "label", "fold"],
)

MODEL_TEST = "mobilenetv2_050"
MODEL_TEST_COMPOSITE_CLASSIFIER = "vgg11_bn"


@pytest.mark.parametrize("learning_method", ["from_scratch", "freezed", "unfreezed"])
@pytest.mark.parametrize("extra_layer", [None, 500])
@pytest.mark.parametrize("dropout", [None, 0.3])
def test_vision_classifier_load_model(learning_method, extra_layer, dropout):
    """Check that VisionClassifier is instantiated and the model is loaded."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=4,
        learning_method=learning_method,
        dropout=dropout,
        extra_layer=extra_layer,
        task="single_label",
    )

    assert isinstance(vc, VisionClassifier)


def test_vision_classifier_load_model_with_composite_classifier_index():
    """Check that VisionClassifier is instantiated and the model is loaded with composite classifier index."""
    vc = VisionClassifier(
        model_name=MODEL_TEST_COMPOSITE_CLASSIFIER,
        num_classes=4,
        task="single_label",
    )

    assert isinstance(vc, VisionClassifier)


def test_vision_classifier_load_model_custom_weights():
    """Check that VisionClassifier is instantiated and the model is loaded with custom weight."""
    vc = VisionClassifier(
        model_name=MODEL_TEST_COMPOSITE_CLASSIFIER,
        num_classes=2,
        weights_path=f"{TEST_PATH}/resources/custom_weights/vgg1_bn_single_label_weights.pt",
        task="single_label",
    )

    assert isinstance(vc, VisionClassifier)


def test_vision_classifier_predict_single_label_series():
    """Check that VisionClassifier predict single label problem with Pandas Series."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="single_label",
    )

    predictions = vc.predict(SINGLE_LABEL_DATAFRAME["path"])

    assert len(predictions) == len(SINGLE_LABEL_DATAFRAME)

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )

    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_classifier_predict_single_label_dataframe():
    """Check that VisionClassifier predict single label problem with Pandas DataFrame."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="single_label",
    )

    predictions = vc.predict(SINGLE_LABEL_DATAFRAME)

    assert len(predictions) == len(SINGLE_LABEL_DATAFRAME)

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )

    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_classifier_predict_single_label_one_image():
    """Check that VisionClassifier predict single label problem with one image."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="single_label",
    )

    predictions = vc.predict(f"{TEST_PATH}/resources/images/train/cat/cat1.jpg")

    assert len(predictions) == 1

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )
    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_classifier_predict_single_label_path():
    """Check that VisionClassifier predict single label problem with path to directory."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="single_label",
    )

    data_dir = f"{TEST_PATH}/resources/images/val"

    number_of_images = 0
    for _, _, files in os.walk(data_dir):
        number_of_images += len(files)

    predictions = vc.predict(data_dir)

    assert len(predictions) == number_of_images

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )

    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_predict_custom_weights():
    """Check that VisionClassifier predict single label problem with custom weights."""
    vc = VisionClassifier(
        model_name=MODEL_TEST_COMPOSITE_CLASSIFIER,
        num_classes=2,
        weights_path=f"{TEST_PATH}/resources/custom_weights/vgg1_bn_single_label_weights.pt",
        task="single_label",
    )

    data_dir = f"{TEST_PATH}/resources/images/val"

    number_of_images = 0
    for _, _, files in os.walk(data_dir):
        number_of_images += len(files)

    predictions = vc.predict(data_dir)

    assert len(predictions) == number_of_images

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )

    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_classifier_predict_multi_label():
    """Check that VisionClassifier predict multi label."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=25,
        task="multi_label",
    )

    data = pd.read_csv(f"{TEST_PATH}/resources/multilabel/train.csv")
    data["path"] = data["path"].apply(lambda x: f"{TEST_PATH}/{x}")

    predictions = vc.predict(data)

    assert len(predictions) == len(data)

    for pred in predictions:
        assert all(
            key in pred
            for key in ["image_path", "probabilities", "prediction", "real_label"]
        )

    assert isinstance(predictions[0]["image_path"], str)

    for key in ["probabilities", "prediction", "real_label"]:
        assert isinstance(predictions[0][key], np.ndarray)

    assert all(
        (predictions[0]["probabilities"] >= 0) & (predictions[0]["probabilities"] <= 1),
    )


def test_vision_classifier_data_value_error():
    """Check that VisionClassifier predict raise a ValueError with numeric data."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="single_label",
    )

    with pytest.raises(ValueError):
        vc.predict(34)


def test_vision_classifier_task_not_suported_error():
    """Check that VisionClassifier raise a ValueError with bad task."""
    with pytest.raises(ValueError):
        VisionClassifier(
            model_name=MODEL_TEST,
            num_classes=2,
            task="multi_single_label",
        )


def test_vision_classifier_learning_method_not_suported_error():
    """Check that VisionClassifier raise a ValueError with bad learning_method."""
    with pytest.raises(ValueError):
        VisionClassifier(
            model_name=MODEL_TEST,
            num_classes=2,
            learning_method="bad_method",
        )


def test_vision_classifier_duplicated_columns_error():
    """Check that VisionClassifier predict raise a ValueError with duplicated columns."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task="multi_label",
    )

    data = pd.read_csv(f"{TEST_PATH}/resources/multilabel/train.csv")
    data["path"] = data["path"].apply(lambda x: f"{TEST_PATH}/{x}")
    data = data.rename({"Adventure": "Action"}, axis=1)

    with pytest.raises(ValueError):
        vc.predict(data)


@pytest.mark.parametrize(
    "task, data",
    [
        ("single_label", SINGLE_LABEL_DATAFRAME.drop(["path"], axis=1)),
        (
            "multi_label",
            pd.read_csv(f"{TEST_PATH}/resources/multilabel/train.csv").drop(
                ["path"],
                axis=1,
            ),
        ),
    ],
)
def test_vision_classifier_missing_columns_error(task, data):
    """Check that VisionClassifier predict raise a ValueError with missing columns."""
    vc = VisionClassifier(
        model_name=MODEL_TEST,
        num_classes=2,
        task=task,
    )

    with pytest.raises(ValueError):
        vc.predict(data)
