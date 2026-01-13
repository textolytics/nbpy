"""
Kraken Tick to InfluxDB Subscriber

Subscribes to Kraken tick data and writes it to InfluxDB.
"""

import logging
import sys
from typing import Dict, Optional, Tuple

try:
    from influxdb import InfluxDBClient
except ImportError:
    InfluxDBClient = None

import zmq

from nbpy.zmq import BaseSubscriber, KRAKEN_TICK_PUB

logger = logging.getLogger(__name__)


class KrakenTickToInfluxDBSubscriber(BaseSubscriber):
    """Subscriber that writes Kraken tick data to InfluxDB"""
    
    def __init__(
        self,
        influxdb_host: str = 'localhost',
        influxdb_port: int = 8086,
        influxdb_user: str = 'zmq',
        influxdb_password: str = 'zmq',
        influxdb_db: str = 'tick',
        zmq_host: str = 'localhost',
        port_config=None
    ):
        if port_config is None:
            # Use new port 5558 for publishers, map SUB to different port
            port_config = KRAKEN_TICK_PUB
        
        super().__init__(port_config, host=zmq_host)
        
        self.influxdb_host = influxdb_host
        self.influxdb_port = influxdb_port
        self.influxdb_db = influxdb_db
        
        # Initialize InfluxDB client
        if InfluxDBClient is None:
            logger.error("influxdb client library not available")
            self.influxdb_client = None
        else:
            try:
                self.influxdb_client = InfluxDBClient(
                    host=influxdb_host,
                    port=influxdb_port,
                    username=influxdb_user,
                    password=influxdb_password,
                    database=influxdb_db,
                    use_udp=False
                )
                logger.info(f"Connected to InfluxDB at {influxdb_host}:{influxdb_port}/{influxdb_db}")
            except Exception as e:
                logger.error(f"Failed to connect to InfluxDB: {e}")
                self.influxdb_client = None
    
    def _parse_instrument_pair(self, instrument: str) -> Tuple[str, str]:
        """
        Parse instrument pair into base and term currencies
        
        Handles various Kraken naming conventions:
        - XXRPZ -> XRP/USD
        - EURUSD -> EUR/USD
        - XBTUSDT -> XBT/USD
        """
        base_ccy = ""
        term_ccy = ""
        
        if instrument[0] == 'X' and instrument[-4] == 'Z':
            base_ccy = instrument[1:4]
            term_ccy = instrument[-3:]
        elif len(instrument) == 6 and instrument[-4] != '_':
            base_ccy = instrument[0:3]
            term_ccy = instrument[3:6]
        elif instrument[0] == 'X' and instrument[-4] == 'X':
            base_ccy = instrument[1:4]
            term_ccy = instrument[-3:]
        elif instrument[0] != 'X' and instrument[-4] == 'Z':
            base_ccy = instrument[0:4]
            term_ccy = instrument[-3:]
        elif instrument[0:4] == 'DASH':
            base_ccy = instrument[0:4]
            term_ccy = instrument[-3:]
        else:
            # Fallback
            base_ccy = instrument[:-3]
            term_ccy = instrument[-3:]
        
        return base_ccy, term_ccy
    
    def _process_tick_data(self, tick_data: Dict) -> None:
        """Process and write tick data to InfluxDB"""
        if self.influxdb_client is None:
            logger.warning("InfluxDB client not available, skipping write")
            return
        
        try:
            # Extract instrument data
            result = tick_data.get('result', {})
            points = []
            
            for instrument, tick_info in result.items():
                try:
                    # Parse tick fields
                    # Kraken format: [ask_price, ask_vol_whole, ask_vol_lot]
                    # [bid_price, bid_vol_whole, bid_vol_lot]
                    # [last_trade_price, last_trade_vol]
                    # [volume_today, volume_24h]
                    # [vwap_today, vwap_24h]
                    # [trades_today, trades_24h]
                    # [low_today, low_24h]
                    # [high_today, high_24h]
                    # [opening_price]
                    
                    if not isinstance(tick_info, (list, tuple)) or len(tick_info) < 9:
                        logger.warning(f"Invalid tick format for {instrument}: {tick_info}")
                        continue
                    
                    # Extract values
                    ask_price = float(tick_info[0][0]) if tick_info[0] else 0.0
                    ask_whole_lot_volume = float(tick_info[0][1]) if len(tick_info[0]) > 1 else 0.0
                    ask_lot_volume = float(tick_info[0][2]) if len(tick_info[0]) > 2 else 0.0
                    
                    bid_price = float(tick_info[1][0]) if tick_info[1] else 0.0
                    bid_whole_lot_volume = float(tick_info[1][1]) if len(tick_info[1]) > 1 else 0.0
                    bid_lot_volume = float(tick_info[1][2]) if len(tick_info[1]) > 2 else 0.0
                    
                    last_trade_price = float(tick_info[2][0]) if tick_info[2] else 0.0
                    last_trade_lot_volume = float(tick_info[2][1]) if len(tick_info[2]) > 1 else 0.0
                    
                    volume_today = float(tick_info[3][0]) if tick_info[3] else 0.0
                    volume_24h = float(tick_info[3][1]) if len(tick_info[3]) > 1 else 0.0
                    
                    vwap_today = float(tick_info[4][0]) if tick_info[4] else 0.0
                    vwap_24h = float(tick_info[4][1]) if len(tick_info[4]) > 1 else 0.0
                    
                    trades_today = float(tick_info[5][0]) if tick_info[5] else 0.0
                    trades_24h = float(tick_info[5][1]) if len(tick_info[5]) > 1 else 0.0
                    
                    low_today = float(tick_info[6][0]) if tick_info[6] else 0.0
                    low_24h = float(tick_info[6][1]) if len(tick_info[6]) > 1 else 0.0
                    
                    high_today = float(tick_info[7][0]) if tick_info[7] else 0.0
                    high_24h = float(tick_info[7][1]) if len(tick_info[7]) > 1 else 0.0
                    
                    opening_price = float(tick_info[8]) if tick_info[8] else 0.0
                    
                    # Parse base/term currencies
                    base_ccy, term_ccy = self._parse_instrument_pair(instrument)
                    
                    # Create InfluxDB point
                    point = {
                        "measurement": "tick",
                        "tags": {
                            "instrument": str(instrument),
                            "base_ccy": base_ccy,
                            "term_ccy": term_ccy
                        },
                        "fields": {
                            "ask_price": ask_price,
                            "ask_whole_lot_volume": ask_whole_lot_volume,
                            "ask_lot_volume": ask_lot_volume,
                            "bid_price": bid_price,
                            "bid_whole_lot_volume": bid_whole_lot_volume,
                            "bid_lot_volume": bid_lot_volume,
                            "last_trade_price": last_trade_price,
                            "last_trade_lot_volume": last_trade_lot_volume,
                            "volume_today": volume_today,
                            "volume_24h": volume_24h,
                            "vwap_today": vwap_today,
                            "vwap_24h": vwap_24h,
                            "trades_today": trades_today,
                            "trades_24h": trades_24h,
                            "low_today": low_today,
                            "low_24h": low_24h,
                            "high_today": high_today,
                            "high_24h": high_24h,
                            "opening_price": opening_price
                        }
                    }
                    points.append(point)
                
                except Exception as e:
                    logger.error(f"Failed to parse tick data for {instrument}: {e}")
            
            # Write all points to InfluxDB
            if points:
                self.influxdb_client.write_points(
                    points,
                    batch_size=500,
                    time_precision='ms'
                )
                logger.debug(f"Wrote {len(points)} points to InfluxDB")
        
        except Exception as e:
            logger.error(f"Error processing tick data: {e}")
    
    def run(self, timeout: Optional[int] = None) -> None:
        """Run the subscriber loop"""
        logger.info(f"Starting Kraken tick subscriber for InfluxDB")
        self.running = True
        
        try:
            while self.running:
                try:
                    if timeout is not None:
                        if self.socket.poll(timeout) == 0:
                            continue
                    
                    # Receive MessagePack message
                    topic, tick_data = self.recv_msgpack()
                    logger.debug(f"Received tick data from topic {topic}")
                    
                    # Process and write to InfluxDB
                    self._process_tick_data(tick_data)
                
                except Exception as e:
                    logger.error(f"Error in message loop: {e}")
        
        except KeyboardInterrupt:
            logger.info("Subscriber interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.influxdb_client:
            try:
                self.influxdb_client.close()
                logger.info("Closed InfluxDB connection")
            except Exception as e:
                logger.error(f"Error closing InfluxDB: {e}")
        
        super().cleanup()


def main(
    influxdb_host: str = 'localhost',
    influxdb_port: int = 8086,
    influxdb_user: str = 'zmq',
    influxdb_password: str = 'zmq',
    influxdb_db: str = 'tick',
    zmq_host: str = 'localhost'
) -> None:
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        zmq_host = sys.argv[1]
    if len(sys.argv) > 2:
        influxdb_host = sys.argv[2]
    
    subscriber = KrakenTickToInfluxDBSubscriber(
        influxdb_host=influxdb_host,
        influxdb_port=influxdb_port,
        influxdb_user=influxdb_user,
        influxdb_password=influxdb_password,
        influxdb_db=influxdb_db,
        zmq_host=zmq_host
    )
    subscriber.run()


if __name__ == '__main__':
    main()
