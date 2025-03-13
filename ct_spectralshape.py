from coldtype import *

mt = MidiTimeline(ººsiblingºº("media/wren.midi"))
wav = ººsiblingºº("media/wren.wav")

fnt = "Webdings"

@animation((1080, 9/16*1080), tl=mt, bg=0, audio=wav)
def cc(f):
    # cache(?) midi data for this frame
    mt.hold(f.i)

    birdsong_kurtosis = ez(mt.ci(3), "eeo", rng=(0.0, 1.0))

    return (
        P(
            StSt(
                "",
                fnt,
                200,
            ),
        )
        .mapv(lambda e, p: (p.f(hsl(0.3+0.5*birdsong_kurtosis, s=0.2+0.6*birdsong_kurtosis, l=0.25+0.5*birdsong_kurtosis))))
        .s(1).sw(15).sf(1) # outlines
        .layer(2) # two rows
        .stack(95) # spacing between rows
        .align(f.a.r) # center
    )
