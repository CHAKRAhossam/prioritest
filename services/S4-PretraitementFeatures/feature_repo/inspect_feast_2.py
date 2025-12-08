import feast.cli
import click

print(f"Type of feast.cli.cli: {type(feast.cli.cli)}")
print(f"Is feast.cli.cli callable? {callable(feast.cli.cli)}")
print(f"Is feast.cli.cli a click command? {isinstance(feast.cli.cli, click.Command)}")

if hasattr(feast.cli, "apply_total_command"):
    print(f"Type of feast.cli.apply_total_command: {type(feast.cli.apply_total_command)}")
    print(f"Is feast.cli.apply_total_command callable? {callable(feast.cli.apply_total_command)}")
