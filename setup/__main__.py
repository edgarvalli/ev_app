import sys
from pathlib import Path

app_path = Path(__file__).parent.parent
sys.path.insert(0,str(app_path))

import dbinit