from infrastructure import preconfigure_host
from execute import execute_experiments
from generate import map_experiments
from generate import flat_experiments
from configuration import REPEAT_COUNT, RESULTS_FOLDER

def main():
    preconfigure_host()
    experiments = map_experiments(flat_experiments, REPEAT_COUNT)
    execute_experiments(experiments, RESULTS_FOLDER)

if __name__ == "__main__":
    main()