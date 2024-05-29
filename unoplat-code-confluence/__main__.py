import argparse
import json
from os import get_terminal_size
import os
from loguru import logger
import datetime
from codebaseparser.ArchGuardHandler import ArchGuardHandler
import re
from downloader.downloader import Downloader
from loader import iload_json, iparse_json
from loader.json_loader import JsonLoader
from loader.parse_json import JsonParser
from nodeparser.nodesummariser import NodeSummariser
from nodeparser.isummariser import ISummariser
from settings.appsettings import AppSettings


def main(iload_json, iparse_json,isummariser,json_configuration_data):
    settings = AppSettings()
    get_codebase_metadata(json_configuration_data,settings,iload_json,iparse_json,isummariser)
    

def handle_toggle(value):
    global selected_language
    selected_language = value
    logger.info(f"Selected language: {value}")


def get_codebase_metadata(json_configuration_data,settings,iload_json,iparse_json,isummariser):
    # Collect necessary inputs from the user to set up the codebase indexing
    local_workspace_path = json_configuration_data["local_workspace_path"]
    programming_language = json_configuration_data["programming_language"]
    output_path_field = json_configuration_data["output_path"]
    codebase_name_field = json_configuration_data["codebase_name"]
    github_token = json_configuration_data["repo"]["github_token"]
    arcguard_cli_repo = json_configuration_data["repo"]["download_url"]
    local_download_directory = json_configuration_data["repo"]["download_directory"]


    # Button to submit the indexing
    start_parsing(
        local_workspace_path,
        # move this when expanding to new languages
        programming_language,
        output_path_field,
        codebase_name_field,
        settings,
        github_token,
        arcguard_cli_repo,
        local_download_directory,
        iload_json,
        iparse_json,
        isummariser
    )

def download_and_continue(settings,manager):
    try:
        jar_path = Downloader.download_latest_jar(settings.download_url, settings.download_directory, settings.github_token)
        print(f"Download completed: {jar_path}")
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        manager.stop() 
        return jar_path

def ensure_jar_downloaded(github_token,arcguard_cli_repo,local_download_directory):
    # Compile the regex pattern for the JAR file
    jar_pattern = re.compile(r"scanner_cli-.*-all\.jar")

    # Check if any file matching the pattern exists in the download directory
    existing_jars = [f for f in os.listdir(local_download_directory) if jar_pattern.match(f)]

    if not existing_jars:
        logger.info("Downloading utility to parse codebase...")
        # No JAR matches, need to download
        jar_path = Downloader.download_latest_jar(arcguard_cli_repo, local_download_directory, github_token)
        logger.info("Download finished JAR file...")
    else:
        # Use the first matching JAR found
        jar_path = os.path.join(local_download_directory, existing_jars[0])
        logger.info("Using existing JAR:")
        logger.info(f"JAR Path: {jar_path}")
    
    return jar_path

def start_parsing(local_workspace_path, programming_language, output_path, codebase_name, settings, github_token, arcguard_cli_repo, local_download_directory, iload_json, iparse_json, isummariser):

    # Log the start of the parsing process
    logger.info("Starting parsing process...")
    
    # Ensure the JAR is downloaded or use the existing one
    jar_path = ensure_jar_downloaded(github_token,arcguard_cli_repo,local_download_directory)

    logger.info(f"Local Workspace URL: {local_workspace_path}")
    logger.info(f"Programming Language: {programming_language}")
    logger.info(f"Output Path: {output_path}")
    logger.info(f"Codebase Name: {codebase_name}")

    # Initialize the ArchGuard handler with the collected parameters.
    archguard_handler = ArchGuardHandler(
        jar_path=jar_path,
        language=programming_language,
        codebase_path=local_workspace_path,
        codebase_name=codebase_name,
        output_path=output_path
    )
    
    chapi_metadata_path = archguard_handler.run_scan()

    chapi_metadata = iload_json.load_json_from_file(chapi_metadata_path)
   
    current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    output_filename = f"{codebase_name}_{current_timestamp}.md"

    with open(os.path.join(output_path, output_filename), 'a+') as md_file:
        for node in iparse_json.parse_json_to_nodes(chapi_metadata, isummariser):
            if node.type == "CLASS":
                md_file.write(f"{node.summary}\n\n")
    # with open('codebase_summary.json', 'w') as file:
    #     json.dump(codebase_metadata, file)
    
    logger.info("Parsing process completed.")

    
if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='pydantic.*')
    parser = argparse.ArgumentParser(description="Codebase Parser CLI")
    parser.add_argument("--config", help="Path to configuration file for unoplat utility", default=os.getcwd() + '/default_config.json', type=str)
    args = parser.parse_args()

    iload_json = JsonLoader()
    iparse_json = JsonParser()
    isummariser = NodeSummariser()
    #loading the config
    json_configuration_data = iload_json.load_json_from_file(args.config)

    #loading and setting the logging config
    logging_config = iload_json.load_json_from_file("loguru.json")
    logger.configure(handlers=logging_config["handlers"])

    main(iload_json, iparse_json, isummariser,json_configuration_data)
    # unoplat_agent_setup =UnoplatAgent()
    # unoplat_agent_setup.run_crew()