class TimingPoint:
    time: int
    beat_length: float
    meter: int
    uninherited: bool
    slider_velocity: float

    def __init__(
        self,
        time: int,
        beat_length: float,
        meter: int,
        uninherited: bool,
        slider_velocity: float = 1,
    ):
        self.time = time
        self.beat_length = beat_length
        self.meter = meter
        self.uninherited = uninherited
        self.slider_velocity = slider_velocity

    def __str__(self):
        return f"Time: {self.time}, Beat Length: {round(self.beat_length,2)} equal to {round(60000/self.beat_length,2)} BPM, Slider Velocity: {self.slider_velocity}, Meter: {self.meter}, Uninherited: {self.uninherited}"

    def parse(current: str):
        data = current.split(",")

        time = round(float(data[0]))
        beat_length = float(data[1])
        meter = round(float(data[2]))
        uninherited = bool(int(data[6]))
        slider_velocity = 1

        if uninherited == False:
            return None

        return TimingPoint(time, beat_length, meter, uninherited, slider_velocity)

    def parse_next(self, next: str):
        data = next.split(",")

        time = round(float(data[0]))
        beat_length = float(data[1])
        meter = round(float(data[2]))
        uninherited = bool(int(data[6]))
        slider_velocity = 1

        if uninherited == False:
            beat_length = self.beat_length
            slider_velocity = self.slider_velocity

            meter = self.meter

        return TimingPoint(time, beat_length, meter, uninherited, slider_velocity)


class TimingPoints:
    data: list[TimingPoint]

    def __init__(self, data: list[str]):
        self.data = []
        cur_timing = TimingPoint.parse(data[0])
        for i in range(1, len(data)):
            self.data.append(cur_timing)
            cur_timing = cur_timing.parse_next(data[i])

        self.data.append(cur_timing)

    def __str__(self):
        return str(self.data)

    def inhabited_points(self):
        return [timing for timing in self.data if timing.uninherited]

    def beats_point(self, end: int) -> list[int]:
        timing_points = self.inhabited_points()
        # print(f"{timing_points=}")
        # for timing in timing_points:
        #     print(timing)
        timing_points_index = 0
        cur_timing = timing_points[0].time
        next_timing_points_start = -1
        if len(timing_points) > 1:
            next_timing_points_start = timing_points[1].time
        beats = []

        while True:
            if cur_timing > end:
                break

            beats.append(round(cur_timing))
            cur_timing += timing_points[timing_points_index].beat_length

            if (
                next_timing_points_start != -1
                and cur_timing > next_timing_points_start
                and next_timing_points_start > 0
            ):
                next_timing_points_start = -1
                timing_points_index += 1

                if timing_points_index < len(timing_points):
                    next_timing_points_start = timing_points[timing_points_index].time
                else:
                    timing_points_index -= 1
                # print(f"{timing_points_index=} {len(timing_points)} {next_timing_points_start=}")

        return beats


if __name__ == "__main__":
    to_parse = [
        "558,508.474576271186,4,1,0,65,1,0",
        "558,-100,4,1,0,65,0,0",
        "8693,-111.111111111111,4,1,0,50,0,0",
        "20896,-95.2380952380952,4,1,0,60,0,0",
        "33227,-105.263157894737,4,1,0,50,0,0",
        "41363,-117.647058823529,4,1,0,40,0,0",
        "45303,-100,4,1,0,60,0,0",
        "49371,-86.9565217391304,4,1,0,75,0,1",
        "79880,-86.9565217391304,4,1,0,75,0,0",
        "80007,-100,4,1,0,60,0,0",
        "85727,-100,4,1,0,20,0,0",
    ]
    cur_timing = TimingPoints(to_parse)
    # cur_timing = TimingPoint.parse(to_parse[0])
    # for i in range(1, len(to_parse)):
    #     print(cur_timing)
    #     cur_timing = cur_timing.parse_next(to_parse[i])
    print(cur_timing.data[0])
    print(cur_timing.inhabited_points()[0])
    print(cur_timing.beats_point(100000))
