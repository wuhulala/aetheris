import importlib.util
import json
import logging
import os
import subprocess
import sys
import traceback
from agents.space import AGENT_SPACE

from config import AGENTS_DIR

if not os.path.exists(AGENTS_DIR):
    os.makedirs(AGENTS_DIR)

PIPELINES = {}
PIPELINE_MODULES = {}

def get_all_pipelines():
    pipelines = {}
    for pipeline_id in PIPELINE_MODULES.keys():
        pipeline = PIPELINE_MODULES[pipeline_id]

        pipelines[pipeline_id] = {
            "module": pipeline_id,
            "type": (pipeline.type if hasattr(pipeline, "type") else "pipe"),
            "id": pipeline_id,
            "name": (pipeline.name if hasattr(pipeline, "name") else pipeline_id),
            "valves": pipeline.valves if hasattr(pipeline, "valves") else None,
        }
    return pipelines


def parse_frontmatter(content):
    frontmatter = {}
    for line in content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip().lower()] = value.strip()
    return frontmatter


def install_frontmatter_requirements(requirements):
    if requirements:
        req_list = [req.strip() for req in requirements.split(",")]
        for req in req_list:
            print(f"Installing requirement: {req}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    else:
        print("No requirements found in frontmatter.")


async def load_agent(module_name, module_path):
    # TODO
    try:
        # Read the module content
        with open(module_path, "r") as file:
            content = file.read()

        # Parse frontmatter
        frontmatter = {}
        if content.startswith('"""'):
            end = content.find('"""', 3)
            if end != -1:
                frontmatter_content = content[3:end]
                frontmatter = parse_frontmatter(frontmatter_content)

        # Install requirements if specified
        if "requirements" in frontmatter:
            install_frontmatter_requirements(frontmatter["requirements"])

        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logging.info(f"Loaded module start: {module.__name__}")
        if hasattr(module, "Pipeline"):
            return module.Pipeline()
        else:
            logging.info(f"Loaded module failed: {module.__name__ } No Pipeline class found")
            raise Exception("No Pipeline class found")
    except Exception as e:
        logging.info(f"Error loading module: {module_name}, error is {e}")
        traceback.print_exc()
        # Move the file to the error folder
        failed_pipelines_folder = os.path.join(AGENTS_DIR, "failed")
        if not os.path.exists(failed_pipelines_folder):
            os.makedirs(failed_pipelines_folder)

        # failed_file_path = os.path.join(failed_pipelines_folder, f"{module_name}.py")
        # if module_path.__contains__(PIPELINES_DIR):
        #     os.rename(module_path, failed_file_path)
        print(e)
    return None


async def load_modules_from_directory(directory):
    logging.info(f"load_modules_from_directory: {directory}")
    global PIPELINE_MODULES

    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # Remove the .py extension
            module_path = os.path.join(directory, filename)

            agent = await load_agent(module_name, module_path)
            if agent:

                pipeline_id = agent.id if hasattr(agent, "id") else module_name
                PIPELINE_MODULES[pipeline_id] = agent

                logging.info(f"Loaded module success: {module_name}")
            else:
                logging.warning(f"No Pipeline class found in {module_name}")

    AGENT_SPACE.agent_modules = PIPELINE_MODULES
    AGENT_SPACE.agents_meta = get_all_pipelines()