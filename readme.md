# PY GAME ZERO PLATFORMER

Simple pgzero platformer demo.

## To run

```shell
pgzrun main.py
```

## To test/debug

Run watch_pgzero.py. The game will launch. Any changes made to the py files will make de game relaunch automatically.

Changing DEBUG to 1 in settings.txt will show debug informations on screen, and enable more keys:

| key | action | description |
| --- | ------ | ----------- |
| TAB | Toggle debug info | Toggle on-screen debug information |
| SPACE | Advance frame | While paused (P), pressing SPACE will advance one frame. Actions can be performed even when paused |
| ARROWS | Move camera | Move camera freely. Will place the player in the center of camera |