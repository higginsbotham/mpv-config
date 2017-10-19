import vapoursynth as vs
import edi_rpow2 as edi
import havsfunc as haf
import hysteria as hys
core = vs.get_core()

try:
    core.std.LoadPlugin(path="/usr/local/lib/libmvtools.dylib")
except:
    print('Error loading MVTools. Already loaded?')

if "video_in" in globals():
    clip = video_in
else:
    try:
        core.std.LoadPlugin(path="/usr/local/lib/libffms2.dylib")
    except:
        print('Error loading libffms2. Already loaded?')
    clip = core.ffms2.Source(source=in_filename)
    dst_fps=float(display_fps)
    max_flow_width  = 1920
    max_flow_height = 1200
    search_arg = 8
    acc = 2

src_aspect_numdem=str(src_aspect).split(":")

src_aspect_numdem=["4","3"]
new_width=int(clip.height) * ( int(src_aspect_numdem[0]) / int(src_aspect_numdem[1]) )
new_height=int(clip.height)

# Deinterlace
# For working with interlaced video, see 7.1.8 at https://www.mplayerhq.hu/DOCS/HTML/en/menc-feat-dvd-mpeg4.html.
# Crop height and y-offset must be multiples of 4.
# Any vertical scaling must be performed in interlaced mode for interlaced-destined material.
# Postprocessing and denoising filters may not work as expected unless you take special care to operate them a field at a time, and they may damage the video if used incorrectly.

clip = core.nnedi3.nnedi3(clip=clip, field=1, dh=True, nsize=3, nns=4, qual=1, pscrn=4)
clip = haf.daa(clip)

# Increase bit depth, etc., for filters.
clip = core.fmtc.bitdepth(clip=clip,bits=16)

# Enlarging, progressive input only.
#clip = edi.nnedi3_rpow2(clip=clip, rfactor=2, correct_shift="zimg", nsize=4, nns=3, qual=2, pscrn=4)

# Colorspace conversion:
# Matrix options: https://github.com/EleonoreMizo/fmtconv/blob/master/src/fmtc/Matrix.cpp#L589
# Transfer options: https://github.com/EleonoreMizo/fmtconv/blob/master/src/fmtc/Transfer.cpp#L425
# Primary options: https://github.com/EleonoreMizo/fmtconv/blob/master/src/fmtc/Primaries.cpp#L422
clip = core.fmtc.resample(clip=clip, css="444",w=int(new_width),h=int(new_height),kernel="spline64")
clip = core.fmtc.matrix (clip=clip, mats=src_mats)
clip = core.fmtc.transfer (clip=clip, transs=src_trans, transd="linear")
clip = core.fmtc.primaries (clip=clip, prims=src_prims, primd="709")
clip = core.fmtc.transfer (clip=clip, transs="linear", transd="470m")
clip = core.fmtc.matrix (clip=clip, mat="709")

# Motion interpolation:
# skip motion interpolation completely for content exceeding the limits below
max_width  = 1920
max_height = 1200
max_fps    = 60
# use BlockFPS instead of FlowFPS for content exceeding the limits below
max_flow_width  = 1280
max_flow_height = 720
# a block is considered as changed when 8*8*x > th_block|flow_diff with 8*8
# being the size of a block (scaled internally) and x the difference of each
# pixel within this block, default 400
th_block_diff = 8*8*7
th_flow_diff  = 8*8*7
# (threshold/255)% blocks have to change to consider this a scene change
# (= no motion compensation), default 130, old values 14
th_block_changed = 12
th_flow_changed  = 12
# size of blocks the analyse step is performed on
blocksize = 2**4
# motion estimation accuracy, precision to 1/acc pixel
acc = 1
# search algorithm and argument, old values 3 and 2
search_alg = 3
search_arg = 2
# processing mask mode (FlowFPS), old value is 1
msk = 2

# Seems to choke when you pass it more than six decimals.
container_fps = round(float(container_fps), 6)

source_num = int(container_fps * 1e6)
source_den = int(1e6)

target_num = int(source_num * 2)
target_den = int(1e6)

if not (clip.width > max_width or clip.height > max_height or container_fps > max_fps):
    clip = core.std.AssumeFPS(clip, fpsnum=source_num, fpsden=source_den)
    sup  = core.mv.Super(clip, pel=acc, hpad=blocksize, vpad=blocksize)
    if "video_in" in globals():
        bv   = core.mv.Analyse(sup, blksize=blocksize, isb=True , chroma=True, search=search_alg, searchparam=search_arg)
        fv   = core.mv.Analyse(sup, blksize=blocksize, isb=False, chroma=True, search=search_alg, searchparam=search_arg)
    else:
        bv   = core.mv.Analyse(sup, truemotion=True, blksize=blocksize, isb=True , chroma=True, search=search_alg, searchparam=search_arg)
        fv   = core.mv.Analyse(sup, truemotion=True, blksize=blocksize, isb=False, chroma=True, search=search_alg, searchparam=search_arg)

    use_block = clip.width > max_flow_width or clip.height > max_flow_height
    if use_block:
        clip = core.mv.BlockFPS(clip, sup, bv, fv, num=target_num, den=target_den,
                                mode=3, thscd1=th_block_diff, thscd2=th_block_changed)
    else:
        clip = core.mv.FlowFPS(clip, sup, bv, fv, num=target_num, den=target_den,
                               mask=msk, thscd1=th_flow_diff, thscd2=th_flow_changed)
    print('motion-interpolation: {0} -> {1} FPS | {3} | {2} Hz'
          .format(source_num / source_den, target_num / target_den,
                  display_fps, use_block and "block" or "flow"))
else:
    print('motion-interpolation: skipping {0}x{1} {2} FPS video'
          .format(clip.width, clip.height, container_fps))

# Noise reduction.
super = core.mv.Super(clip, pel=2, sharp=1)
backward_vec2 = core.mv.Analyse(super, isb = True, delta = 2, overlap=4)
backward_vec1 = core.mv.Analyse(super, isb = True, delta = 1, overlap=4)
forward_vec1 = core.mv.Analyse(super, isb = False, delta = 1, overlap=4)
forward_vec2 = core.mv.Analyse(super, isb = False, delta = 2, overlap=4)
clip = core.mv.Degrain2(clip, super, backward_vec1,forward_vec1,backward_vec2,forward_vec2,thsad=400)

# Deband.
#clip = core.f3kdb.Deband(clip)

# Return the clip to rights, correcting aspect ratio.
clip = core.fmtc.resample (clip=clip, css="420")
clip = core.fmtc.bitdepth (clip=clip, bits=8)

# Sharpening.
clip = hys.Hysteria(clip,2.0,lowthresh=9,highthresh=17)

clip.set_output()
