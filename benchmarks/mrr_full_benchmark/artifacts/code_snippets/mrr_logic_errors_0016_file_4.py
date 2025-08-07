def process_data(data: List[Dict]) -> Dict[str, Any]:
    """Process input data and return aggregated results."""
    results = {}
    for item in data:
        key = item.get('id')
        if key and validate_item(item):
            results[key] = transform_item(item)
    return results

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from .utils import validate_data, transform_data
from ..core import BaseProcessor