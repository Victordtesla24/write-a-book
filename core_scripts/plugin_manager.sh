#!/bin/zsh

# Plugin manager script
# Follows agent_directives.md for plugin management and extensibility

set -e

# Load core scripts
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
source "${SCRIPT_DIR}/config_manager.sh"

# Plugin directory
PLUGIN_DIR="${CONFIG[project_root]}/plugins"

# Plugin registry
typeset -A PLUGINS
typeset -A PLUGIN_HOOKS

# Function to initialize plugin system
init_plugins() {
    local log_file="$1"
    
    # Create plugin directory if it doesn't exist
    mkdir -p "${PLUGIN_DIR}"
    
    # Create plugin registry file if it doesn't exist
    local registry_file="${PLUGIN_DIR}/registry.txt"
    touch "${registry_file}"
    
    # Load registered plugins
    while IFS=':' read -r name version; do
        if [[ -n "${name}" ]]; then
            PLUGINS[$name]="${version}"
        fi
    done < "${registry_file}"
    
    # Log initialization
    {
        echo "Plugin system initialized at: $(date)"
        echo "Registered plugins: ${#PLUGINS[@]}"
    } >> "${log_file}"
}

# Function to register a plugin
register_plugin() {
    local name="$1"
    local version="$2"
    local entry_point="$3"
    local log_file="$4"
    
    # Validate plugin
    if [[ -z "${name}" ]] || [[ -z "${version}" ]] || [[ -z "${entry_point}" ]]; then
        echo "Error: Missing required plugin information"
        return 1
    fi
    
    # Check if plugin directory exists
    local plugin_dir="${PLUGIN_DIR}/${name}"
    if [[ ! -d "${plugin_dir}" ]]; then
        mkdir -p "${plugin_dir}"
    fi
    
    # Copy entry point script
    if [[ -f "${entry_point}" ]]; then
        cp "${entry_point}" "${plugin_dir}/main.sh"
        chmod 755 "${plugin_dir}/main.sh"
    else
        echo "Error: Plugin entry point not found: ${entry_point}"
        return 1
    fi
    
    # Update registry
    PLUGINS[$name]="${version}"
    local registry_file="${PLUGIN_DIR}/registry.txt"
    echo "${name}:${version}" >> "${registry_file}"
    
    # Log registration
    {
        echo "Plugin registered at: $(date)"
        echo "Name: ${name}"
        echo "Version: ${version}"
        echo "Entry point: ${entry_point}"
    } >> "${log_file}"
    
    return 0
}

# Function to load a plugin
load_plugin() {
    local name="$1"
    local log_file="$2"
    
    # Check if plugin exists
    if [[ -z "${PLUGINS[$name]}" ]]; then
        echo "Error: Plugin not found: ${name}"
        return 1
    fi
    
    # Check if plugin is already loaded
    if [[ -n "${PLUGIN_HOOKS[$name]}" ]]; then
        return 0
    fi
    
    # Load plugin
    local plugin_script="${PLUGIN_DIR}/${name}/main.sh"
    if [[ -f "${plugin_script}" ]]; then
        source "${plugin_script}"
        PLUGIN_HOOKS[$name]="loaded"
        
        # Log loading
        {
            echo "Plugin loaded at: $(date)"
            echo "Name: ${name}"
            echo "Version: ${PLUGINS[$name]}"
        } >> "${log_file}"
        
        return 0
    else
        echo "Error: Plugin script not found: ${plugin_script}"
        return 1
    fi
}

# Function to unload a plugin
unload_plugin() {
    local name="$1"
    local log_file="$2"
    
    # Check if plugin exists and is loaded
    if [[ -z "${PLUGIN_HOOKS[$name]}" ]]; then
        return 0
    fi
    
    # Unload plugin
    unset PLUGIN_HOOKS[$name]
    
    # Log unloading
    {
        echo "Plugin unloaded at: $(date)"
        echo "Name: ${name}"
        echo "Version: ${PLUGINS[$name]}"
    } >> "${log_file}"
    
    return 0
}

# Function to list plugins
list_plugins() {
    local log_file="$1"
    
    # Print header
    echo "Registered plugins:"
    echo "-----------------"
    
    # List all plugins
    for name in "${(k)PLUGINS[@]}"; do
        local status="unloaded"
        if [[ -n "${PLUGIN_HOOKS[$name]}" ]]; then
            status="loaded"
        fi
        echo "${name} (${PLUGINS[$name]}) - ${status}"
    done
    
    # Log listing
    {
        echo "Plugin list generated at: $(date)"
        echo "Total plugins: ${#PLUGINS[@]}"
        echo "Loaded plugins: ${#PLUGIN_HOOKS[@]}"
    } >> "${log_file}"
}

# Function to validate plugin
validate_plugin() {
    local name="$1"
    local version="$2"
    local entry_point="$3"
    
    # Check required fields
    if [[ -z "${name}" ]] || [[ -z "${version}" ]] || [[ -z "${entry_point}" ]]; then
        return 1
    fi
    
    # Check version format (semver)
    if ! [[ "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 1
    fi
    
    # Check entry point exists and is executable
    if [[ ! -f "${entry_point}" ]] || [[ ! -x "${entry_point}" ]]; then
        return 1
    fi
    
    return 0
}

# Export functions
functions[init_plugins]=$functions[init_plugins]
functions[register_plugin]=$functions[register_plugin]
functions[load_plugin]=$functions[load_plugin]
functions[unload_plugin]=$functions[unload_plugin]
functions[list_plugins]=$functions[list_plugins]
functions[validate_plugin]=$functions[validate_plugin] 