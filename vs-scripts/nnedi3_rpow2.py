import vapoursynth as vs
import edi_rpow2 as edi
core = vs.get_core()
if "video_in" in globals():
    clip = video_in
else:
    try:
        core.std.LoadPlugin(path="/usr/local/lib/libffms2.dylib")
    except:
        print('Error loading libffms2. Already loaded?')
    clip = core.ffms2.Source(source=in_filename)

# Increase bit depth, etc., for filters.
clip = core.fmtc.bitdepth(clip=clip,bits=16)
clip = edi.nnedi3_rpow2(clip=clip, rfactor=2, correct_shift="zimg", nsize=4, nns=3, qual=2, pscrn=4)
clip = core.fmtc.bitdepth (clip=clip, bits=8)
clip = core.fmtc.resample(clip=clip, scale=1/2, kernel="bicubic")
clip.set_output()
