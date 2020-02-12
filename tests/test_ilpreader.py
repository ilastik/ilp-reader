import pathlib

import pytest

import ilpreader as ilp


@pytest.fixture
def datadir(request):
    return pathlib.Path(request.fspath.dirname) / "data"


def test_read(datadir):
    project = ilp.read(
        datadir / "pixel-classification-0001" / "pixel-classification.ilp"
    )

    # Only test labels' shapes.
    labels, project.labels = project.labels, ()
    assert len(labels) == 1
    assert labels[0].coords.shape == (3, 602)
    assert labels[0].data.shape == (602,)

    assert project == ilp.PixelClassification(
        time="Mon Dec  2 11:21:31 2019",
        ilastik_version="1.3.3post1",
        lanes=(
            ilp.Lane(
                source=ilp.InputMeta(
                    uuid="2bf8ce38-14ed-11ea-8cfa-9cb6d0beba4b",
                    name="input",
                    shape=(1024, 1344, 1),
                    dims=("y", "x", "c"),
                    location="FileSystem",
                    path="data/input.png",
                ),
                mask=None,
            ),
        ),
        features=frozenset(
            {
                ilp.Feature(
                    name="GaussianSmoothing", scale=1.6, dims=frozenset({"x", "y"})
                ),
                ilp.Feature(
                    name="LaplacianOfGaussian", scale=5, dims=frozenset({"x", "y"})
                ),
                ilp.Feature(
                    name="DifferenceOfGaussians", scale=1, dims=frozenset({"x", "y"})
                ),
                ilp.Feature(
                    name="StructureTensorEigenvalues",
                    scale=0.7,
                    dims=frozenset({"x", "y"}),
                ),
                ilp.Feature(
                    name="HessianOfGaussianEigenvalues",
                    scale=3.5,
                    dims=frozenset({"x", "y"}),
                ),
            }
        ),
        classes={
            1: ilp.Class(name="Background", color="#ffe119"),
            2: ilp.Class(name="Dim Cells", color="#0082c8"),
            3: ilp.Class(name="Bright Cells", color="#e6194b"),
        },
        labels=(),
    )
