import vapoursynth as vs
core = vs.get_core()

if "video_in" in globals():
    # realtime
    clip = video_in

else:
    # run with vspipe
    core.std.LoadPlugin(path="/usr/local/lib/libffms2.dylib")
    clip = core.ffms2.Source(source=in_filename)


core.nnedi3.nnedi3_rpow2(video_in, 2).set_output()
