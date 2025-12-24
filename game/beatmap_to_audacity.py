#!/usr/bin/env python3
"""
Convert rhythm game beatmap to Audacity label file for manual editing.

Usage:
    python beatmap_to_audacity.py input_beatmap.txt output_labels.txt
"""

import sys

def convert_beatmap_to_audacity(input_file, output_file):
    """Convert beatmap format to Audacity label file"""
    timestamps = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                timestamp = float(line)
                timestamps.append(timestamp)
            except ValueError:
                continue
    
    # Write to Audacity label file
    # Format: START\tEND\tLABEL
    with open(output_file, 'w') as f:
        for timestamp in timestamps:
            # Use same timestamp for start and end (point label)
            f.write(f'{timestamp:.6f}\t{timestamp:.6f}\t\n')
    
    print(f'✓ Converted {len(timestamps)} beats from {input_file}')
    print(f'✓ Audacity label file saved to {output_file}')
    
    # Show some stats
    if len(timestamps) > 1:
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        bpm = 60.0 / avg_interval if avg_interval > 0 else 0
        print(f'  Average interval: {avg_interval:.3f}s')
        print(f'  Approximate BPM: {bpm:.1f}')
        print(f'  First beat: {timestamps[0]:.3f}s')
        print(f'  Last beat: {timestamps[-1]:.3f}s')
    
    print('')
    print('To edit in Audacity:')
    print('  1. Open your audio file in Audacity')
    print('  2. File → Import → Labels... and select the label file')
    print('  3. Adjust labels by dragging them')
    print('  4. Add new labels: Click position, press Ctrl+M while playing')
    print('  5. Delete labels: Click label, press Delete')
    print('  6. File → Export → Export Labels')
    print('  7. Convert back using: python audacity_to_beatmap.py labels.txt output.beatmap.txt')

def main():
    if len(sys.argv) != 3:
        print('Usage: python beatmap_to_audacity.py input_beatmap.txt output_labels.txt')
        print('')
        print('Example:')
        print('  python beatmap_to_audacity.py input_beatmap.beatmap.txt dae_song_labels.txt')
        print('')
        print('This converts your beatmap to Audacity labels for manual editing.')
        print('You can then refine the timing visually in Audacity.')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        convert_beatmap_to_audacity(input_file, output_file)
    except FileNotFoundError:
        print(f'Error: File not found: {input_file}')
        print('Make sure the beatmap file exists in the current directory.')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()