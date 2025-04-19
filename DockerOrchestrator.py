import json
import os
import subprocess
import threading
import time
from typing import List


class DockerOrchestrator():
    
    """
    Having the whole riddle generation dockerized, allows for parallelization. This Class automizes the process, by: 
        -loading a master config, containing a list of multiple individual riddle configs
        -preparing all experiments
        -start each experiment container in a new thread
        -wait for all containers to finish
    """

    def __init__(self,input_config_path,experiment_path):
        """Initializes DockerOrchestrator, sets experiment path and reads input config

        Args:
            input_config_path (str): path to the input config
            experiment_path (str): path, where all experiments will be stored
        """

        self.experiment_path = experiment_path
        with open(input_config_path) as config_file:
            self.input_config = json.load(config_file)
        
    def run_experiments(self):
        """ Loops over all experiment configs given in the input config, prepares each experiment and then runs it."""

        docker_threads = []
        for experiment_config in self.input_config:
            self.prepare_experiment(experiment_config)
            self.start_experiment(docker_threads)
            time.sleep(5)

        for docker_thread in docker_threads:
            docker_thread.join()

    def prepare_experiment(self,experiment_config):
        """ Prepare experiment:
            -create needed directories (input/output)
            -set environment variables needed by the experiments container

        Args:
            experiment_config (dict): experiment config containing all relevant information for the experiment
        """

        RIDDLE_NAME = experiment_config["riddle_name"]
        X_DIMENSION = experiment_config["dimensions"]["x"]
        Y_DIMENSION = experiment_config["dimensions"]["y"]
        riddle_name_path = f"{RIDDLE_NAME}_{X_DIMENSION}x{Y_DIMENSION}"
        
        input_path = os.path.join(self.experiment_path,riddle_name_path,"input")
        output_path = os.path.join(self.experiment_path,riddle_name_path,"output")

        # create input and outupt directories:
        os.makedirs(input_path,exist_ok=True)
        os.makedirs(output_path,exist_ok=True)
        os.makedirs(os.path.join(output_path,"svg"),exist_ok=True)

        config_file_name = f"{RIDDLE_NAME}.json"
    
        # set environment variables
        os.environ["DO_INPUT_PATH"] = input_path
        os.environ["DO_OUTPUT_PATH"] = output_path
        os.environ["DO_CONFIG_FILE"] = config_file_name
        os.environ["CONTAINER_NAME"] = riddle_name_path
        
        config_file_local_path = os.path.join(input_path,config_file_name)
        self.save_config(config_file_local_path,experiment_config)


    def start_experiment(self,docker_threads:List[threading.Thread]):
        """start a new experiment in a thread and append the thread to given list

        Args:
            docker_threads (List[threading.Thread]): List containing all experiment threads
        """

        if len(docker_threads)==0:
            showStdout=True
        else:
            showStdout=False
        compose_files = ["docker-compose.yml"]
        options = [ ]
        riddle_generator = threading.Thread(target=self.start_docker_compose_run, args=("riddle_generator", "RiddleGenerator", compose_files,options ,showStdout), daemon=False)
        docker_threads.append(riddle_generator)
        riddle_generator.start()



    def save_config(self,output_path,experiment_config):
        """ Save config to given output path

        Args:
            output_path (str): _description_
            experiment_config (dict): _description_
        """

        with open(output_path, 'w') as config_file:
            json.dump(experiment_config, config_file)

    
    def start_docker_compose_run(self,projectName, service, composeFiles, options, showStdout=True):
        """
        Starts the given docker service with docker compose run under the given path 'cwd' and with the given project name.
        The docker compose files must be inside the 'cwd' path.
        """

        composeFilesInDockerCmd = " ".join("-f " + composeFile for composeFile in composeFiles)
        composeOptionsInDockerCmd = " ".join(option for option in options)
        dockerComposeRunCommand = "docker compose -p {} {} run {} {}".format(projectName, composeFilesInDockerCmd, composeOptionsInDockerCmd, service)
        print(dockerComposeRunCommand)
        if showStdout:
            subprocess.call(dockerComposeRunCommand, shell=True)
        else:
            subprocess.call(dockerComposeRunCommand, shell=True, stdout=subprocess.DEVNULL)

if __name__=="__main__":
    input_config_path = "/home/lukas/repositories/riddle-generator/all_experiment_configs.json"
    experiment_path = "./experiments"
    docker_orchestrator = DockerOrchestrator(input_config_path,experiment_path)
    docker_orchestrator.run_experiments()

