#!/bin/zsh

# Project customizer script
# Follows agent_directives.md for project customization

set -e

# Load core scripts
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
source "${SCRIPT_DIR}/config_manager.sh"
source "${SCRIPT_DIR}/resource_manager.sh"

# Custom settings file
CUSTOM_SETTINGS="${CONFIG[project_root]}/config/custom_settings.conf"

# Function to initialize customization
init_customization() {
    local log_file="$1"
    
    # Create custom settings file if it doesn't exist
    if [[ ! -f "${CUSTOM_SETTINGS}" ]]; then
        {
            echo "# Project customization settings"
            echo "# Generated at: $(date)"
            echo
            echo "# Project structure"
            echo "custom_src_dir=src"
            echo "custom_test_dir=tests"
            echo "custom_docs_dir=docs"
            echo
            echo "# Build settings"
            echo "custom_build_tool=make"
            echo "custom_build_target=all"
            echo
            echo "# Test settings"
            echo "custom_test_framework=pytest"
            echo "custom_test_pattern=test_*.py"
            echo
            echo "# Documentation settings"
            echo "custom_doc_tool=sphinx"
            echo "custom_doc_source=docs/source"
            echo "custom_doc_build=docs/build"
            echo
            echo "# Deployment settings"
            echo "custom_deploy_method=local"
            echo "custom_deploy_target=/opt/app"
        } > "${CUSTOM_SETTINGS}"
        
        # Protect settings file
        protect_files "${CUSTOM_SETTINGS}"
    fi
    
    # Log initialization
    {
        echo "Project customization initialized at: $(date)"
        echo "Custom settings file: ${CUSTOM_SETTINGS}"
    } >> "${log_file}"
}

# Function to load custom settings
load_custom_settings() {
    local log_file="$1"
    typeset -g -A CUSTOM_CONFIG
    
    if [[ -f "${CUSTOM_SETTINGS}" ]]; then
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "${key}" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${key}" ]] && continue
            
            # Trim whitespace
            key=$(echo "${key}" | xargs)
            value=$(echo "${value}" | xargs)
            
            # Store in custom configuration
            CUSTOM_CONFIG[$key]="${value}"
        done < "${CUSTOM_SETTINGS}"
        
        # Log loading
        {
            echo "Custom settings loaded at: $(date)"
            echo "Total settings: ${#CUSTOM_CONFIG[@]}"
        } >> "${log_file}"
    else
        echo "Error: Custom settings file not found"
        return 1
    fi
}

# Function to get custom setting
get_custom_setting() {
    local key="$1"
    local default_value="$2"
    
    if [[ -n "${CUSTOM_CONFIG[$key]}" ]]; then
        echo "${CUSTOM_CONFIG[$key]}"
    elif [[ -n "${default_value}" ]]; then
        echo "${default_value}"
    else
        return 1
    fi
}

# Function to set custom setting
set_custom_setting() {
    local key="$1"
    local value="$2"
    local log_file="$3"
    
    # Update custom configuration
    CUSTOM_CONFIG[$key]="${value}"
    
    # Update settings file
    local temp_file
    temp_file=$(mktemp)
    
    # Preserve comments and format
    while IFS= read -r line; do
        if [[ "${line}" =~ ^[[:space:]]*${key}= ]]; then
            echo "${key}=${value}"
        else
            echo "${line}"
        fi
    done < "${CUSTOM_SETTINGS}" > "${temp_file}"
    
    mv "${temp_file}" "${CUSTOM_SETTINGS}"
    
    # Protect settings file
    protect_files "${CUSTOM_SETTINGS}"
    
    # Log update
    {
        echo "Custom setting updated at: $(date)"
        echo "Key: ${key}"
        echo "Value: ${value}"
    } >> "${log_file}"
}

# Function to apply customizations
apply_customizations() {
    local log_file="$1"
    
    # Load custom settings
    load_custom_settings "${log_file}" || return 1
    
    # Create custom directories
    local src_dir
    local test_dir
    local docs_dir
    src_dir=$(get_custom_setting "custom_src_dir" "src")
    test_dir=$(get_custom_setting "custom_test_dir" "tests")
    docs_dir=$(get_custom_setting "custom_docs_dir" "docs")
    
    mkdir -p "${CONFIG[project_root]}/${src_dir}"
    mkdir -p "${CONFIG[project_root]}/${test_dir}"
    mkdir -p "${CONFIG[project_root]}/${docs_dir}"
    
    # Set up documentation
    local doc_tool
    local doc_source
    local doc_build
    doc_tool=$(get_custom_setting "custom_doc_tool" "sphinx")
    doc_source=$(get_custom_setting "custom_doc_source" "docs/source")
    doc_build=$(get_custom_setting "custom_doc_build" "docs/build")
    
    if [[ "${doc_tool}" == "sphinx" ]]; then
        mkdir -p "${CONFIG[project_root]}/${doc_source}"
        mkdir -p "${CONFIG[project_root]}/${doc_build}"
    fi
    
    # Log customization
    {
        echo "Project customizations applied at: $(date)"
        echo "Source directory: ${src_dir}"
        echo "Test directory: ${test_dir}"
        echo "Documentation directory: ${docs_dir}"
        echo "Documentation tool: ${doc_tool}"
    } >> "${log_file}"
}

# Function to validate customizations
validate_customizations() {
    local log_file="$1"
    local errors=0
    
    # Load custom settings
    load_custom_settings "${log_file}" || return 1
    
    # Validate directories
    local src_dir
    local test_dir
    local docs_dir
    src_dir=$(get_custom_setting "custom_src_dir")
    test_dir=$(get_custom_setting "custom_test_dir")
    docs_dir=$(get_custom_setting "custom_docs_dir")
    
    for dir in "${src_dir}" "${test_dir}" "${docs_dir}"; do
        if [[ ! -d "${CONFIG[project_root]}/${dir}" ]]; then
            echo "Error: Directory not found: ${dir}"
            errors=$((errors + 1))
        fi
    done
    
    # Validate build settings
    local build_tool
    build_tool=$(get_custom_setting "custom_build_tool")
    if ! command -v "${build_tool}" >/dev/null 2>&1; then
        echo "Error: Build tool not found: ${build_tool}"
        errors=$((errors + 1))
    fi
    
    # Validate test settings
    local test_framework
    test_framework=$(get_custom_setting "custom_test_framework")
    if ! command -v "${test_framework}" >/dev/null 2>&1; then
        echo "Error: Test framework not found: ${test_framework}"
        errors=$((errors + 1))
    fi
    
    # Log validation
    {
        echo "Project customization validation at: $(date)"
        echo "Total errors: ${errors}"
    } >> "${log_file}"
    
    return "${errors}"
}

# Export functions
functions[init_customization]=$functions[init_customization]
functions[load_custom_settings]=$functions[load_custom_settings]
functions[get_custom_setting]=$functions[get_custom_setting]
functions[set_custom_setting]=$functions[set_custom_setting]
functions[apply_customizations]=$functions[apply_customizations]
functions[validate_customizations]=$functions[validate_customizations] 