import time
from unittest import TestCase
from buttons import State, Button
__author__ = 'lars'

TIME_MARGIN = 0.2


def greater_than(timeout):
	return timeout + TIME_MARGIN


def lower_than(timeout):
	return timeout + TIME_MARGIN


class Event(object):

	"""
	Define states
	"""

	def __init__(self):
		self.action = None

	def push(self):
		self.action = State.PUSH

	def hold(self):
		self.action = State.HOLD

	def release(self):
		self.action = State.RELEASE


class TestButton(TestCase):

	"""
	Test buttons for each state
	"""

	# run before each test
	def setUp(self):

		self.event = Event()
		self.button = Button(push=self.event.push, hold=self.event.hold, release=self.event.release)

	def tearDown(self):
		"""
		Prevents further evaluation in timer thread by setting state to RELEASE (initial state)
		"""

		self.button.state = State.RELEASE

	def test_from_init_to_push(self):

		"""
		Check transition from INIT to PUSH.

		Trigger action for PUSH.
		"""

		self.button.set_state_push()
		self.assertEqual(self.button.state, State.PUSH)
		self.assertEqual(self.event.action, State.PUSH)

	def test_from_init_to_hold(self):

		"""
		Check transition from INIT to HOLD.

		No action expected.
		"""

		self.button.set_state_hold()
		self.assertEqual(self.button.state, State.HOLD)
		self.assertIsNone(self.event.action)

	def test_from_init_to_release(self):

		"""
		Check transition from INIT to RELEASE.

		No action expected.
		"""

		self.button.set_state_release()
		self.assertEqual(self.button.state, State.RELEASE)
		self.assertIsNone(self.event.action)

	def test_from_push_to_push(self):

		"""
		Check transition from PUSH to PUSH.

		This might happen if signals get lost, etc, hence no action expected?
		"""

		self.button.state = State.PUSH
		self.button.set_state_push()
		self.assertEqual(self.button.state, State.PUSH)
		self.assertIsNone(self.event.action)

	def test_from_push_to_hold(self):

		"""
		Check transition from PUSH to HOLD.

		trigger action for HOLD.
		"""

		self.button.state = State.PUSH
		self.button.set_state_hold()
		self.assertEqual(self.button.state, State.HOLD)
		self.assertEqual(self.event.action, State.HOLD)

	def test_from_push_to_release(self):

		"""
		Check transition from PUSH to RELEASE.

		trigger action for RELEASE.
		"""

		self.button.state = State.PUSH
		self.button.set_state_release()
		self.assertEqual(self.button.state, State.RELEASE)
		self.assertEqual(self.event.action, State.RELEASE)

	def test_from_hold_to_push(self):

		"""
		Check transition from HOLD to PUSH.

		This might happen if signals get lost, etc, hence no action is expected?
		"""

		self.button.state = State.HOLD
		self.button.set_state_push()
		self.assertEqual(self.button.state, State.PUSH)
		self.assertIsNone(self.event.action)

	def test_from_hold_to_hold(self):

		"""
		Check transition from HOLD to HOLD.

		This might happen if a button broadcasting state itself on the IBUS, hence
		action for HOLD is expected.
		"""

		self.button.state = State.HOLD
		self.button.set_state_hold()
		self.assertEqual(self.button.state, State.HOLD)
		self.assertEqual(self.event.action, State.HOLD)

	def test_from_hold_to_release(self):

		"""
		Check transition from HOLD to RELEASE.

		No action is expected - since we have executed an action for HOLD.
		"""

		self.button.state = State.HOLD
		self.button.set_state_release()
		self.assertEqual(self.button.state, State.RELEASE)
		self.assertIsNone(self.event.action)

	def test_from_release_to_push(self):

		"""
		Check transition from RELEASE to PUSH.

		This is the most common case - execute action for PUSH.
		"""

		self.button.state = State.RELEASE
		self.button.set_state_push()
		self.assertEqual(self.button.state, State.PUSH)
		self.assertEqual(self.event.action, State.PUSH)

	def test_from_release_to_hold(self):

		"""
		Check transition from RELEASE to HOLD.

		This might occur if signal for PUSH is lost, but receiving state HOLD
		from the IBUS.

		This is an error-state, hence no action shall be executed.
		"""

		self.button.state = State.RELEASE
		self.button.set_state_hold()
		self.assertEqual(self.button.state, State.HOLD)
		self.assertIsNone(self.event.action)

	def test_from_release_to_release(self):

		"""
		Check transition from RELEASE to RELEASE.

		This is an error-state, and might occur if signal is lost, etc.

		no action is expected.
		"""

		self.button.state = State.RELEASE
		self.button.set_state_release()
		self.assertEqual(self.button.state, State.RELEASE)
		self.assertIsNone(self.event.action)

# TODO: test states without functions bound to each state