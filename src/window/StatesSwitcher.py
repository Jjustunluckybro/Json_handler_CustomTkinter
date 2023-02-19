import customtkinter
import logging


class State:

    def __init__(self, master: customtkinter.CTkBaseClass):
        self.master = master

    def set_state(self):
        raise NotImplementedError

    def remove_state(self):
        raise NotImplementedError


class StateSwitcher:

    def __init__(self, states: dict[str: State], start_state: str):
        """
        :param states: dict with states str name and states objects (Obj should be inited)
        :param start_state: state which will be started when switcher init
        """

        self.logger = logging.getLogger(f"app.main_window.state_switcher")
        self._states = states
        self.is_state_in_states(start_state)
        self._current_state = start_state
        self._set_start_state(start_state)

        self.logger.debug(f"State switcher was init with states: {self._states} | Current state: {self._current_state}")

    def _set_start_state(self, start_state: str) -> None:
        self.is_state_in_states(start_state)
        state_to_set = self._states[start_state]
        state_to_set.set_state()

    def set_new_state(self, new_state: str) -> None:
        """Set new state and remove state was current"""
        current_state: State
        self.logger.debug(f"Try to set new state: '{new_state}', instead: '{self._current_state}'")

        self.is_state_in_states(new_state)

        current_state = self._states[self._current_state]
        current_state.remove_state()

        self._current_state = new_state
        state_to_set: State = self._states[self._current_state]
        state_to_set.set_state()

    def is_state_in_states(self, state: str) -> None:
        """Check is obj has state with this name and rise exception if not"""
        if state not in self._states:
            self.logger.error(f"Not found {state} in available states")
            raise Exception  # TODO: Custom exception
        self.logger.debug(f"Found state {state} in available states")

    def get_current_state_name(self) -> str:
        return self._current_state

    def get_current_state(self):
        """Return current state obj"""
        return self._states[self._current_state]
