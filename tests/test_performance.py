#!/usr/bin/env python3
"""
Performance tests for DBL - Testing with large number of tables
"""

import os
import sys
import time
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_dbl(*args):
    """Run DBL command"""
    cmd = [sys.executable, '-m', 'dbl'] + list(args)
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"DBL command failed: {' '.join(args)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise Exception(f"Command failed: {' '.join(args)}")
    return result.stdout

def test_performance_large_schema():
    """Test performance with many tables"""
    print("🧪 Testing performance with large schema...")

    test_dir = tempfile.mkdtemp(prefix="dbl_perf_test_")
    os.chdir(test_dir)

    db_name = f"perftest_{int(time.time())}"

    try:
        # Create config
        config_content = f"""
db_type: postgres
db_name: {db_name}
host: localhost
port: 5432
user: admin
password: pass
track_tables: []
"""
        with open('dbl.yaml', 'w') as f:
            f.write(config_content)

        run_dbl('init')

        # Create database
        subprocess.run(f'docker exec dbl_demo_pg psql -U admin -d myapp -c "CREATE DATABASE {db_name};"', shell=True, check=True)

        # Create many tables
        num_tables = 20
        print(f"Creating {num_tables} tables...")
        start_time = time.time()
        for i in range(num_tables):
            subprocess.run(f'docker exec dbl_demo_pg psql -U admin -d {db_name} -c "CREATE TABLE table_{i} (id SERIAL PRIMARY KEY, data TEXT);"', shell=True, check=True)
        create_time = time.time() - start_time
        print(".2f")

        # Diff
        print("Running diff...")
        start_time = time.time()
        run_dbl('diff')
        diff_time = time.time() - start_time
        print(".2f")

        # Commit
        print("Committing...")
        start_time = time.time()
        run_dbl('commit', '-m', f'Created {num_tables} tables')
        commit_time = time.time() - start_time
        print(".2f")

        print("✅ Performance test passed!")
        print(f"Total time: {create_time + diff_time + commit_time:.2f}s")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    finally:
        os.chdir(Path(__file__).parent.parent)
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    print("⏳ Waiting for database...")
    time.sleep(5)

    success = test_performance_large_schema()

    if success:
        print("🎉 Performance test passed!")
        sys.exit(0)
    else:
        print("💥 Performance test failed!")
        sys.exit(1)