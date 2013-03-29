from sublime import set_timeout
from functools import partial


def do_when(conditional, callback, interval=50, *args, **kwargs):
    """Executes a callback when a condition is met.
    The conditional is run at the supplied polling interval.

    Keyword arguments:
    conditional -- Lambda that tests when ready to call the callback.
    callback -- Lambda callback to be callled when condition is met.
    interval -- The interval to poll with in milliseconds.
    Defaults to 50 milliseconds.

    """
    if conditional():
        return callback(*args, **kwargs)
    set_timeout(partial(do_when, conditional, callback, *args, **kwargs),
        interval)

    # Example usage:
    # do_when(lambda: not self.active_view().is_loading(),
    # 	lambda: self.active_view().set_viewport_position(position, False))
