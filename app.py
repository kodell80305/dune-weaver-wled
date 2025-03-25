
from wled_web_server import start_flask, init_config
from wled_rpi import update_segments, run_rpi_app

# Main entry point for the WLED Raspberry Pi application.  Assume the order is important, for reasons
# that are not clear to me. 
if __name__ == '__main__':
    config = init_config()
    update_segments(config)
    start_flask()
    run_rpi_app()
