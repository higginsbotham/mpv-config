import vapoursynth as vs
core = vs.get_core()
try:
    core.std.LoadPlugin(path="/usr/local/lib/libmvtools.dylib")
except:
    print('Error loading MVTools. Already loaded?')

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

if "video_in" in globals():
    # realtime
    clip = video_in

else:
    # run with vspipe
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

# Seems to choke when you pass it more than six decimals.
container_fps = round(float(container_fps), 6)

source_num = int(container_fps * 1e6)
source_den = int(1e6)

target_num = int(source_num * 2)
target_den = int(1e6)
while (target_num > max_fps):
    target_num /= 2

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

clip.set_output()
