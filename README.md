# Cellular Automata Simulator
Generalized program for visualizing different cellular automata rules.  Rules are written in RLE format.

# Running the Program
```bash
py simulation.py
```
# Controls
## Keyboard Controls
* C: Clear the World
* N: Randomly Repopulate the World
* E: Export Image to File System
* P: Pause and Unpause Simulation
* ESC: Quit the game and end the simulation

## Drawing Patterns to the World
There may be cases where you want to draw a predefined pattern.  To do this, first pause the simulation by pressing the 'P' key, and then click and drag the mouse.

## Erasing Patterns from the World
There will be instances where you want to remove living tiles from the world.  You may wish to take control of the simulation, or maybe want to erase a stray line from the drawing process.  In either case, make sure the game is paused by pressing the 'P' key.  Erasing is much like drawing, but you will need to hold down the CTRL key as you drag the mouse around the canvas.

## Summary of Mouse Rules
* Click and Drag: Draw
* Click and Drag + CTRL: Erase

# Understanding the Simulated World
Numerous values can be set at the top of the simulation.py file, including those controlling screen size and the grid size.  Regardless of the size of the world, it is always modeled as a taurus.  This means that when a glider goes off the right side it will reappear on the left.  If it disappears on the bottom, it will reappear at the top.

# Specifying Rules
Rules are specified in the standard RLE format.  You can provide a rule at the top of the file in the form "B123/S123."  The first set of numbers represents the conditions under which a dead cell will come to life, that is under what conditions a birth will occur.  In the provided example, a dead cell will come to life if it has one, two, or three living neighbors.  The second set of numbers describes the conditions under which a living cell will survive.  In our example, cells with one, two, or three living neighbors will survive to the next time step.  If you want to play with the possibilities, you can supply the string "random" and the simulation will generate a RLE rule on your behalf.

# Example RLE Rules
Try out some of these patterns
## Replicators
* B1357/S1357
* B147/S4
* B12345/S467
* B146/S147
## Conway's Game of Life
* B3/S23
## Life Without Death
* B3/S012345678
## Ripples
* B1234567/S

# Other Parameters
By changing the flags at the top of the file, users can also change the colors of living and dead cells.  The background color, seen in the borders, can also be customized.  The borders themselves can be turned on and off.  If you want to start with a blank canvas, set the POPULATE flag to False.  And finally, if you want the entire simulation to change colors with each time step, set the STROBE flag to True.  This is not recommended if you suffer epileptic seizures.

# Saving Captures
If you encounter interesting patterns that you wish to save to a .png tile on your local machine, you can hit the 'E' key.  The image will be saved to the same directory that houses the simulation.py file.
