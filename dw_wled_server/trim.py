import math
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import argparse
import sys

def read_segments(file_path):
    print(f"Reading segments from {file_path}...")
    with open(file_path, 'r') as file:
        segments = []
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                segments.append(tuple(map(float, line.split())))
    print(f"Read {len(segments)} segments.")
    return segments

def write_segments(file_path, segments):
    print(f"Writing {len(segments)} segments to {file_path}...")
    with open(file_path, 'w') as file:
        for segment in segments:
            file.write(f"{segment[0]} {segment[1]}\n")
    print(f"Segments written to {file_path}.")

def filter_segments(segments, threshold_percent, diameter):
    print(f"Filtering segments with threshold percent {threshold_percent}% and diameter {diameter}...")
    threshold_distance = (threshold_percent / 100) * diameter
    filtered_segments = [segments[0]]
    for i in range(1, len(segments)):
        r1, theta1 = segments[i-1]
        r2, theta2 = segments[i]
        distance = math.sqrt(r1**2 + r2**2 - 2*r1*r2*math.cos(math.radians(theta2 - theta1)))
        if distance >= threshold_distance:
            filtered_segments.append(segments[i])
    print(f"Filtered down to {len(filtered_segments)} segments.")
    return filtered_segments

def generate_histogram(segments, n_buckets):
    print(f"Generating histogram with {n_buckets} buckets...")
    distances = []
    for i in range(1, len(segments)):
        r1, theta1 = segments[i-1]
        r2, theta2 = segments[i]
        distance = math.sqrt(r1**2 + r2**2 - 2*r1*r2*math.cos(math.radians(theta2 - theta1)))
        distances.append(distance)
    
    plt.hist(distances, bins=n_buckets)
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.title('Histogram of Path Lengths')
    plt.show(block=False)
    print("Histogram generated.")

def douglas_peucker(segments, epsilon):
    print(f"Applying Douglas-Peucker algorithm with epsilon {epsilon}...")
    def perpendicular_distance(point, start, end):
        if start == end:
            return math.sqrt((point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2)
        else:
            n = abs((end[1] - start[1]) * point[0] - (end[0] - start[0]) * point[1] + end[0] * start[1] - end[1] * start[0])
            d = math.sqrt((end[1] - start[1]) ** 2 + (end[0] - start[0]) ** 2)
            return n / d

    def rdp(points, epsilon):
        dmax = 0.0
        index = 0
        end = len(points)
        for i in range(1, end - 1):
            d = perpendicular_distance(points[i], points[0], points[end - 1])
            if d > dmax:
                index = i
                dmax = d
        if dmax >= epsilon:
            results1 = rdp(points[:index + 1], epsilon)
            results2 = rdp(points[index:], epsilon)
            return results1[:-1] + results2
        else:
            return [points[0], points[end - 1]]

    result = rdp(segments, epsilon)
    print(f"Douglas-Peucker algorithm reduced segments to {len(result)}.")
    return result

def process_files(file_paths, threshold_percent, diameter, n_buckets, epsilon, use_douglas_peucker):
    for file_path in file_paths:
        segments = read_segments(file_path)
        if use_douglas_peucker:
            processed_segments = douglas_peucker(segments, epsilon)
        else:
            processed_segments = filter_segments(segments, threshold_percent, diameter)
        output_file_path = f"processed_{os.path.basename(file_path)}"
        write_segments(output_file_path, processed_segments)
        generate_histogram(processed_segments, n_buckets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and trim path segments.')
    parser.add_argument('file_paths', nargs='+', help='List of file paths to process')
    parser.add_argument('--threshold_percent', type=float, default=0.5, help='Threshold percent for filtering segments (default: 0.5)')
    parser.add_argument('--diameter', type=float, default=40, help='Diameter of the circle (default: 40)')
    parser.add_argument('--n_buckets', type=int, default=10, help='Number of buckets for the histogram (default: 10)')
    parser.add_argument('--epsilon', type=float, help='Epsilon value for Douglas-Peucker algorithm. A reasonable range is 0.1 to 10.0. It determines the maximum distance a point can deviate from the line before it is considered significant.')
    parser.add_argument('--use_douglas_peucker', action='store_true', help='Use Douglas-Peucker algorithm for trimming segments')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.use_douglas_peucker and args.epsilon is None:
        parser.error("--epsilon is required when --use_douglas_peucker is specified")

    process_files(args.file_paths, args.threshold_percent, args.diameter, args.n_buckets, args.epsilon, args.use_douglas_peucker)

# Example usage:
# python trim.py file1.thr file2.thr --threshold_percent 5 --diameter 100 --n_buckets 10
# python trim.py file1.thr file2.thr --epsilon 1.0 --use_douglas_peucker