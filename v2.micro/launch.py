from .app import controller




import argparse
import logging
import sys
import datetime


def main():
    
    
    parser = argparse.ArgumentParser(description='A script with verbose, logging, and headless options.')
    
    # Verbose option
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output', default=True)
    
    # Logging settings
    parser.add_argument('-l', '--log', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='WARNING', help='Set the logging level')
    
    # Headless mode option
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    
    
    # Setup logger
    logging.getLogger().setLevel(logging.NOTSET) 
      
    handler = logging.FileHandler(filename='tmp.log')
    handler.setLevel(args.log)
    formatter = logging.Formatter('[%(asctime)s] - In: %(pathname)s - At: %(filename)s->%(funcName)s->%(lineno)d: \n\t[%(levelname)s]: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    
    if args.verbose:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG) #TODO: set to INFO later
        formatter = logging.Formatter('%(levelname)s - %(filename)s>%(funcName)s>%(lineno)d: %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    logger = logging.getLogger("app_logger." + datetime.datetime.now().strftime("%C"))
    logger.debug("logger setup complete")
    
    if args.verbose:
        logger.info("Script is running in verbose mode")
    
    logger.info("Logging level is set to %s", args.log)
    
    if args.headless:
        logger.info("Headless mode is enabled")
    
    # Main logic of your script goes here
    logger.info("Script execution started")
    
    controller: Controller = Controller(logger, False)
    
    
    

if __name__ == "__main__":
    main()