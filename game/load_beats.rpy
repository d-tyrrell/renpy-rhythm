init python:
    import random

    def load_beats(path):
        beats = []
        try:
            for line in renpy.file(path):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Accept "1.23" or "1234" ms if you want
                t = float(line)
                beats.append(t)
        except Exception as e:
            renpy.log("Beatmap load error: %r" % e)
        return beats
