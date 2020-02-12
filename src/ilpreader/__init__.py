"""Read ilastik project files."""

from __future__ import annotations

import json
import operator
import os
import re
from dataclasses import dataclass
from typing import FrozenSet, Mapping, Optional, Sequence, Tuple

import h5py
import numpy


@dataclass
class PixelClassification:
    time: str
    ilastik_version: str
    lanes: Sequence[Lane]
    features: FrozenSet[Feature]
    classes: Mapping[int, Class]
    labels: Sequence[Sparse]


@dataclass
class Lane:
    source: Optional[InputMeta]
    mask: Optional[InputMeta]


@dataclass(frozen=True)
class InputMeta:
    uuid: str
    name: str
    shape: Tuple[int, ...]
    dims: Tuple[str, ...]
    location: str
    path: str


@dataclass
class Sparse:
    coords: numpy.ndarray
    data: numpy.ndarray


@dataclass(frozen=True)
class Feature:
    name: str
    scale: float
    dims: FrozenSet[str]


@dataclass(frozen=True)
class Class:
    name: str
    color: str


def read(d):
    if isinstance(d, h5py.Group):
        return _read(d)
    with h5py.File(os.fspath(d), mode="r") as f:
        return _read(f)


def _read(d):
    workflow = d["workflowName"][()].decode()
    if workflow != "Pixel Classification":
        raise NotImplementedError(f"workflow {workflow!r}")
    return PixelClassification(
        time=d["time"][()].decode(),
        ilastik_version=d["ilastikVersion"][()].decode(),
        lanes=_read_lanes(d),
        features=_read_features(d),
        classes=_read_classes(d),
        labels=_read_labelsets(d),
    )


def _read_lanes(d):
    return tuple(
        Lane(
            source=_read_input_meta(d, lane_key=k, role_key="Raw Data"),
            mask=_read_input_meta(d, lane_key=k, role_key="Prediction Mask"),
        )
        for k in sorted(d["Input Data/infos"])
        if k.startswith("lane")
    )


def _read_input_meta(d, *, lane_key, role_key):
    role = d.get(f"Input Data/infos/{lane_key}/{role_key}")

    # bool(h5py.Group) == True even if len(h5py.Group) == 0.
    if not (role and len(role)):
        return None

    axis_tags = role["axistags"][()].decode()
    dims = tuple(ax["key"] for ax in json.loads(axis_tags)["axes"])

    location = role["location"][()].decode()
    if location == "FileSystem":
        path = role["filePath"][()].decode()
    elif location == "ProjectInternal":
        path = role["inner_path"][()].decode()
    else:
        path = ""

    return InputMeta(
        uuid=role["datasetId"][()].decode(),
        name=role["nickname"][()].decode(),
        shape=tuple(role["shape"]),
        dims=dims,
        location=location,
        path=path,
    )


def _read_labelsets(d):
    return tuple(
        _read_labels(d, label_key=k)
        for k in d["PixelClassification/LabelSets"]
        if k.startswith("label")
    )


def _read_labels(d, *, label_key):
    blocks = [
        _read_label_block(d, label_key=label_key, block_key=k)
        for k in sorted(d[f"PixelClassification/LabelSets/{label_key}"])
        if k.startswith("block")
    ]

    if not all(len(b) == len(blocks[0]) for b in blocks[1:]):
        raise ValueError("blocks have different dimension counts")

    *coords, data = map(list, zip(*blocks))
    return Sparse(coords=numpy.block(coords), data=numpy.concatenate(data))


def _read_label_block(d, *, label_key, block_key):
    block = d[f"PixelClassification/LabelSets/{label_key}/{block_key}"]

    roi = block.attrs["blockSlice"]
    offsets = list(map(int, re.findall(rb"(\d+):\d+", roi)))
    if len(offsets) != block.ndim:
        raise ValueError("cannot match label block with it's ROI")

    # h5py doesn't support arbitrary fancy indexing.
    block = numpy.asarray(block)

    rel_idx = numpy.nonzero(block)
    abs_idx = map(operator.add, rel_idx, offsets)
    labels = block[rel_idx]
    return [*abs_idx, labels]


def _read_features(d):
    fs = d["FeatureSelections"]
    selections = fs["SelectionMatrix"]
    names = list(map(bytes.decode, fs["FeatureIds"]))
    scales = fs["Scales"]

    xy, xyz = frozenset("xy"), frozenset("xyz")
    dims = [xy if in2d else xyz for in2d in fs["ComputeIn2d"]]

    if not (selections.shape == (len(names), len(scales)) and len(scales) == len(dims)):
        raise ValueError("invalid feature attributes")

    return frozenset(
        Feature(name=names[row], scale=scales[col], dims=dims[col])
        for row, col in numpy.argwhere(selections)
    )


def _read_classes(d):
    pc = d["PixelClassification"]
    labels = pc["ClassifierForests/known_labels"]
    names = list(map(bytes.decode, pc["LabelNames"]))
    colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in pc["LabelColors"]]

    if not (len(labels) == len(names) == len(colors)):
        raise ValueError("invalid class attributes")

    return {
        label: Class(name=name, color=color)
        for label, name, color in zip(labels, names, colors)
    }
