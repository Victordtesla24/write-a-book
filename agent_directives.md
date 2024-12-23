# Rules for AI

## Core Responsibilities

• Act as an autonomous, proficient coding agent focused on ensuring project quality, cost-effectiveness, and automation.
• Follow directives precisely for consistent project improvement and reliability.
• Optimize input/output token sizes and adjust memory thresholds as per AI model guidelines.
• Maintain real-time monitoring and alerting for system health.

## Script Management

### Core Scripts

• config_manager.sh: Centralized configuration management
  - Handles environment-specific settings
  - Manages security policies
  - Controls monitoring thresholds
  - Validates configuration integrity

• plugin_manager.sh: Plugin system and extensibility
  - Manages plugin lifecycle
  - Handles dependencies
  - Provides plugin isolation
  - Validates plugin compatibility

• resource_manager.sh: Resource monitoring and optimization
  - Real-time system metrics collection
  - Resource usage optimization
  - Performance monitoring
  - Alert threshold management

• progress_reporter.sh: Progress tracking and reporting
  - Real-time progress updates
  - Task completion metrics
  - Performance analytics
  - Status visualization

• project_customizer.sh: Project-specific customizations
  - Environment configuration
  - Build settings management
  - Deployment preferences
  - Testing framework setup

• main.sh: Main orchestrator script
  - Workflow coordination
  - Error handling
  - Logging management
  - Script initialization

• monitoring_server.sh: Real-time monitoring
  - Continuous system monitoring
  - Metrics visualization
  - Performance dashboards
  - Alert management

## Resource Management

• Dynamically adjust memory, AI response limits, and token usage thresholds.
• Optimize resource utilisation to minimize costs while maintaining high accuracy.
• Monitor and report resource usage through resource_manager.sh.
• Enforce resource limits based on project configuration.
• Implement real-time monitoring and alerting.
• Generate performance dashboards and reports.
• Maintain historical metrics for trend analysis.

## Automation & Error Handling

• Use logs and configurations to monitor errors and fix them.
• Employ iterative workflows to re-run scripts like verify_and_fix.sh until all errors are resolved.
• Utilize error pattern detection, automatic fixes, and external research as fallback mechanisms.
• Enhance error handling by logging unresolved issues for manual intervention if necessary.
• Implement automated recovery procedures.
• Maintain error pattern database for quick resolution.
• Provide real-time error notifications.

## Version Control & Testing

• Maintain a clean and descriptive commit history, leveraging dynamic commit messages based on resolved issues.
• Regularly update and execute test suites for all changes.
• Use iterative testing workflows to ensure comprehensive coverage and resolution of errors.
• Implement continuous integration checks.
• Monitor test coverage metrics.
• Automate regression testing.

## Documentation

• Automatically update:
  ◦ README.md: With usage instructions and project setup details.
  ◦ changelog: With detailed logs of changes, fixes, and new features.
  ◦ API docs and architecture diagrams: Reflecting the current state of the project.
  ◦ Performance reports: System metrics and optimization recommendations.
  ◦ Monitoring dashboards: Real-time system status and metrics.
• Enrich documentation with:
  ◦ Error resolution guides
  ◦ Performance optimization tips
  ◦ System health metrics
  ◦ Resource utilization patterns

## Monitoring & Metrics

• Real-time System Monitoring:
  ◦ CPU usage tracking
  ◦ Memory utilization
  ◦ Disk space monitoring
  ◦ Network performance
  ◦ Process health checks

• Performance Metrics:
  ◦ Response time tracking
  ◦ Resource efficiency
  ◦ Error rates
  ◦ System bottlenecks

• Visualization & Reporting:
  ◦ Real-time dashboards
  ◦ Trend analysis
  ◦ Alert notifications
  ◦ Performance reports

## Optimal Workflow

### For a New Project

1. Test Dashboard Setup (MANDATORY)
   ◦ Initialize test dashboard using run_dashboard.sh
   ◦ Configure test verification settings
   ◦ Set up continuous test monitoring
   ◦ Verify dashboard accessibility

2. Environment Setup
   ◦ Run setup_env.sh to initialize the project
   ◦ Configure monitoring thresholds
   ◦ Set up real-time metrics collection
   ◦ Initialize performance dashboards

3. Development Iteration
   ◦ Monitor system resources continuously
   ◦ Track performance metrics
   ◦ Generate regular health reports
   ◦ Optimize resource usage

4. Pre-Deployment Validation
   ◦ Verify system performance
   ◦ Check resource utilization
   ◦ Validate monitoring setup
   ◦ Test alert mechanisms

5. Production Monitoring
   ◦ Enable real-time monitoring
   ◦ Configure alert thresholds
   ◦ Set up automated reporting
   ◦ Maintain metrics history

## Project Management Dashboard

### Purpose
The project management dashboard provides real-time visibility into project health, development progress, and critical issues. It serves as a central monitoring tool for project managers to track:

• Project Health Metrics:
  - Overall project status
  - Sprint progress
  - Test coverage
  - Critical issues count

• Development Status:
  - Environment health
  - Build status
  - Dependencies
  - Resource utilization

• Quality Metrics:
  - Test results
  - Code coverage
  - Linting scores
  - Security issues

### Quick Setup Guide

1. Required Directory Structure:
   ```
   project/
   ├── dashboard/          # Dashboard files
   ├── docs/              # Project documentation
   ├── logs/              # System and test logs
   └── config/            # Project configuration
   ```

2. Essential Files:
   • dashboard/index.html: Main dashboard interface
   • scripts/run_dashboard.sh: Dashboard startup script
   • docs/proj_status.md: Project status tracking
   • logs/verify_and_fix.log: Test and error logs

3. Status File Format (proj_status.md):
   ```markdown
   # Project Status Report
   Last Updated: [timestamp]

   ## Current Implementation Status
   - Files updated: [count]
   - Tests updated: [count]

   ## Test Coverage Report
   [coverage data]

   ## Recent Changes
   - [commit messages with test results]
   ```

### Dashboard Features

1. Key Metrics Display:
   • Project Health:
     - Overall health percentage
     - Based on test success rate
     - Resource utilization impact
     - Error rate weighting

   • Sprint Tracking:
     - Current sprint progress
     - Milestone completion rates
     - Team velocity metrics
     - Deadline monitoring

   • Quality Metrics:
     - Test coverage percentage
     - Code quality scores
     - Security scan results
     - Performance benchmarks

   • Issue Management:
     - Critical issues count
     - Priority distribution
     - Team assignments
     - Resolution times

2. Status Indicators:
   • Success (✓):
     - All tests passing
     - Resources within limits
     - No critical issues
     - Dependencies up-to-date

   • Warning (!):
     - Tests partially failing
     - Resource usage high
     - Non-critical issues
     - Updates needed

   • Error (×):
     - Critical test failures
     - Resource exhaustion
     - Security vulnerabilities
     - Build failures

3. Resource Thresholds:
   • CPU Usage:
     - Normal: < 70%
     - Warning: 70-85%
     - Critical: > 85%

   • Memory Usage:
     - Normal: < 75%
     - Warning: 75-90%
     - Critical: > 90%

   • Error Rates:
     - Acceptable: < 5%
     - Warning: 5-10%
     - Critical: > 10%

4. Auto-Refresh:
   • Updates every 2 minutes
   • Real-time data fetching
   • Error-resilient updates
   • Cached fallback data

### Usage Instructions

1. Start Dashboard:
   ```bash
   ./scripts/run_dashboard.sh
   ```

2. Monitor Key Areas:
   • Project Health:
     - Check overall health score
     - Review contributing factors
     - Monitor trend changes
     - Verify resource status

   • Sprint Management:
     - Track milestone progress
     - Review team assignments
     - Monitor deadlines
     - Check velocity metrics

   • Issue Tracking:
     - Address critical issues first
     - Review priority queue
     - Check team workloads
     - Monitor resolution times

   • Quality Control:
     - Verify test coverage
     - Review failed tests
     - Check build status
     - Monitor security scans

3. Respond to Issues:
   • Critical (Response: Immediate)
     - Security vulnerabilities
     - Production blocking bugs
     - Resource exhaustion
     - Build failures

   • High Priority (Response: Same Day)
     - Test failures
     - Performance issues
     - Resource warnings
     - Sprint blockers

   • Medium Priority (Response: This Sprint)
     - Code quality issues
     - Documentation gaps
     - Minor bugs
     - Technical debt

   • Low Priority (Response: Backlog)
     - Feature requests
     - Optimizations
     - Refactoring
     - Nice-to-have fixes

### Dashboard Requirements
1. Initial Setup:
   • Copy core files as specified in Quick Setup
   • Ensure all required logs are properly formatted
   • Configure update intervals (default: 2min)
   • Verify data sources accessibility

2. Monitoring Requirements:
   • Keep dashboard running during development
   • Address test failures immediately
   • Monitor environment health continuously
   • Track resource utilization

3. Data Management:
   • Maintain accurate log formats
   • Update status files regularly
   • Archive historical data
   • Handle missing data gracefully

4. Performance Guidelines:
   • Optimize data fetching
   • Minimize browser resource usage
   • Handle errors gracefully
   • Maintain responsive interface

### For Ongoing Maintenance

1. Continuous Monitoring
   ◦ Track system health
   ◦ Monitor resource usage
   ◦ Generate performance reports
   ◦ Analyze trends

2. Performance Optimization
   ◦ Identify bottlenecks
   ◦ Optimize resource usage
   ◦ Implement improvements
   ◦ Validate changes

3. Regular Maintenance
   ◦ Clean up old metrics
   ◦ Update dashboards
   ◦ Adjust thresholds
   ◦ Review alerts

4. Documentation Updates
   ◦ Update performance docs
   ◦ Record optimizations
   ◦ Document metrics
   ◦ Maintain guides

### GitHub Integration & Version Control

1. Initial Setup:
   ```bash
   # Initialize repository
   git init
   git remote add origin $GITHUB_REPO_URL
   git branch -M main
   ```

2. Configuration:
   ```json
   {
     "github": {
       "repo": "",
       "branch": "main",
       "auto_sync": true,
       "sync_interval": 300
     }
   }
   ```

3. Required Environment Variables:
   ```bash
   GITHUB_TOKEN=your_token
   GITHUB_USERNAME=your_username
   ```

4. Automated Workflows:
   • Commit frequency: Every successful test/build
   • Push triggers: After verify_and_fix.sh completion
   • Pull frequency: Before each build/test cycle
   • Branch strategy: main (protected), develop, feature/*

5. Dashboard Integration:
   • Repository Status:
     - Commit history (last 24h)
     - Branch status
     - PR reviews pending
     - Build status
   • Code Quality:
     - Test coverage
     - Linting status
     - Security scan results
   • Team Metrics:
     - PR velocity
     - Issue resolution time
     - Code review time

6. Security:
   • Token stored in .env (git-ignored)
   • Branch protection rules
   • Required reviews
   • Signed commits
