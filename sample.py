import pandas as pd
import numpy as np
from datetime import datetime, timedelta

NUM_CROSSINGS = 100
# Create sample data
np.random.seed(99)  # For reproducibility

# Generate 10 datetimes spaced by minutes
start_time = datetime.now()
times = [start_time - timedelta(minutes=i*5) for i in range(NUM_CROSSINGS)]

# Random directions
directions = np.random.choice(['in', 'out', 'turnback'], size=NUM_CROSSINGS)

# Random categories
categories = np.random.choice(['car', 'person'], size=NUM_CROSSINGS)

# Create DataFrame
df = pd.DataFrame({
    'crossed_at': times,
    'direction': directions,
    'category': categories
})
