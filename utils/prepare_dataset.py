import osu_reader

# file = "../music/1998016/Ueda Reina - Literature (TV Size) (-Aqua) [Ashen].osu"
file = "../music/1342378/Ueda Reina - Literature (TV Size) (-Aqua) [Ashen].osu"
reader = osu_reader.OsuTaikoReader(file)
duration = reader.audio.duration()

beats = reader.timing_points.beats_point(duration*1000)
meter = reader.timing_points.data[0].meter

bars = []

for i in range(0, int(len(beats)/meter)):
    beats_in_bar = beats[i*meter:((i+1)*meter+1)]
    bars.append((beats_in_bar[0], beats_in_bar[-1]-1))
    
print(f"{bars=}")

for bar in bars:
    print(f"bar {bar}")
    progress = lambda x: (x-bar[0])/(bar[1]-bar[0])
    noteobjects = reader.hit_objects[bar[0]:bar[1]]
    objects = [(progress(note[0])*16, note[1]) for note in noteobjects]
    print(f"{objects=}")
    
    arr = [0]*17
    for note in objects:
        arr[round(note[0])] = 1
        
    print(arr)