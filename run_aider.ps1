# Continuously runs aider with COMMANDS.txt until Exc is pressed

Write-Host "Running aider in a loop. Press Esc to exit..."

while ($true) {
    # Run aider with COMMANDS.txt
    aider --load COMMANDS.txt
    
    # Check if Esc key was pressed
    if ($Host.UI.RawUI.KeyAvailable -and ($Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode -eq 27)) {
        Write-Host "`nExiting..."
        break
    }
}
