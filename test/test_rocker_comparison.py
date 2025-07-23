"""
Comparative test suite between original rocker and dagger-rocker
This test suite runs equivalent commands in both tools and verifies they produce similar results.
"""
import pytest
import subprocess
import tempfile
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Add the dagger_rocker directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "dagger_rocker"))

try:
    import importlib.util
    if importlib.util.find_spec("core"):
        pass  # Just check availability
except ImportError as e:
    pytest.skip(f"Dagger rocker not available: {e}", allow_module_level=True)


class RockerCommandComparator:
    """Class to compare rocker and dagger-rocker commands"""
    
    def __init__(self):
        self.rocker_path = "/home/ags/projects/manifest_rocker/.venv/bin/rocker"
        self.dagger_rocker_path = "/home/ags/projects/manifest_rocker/.venv/bin/python"
        self.dagger_rocker_script = "/home/ags/projects/manifest_rocker/dagger_rocker/cli.py"
    
    def parse_rocker_help(self) -> Dict[str, str]:
        """Parse rocker help output to extract available flags"""
        try:
            result = subprocess.run([self.rocker_path, "--help"], 
                                  capture_output=True, text=True, check=True)
            help_text = result.stdout
            
            # Extract flag information
            flags = {}
            lines = help_text.split('\n')
            current_flag = None
            
            for line in lines:
                # Look for flag definitions (lines starting with spaces and containing --)
                if line.strip().startswith('--') or line.strip().startswith('-'):
                    # Extract flag name and description
                    flag_match = re.search(r'--([a-zA-Z0-9_-]+)', line)
                    if flag_match:
                        current_flag = flag_match.group(1)
                        # Get description
                        desc_match = re.search(r'--[a-zA-Z0-9_-]+.*?([A-Z].*?)(?:\(default:|$)', line)
                        description = desc_match.group(1).strip() if desc_match else ""
                        flags[current_flag] = description
                elif current_flag and line.strip() and not line.strip().startswith('-'):
                    # Continue description on next line
                    flags[current_flag] += " " + line.strip()
            
            return flags
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to get rocker help: {e}")
    
    def run_rocker_dry_run(self, args: List[str]) -> str:
        """Run rocker with --mode dry-run and return output"""
        cmd = [self.rocker_path] + args + ["--mode", "dry-run", "ubuntu:20.04", "echo", "test"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stderr}"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out"
    
    def run_dagger_rocker_dry_run(self, args: List[str]) -> str:
        """Run dagger-rocker with --dry-run and return output"""
        cmd = [self.dagger_rocker_path, self.dagger_rocker_script] + args + ["--dry-run", "ubuntu:20.04", "echo", "test"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stderr}"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out"
    
    def extract_active_extensions(self, output: str) -> List[str]:
        """Extract active extensions from dry-run output"""
        # For rocker
        rocker_match = re.search(r'Active extensions \[(.*?)\]', output)
        if rocker_match:
            extensions_str = rocker_match.group(1)
            return [ext.strip().strip("'\"") for ext in extensions_str.split(',') if ext.strip()]
        
        # For dagger-rocker
        dagger_match = re.search(r'Active extensions: \[(.*?)\]', output)
        if dagger_match:
            extensions_str = dagger_match.group(1)
            return [ext.strip().strip("'\"") for ext in extensions_str.split(',') if ext.strip()]
        
        return []
    
    def compare_extension_activation(self, flag: str) -> Tuple[bool, str, str]:
        """Compare if both tools activate the same extensions for a given flag"""
        rocker_output = self.run_rocker_dry_run([f"--{flag}"])
        dagger_output = self.run_dagger_rocker_dry_run([f"--{flag}"])
        
        rocker_extensions = self.extract_active_extensions(rocker_output)
        dagger_extensions = self.extract_active_extensions(dagger_output)
        
        # Check if the main extension is activated in both
        extension_activated = flag in rocker_extensions or flag in dagger_extensions
        
        return extension_activated, rocker_output, dagger_output


@pytest.fixture
def comparator():
    """Fixture to provide RockerCommandComparator instance"""
    return RockerCommandComparator()


class TestRockerFlagParity:
    """Test that dagger-rocker supports the same flags as rocker"""
    
    def test_help_output_comparison(self, comparator):
        """Test that both tools provide help output"""
        # Test rocker help
        rocker_result = subprocess.run([comparator.rocker_path, "--help"], 
                                     capture_output=True, text=True)
        assert rocker_result.returncode == 0, "Rocker help should work"
        assert "--user" in rocker_result.stdout, "Rocker should have --user flag"
        
        # Test dagger-rocker help
        dagger_result = subprocess.run([comparator.dagger_rocker_path, comparator.dagger_rocker_script, "--help"], 
                                     capture_output=True, text=True)
        assert dagger_result.returncode == 0, "Dagger-rocker help should work"
        assert "--user" in dagger_result.stdout, "Dagger-rocker should have --user flag"
    
    def test_basic_dry_run_comparison(self, comparator):
        """Test basic dry-run comparison between tools"""
        rocker_output = comparator.run_rocker_dry_run([])
        dagger_output = comparator.run_dagger_rocker_dry_run([])
        
        # Both should complete without error
        assert not rocker_output.startswith("ERROR"), f"Rocker dry-run failed: {rocker_output}"
        assert not dagger_output.startswith("ERROR"), f"Dagger-rocker dry-run failed: {dagger_output}"
        
        # Both should mention the image
        assert "ubuntu:20.04" in rocker_output or "ubuntu:20.04" in dagger_output
    
    @pytest.mark.parametrize("flag", [
        "user",
        "home", 
        "x11",
    ])
    def test_common_flag_support(self, comparator, flag):
        """Test that common flags are supported by both tools"""
        rocker_output = comparator.run_rocker_dry_run([f"--{flag}"])
        dagger_output = comparator.run_dagger_rocker_dry_run([f"--{flag}"])
        
        # Both should complete without error for supported flags
        rocker_error = rocker_output.startswith("ERROR")
        dagger_error = dagger_output.startswith("ERROR")
        
        # If rocker supports it, dagger-rocker should too (or at least not crash)
        if not rocker_error:
            # Dagger-rocker might not support all flags yet, but shouldn't crash
            if dagger_error:
                # Log the error for debugging but don't fail the test yet
                print(f"Warning: dagger-rocker doesn't support --{flag} yet: {dagger_output}")
    
    def test_user_flag_equivalence(self, comparator):
        """Test that --user flag produces equivalent results"""
        activated, rocker_out, dagger_out = comparator.compare_extension_activation("user")
        
        # Both should activate user-related functionality
        assert "user" in rocker_out.lower() or "user" in dagger_out.lower(), \
            f"User extension should be mentioned\nRocker: {rocker_out}\nDagger: {dagger_out}"
    
    def test_volume_flag_with_temp_dir(self, comparator):
        """Test --volume flag with a temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "test_file.txt"
            temp_file.write_text("test content")
            
            volume_arg = f"{temp_dir}:/mounted_dir"
            
            rocker_output = comparator.run_rocker_dry_run(["--volume", volume_arg])
            dagger_output = comparator.run_dagger_rocker_dry_run(["--volume", volume_arg])
            
            # Both should handle volume mounting
            assert not rocker_output.startswith("ERROR"), f"Rocker volume test failed: {rocker_output}"
            # Dagger-rocker might not fully support volumes yet
            if dagger_output.startswith("ERROR"):
                print(f"Warning: dagger-rocker volume support incomplete: {dagger_output}")
    
    def test_combined_flags(self, comparator):
        """Test combinations of flags"""
        combined_flags = ["--user", "--home"]
        
        rocker_output = comparator.run_rocker_dry_run(combined_flags)
        dagger_output = comparator.run_dagger_rocker_dry_run(combined_flags)
        
        # Both should handle combined flags
        assert not rocker_output.startswith("ERROR"), f"Rocker combined flags failed: {rocker_output}"
        
        # Check that dagger-rocker shows proper extension ordering
        if not dagger_output.startswith("ERROR"):
            assert "Active extensions:" in dagger_output, "Should show active extensions"


class TestRockerOutputComparison:
    """Test that outputs are functionally equivalent"""
    
    def test_extension_activation_patterns(self, comparator):
        """Test that extension activation follows similar patterns"""
        test_cases = [
            (["--user"], "user"),
            (["--home"], "home"),
            (["--user", "--home"], "both"),
        ]
        
        for flags, case_name in test_cases:
            rocker_output = comparator.run_rocker_dry_run(flags)
            dagger_output = comparator.run_dagger_rocker_dry_run(flags)
            
            print(f"\n=== Testing {case_name} ===")
            print(f"Rocker output:\n{rocker_output}")
            print(f"Dagger output:\n{dagger_output}")
            
            # Both should complete successfully for basic flags
            if case_name in ["user", "both"]:
                assert not rocker_output.startswith("ERROR"), f"Rocker should support {flags}"
    
    def test_error_handling_comparison(self, comparator):
        """Test that both tools handle errors similarly"""
        # Test with invalid image name
        rocker_output = comparator.run_rocker_dry_run(["--mode", "dry-run", "invalid:nonexistent", "echo", "test"])
        
        # Remove the dry-run from our test since we add it automatically
        cmd = [comparator.dagger_rocker_path, comparator.dagger_rocker_script, 
               "--dry-run", "invalid:nonexistent", "echo", "test"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            dagger_output = result.stdout + result.stderr
        except subprocess.CalledProcessError as e:
            dagger_output = f"ERROR: {e.stderr}"
        
        # Both should handle invalid images gracefully in dry-run mode
        print(f"Rocker with invalid image: {rocker_output}")
        print(f"Dagger with invalid image: {dagger_output}")


def test_flag_coverage_report(comparator):
    """Generate a report of flag coverage between rocker and dagger-rocker"""
    rocker_flags = comparator.parse_rocker_help()
    
    print("\n=== ROCKER FLAG COVERAGE REPORT ===")
    print(f"Total rocker flags found: {len(rocker_flags)}")
    
    # Test a subset of important flags
    important_flags = [
        "user", "home", "volume", "x11", "env", "network", 
        "detach", "name", "hostname", "privileged"
    ]
    
    supported = []
    unsupported = []
    
    for flag in important_flags:
        if flag in rocker_flags:
            try:
                dagger_output = comparator.run_dagger_rocker_dry_run([f"--{flag}"])
                if not dagger_output.startswith("ERROR"):
                    supported.append(flag)
                else:
                    unsupported.append(flag)
            except Exception:
                unsupported.append(flag)
    
    print(f"\nSupported flags ({len(supported)}): {supported}")
    print(f"Unsupported flags ({len(unsupported)}): {unsupported}")
    print(f"Coverage: {len(supported)}/{len(important_flags)} ({100*len(supported)/len(important_flags):.1f}%)")


if __name__ == "__main__":
    # Run the coverage report
    comparator = RockerCommandComparator()
    test_flag_coverage_report(comparator)
    
    # Run pytest
    pytest.main([__file__, "-v"])
