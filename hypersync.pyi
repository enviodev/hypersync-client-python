import asyncio

class hypersync_client:

    @classmethod
    def new(config: dict) -> hypersync_client:
        """
        Create a new client with given config
        """

    @classmethod
    def get_height(self) -> int:
        """
        Get the height of the source hypersync instance
        """

    @classmethod
    def create_parquet_folder(self, query: dict, parquet_config: dict) -> None:
        """
        Create a parquet file by executing a query.
    
        Path should point to a folder that will contain the parquet files in the end.
        """
    
    @classmethod
    def send_req(self, query: dict) -> asyncio.Future:
        """
        Send a query request to the source hypersync instance.

        Returns a query response which contains block, tx and log data.
        """
    
    @classmethod
    def send_events_req(self, query: dict) -> asyncio.Future:
        """
        Send a event query request to the source hypersync instance.

        This executes the same query as send_req function on the source side but
        it groups data for each event(log) so it is easier to process it.
        """