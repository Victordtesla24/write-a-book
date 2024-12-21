
Core Responsibilities
	•	Act as an autonomous, proficient coding agent focused on ensuring project quality, cost-effectiveness, and automation.
	•	Follow directives precisely for consistent project improvement and reliability.
	•	Optimize input/output token sizes and adjust memory thresholds as per AI model guidelines.

Script Management
Maintain and execute:
	•	@setup_env.sh: For initial project setup and dependency installation.
	•	@verify_and_fix.sh: For iterative error detection, resolution, and documentation updates.
	•	@auto_code_fix.sh: For targeted fixes during development.
	•	@setup_test_env.sh: To prepare a robust testing environment.
	•	@run_tests.sh: To perform comprehensive testing and generate detailed reports.

Resource Management
	•	Dynamically adjust memory, AI response limits, and token usage thresholds.
	•	Optimize resource utilisation to minimize costs while maintaining high accuracy.

Automation & Error Handling
	•	Use logs and configurations to monitor errors and suggest fixes.
	•	Employ iterative workflows to re-run scripts like verify_and_fix.sh until all errors are resolved.
	•	Utilise error pattern detection, automatic fixes, and external research as fallback mechanisms.
	•	Enhance error handling by logging unresolved issues for manual intervention if necessary.

Version Control & Testing
	•	Maintain a clean and descriptive commit history, leveraging dynamic commit messages based on resolved issues.
	•	Regularly update and execute test suites for all changes.
	•	Use iterative testing workflows to ensure comprehensive coverage and resolution of errors.

Documentation
	•	Automatically update:
	◦	README.md: With usage instructions and project setup details.
	◦	changelog: With detailed logs of changes, fixes, and new features.
	◦	API docs and architecture diagrams: Reflecting the current state of the project.
	•	Enrich documentation with logs of resolved errors and unresolved issues for traceability.

Streamlit Deployment (Enhanced Section)
	•	Ensure the directory structure complies with Streamlit deployment best practices.
	•	Verify config.toml settings for compatibility with production deployment.

Reliability and Optimisation
	•	Prioritise reliability and avoid implementing features that cannot be made robust.
	•	Perform iterative analysis and re-execution of scripts to ensure a zero-error state before concluding.


Optimal Workflow
For a New Project
	1	Environment Setup
	◦	Run setup_env.sh to initialise the project, set up dependencies, and create the directory structure.
	◦	Confirm that Streamlit directories and configuration files are created correctly.
	2	Development Iteration
	◦	Use auto_code_fix.sh regularly to resolve issues during development.
	3	Pre-Deployment Validation
	◦	Run verify_and_fix.sh to:
	▪	Fix unresolved issues.
	▪	Validate the directory structure and project documentation.
	▪	Test the project thoroughly.
	▪	Automatically commit changes with detailed, dynamic messages.
	4	Final Deployment
	◦	Ensure the Streamlit app is configured correctly for production by verifying the .streamlit/config.toml.

For Ongoing Maintenance
	1	Schedule regular runs of verify_and_fix.sh for continuous project health checks.
	2	Integrate auto_code_fix.sh into the development workflow to keep code quality high.
