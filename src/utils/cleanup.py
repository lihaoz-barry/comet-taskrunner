"""
Cleanup utilities for temporary files
"""
import os
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def cleanup_temp_files(project_root: Path = None):
    """
    Clean up temporary files and directories.
    
    Args:
        project_root: Project root directory (default: auto-detect)
    """
    if project_root is None:
        # Auto-detect project root (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
    
    # Directories to clean (complete removal)
    temp_dirs = [
        project_root / "screenshots",
    ]
    
    # __pycache__ directories (recursive search)
    pycache_dirs = list(project_root.rglob("__pycache__"))
    
    cleaned_count = 0
    
    logger.info("="*50)
    logger.info("Starting cleanup of temporary files...")
    logger.info("="*50)
    
    # Clean specified directories
    for dir_path in temp_dirs:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"  ✓ Removed: {dir_path.name}/")
                cleaned_count += 1
            except Exception as e:
                logger.warning(f"  ⚠ Failed to remove {dir_path}: {e}")
    
    # Clean __pycache__ directories
    for pycache_dir in pycache_dirs:
        if pycache_dir.exists():
            try:
                shutil.rmtree(pycache_dir)
                logger.debug(f"  ✓ Removed: {pycache_dir}")
                cleaned_count += 1
            except Exception as e:
                logger.warning(f"  ⚠ Failed to remove {pycache_dir}: {e}")
    
    # Clean .pyc and .pyo files
    pyc_files = list(project_root.rglob("*.pyc"))
    pyo_files = list(project_root.rglob("*.pyo"))
    
    for file_path in pyc_files + pyo_files:
        try:
            file_path.unlink()
            logger.debug(f"  ✓ Removed: {file_path.name}")
            cleaned_count += 1
        except Exception as e:
            logger.warning(f"  ⚠ Failed to remove {file_path}: {e}")
    
    logger.info("="*50)
    if cleaned_count > 0:
        logger.info(f"✓ Cleanup complete: {cleaned_count} items removed")
    else:
        logger.info("✓ No temporary files to clean")
    logger.info("="*50)
    
    return cleaned_count
