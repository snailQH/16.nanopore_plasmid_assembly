import shutil
import logging

logger = logging.getLogger(__name__)

def check_dependencies():
    """
    Checks for required command-line tools in the system's PATH.

    Returns:
        list: A list of missing tools. If all tools are found, returns an empty list.
    """
    required_tools = [
        "chopper",
        "flye",
        "medaka",
        "prokka",
        "NanoPlot",
        "minimap2",
        "samtools",
    ]
    
    missing_tools = []
    logger.info("Checking for required dependencies...")
    for tool in required_tools:
        if shutil.which(tool) is None:
            missing_tools.append(tool)
            logger.warning(f"Dependency not found: {tool}")
        else:
            logger.info(f"Found dependency: {tool}")
            
    return missing_tools
