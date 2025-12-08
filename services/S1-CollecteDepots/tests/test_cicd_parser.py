"""Tests for CI/CD parsers."""
import pytest
from src.services.cicd_parser import JaCoCoParser, SurefireParser, PITParser, get_parser


def test_jacoco_parser():
    """Test JaCoCo parser."""
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <report>
        <package name="com.example">
            <class name="TestClass">
                <method name="testMethod" desc="()V">
                    <counter type="INSTRUCTION" covered="10" missed="5"/>
                </method>
                <counter type="INSTRUCTION" covered="10" missed="5"/>
                <counter type="BRANCH" covered="2" missed="1"/>
                <counter type="LINE" covered="8" missed="2"/>
            </class>
        </package>
    </report>
    """
    
    result = JaCoCoParser.parse_from_content(xml_content)
    
    assert result["type"] == "jacoco"
    assert "summary" in result
    assert "classes" in result
    assert result["summary"]["total_instructions"] > 0


def test_surefire_parser():
    """Test Surefire parser."""
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="2" failures="0" errors="0" skipped="0">
        <testcase name="test1" classname="TestClass" time="0.1"/>
        <testcase name="test2" classname="TestClass" time="0.2">
            <failure message="Test failed" type="AssertionError">Stack trace</failure>
        </testcase>
    </testsuite>
    """
    
    result = SurefireParser.parse_from_content(xml_content)
    
    assert result["type"] == "surefire"
    assert result["summary"]["total_tests"] == 2
    assert result["summary"]["total_failures"] == 1
    assert len(result["tests"]) == 2


def test_pit_parser():
    """Test PIT parser."""
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <mutations>
        <mutation detected="true" status="KILLED" mutatedClass="TestClass" mutatedMethod="testMethod" mutator="MathMutator" lineNumber="10">
            <killingTest>TestClass.testMethod</killingTest>
        </mutation>
        <mutation detected="false" status="SURVIVED" mutatedClass="TestClass" mutatedMethod="testMethod2" mutator="ConditionalMutator" lineNumber="20"/>
    </mutations>
    """
    
    result = PITParser.parse_from_content(xml_content)
    
    assert result["type"] == "pit"
    assert result["summary"]["total_mutations"] == 2
    assert result["summary"]["killed_mutations"] == 1
    assert result["summary"]["survived_mutations"] == 1


def test_get_parser():
    """Test parser factory."""
    assert get_parser("jacoco") == JaCoCoParser
    assert get_parser("surefire") == SurefireParser
    assert get_parser("pit") == PITParser
    assert get_parser("unknown") is None

