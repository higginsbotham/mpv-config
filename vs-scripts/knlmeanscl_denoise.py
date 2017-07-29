import vapoursynth as vs
core = vs.get_core()
if "video_in" in globals():
    clip = video_in
else:
    clip = core.ffms2.Source(source=in_filename)

clip = core.knlm.KNLMeansCL(clip, d=3, a=3, s=4, h=1.2, channels="auto", wmode=0, wref=1.0)
clip.set_output()
