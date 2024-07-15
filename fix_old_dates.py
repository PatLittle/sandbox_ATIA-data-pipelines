import re

import pandas as pd
df = pd.read_csv('full_witness_meetings_output.csv')
df['Date'] = df['Date'].apply(lambda x: x if re.match(r'\d{4}-\d{2}-\d{2}', x) else pd.to_datetime(x, format='%A, %B %d, %Y').strftime('%Y-%m-%d'))
df.to_csv('full_witness_meetings_output.csv', index=False)



