import matplotlib.pyplot as plt
import json
import time

def plot_data():
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()

    while True:
        try:
            with open('generation_data.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            time.sleep(1)
            continue

        generations = list(range(1, len(data['avg_scores']) + 1))
        avg_scores = data['avg_scores']
        high_scores = data['high_scores']
        fitness_values = data['fitness_values']

        ax.clear()
        ax.plot(generations, high_scores, label='Max Score', color='green')
        ax.plot(generations, avg_scores, label='Average Score', color='blue')
        ax.plot(generations, fitness_values, label='Average Fitness', color='red')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Value')
        ax.set_title('Fitness and Scores over Generations')
        ax.legend()
        ax.grid(True)
        plt.pause(1)  # Update every second

if __name__ == "__main__":
    plot_data()