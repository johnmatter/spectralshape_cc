import argparse
import mido
import matplotlib.pyplot as plt
from collections import defaultdict
import math
import re
import json

"""
View the CC values of a MIDI file over time.
Intended as diagnostic info for coldtype animations.
"""

# Global layout variables
n_cols = 3  # Number of columns in the subplot grid
n_rows = None  # Number of rows (will be calculated based on CCs if None)

def read_midi_cc_and_metadata(file_path):
    """ Reads a MIDI file and extracts CC values and metadata text events """
    mid = mido.MidiFile(file_path)
    
    # Dictionary to store CC values per channel
    cc_data = defaultdict(lambda: defaultdict(list))
    
    # Dictionary to store metadata from text events
    cc_names = {}
    track_title = None
    
    time = 0
    for msg in mid:
        time += msg.time
        
        if msg.type == 'control_change':
            cc_data[msg.channel][msg.control].append((time, msg.value))
        
        # Handle meta messages based on their specific types
        elif msg.is_meta:
            # Track name / title
            if msg.type == 'track_name':
                track_title = msg.name
            
            # Text events
            elif msg.type == 'text':
                # Get the text content
                text_content = getattr(msg, 'text', None)
                
                if text_content:
                    # Look for CC mapping in format "CC# = Name"
                    match = re.match(r'CC(\d+)\s*=\s*(.+)', text_content)
                    if match:
                        cc_num = int(match.group(1))
                        feature_name = match.group(2).strip()
                        cc_names[cc_num] = feature_name
                    
                    # Check if it's a JSON mapping
                    elif text_content.startswith('{') and text_content.endswith('}'):
                        try:
                            json_data = json.loads(text_content)
                            if isinstance(json_data, dict):
                                # Convert string keys to integers if needed
                                for key, value in json_data.items():
                                    cc_names[int(key) if key.isdigit() else key] = value
                        except json.JSONDecodeError:
                            print(f"Warning: Failed to parse JSON: {text_content[:50]}...")

    return cc_data, cc_names, track_title

def plot_midi_cc(cc_data, cc_names=None, track_title=None):
    """ Plots CC data with one subplot per CC, using feature names if available """
    # Collect all unique CCs across all channels
    all_ccs = []
    for channel, controls in cc_data.items():
        for control in controls:
            all_ccs.append((channel, control))
    
    # Calculate number of rows if not provided
    global n_rows
    if n_rows is None:
        n_rows = math.ceil(len(all_ccs) / n_cols)
    
    # Create figure with subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 2.0 * n_rows), sharex=True)
    
    # Handle case where there's only one row or column
    if n_rows == 1 and n_cols == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [axes]
    elif n_cols == 1:
        axes = [[ax] for ax in axes]
    
    # Plot each CC on its own subplot
    for idx, (channel, control) in enumerate(all_ccs):
        if idx >= n_rows * n_cols:
            print(f"Warning: Not enough subplots for all CCs. Increase n_rows or n_cols.")
            break
            
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row][col]
        
        values = cc_data[channel][control]
        times, vals = zip(*values)
        ax.plot(times, vals, marker='', linestyle='-', color=f'C{idx % 10}')
        
        # Use feature name if available, otherwise use CC number
        if cc_names and control in cc_names:
            title = f'Ch {channel} CC {control}: {cc_names[control]}'
        else:
            title = f'Ch {channel} CC {control}'
            
        ax.set_title(title)
        ax.set_ylabel('Value (0-127)')
        ax.set_ylim(-5, 132)  # Give some padding to the y-axis range
        ax.grid(True)
    
    # Hide unused subplots
    for idx in range(len(all_ccs), n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row][col].set_visible(False)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)  # Increase padding below the figure title
    
    # Use track title if available
    if track_title:
        plt.suptitle(track_title, fontsize=14, y=0.98)
    else:
        plt.suptitle('MIDI CC Values Over Time', fontsize=14, y=0.98)
        
    plt.xlabel('Time (s)')
    plt.show()

def main(args):
    # Update global variables if provided as arguments
    global n_cols, n_rows
    if args.cols:
        n_cols = args.cols
    if args.rows:
        n_rows = args.rows
        
    midi_file = args.midi_file
    cc_data, cc_names, track_title = read_midi_cc_and_metadata(midi_file)

    plot_midi_cc(cc_data, cc_names, track_title)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot MIDI CC values over time')
    parser.add_argument('midi_file', type=str, help='Path to the MIDI file')
    parser.add_argument('--cols', type=int, help='Number of columns in the subplot grid')
    parser.add_argument('--rows', type=int, help='Number of rows in the subplot grid')
    args = parser.parse_args()
    main(args)
