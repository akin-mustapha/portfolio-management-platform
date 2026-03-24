import logging

from ...application.policies import Pipeline
from .pipeline_asset_gold import PipelineAssetGold
from .pipeline_account_gold import PipelineAccountGold

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


class PipelineT212Gold(Pipeline):
    _pipeline_name = "t212_gold"

    def __init__(self):
        self._asset_gold = PipelineAssetGold()
        self._account_gold = PipelineAccountGold()

    def run(self):
        logging.info(f"[{self._pipeline_name}] Running asset gold")
        self._asset_gold.run()
        logging.info(f"[{self._pipeline_name}] Running account gold")
        self._account_gold.run()


if __name__ == "__main__":
    PipelineT212Gold().run()
