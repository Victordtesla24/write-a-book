#!/bin/bash

# Backup the original .zshrc file
sudo cp ~/.zshrc ~/.zshrc.backup

# Change ownership of .zshrc to your user
sudo chown $USER:$(id -gn) ~/.zshrc

# Add the PATH modification to .zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' | sudo tee -a ~/.zshrc

# Set correct permissions
sudo chmod 644 ~/.zshrc

# Display the changes
echo "The following line has been added to your .zshrc file:"
tail -n 1 ~/.zshrc

echo "Your original .zshrc has been backed up to ~/.zshrc.backup"
echo "Please run 'source ~/.zshrc' to apply the changes"
