﻿# copied from https://stackoverflow.com/a/43667367/1193986
#
# (c) umichscoots 2017
# License unsepcified. Assumed to be CC-by-sa as is StackOverflow's policy
#
# The class LocalProxy is taken from the werkzeug project
# https://raw.githubusercontent.com/pallets/werkzeug/ef545f0d0bf28cbad02066b4cb7471bea50a93ee/src/werkzeug/local.py
# It is licensed under the BSD-3-Clause License
#
# I guess that means the result is CC-by-SA

import threading
import sys
import Python_pb2

from typing import Any
from typing import Optional
from typing import Union

# Save all of the objects for use later.
orig_stdout = sys.stdout
orig_stderr = sys.stderr
thread_proxies = {}

class StdoutFowarder():

    def __init__(self, token, responseQueue):
        self.token = token
        self.responseQueue = responseQueue

    def write(self,msg):
        # We route output to a queue regardless of whether we are collecting output in a stringIO. 
        # The main entrypoint method will iterate through the queue and yield each of the responses to the grpc caller. 
        # Grpc will send the responses back to the client where they can be read using an AsyncServerStreamingCall.
        # This stream can be read and the responses can be forwarded to all consumers such as the sequencer Python log stream
        self.responseQueue.add_response(Python_pb2.PythonResponse(token=self.token, output=msg))
        
    def flush(self):
        pass # flush has no function on redirected output stream

class LocalProxy:
    """Acts as a proxy for a werkzeug local.  Forwards all operations to
    a proxied object.  The only operations not supported for forwarding
    are right handed operands and any kind of assignment.
    Example usage::
        from werkzeug.local import Local
        l = Local()
        # these are proxies
        request = l('request')
        user = l('user')
        from werkzeug.local import LocalStack
        _response_local = LocalStack()
        # this is a proxy
        response = _response_local()
    Whenever something is bound to l.user / l.request the proxy objects
    will forward all operations.  If no object is bound a :exc:`RuntimeError`
    will be raised.
    To create proxies to :class:`Local` or :class:`LocalStack` objects,
    call the object as shown above.  If you want to have a proxy to an
    object looked up by a function, you can (as of Werkzeug 0.6.1) pass
    a function to the :class:`LocalProxy` constructor::
        session = LocalProxy(lambda: get_current_request().session)
    .. versionchanged:: 0.6.1
       The class can be instantiated with a callable as well now.
    """

    __slots__ = ("__local", "__dict__", "__name__", "__wrapped__")

    def __init__(
        self, local: Union[Any, "LocalProxy", "LocalStack"], name: Optional[str] = None,
    ) -> None:
        object.__setattr__(self, "_LocalProxy__local", local)
        object.__setattr__(self, "__name__", name)
        if callable(local) and not hasattr(local, "__release_local__"):
            # "local" is a callable that is not an instance of Local or
            # LocalManager: mark it as a wrapped function.
            object.__setattr__(self, "__wrapped__", local)

    def _get_current_object(self,) -> object:
        """Return the current object.  This is useful if you want the real
        object behind the proxy at a time for performance reasons or because
        you want to pass the object into a different context.
        """
        if not hasattr(self.__local, "__release_local__"):
            return self.__local()
        try:
            return getattr(self.__local, self.__name__)
        except AttributeError:
            raise RuntimeError(f"no object bound to {self.__name__}")

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:
            raise AttributeError("__dict__")

    def __repr__(self) -> str:
        try:
            obj = self._get_current_object()
        except RuntimeError:
            return f"<{type(self).__name__} unbound>"
        return repr(obj)

    def __bool__(self) -> bool:
        try:
            return bool(self._get_current_object())
        except RuntimeError:
            return False

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:
            return []

    def __getattr__(self, name: str) -> Any:
        if name == "__members__":
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._get_current_object()[key] = value  # type: ignore

    def __delitem__(self, key):
        del self._get_current_object()[key]

    __setattr__ = lambda x, n, v: setattr(x._get_current_object(), n, v)  # type: ignore
    __delattr__ = lambda x, n: delattr(x._get_current_object(), n)  # type: ignore
    __str__ = lambda x: str(x._get_current_object())  # type: ignore
    __lt__ = lambda x, o: x._get_current_object() < o
    __le__ = lambda x, o: x._get_current_object() <= o
    __eq__ = lambda x, o: x._get_current_object() == o  # type: ignore
    __ne__ = lambda x, o: x._get_current_object() != o  # type: ignore
    __gt__ = lambda x, o: x._get_current_object() > o
    __ge__ = lambda x, o: x._get_current_object() >= o
    __hash__ = lambda x: hash(x._get_current_object())  # type: ignore
    __call__ = lambda x, *a, **kw: x._get_current_object()(*a, **kw)
    __len__ = lambda x: len(x._get_current_object())
    __getitem__ = lambda x, i: x._get_current_object()[i]
    __iter__ = lambda x: iter(x._get_current_object())
    __contains__ = lambda x, i: i in x._get_current_object()
    __add__ = lambda x, o: x._get_current_object() + o
    __sub__ = lambda x, o: x._get_current_object() - o
    __mul__ = lambda x, o: x._get_current_object() * o
    __floordiv__ = lambda x, o: x._get_current_object() // o
    __mod__ = lambda x, o: x._get_current_object() % o
    __divmod__ = lambda x, o: x._get_current_object().__divmod__(o)
    __pow__ = lambda x, o: x._get_current_object() ** o
    __lshift__ = lambda x, o: x._get_current_object() << o
    __rshift__ = lambda x, o: x._get_current_object() >> o
    __and__ = lambda x, o: x._get_current_object() & o
    __xor__ = lambda x, o: x._get_current_object() ^ o
    __or__ = lambda x, o: x._get_current_object() | o
    __div__ = lambda x, o: x._get_current_object().__div__(o)
    __truediv__ = lambda x, o: x._get_current_object().__truediv__(o)
    __neg__ = lambda x: -(x._get_current_object())
    __pos__ = lambda x: +(x._get_current_object())
    __abs__ = lambda x: abs(x._get_current_object())
    __invert__ = lambda x: ~(x._get_current_object())
    __complex__ = lambda x: complex(x._get_current_object())
    __int__ = lambda x: int(x._get_current_object())
    __long__ = lambda x: long(x._get_current_object())  # type: ignore # noqa
    __float__ = lambda x: float(x._get_current_object())
    __oct__ = lambda x: oct(x._get_current_object())
    __hex__ = lambda x: hex(x._get_current_object())
    __index__ = lambda x: x._get_current_object().__index__()
    __coerce__ = lambda x, o: x._get_current_object().__coerce__(x, o)
    __enter__ = lambda x: x._get_current_object().__enter__()
    __exit__ = lambda x, *a, **kw: x._get_current_object().__exit__(*a, **kw)
    __radd__ = lambda x, o: o + x._get_current_object()
    __rsub__ = lambda x, o: o - x._get_current_object()
    __rmul__ = lambda x, o: o * x._get_current_object()
    __rdiv__ = lambda x, o: o / x._get_current_object()
    __rtruediv__ = __rdiv__
    __rfloordiv__ = lambda x, o: o // x._get_current_object()
    __rmod__ = lambda x, o: o % x._get_current_object()
    __rdivmod__ = lambda x, o: x._get_current_object().__rdivmod__(o)
    __copy__ = lambda x: copy.copy(x._get_current_object())
    __deepcopy__ = lambda x, memo: copy.deepcopy(x._get_current_object(), memo)


def redirect(token, client):
    """
    Enables the redirect for the current thread's output
    object and returns the object.

    :return: The StdoutForwarder object.
    :rtype: ``StdoutForwarder``
    """
    # Get the current thread's identity.
    ident = threading.currentThread().ident

    # Enable the redirect and return the cStringIO object.
    thread_proxies[ident] = StdoutFowarder(token, client)
    return thread_proxies[ident]

def stop_redirect():
    """
    Disables the redirect for the current thread's output
    """
    # Get the current thread's identity.
    ident = threading.currentThread().ident

    # Only act on proxied threads.
    if ident not in thread_proxies:
        return

    # delete the proxy.
    del thread_proxies[ident]

def _get_stream(original):
    """
    Returns the inner function for use in the LocalProxy object.

    :param original: The stream to be returned if thread is not proxied.
    :type original: ``file``
    :return: The inner function for use in the LocalProxy object.
    :rtype: ``function``
    """
    def proxy():
        """
        Returns the original stream if the current thread is not proxied,
        otherwise we return the proxied item.

        :return: The stream object for the current thread.
        :rtype: ``file``
        """
        # Get the current thread's identity.
        ident = threading.currentThread().ident

        # Return the proxy, otherwise return the original.
        return thread_proxies.get(ident, original)

    # Return the inner function.
    return proxy


def enable_proxy():
    """
    Overwrites stdout, and stderr with the proxied
    objects.
    """
    sys.stdout = LocalProxy(_get_stream(sys.stdout))
    sys.stderr = LocalProxy(_get_stream(sys.stderr))

def disable_proxy():
    """
    Overwrites stdout and stderr with the original
    objects.
    """
    sys.stdout = orig_stdout
    sys.stderr = orig_stderr