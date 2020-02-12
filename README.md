# ilp-reader

Read ilastik .ilp files.

![Travis (.com)](https://img.shields.io/travis/com/ilastik/ilp-reader?style=for-the-badge)
![Codecov](https://img.shields.io/codecov/c/github/ilastik/ilp-reader?style=for-the-badge)

## Development

- Initial setup:
  1. Install [tox](https://tox.readthedocs.io): `pip install tox`
  2. Create a development environment: `tox -e ilp-reader-dev`
  3. Activate the development environment: `. .tox/ilp-reader-dev/bin/activate`
- Format code: `make fmt` or just `make`
- Run tests: `tox`
- Coverage report: `tox -e report` and open `.htmlcov/index.html`
