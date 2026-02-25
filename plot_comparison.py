import matplotlib
from matplotlib import pyplot as plt
import numpy as np

entry_tokens_all = np.array([123075, 121532, 135872, 102987, 134415, 14016, 60232, 102164, 110768, 97436, 95793, 116429])
times_taken_seconds_all = np.array([142, 168, 168, 455, 160, 67, 145, 260, 419, 136, 427, 546])
times_taken_minutes_all= np.array([2.37, 2.8, 2.8, 7.583, 2.667, 1.1167, 2.4167, 4.33, 6.983, 2.267, 7.1167, 9.1])

entry_tokens_demo2pilots = np.array([14016, 60232, 102164, 110768, 97436, 95793, 116429])
times_taken_seconds_demo2pilots = np.array([67, 145, 260, 419, 136, 427, 546])
times_taken_minutes_demo2pilots = np.array([1.1167, 2.4167, 4.33, 6.983, 2.267, 7.1167, 9.1])

entry_tokens_cpc2 = np.array([123075, 121532, 135872, 102987, 134415])
times_taken_seconds_cpc2 = np.array([142, 168, 168, 455, 160])
times_taken_minutes_cpc2 = np.array([2.37, 2.8, 2.8, 7.583, 2.667])

plt.figure(figsize=(15, 10))

plt.subplot(4, 2, 1)
plt.bar(entry_tokens_all, times_taken_seconds_all)
plt.xlabel("Entry Tokens")
plt.ylabel("Time Taken (s)")
plt.title("# of Entry Tokens vs Time Taken on Questions (s)")
plt.grid()


plt.subplot(4, 2, 2)
plt.bar(entry_tokens_all, times_taken_minutes_all)
plt.xlabel("Entry Tokens")
plt.ylabel("Time Taken (min)")
plt.title("# of Entry Tokens vs Time Taken on Questions (min)")
plt.grid()


plt.subplot(4, 2, 3)
plt.bar(entry_tokens_demo2pilots, times_taken_seconds_demo2pilots)
plt.xlabel("Entry Tokens")
plt.ylabel("Time Taken (s)")
plt.title("Demo2Pilots: # of Entry Tokens vs Time Taken on Questions (s)")
plt.grid()


plt.subplot(4, 2, 4)
plt.bar(entry_tokens_demo2pilots, times_taken_minutes_demo2pilots)
plt.xlabel("Entry Tokens")
plt.ylabel("Time Taken (min)")
plt.title("Demo2Pilots: # of Entry Tokens vs Time Taken on Questions (min)")
plt.grid()

plt.tight_layout()
plt.show()