#!/bin/bash

# Активира виртуалната среда
source venv/bin/activate

# Изпълнява главния Python скрипт
echo "🚀 Стартиране на Orbitron-AI Pipeline..."
python scripts/run_pipeline.py
echo "🏁 Pipeline завърши."