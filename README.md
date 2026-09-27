# CodePulse

CodePulse is a lightweight command‑line tool and Python library that aggregates several maintainability metrics into a single, easy‑to‑read report. It focuses on:

* **Verbosity** – average lines‑of‑code per function.
* **Duplication** – number of duplicate lines across files.
* **Erosion** – ratio of duplicate lines to total lines, indicating potential code churn due to duplication.
* **Cognitive Complexity** – count of statements per function.

The tool is designed for quick, local analysis and can be integrated into CI pipelines.

## Installation

```bash
pip install .
```

## Usage

```bash
# Analyze the current directory
codepulse analyze .
```

The command outputs a JSON report to stdout. Use `-o <file>` to write to a file.

## Library API

```python
from metrics import analyze
report = analyze("./my_project")
print(report)
```

## Extending

The core logic lives in `metrics.py`.  Adding support for other languages would require extending this module; the `LanguageAnalyzer` base class is not currently used by the analysis pipeline.

## License

MIT

<!-- ORION-MONETIZATION:START -->
## Support

If you find CodePulse helpful, please consider supporting its continued development with a $5 donation: https://paypal.me/Damonwill. Your contribution helps maintain the tool and enables optional support for contributors.
<!-- ORION-MONETIZATION:END -->
