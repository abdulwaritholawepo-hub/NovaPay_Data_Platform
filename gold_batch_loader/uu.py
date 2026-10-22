from collections import Counter

my_list = ["apple", "banana", "apple", "orange", "banana", "apple"]

# Count frequencies of all items
frequencies = Counter(my_list)
print(frequencies)
# Output: Counter({'apple': 3, 'banana': 2, 'orange': 1})

# To get the count of a specific duplicate item:
print(frequencies["apple"])  # Output: 3

duplicate_counts = {item: count for item,
                    count in frequencies.items() if count > 1}
print(duplicate_counts)
# Output: {'apple': 3, 'banana': 2}
