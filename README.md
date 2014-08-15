# jum.py
A sublime plugin that creates dynamic hot keys to jump around files across visible views and windows.

## Unsupported & Unfinished Package
For some reason people are still landing here and starring this package...

Please note that **this package is both unfinished and unsupported**.  I have no immediate plans to continue this.  There was some good code in here that was almost working.  I had to do some extreme hacks to combat sublime's difficult architecture.

If you want to look through the code, you'll have to look through a few branches.  They each have different techniques and different feature sets.  I had jumps working across not just views/panes but windows.  Unfortunately there were threading issues and well lots of other ones too.  Sublime made it very hard to test. 

## Why switch to Atom?
The [Atom](https://atom.io/) package architecture is much more powerful and a lot more flexible.

Feel free to Fork or look for code examples here, but I do suggest everyone check out Atom, it's open source and shaping up very nicely.

Also, if you like Atom check out:
[Jumpy in Atom](https://atom.io/packages/jumpy)

## How to jump
1. Hit <kbd>alt</kbd> + <kbd>space</kbd>
2. Choose from your presented labels:
![screenshot](https://raw.github.com/DavidLGoldberg/jum.py/master/example_jumpy_labels.png)
3. Enter two characters.
4. Keep coding!

## Settings

    {
	// Can be turned off to potentially improve performance or make less confusing.
        "jumpy_use_file_extensions": true,
        
        "jumpy_use_upper_case_labels": false
	}

## Key Bindings
### Defaults
* Enter jump mode (default): <kbd>alt</kbd> + <kbd>space</kbd>
* Reset first character entered: <kbd>backspace</kbd>
* Cancel/exit jump mode (defualt): <kbd>esc</kbd> or <kbd>space</kbd>

### Fix for Vintage + common jj binding
The following line must be placed wherever you have defined your "jj" command:

    { "key": "setting.jumpy_jump_mode", "operand": false }

as shown below:

    { "keys": ["j", "j"], "command": "exit_insert_mode",
		"context":
		[
			{ "key": "setting.jumpy_jump_mode", "operand": false },
			{ "key": "setting.command_mode", "operand": false },
			{ "key": "setting.is_widget", "operand": false }
		]
	}

## Notes
* Works great with or without Vintage
* **Vintage Modes** supported
  * command mode
  * insert mode
  * visual mode (sorry cancels select at the moment)

## TODO
* Remove unreachable highlights after first character hit (to reduce noise).
* Refer to the issues section for minor details.
