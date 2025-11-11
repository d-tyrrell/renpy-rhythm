init python:
    import random  # <-- REQUIRED for random_laser_color

    # bright-ish neon palette
    def random_laser_color():
        return random.choice(["#0ff", "#f0f", "#ff0", "#0f8", "#08f", "#f80"])


init python:
    # Utility: pick a bright color (you can restrict to a palette if you want)
    def random_laser_color():
        # neon-ish choices work well
        return random.choice(["#0ff", "#f0f", "#ff0", "#0f8", "#08f", "#f80"])


transform addblend:
    blend "add"

transform laser_anim(theta=0, dur=0.25):
    anchor (0.5, 0.5)
    rotate theta
    alpha 0.0
    on show:
        parallel:
            linear dur*0.3 alpha 0.85
            linear dur*0.7 alpha 0.0
        parallel:
            linear dur*0.5 xzoom 0.6
            linear dur*0.5 xzoom 1.2
    on hide:
        alpha 0.0


transform addblend:
    blend "add"


screen laser_bg(beats, channel=None, intensity=1, offset=0.0):
    # --- persistent screen state ---
    default idx = 0
    default lasers = []
    default resolved_channel = channel

    # --- debug state so first frame never crashes ---
    default debug_pos = 0.0
    default debug_next = None
    default debug_idx = 0
    default debug_total = 0
    default debug_spawned = 0
    default debug_cur = "None"
    default debug_raw = 0.0
    default fake_pos = 0.0
    default test_ticks = 0



    # quick heartbeat
    $ tick = 1.0 / 60.0

        # fire every frame; bump a counter so we can see it move
    timer 0.0 repeat True action [
        SetScreenVariable("_ticks", test_ticks + 1),
        Function(_laser_tick, beats, channel, intensity, offset)
    ]

    text ("ticks=%d" % test_ticks) xalign 0.30 yalign 0.01

    # optional banner so you know it's on
    text "Laser BG Loaded" xalign 0.5 yalign 0.10 color "#0f0"

    # debug overlay
    text ("LASERS • ch=%s" % (resolved_channel if resolved_channel else "…")) xalign 0.01 yalign 0.01
    text ("pos=%.2f  next=%s" % (debug_pos, ("%.2f" % debug_next) if debug_next is not None else "—")) xalign 0.01 yalign 0.05
    text ("idx=%d / %d   spawned=%d   count=%d" % (debug_idx, debug_total, debug_spawned, len(lasers))) xalign 0.01 yalign 0.09
    text ("cur=%s" % (debug_cur if debug_cur is not None else "None")) xalign 0.01 yalign 0.12
    text ("raw=%.2f" % (debug_raw if debug_raw is not None else 0.0)) xalign 0.18 yalign 0.12

    # render beams
    for l in lasers:
        $ beam = Solid(l["color"], xysize=(l["w"], l["h"]))
        add beam at addblend, laser_anim(theta=l["theta"], dur=l["dur"]) xpos l["x"] ypos l["y"] anchor (0.5, 0.5)

init python:
    POSSIBLE_CHANNELS = [CHANNEL_RHYTHM_GAME, "music", "sound", "voice", "sfx"]

    def _laser_tick(beats, channel, intensity, offset):
        scr = renpy.current_screen()
        if not scr:
            return
        scope = scr.scope

        # pull state
        lasers = scope.get("lasers", [])
        idx    = int(scope.get("idx", 0))

        # -------- resolve channel (prefer the one passed in) --------
        ch = scope.get("resolved_channel")

        if channel:
            try:
                # as soon as anything is queued, lock to this channel
                if renpy.music.get_playing(channel=channel) is not None:
                    ch = channel
                    scope["resolved_channel"] = ch
            except Exception:
                pass

        if scope.get("resolved_channel") is None:
            # bootstrap search
            candidates = ([channel] if channel else []) + [c for c in POSSIBLE_CHANNELS if c != channel]
            for c in candidates:
                try:
                    if renpy.music.get_playing(channel=c) is not None:
                        ch = c
                        break
                except Exception:
                    pass
            scope["resolved_channel"] = ch

        # -------- scale beats once (ms -> s if needed), reset idx once --------
        beats_scaled = scope.get("beats_scaled")
        if beats_scaled is None:
            bmax  = max(beats) if beats else 0.0
            scale = 0.001 if bmax > 600 else 1.0
            beats_scaled = [b * scale for b in beats]
            scope["beats_scaled"] = beats_scaled
            idx = 0
            scope["idx"] = 0

        # -------- playhead: prefer raw channel time; fallback to local clock --------
        # local accumulator so we can spawn even if get_pos() is 0 for a moment
        fake_pos = float(scope.get("fake_pos", 0.0))
        raw = 0.0
        cur = None

        if scope.get("resolved_channel"):
            try:
                raw = renpy.music.get_pos(channel=scope["resolved_channel"]) or 0.0
                cur = renpy.music.get_playing(channel=scope["resolved_channel"]) or None
            except Exception:
                pass

        # if audio time is advancing, trust it; otherwise tick our own timebase
        if raw > 0.0:
            pos = raw
            fake_pos = raw
        else:
            # advance ~60 fps
            pos = fake_pos + (1.0 / 60.0)
            fake_pos = pos

        scope["fake_pos"] = fake_pos

        # debug exports
        scope["debug_cur"]   = cur if cur is not None else "None"
        scope["debug_raw"]   = raw
        scope["debug_pos"]   = pos
        scope["debug_next"]  = (beats_scaled[idx] if idx < len(beats_scaled) else None)
        scope["debug_idx"]   = idx
        scope["debug_total"] = len(beats_scaled)

        # -------- spawn when crossing beats --------
        spawned = 0
        while idx < len(beats_scaled) and beats_scaled[idx] <= pos:
            spawned += 1
            idx += 1
        scope["idx"] = idx
        scope["debug_spawned"] = spawned

        if spawned > 0:
            # scale bursts with intensity; cap to avoid spam
            count = max(spawned, int(spawned * (1 + intensity)))
            count = min(count, 10)
            for _ in range(count):
                w     = renpy.random.randint(900, 1500)
                h     = renpy.random.randint(10, 18)
                theta = renpy.random.randint(0, 179)
                dur   = renpy.random.uniform(0.35, 0.55)
                color = random_laser_color()
                x     = renpy.random.uniform(0.05, 0.95) * config.screen_width
                y     = renpy.random.uniform(0.15, 0.85) * config.screen_height
                lasers.append(dict(x=x, y=y, w=w, h=h, color=color, theta=theta, dur=dur, expiry=pos + dur))

        # prune expired beams
        scope["lasers"] = [l for l in lasers if pos <= l["expiry"]]
        renpy.restart_interaction()
