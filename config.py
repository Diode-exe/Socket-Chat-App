import logging

class Config():
    def get_config_bool(key):
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Convert to boolean (0 = False, 1 = True)
                        return value == "1"
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return False
        return False  # Default to False if not found

    def get_config_port():
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.lower().startswith("port:"):
                        value = line.split(":", 1)[1].strip()
                        try:
                            return int(value)  # return as integer
                        except ValueError:
                            logging.error(f"Invalid port value: {value}")
                            return None
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return None

        return None  # Default if "port:" not found

    def get_config_value(key, default=None):
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Try to convert to int if possible
                        if value.isdigit():
                            return int(value)
                        try:
                            return float(value)  # handles decimal numbers
                        except ValueError:
                            return value  # fallback to raw string
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return default
        return default
    
if __name__ == "__main__":
    print("This is a library, and not meant to run directly")