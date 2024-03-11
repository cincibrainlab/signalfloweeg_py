# This is a simple "Hello World" script written in Julia.
# To use this script in VS Code, follow these steps:
# 1. Ensure you have Julia installed on your system. You can download it from https://julialang.org/downloads/
# 2. Install the Julia extension for VS Code from the marketplace. This will provide syntax highlighting and other useful features for Julia.
# 3. Save this script with a ".jl" extension, for example, "hello_world.jl".
# 4. Open a terminal in VS Code (Terminal > New Terminal).
# 5. Navigate to the directory where you saved the script.
# 6. Type `julia hello_world.jl` and press Enter to run the script.
using Crayons

# A more complex "Hello World" demonstration in Julia
# This script will greet the world and then perform a simple calculation
import Pkg; Pkg.add("Crayons")
# Greeting the world
println("Hello World, Julia")

# Performing a simple calculation
a = 5
b = 7
sum = a + b
println("The sum of ", a, " and ", b, " is ", sum)
# End of Selection

using Base: sleep

function animate_greeting()
    for i in 1:1
        print("\rHello World, Julia - Animation Step: $i")
        sleep(0.5) # Wait for 0.5 seconds
    end
    println("\nAnimation Complete!")
end

animate_greeting()

# Function to demonstrate printing in multiple colors
function demo_multiple_colors()
    # Create a Crayon object with the color red
    red_crayon = Crayon(foreground=:red)

    # Apply the red Crayon to the string
    println(red_crayon("ghg"))
    
    using Crayons.Box
    print(GREEN_FG, "This is in green")
    print(BOLD, GREEN_FG, BLUE_BG, "Bold green on blue")
end

# Call the function to demonstrate the colored output
demo_multiple_colors()

