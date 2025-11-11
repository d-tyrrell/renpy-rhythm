# save as tools/onsets_to_beatmap.py (for example)
import sys, math
infile, outfile = sys.argv[1], sys.argv[2]

with open(infile) as f:
    # aubio prints one time per line
    times = [float(line.strip()) for line in f if line.strip()]

# Example beatmap: one timestamp per line with 3 decimal places
with open(outfile, "w") as out:
    for t in times:
        out.write(f"{t:.3f}\n")
