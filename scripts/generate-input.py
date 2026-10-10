#!/usr/bin/env python3
"""Identical generator action used by each orchestrator."""
import json,sys
from pathlib import Path
kind,output=sys.argv[1:]
value=json.loads(Path('inputs/spec.json').read_text())['value']
text=f'#pragma once\n#define GENERATED_VALUE {value}\n' if kind=='header' else '#include "config.h"\nint generated_value(){return GENERATED_VALUE;}\n'
Path(output).write_text(text)
