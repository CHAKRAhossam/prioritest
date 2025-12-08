"""Parsers for CI/CD reports (JaCoCo, Surefire, PIT)."""
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from io import BytesIO
import requests

logger = logging.getLogger(__name__)


class CIArtifactParser:
    """Base class for CI/CD artifact parsers."""
    
    @staticmethod
    def parse_from_url(url: str) -> Optional[Dict[str, Any]]:
        """Parse artifact from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return CIArtifactParser.parse_from_content(response.content)
        except Exception as e:
            logger.error(f"Error downloading artifact from {url}: {e}")
            return None
    
    @staticmethod
    def parse_from_content(content: bytes) -> Dict[str, Any]:
        """Parse artifact from content bytes."""
        raise NotImplementedError


class JaCoCoParser(CIArtifactParser):
    """Parser for JaCoCo XML reports."""
    
    @staticmethod
    def parse_from_content(content: bytes) -> Dict[str, Any]:
        """
        Parse JaCoCo XML report.
        
        Returns:
            Dict with coverage metrics per class
        """
        try:
            root = ET.fromstring(content)
            
            # Initialize counters
            total_instructions = 0
            covered_instructions = 0
            total_branches = 0
            covered_branches = 0
            total_lines = 0
            covered_lines = 0
            
            classes = []
            
            # Parse package elements
            for package in root.findall(".//package"):
                package_name = package.get("name", "")
                
                for class_elem in package.findall("class"):
                    class_name = class_elem.get("name", "").split(".")[-1]
                    full_class_name = f"{package_name}.{class_name}" if package_name else class_name
                    
                    # Get method coverage
                    methods = []
                    for method in class_elem.findall("method"):
                        method_name = method.get("name", "")
                        method_desc = method.get("desc", "")
                        
                        counter = method.find("counter")
                        if counter is not None:
                            method_covered = int(counter.get("covered", 0))
                            method_missed = int(counter.get("missed", 0))
                            methods.append({
                                "name": method_name,
                                "desc": method_desc,
                                "covered": method_covered,
                                "missed": method_missed
                            })
                    
                    # Get class-level counters
                    counter = class_elem.find("counter")
                    if counter is not None:
                        counter_type = counter.get("type", "")
                        covered = int(counter.get("covered", 0))
                        missed = int(counter.get("missed", 0))
                        total = covered + missed
                        
                        if counter_type == "INSTRUCTION":
                            total_instructions += total
                            covered_instructions += covered
                        elif counter_type == "BRANCH":
                            total_branches += total
                            covered_branches += covered
                        elif counter_type == "LINE":
                            total_lines += total
                            covered_lines += covered
                        
                        classes.append({
                            "name": full_class_name,
                            "package": package_name,
                            "covered": covered,
                            "missed": missed,
                            "total": total,
                            "coverage": (covered / total * 100) if total > 0 else 0,
                            "methods": methods
                        })
            
            return {
                "type": "jacoco",
                "summary": {
                    "total_instructions": total_instructions,
                    "covered_instructions": covered_instructions,
                    "instruction_coverage": (covered_instructions / total_instructions * 100) if total_instructions > 0 else 0,
                    "total_branches": total_branches,
                    "covered_branches": covered_branches,
                    "branch_coverage": (covered_branches / total_branches * 100) if total_branches > 0 else 0,
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "line_coverage": (covered_lines / total_lines * 100) if total_lines > 0 else 0
                },
                "classes": classes
            }
            
        except ET.ParseError as e:
            logger.error(f"Error parsing JaCoCo XML: {e}")
            return {"type": "jacoco", "error": str(e)}
        except Exception as e:
            logger.error(f"Error processing JaCoCo report: {e}")
            return {"type": "jacoco", "error": str(e)}


class SurefireParser(CIArtifactParser):
    """Parser for Surefire XML reports."""
    
    @staticmethod
    def parse_from_content(content: bytes) -> Dict[str, Any]:
        """
        Parse Surefire XML report.
        
        Returns:
            Dict with test execution results
        """
        try:
            root = ET.fromstring(content)
            
            tests = []
            total_tests = 0
            total_failures = 0
            total_errors = 0
            total_skipped = 0
            
            # Parse testcase elements
            for testcase in root.findall(".//testcase"):
                test_name = testcase.get("name", "")
                class_name = testcase.get("classname", "")
                time = float(testcase.get("time", 0))
                
                total_tests += 1
                
                test_result = {
                    "name": test_name,
                    "class": class_name,
                    "time": time,
                    "status": "passed"
                }
                
                # Check for failures or errors
                failure = testcase.find("failure")
                error = testcase.find("error")
                skipped = testcase.find("skipped")
                
                if failure is not None:
                    total_failures += 1
                    test_result["status"] = "failed"
                    test_result["failure"] = {
                        "message": failure.get("message", ""),
                        "type": failure.get("type", ""),
                        "text": failure.text
                    }
                elif error is not None:
                    total_errors += 1
                    test_result["status"] = "error"
                    test_result["error"] = {
                        "message": error.get("message", ""),
                        "type": error.get("type", ""),
                        "text": error.text
                    }
                elif skipped is not None:
                    total_skipped += 1
                    test_result["status"] = "skipped"
                    test_result["skipped"] = {
                        "message": skipped.get("message", ""),
                        "text": skipped.text
                    }
                
                tests.append(test_result)
            
            return {
                "type": "surefire",
                "summary": {
                    "total_tests": total_tests,
                    "total_failures": total_failures,
                    "total_errors": total_errors,
                    "total_skipped": total_skipped,
                    "total_passed": total_tests - total_failures - total_errors - total_skipped,
                    "pass_rate": ((total_tests - total_failures - total_errors - total_skipped) / total_tests * 100) if total_tests > 0 else 0
                },
                "tests": tests
            }
            
        except ET.ParseError as e:
            logger.error(f"Error parsing Surefire XML: {e}")
            return {"type": "surefire", "error": str(e)}
        except Exception as e:
            logger.error(f"Error processing Surefire report: {e}")
            return {"type": "surefire", "error": str(e)}


class PITParser(CIArtifactParser):
    """Parser for PIT mutation testing XML reports."""
    
    @staticmethod
    def parse_from_content(content: bytes) -> Dict[str, Any]:
        """
        Parse PIT XML report.
        
        Returns:
            Dict with mutation testing results
        """
        try:
            root = ET.fromstring(content)
            
            mutations = []
            total_mutations = 0
            killed_mutations = 0
            survived_mutations = 0
            timed_out_mutations = 0
            
            # Parse mutation elements
            for mutation in root.findall(".//mutation"):
                total_mutations += 1
                
                detected = mutation.get("detected", "false").lower() == "true"
                status = mutation.get("status", "")
                
                if detected or status == "KILLED":
                    killed_mutations += 1
                elif status == "SURVIVED":
                    survived_mutations += 1
                elif status == "TIMED_OUT":
                    timed_out_mutations += 1
                
                mutations.append({
                    "mutated_class": mutation.get("mutatedClass", ""),
                    "mutated_method": mutation.get("mutatedMethod", ""),
                    "mutator": mutation.get("mutator", ""),
                    "line_number": int(mutation.get("lineNumber", 0)),
                    "detected": detected,
                    "status": status,
                    "killing_tests": [test.text for test in mutation.findall("killingTest")]
                })
            
            return {
                "type": "pit",
                "summary": {
                    "total_mutations": total_mutations,
                    "killed_mutations": killed_mutations,
                    "survived_mutations": survived_mutations,
                    "timed_out_mutations": timed_out_mutations,
                    "mutation_score": (killed_mutations / total_mutations * 100) if total_mutations > 0 else 0
                },
                "mutations": mutations
            }
            
        except ET.ParseError as e:
            logger.error(f"Error parsing PIT XML: {e}")
            return {"type": "pit", "error": str(e)}
        except Exception as e:
            logger.error(f"Error processing PIT report: {e}")
            return {"type": "pit", "error": str(e)}


def get_parser(artifact_type: str) -> Optional[CIArtifactParser]:
    """Get parser for artifact type."""
    parsers = {
        "jacoco": JaCoCoParser,
        "surefire": SurefireParser,
        "pit": PITParser
    }
    return parsers.get(artifact_type.lower())

