from feast.cli import cli
import sys

print(f"Type of cli: {type(cli)}")
print(f"Dir of cli: {dir(cli)}")

# Check for common entry points
if hasattr(cli, 'cli'):
    print(f"cli.cli exists. Type: {type(cli.cli)}")
    print(f"Is cli.cli callable? {callable(cli.cli)}")

if hasattr(cli, 'main'):
    print(f"cli.main exists. Type: {type(cli.main)}")
