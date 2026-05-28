from mcp.server.fastmcp import FastMCP

from skills.requirement_analysis_skill import RequirementAnalysisSkill
from skills.test_case_generation_skill import TestCaseGenerationSkill
from skills.playwright_code_generation_skill import PlaywrightCodeGenerationSkill
from skills.page_object_generation_skill import PageObjectGenerationSkill
from utils.file_writer import FileWriter


mcp = FastMCP("playwright-test-generator")


@mcp.tool()
def generate_test_cases(requirement: str) -> dict:
    """
    Generate structured test cases from a business requirement.
    """
    analysis_skill = RequirementAnalysisSkill()
    test_case_skill = TestCaseGenerationSkill()

    analysis = analysis_skill.analyse(requirement)
    test_cases = test_case_skill.generate_test_cases(analysis)

    return {
        "analysis": analysis,
        "test_cases": test_cases,
    }


@mcp.tool()
def generate_playwright_tests(
    requirement: str,
    output_file: str = "tests/generated/test_generated_login.py",
) -> dict:
    """
    Generate Playwright Pytest automation code from a business requirement.
    """
    analysis_skill = RequirementAnalysisSkill()
    test_case_skill = TestCaseGenerationSkill()
    code_generation_skill = PlaywrightCodeGenerationSkill()

    analysis = analysis_skill.analyse(requirement)
    test_cases = test_case_skill.generate_test_cases(analysis)
    code = code_generation_skill.generate_pytest_code(
        test_cases=test_cases,
        module=analysis["module"],
    )

    FileWriter.write_file(output_file, code)

    return {
        "message": "Playwright test file generated successfully",
        "module": analysis["module"],
        "output_file": output_file,
        "test_case_count": len(test_cases),
    }


@mcp.tool()
def generate_page_object(module_name: str, locators: dict, output_file: str = "") -> dict:
    """
    Generate Page Object Model file from locators.
    """
    page_object_skill = PageObjectGenerationSkill()
    code = page_object_skill.generate_page_object(
        module_name=module_name,
        locators=locators,
    )

    if not output_file:
        output_file = f"pages/{module_name.lower()}_page.py"

    FileWriter.write_file(output_file, code)

    return {
        "message": "Page object generated successfully",
        "module": module_name,
        "output_file": output_file,
    }


@mcp.tool()
def generate_manual_test_document(
    requirement: str,
    output_file: str = "tests/generated/manual_test_cases.md",
) -> dict:
    """
    Generate manual test cases in markdown format.
    """
    analysis_skill = RequirementAnalysisSkill()
    test_case_skill = TestCaseGenerationSkill()

    analysis = analysis_skill.analyse(requirement)
    test_cases = test_case_skill.generate_test_cases(analysis)

    markdown = "# Generated Manual Test Cases\n\n"

    for test_case in test_cases:
        markdown += f"## {test_case['test_case_id']} - {test_case['title']}\n\n"
        markdown += f"**Priority:** {test_case['priority']}\n\n"

        markdown += "**Preconditions:**\n"
        for precondition in test_case["preconditions"]:
            markdown += f"- {precondition}\n"

        markdown += "\n**Steps:**\n"
        for index, step in enumerate(test_case["steps"], start=1):
            markdown += f"{index}. {step}\n"

        markdown += f"\n**Expected Result:** {test_case['expected_result']}\n\n"

    FileWriter.write_file(output_file, markdown)

    return {
        "message": "Manual test document generated successfully",
        "output_file": output_file,
        "test_case_count": len(test_cases),
    }


if __name__ == "__main__":
    print("Starting MCP server on http://127.0.0.1:8000")
    mcp.run(transport="streamable-http")
