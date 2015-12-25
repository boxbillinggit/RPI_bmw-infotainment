from unittest import TestCase
import xml.etree.ElementTree as ElementTree
import signaldb

__author__ = 'lars'


class SignalDB(object):

	"""
	Mock-up for signal-database during test.
	"""

	def __init__(self):

		xmldb = """<?xml version="1.0" encoding="UTF-8"?>
		<IBUS>
			<MESSAGE>

				<DEVICES>
					<byte val="0x00" id="IBUS_DEV">Device description</byte>
					<byte val="0x02" id="IBUS_DEV_MULTIPLE">Double references</byte>
					<byte val="0x03" id="IBUS_DEV_MULTIPLE">Double references</byte>
				</DEVICES>

				<DATA>
					<OPERATIONS>
						<byte val="0x02" id="IBUS_MSG_OPERATION">Operation description</byte>
						<byte val="0x02" id="IBUS_MSG_OPERATION_MULTIPLE">Double references</byte>
						<byte val="0x03" id="IBUS_MSG_OPERATION_MULTIPLE">Double references</byte>
					</OPERATIONS>

					<CATEGORY ref="IBUS_MSG_OPERATION">
						<byte val="0x04" id="button.push"/>
						<byte val="0x05" id="button.hold"/>
						<byte val="0x06" id="button.release"/>
					</CATEGORY>

					<CATEGORY ref="IBUS_MSG_NO_OPERATION_REF">
						<byte val="0x07" id="button-unknown-operation-ref.push"/>
						<byte val="0x08" id="button-unknown-operation-ref.hold"/>
						<byte val="0x09" id="button-unknown-operation-ref.release"/>
					</CATEGORY>

					<CATEGORY ref="IBUS_MSG_OPERATION_MULTIPLE">
						<byte val="0x04" id="button-multiple-refereed.push"/>
						<byte val="0x05" id="button-multiple-refereed.hold"/>
						<byte val="0x06" id="button-multiple-refereed.release"/>
					</CATEGORY>

					<CATEGORY ref="IBUS_MSG_OPERATION">
						<byte val="0x04" id="button-multiple-defined.push"/>
						<byte val="0x05" id="button-multiple-defined.hold"/>
						<byte val="0x06" id="button-multiple-defined.release"/>
					</CATEGORY>

					<CATEGORY ref="IBUS_MSG_OPERATION">
						<byte val="0x04" id="button-multiple-defined.push"/>
						<byte val="0x05" id="button-multiple-defined.hold"/>
						<byte val="0x06" id="button-multiple-defined.release"/>
					</CATEGORY>

				</DATA>
			</MESSAGE>
		</IBUS>
		"""

		# read XML-database
		self.root = ElementTree.fromstring(xmldb)

# rebind xml database i module "signaldb"
signaldb_mockup = SignalDB()
signaldb.root = signaldb_mockup.root


class TestSignaldb(TestCase):

	"""
	Test XML lookup.
	"""

	def test_none_defined(self):

		"""
		if "None" is passed to signal-constructor we will raise an "ArgError".
		"""

		# signaldb.find((None, None, None))

		self.assertRaises(ValueError, lambda: signaldb.find((None, None, None)))

	def test_no_data_defined(self):

		"""
		if no EVENT is passed to signal-constructor we will raise an "ArgError".
		"""

		# signaldb.find(("IBUS_DEV", "IBUS_DEV", None))

		self.assertRaises(ValueError, lambda: signaldb.find(("IBUS_DEV", "IBUS_DEV", None)))

	def test_only_event_defined(self):

		"""
		Normal state - if only EVENT is passed to signal-constructor we will get a constructed signal back.
		"""

		src, dst, data = signaldb.find((None, None, "button.push"))
		self.assertIsNone(src)
		self.assertIsNone(dst)
		self.assertIsNotNone(data)

	def test_event_and_device_defined(self):

		"""
		Normal state - we expecting to get a constructed signal back.
		"""

		src, dst, data = signaldb.find(("IBUS_DEV", "IBUS_DEV", "button.push"))
		self.assertIsNotNone(src)
		self.assertIsNotNone(dst)
		self.assertIsNotNone(data)

	def test_unknown_device_code(self):

		"""
		raise "DBError" if not device defined
		"""

		# signaldb.find(("IBUS_DEV_UNKNOWN", "IBUS_DEV", "button.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find(("IBUS_DEV_UNKNOWN", "IBUS_DEV", "button.push")))

	def test_multiple_device_codes_defined(self):

		"""
		raise "DBError" if devices with same references defined
		"""

		# signaldb.find((None, None, "button-multiple-refereed.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find((None, None, "button-multiple-refereed.push")))

	def test_unknown_event(self):

		"""
		raise "DBError" if not event defined
		"""

		# signaldb.find((None, None, "unknown-event.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find((None, None, "unknown-event.push")))

	def test_multiple_events_defined(self):
		"""
		raise "DBError" if multiple events defined
		"""

		# signaldb.find((None, None, "button-multiple-defined.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find((None, None, "button-multiple-defined.push")))

	def test_unknown_operation_ref(self):

		"""
		raise "DBError" if no reference to operation byte found
		"""

		# signaldb.find((None, None, "button-unknown-operation-ref.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find((None, None, "button-unknown-operation-ref.push")))

	def test_multiple_operation_refs_found(self):
		"""
		raise "DBError" if multiple references to operation byte found
		"""

		# signaldb.find((None, None, "button-multiple-refereed.push"))

		self.assertRaises(signaldb.DBError, lambda: signaldb.find((None, None, "button-multiple-refereed.push")))

# TODO: test missing attributes in database (id, etc)
