import json


class MomoiBot():
    def __init__(self):
        # instance variables
        self.config = None
        self.gateway_url = None

        # actions below
        self.load_config()

    def load_config(self):
        with open('../config.json') as f:
            self.config = json.load(f)


# main entry point
if __name__ == "__main__":
    momoi = MomoiBot()
    print(momoi.config)

