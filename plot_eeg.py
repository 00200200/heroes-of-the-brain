import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv('/home/licho/Programming/HACKATON-HOTB/backend/data/eeg_recordings/eeg_data_20251129_153725.csv')

# Create a figure with multiple subplots
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: EEG Channels
ax1 = axes[0]
for channel in ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']:
    ax1.plot(df.index, df[channel], label=channel, alpha=0.7)
ax1.set_xlabel('Sample Index')
ax1.set_ylabel('Amplitude (µV)')
ax1.set_title('EEG Data - All 8 Channels')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Accelerometer Data
ax2 = axes[1]
ax2.plot(df.index, df['accel_x'], label='accel_x', alpha=0.7)
ax2.plot(df.index, df['accel_y'], label='accel_y', alpha=0.7)
ax2.plot(df.index, df['accel_z'], label='accel_z', alpha=0.7)
ax2.set_xlabel('Sample Index')
ax2.set_ylabel('Acceleration (m/s²)')
ax2.set_title('Accelerometer Data')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Battery Level
ax3 = axes[2]
ax3.plot(df.index, df['battery_level'], color='green', linewidth=2)
ax3.set_xlabel('Sample Index')
ax3.set_ylabel('Battery Level (%)')
ax3.set_title('Battery Level Over Time')
ax3.set_ylim([0, 100])
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/licho/Programming/HACKATON-HOTB/eeg_plot.png', dpi=150, bbox_inches='tight')
print("✓ Plot saved to eeg_plot.png")

# Print basic statistics
print("\nData Statistics:")
print(f"Total samples: {len(df)}")
print(f"Duration: {df['timestamp'].max() - df['timestamp'].min():.2f} seconds")
print(f"\nEEG Channels Summary:")
for channel in ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8']:
    print(f"  {channel}: min={df[channel].min():.2f}, max={df[channel].max():.2f}, mean={df[channel].mean():.2f}")
