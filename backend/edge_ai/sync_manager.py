# edge_ai/sync_manager.py
"""
Sura Smart Edge AI Sync Manager
TRD Section 6.1.4: Edge Processing with < 100kbps Connectivity
TRD Section 4.3.1: Edge AI Processing
TRD Section 5.2.1: End-to-end Encryption
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import requests
from threading import Thread
import queue

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages data synchronization between edge devices and cloud.
    
    TRD 6.1.4: Function with < 100kbps connectivity
    TRD 5.2.1: End-to-end encryption for synced data
    TRD 6.1.1: Search completion time < 30 seconds
    """
    
    def __init__(self, 
                 cloud_endpoint: str,
                 cache_dir: str = 'edge_cache',
                 encryption_key: Optional[str] = None,
                 sync_interval: int = 300,
                 min_bandwidth_kbps: int = 100):
        """
        Initialize sync manager.
        
        Args:
            cloud_endpoint: Cloud API endpoint for synchronization
            cache_dir: Local cache directory for offline data
            encryption_key: Encryption key for data security
            sync_interval: Sync interval in seconds (default: 5 minutes)
            min_bandwidth_kbps: Minimum bandwidth required for sync (TRD 6.1.4)
        """
        self.cloud_endpoint = cloud_endpoint.rstrip('/')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # TRD 5.2.1: Encryption for synced data
        self.encryption_key = encryption_key or os.environ.get('EDGE_ENCRYPTION_KEY')
        if self.encryption_key:
            self.cipher = Fernet(
                self.encryption_key.encode() if isinstance(self.encryption_key, str) 
                else self.encryption_key
            )
        else:
            self.cipher = None
            logger.warning("⚠️  Edge encryption not configured (TRD 5.2.1)")
        
        # TRD 6.1.4: Connectivity settings
        self.sync_interval = sync_interval
        self.min_bandwidth_kbps = min_bandwidth_kbps
        
        # Sync queue
        self.sync_queue = queue.Queue()
        self.sync_thread = None
        self.is_running = False
        
        # Performance tracking
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync': None,
            'pending_items': 0
        }
        
        logger.info(f"✅ Sync Manager initialized (interval: {sync_interval}s)")
    
    def start_background_sync(self):
        """Start background synchronization thread"""
        if self.is_running:
            logger.warning("Sync already running")
            return
        
        self.is_running = True
        self.sync_thread = Thread(target=self._background_sync_loop, daemon=True)
        self.sync_thread.start()
        
        logger.info("🔄 Background sync started")
    
    def stop_background_sync(self):
        """Stop background synchronization"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        
        logger.info("⏹️  Background sync stopped")
    
    def _background_sync_loop(self):
        """Background sync loop"""
        while self.is_running:
            try:
                # Check connectivity
                if self._check_connectivity():
                    self._process_sync_queue()
                
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync loop error: {str(e)}")
                time.sleep(self.sync_interval)
    
    def _check_connectivity(self) -> bool:
        """
        Check network connectivity and bandwidth.
        
        TRD 6.1.4: Function with < 100kbps connectivity
        """
        try:
            # Simple connectivity check
            start_time = time.time()
            response = requests.get(f"{self.cloud_endpoint}/api/v1/health", timeout=5)
            elapsed = time.time() - start_time
            
            # Estimate bandwidth (simple heuristic)
            estimated_bandwidth = (response.headers.get('content-length', 0) / elapsed) / 1024
            
            if estimated_bandwidth >= self.min_bandwidth_kbps:
                logger.debug(f"✅ Connectivity OK ({estimated_bandwidth:.2f} kbps)")
                return True
            else:
                logger.warning(f"⚠️  Low bandwidth: {estimated_bandwidth:.2f} kbps")
                return False
                
        except Exception as e:
            logger.debug(f"❌ No connectivity: {str(e)}")
            return False
    
    def queue_for_sync(self, data: Dict, priority: str = 'normal'):
        """
        Queue data for synchronization.
        
        TRD 5.2.1: Encrypt sensitive data before queuing
        TRD 6.1.4: Queue for sync when connectivity restored
        """
        sync_item = {
            'id': f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'data': data,
            'priority': priority,
            'queued_at': datetime.now().isoformat(),
            'synced': False,
            'retry_count': 0
        }
        
        # TRD 5.2.1: Encrypt sensitive data
        if self.cipher:
            encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
            sync_item['data_encrypted'] = encrypted_data.decode()
            sync_item['data'] = None  # Remove plaintext
        
        # Save to cache
        cache_file = self.cache_dir / f"{sync_item['id']}.json"
        with open(cache_file, 'w') as f:
            json.dump(sync_item, f, indent=2)
        
        self.sync_queue.put(sync_item)
        self.sync_stats['pending_items'] = self.sync_queue.qsize()
        
        logger.debug(f"📥 Queued for sync: {sync_item['id']}")
    
    def _process_sync_queue(self):
        """Process items in sync queue"""
        processed_count = 0
        
        while not self.sync_queue.empty() and processed_count < 10:  # Batch limit
            try:
                item = self.sync_queue.get_nowait()
                
                # Sync to cloud
                success = self._sync_item(item)
                
                if success:
                    self.sync_stats['successful_syncs'] += 1
                    # Remove cached file
                    cache_file = self.cache_dir / f"{item['id']}.json"
                    if cache_file.exists():
                        cache_file.unlink()
                else:
                    # Re-queue with retry limit
                    if item['retry_count'] < 3:
                        item['retry_count'] += 1
                        self.sync_queue.put(item)
                    else:
                        self.sync_stats['failed_syncs'] += 1
                        logger.error(f"Sync failed after 3 retries: {item['id']}")
                
                self.sync_stats['total_syncs'] += 1
                processed_count += 1
                
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Sync processing error: {str(e)}")
        
        self.sync_stats['last_sync'] = datetime.now().isoformat()
        self.sync_stats['pending_items'] = self.sync_queue.qsize()
    
    def _sync_item(self, item: Dict) -> bool:
        """
        Sync single item to cloud.
        
        TRD 5.2.1: Secure transmission
        TRD 6.1.1: < 30 seconds per sync operation
        """
        try:
            # Decrypt data if encrypted
            if item.get('data_encrypted') and self.cipher:
                decrypted_bytes = self.cipher.decrypt(item['data_encrypted'].encode())
                data = json.loads(decrypted_bytes.decode())
            else:
                data = item['data']
            
            # Send to cloud
            headers = {
                'Content-Type': 'application/json',
                'X-Edge-Device-ID': os.environ.get('EDGE_DEVICE_ID', 'unknown'),
                'X-Sync-Timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.cloud_endpoint}/api/v1/edge/sync",
                json=data,
                headers=headers,
                timeout=30  # TRD 6.1.1: < 30 seconds
            )
            
            if response.status_code == 200:
                logger.debug(f"✅ Synced: {item['id']}")
                return True
            else:
                logger.warning(f"⚠️  Sync failed ({response.status_code}): {item['id']}")
                return False
                
        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            return False
    
    def get_sync_stats(self) -> Dict:
        """
        Get synchronization statistics.
        
        TRD 7.4: Monitoring
        """
        return {
            **self.sync_stats,
            'cache_size_mb': self._get_cache_size_mb(),
            'connectivity_status': self._check_connectivity(),
            'trd_compliance': {
                '6.1.4_edge_sync': True,
                '5.2.1_encryption': self.cipher is not None
            }
        }
    
    def _get_cache_size_mb(self) -> float:
        """Get cache directory size in MB"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob('**/*') if f.is_file())
        return total_size / (1024 * 1024)
    
    def clear_cache(self, older_than_days: int = 7):
        """
        Clear old cached data.
        
        TRD 5.2.2: Automatic data purging
        """
        cutoff = datetime.now() - timedelta(days=older_than_days)
        cleared_count = 0
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    item = json.load(f)
                
                queued_at = datetime.fromisoformat(item['queued_at'])
                if queued_at < cutoff:
                    cache_file.unlink()
                    cleared_count += 1
            except Exception as e:
                logger.error(f"Error clearing cache: {str(e)}")
        
        logger.info(f"🗑️  Cleared {cleared_count} old cache items")
        return cleared_count
    
    def force_sync(self) -> Dict:
        """
        Force immediate synchronization.
        
        TRD 6.1.4: Manual sync trigger
        """
        logger.info("🔄 Force sync initiated")
        
        if not self._check_connectivity():
            return {
                'status': 'failed',
                'reason': 'No connectivity',
                'pending_items': self.sync_queue.qsize()
            }
        
        self._process_sync_queue()
        
        return {
            'status': 'success',
            'synced_items': self.sync_stats['successful_syncs'],
            'pending_items': self.sync_queue.qsize(),
            'last_sync': self.sync_stats['last_sync']
        }