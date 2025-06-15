# PY GAME ZERO PLATFORMER

A Pygame Zero platformer demo with a smart map generator built from scratch.

## Requirements

```txt
python
pgzero
pygame (for Rect class)
```

## To run

```shell
pgzrun main.py
```

## Controls

```shell
A/D = Moves horizontally
W = Jumps
ESC = Pauses
Enter/Space = Can be used in menus instead of mouse to play, retry or continue
```

## To test/debug

Run watch_pgzero.py. The game will launch. Any changes made to the py files will make de game relaunch automatically.

Changing DEBUG to 1 in settings.txt will show debug informations on screen, and enable more keys:

| key | action | description |
| --- | ------ | ----------- |
| TAB | Toggle debug info | Toggle on-screen debug information |
| P | Pause frame | Pauses frame. Still captures input, does not show menu and enables frame by frame.
| SPACE | Advance frame | While paused (P), pressing SPACE will advance one frame. Actions can be performed even when paused |
| ARROWS | Move camera | Move camera freely. Will place the player in the center of camera |

### Settings file

In the settings.txt, you can set DEBUG to 1 to use these functions. Aditionally, resolution, default font and window title can be set. Note that if title is different from the provided one, watch_pgzero will not detect window changes.

## Generating maps

The code automatically generates level based on txt information.

To create a level, create a folder numbered 1..n in level_data. Be aware that if a number is skipped in the folder numbering, the level will be ignored.

Each level needs 3 files:

```txt
background.txt = Needs 5 backgrounds tiles to form the background, from top to bottom, separated by line break. Each tile will be parallaxing horizontally from weaker to stronger, so all must be loop-ready

layout.txt = The layout of the map. Instruction will be given below.

tiles.txt = must contain terrain, single_block and hazard paths along with the start of tile names.
    terrain must contain the start of the tile name up until the underscore before the positioning indicator. The folder must have the tiles for each direction (top, left, top-left, etc).
    eg.: if you have 'sprites/tiles/terrain_dirt_block_top', '../terrain_dirt_block_bottom_left', etc, the terrain must be 'sprites/tiles/terrain_dirt_block_'.
    single_block = same as the terrain, but for tiles that uses only one tile vertically (i.e. bottom and top are in the same sprite).
    hazard = the tile for the hazard (instant kill), if used.
    The file also contains decorations, in the format of symbol = filename, symbol being whichever symbol you will use to represent it in the layout.txt.
```

For the music, place the music named stage_{level_number} in /music/. If no music is provided, the music from stage 1 will be used.

### Map Layout

The layout.txt file represents a drawing of the map layout. Each symbol tells the program what to do. Here follows the default symbols:

|Symbol|Representation|
|------|--------------|
|   =  | Hard terrain, like floors, walls and ceilings. The code will decide the best suited tile from the given tiles in tiles.txt, based on neighboring symbols|
| p    | Player spawn point. Will always start facing right. Ideally, place at least 6 spaces alway from any side for proper camera alignment. |
| f    | Exit point, where the level ends
| !    | Hazard defined in tiles.txt. If the player touches it, dies instantly |
|1, 2, 3| Enemy spawn point. 1 represents the jumper type, 2 represents the walker type and 3 represents the shooter type. Will always spawn facing left. |

Any other symbol for decoration you wish to use, place it in tiles.txt along with it's tile/sprite.

If a symbol is not present in tiles.txt and not in this list, it will be ignored. In the files from this project, the dash (-) represents a empty space, but is being ignored by the code.


## Disclaimer

This is a non-commerical, non-profit, personal project.

Most images and sound effects used are from [Kenney](https://kenney.nl), with some images being altered slighty.

Musics from [Sekuora in pixabay](https://pixabay.com/users/sekuora-40269569/).

Font from [GraphicSauce in 1001fonts](https://www.1001fonts.com/users/graphicsauceco/).

Pygame Zero framework made by [Daniel Pope](https://pygame-zero.readthedocs.io/en/stable/index.html)

All credits goes to the authors.