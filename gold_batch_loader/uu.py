from datetime import datetime

# Get current date
now = datetime.now()

# Calculate the quarter
quarter = (now.month - 1) // 3 + 1

print(f"Date: {now.strftime('%Y-%m-%d')}")
print(f"Quarter: Q{quarter}")
