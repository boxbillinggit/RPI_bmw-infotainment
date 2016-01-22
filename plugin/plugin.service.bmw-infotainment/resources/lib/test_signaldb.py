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
		<IBUS	xmlns:device="sdb://device"
				xmlns:signal="sdb://signal"
				xmlns:ref="sdb://reference">

			<MESSAGE>
	
				<byte val="0x00" device:id="IBUS_DEV">Device description</byte>
				<byte val="0x02" device:id="IBUS_DEV_MULTIPLE">Double references</byte>
				<byte val="0x03" device:id="IBUS_DEV_MULTIPLE">Double references</byte>

				<DATA>

					<byte val="0x02" ref:id="REFERENCE_TAG">Operation description</byte>
					<byte val="0x02" ref:id="REFERENCE_TAG_MULTIPLE">Double references</byte>
					<byte val="0x03" ref:id="REFERENCE_TAG_MULTIPLE">Double references</byte>
					<byte			 ref:id="REFERENCE_BYTE_NO_VAL">Double references</byte>
					
					<REFERENCE_BYTE_NO_VAL>
						<byte val="0x04" signal:id="reference-missing-val-attr"/>
					</REFERENCE_BYTE_NO_VAL>

					<REFERENCE_TAG>
						<byte val="0x04" signal:id="button.push"/>
						<byte val="0x05" signal:id="button.hold"/>
						<byte val="0x06" signal:id="button.release"/>
					</REFERENCE_TAG>

					<IBUS_MSG_NO_REF>
						<byte val="0x07" signal:id="button-unknown-ref.push"/>
						<byte val="0x08" signal:id="button-unknown-ref.hold"/>
						<byte val="0x09" signal:id="button-unknown-ref.release"/>
					</IBUS_MSG_NO_REF>

					<REFERENCE_TAG_MULTIPLE>
						<byte val="0x04" signal:id="button-multiple-refereed.push"/>
						<byte val="0x05" signal:id="button-multiple-refereed.hold"/>
						<byte val="0x06" signal:id="button-multiple-refereed.release"/>
					</REFERENCE_TAG_MULTIPLE>

					<REFERENCE_TAG>
						<byte val="0x04" signal:id="button-multiple-defined.push"/>
						<byte val="0x05" signal:id="button-multiple-defined.hold"/>
						<byte val="0x06" signal:id="button-multiple-defined.release"/>
					</REFERENCE_TAG>

					<REFERENCE_TAG>
						<byte val="0x04" signal:id="button-multiple-defined.push"/>
						<byte val="0x05" signal:id="button-multiple-defined.hold"/>
						<byte val="0x06" signal:id="button-multiple-defined.release"/>
					</REFERENCE_TAG>
					
					<REFERENCE_TAG>
						<byte signal:id="button-no-value-defined.push"/>
						<byte signal:id="button-no-value-defined.hold"/>
						<byte signal:id="button-no-value-defined.release"/>
					</REFERENCE_TAG>
					
				</DATA>
			</MESSAGE>
		</IBUS>
		"""

		# read XML-database
		self.root = ElementTree.fromstring(xmldb)

signaldb_mockup = SignalDB()
root = signaldb_mockup.root

# rebind xml database in module "signaldb"
signaldb.root = root
signaldb.parent = dict((c, p) for p in root.getiterator() for c in p)
signaldb.DATA = root.find("./MESSAGE/DATA")


class TestSignaldb(TestCase):

	"""
	Test XML lookup.
	"""

	def test_none_defined(self):

		"""
		if "None" is passed to signal-constructor we will raise an "ArgError".
		"""

		# signaldb.create((None, None, None))

		self.assertRaises(ValueError, signaldb.create, (None, None, None))

	def test_no_data_defined(self):

		"""
		if no EVENT is passed to signal-constructor we will raise an "ArgError".
		"""

		# signaldb.create(("IBUS_DEV", "IBUS_DEV", None))

		self.assertRaises(ValueError, signaldb.create, ("IBUS_DEV", "IBUS_DEV", None))

	def test_only_event_defined(self):

		"""
		Normal state - if only EVENT is passed to signal-constructor we will get a constructed signal back.
		"""

		src, dst, data = signaldb.create((None, None, "button.push"))
		self.assertIsNone(src)
		self.assertIsNone(dst)
		self.assertIsNotNone(data)

	def test_event_and_device_defined(self):

		"""
		Normal state - we expecting to get a constructed signal back.
		"""

		src, dst, data = signaldb.create(("IBUS_DEV", "IBUS_DEV", "button.push"))
		self.assertIsNotNone(src)
		self.assertIsNotNone(dst)
		self.assertIsNotNone(data)

	def test_unknown_device_code(self):

		"""
		raise "DBError" if not device defined
		"""

		# signaldb.create(("IBUS_DEV_UNKNOWN", "IBUS_DEV", "button.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, ("IBUS_DEV_UNKNOWN", "IBUS_DEV", "button.push"))

	def test_multiple_device_codes_defined(self):

		"""
		raise "DBError" if devices with same references defined
		"""

		# signaldb.create((None, None, "button-multiple-refereed.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "button-multiple-refereed.push"))

	def test_unknown_event(self):

		"""
		raise "DBError" if not event defined
		"""

		# signaldb.create((None, None, "unknown-event.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "unknown-event.push"))

	def test_multiple_events_defined(self):
		"""
		raise "DBError" if multiple events defined
		"""

		# signaldb.create((None, None, "button-multiple-defined.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "button-multiple-defined.push"))

	def test_unknown_operation_ref(self):

		"""
		raise "DBError" if no reference byte found for tag
		"""

		# signaldb.create((None, None, "button-unknown-ref.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "button-unknown-ref.push"))

	def test_multiple_operation_refs_found(self):

		"""
		raise "DBError" if multiple references to operation byte found
		"""

		# signaldb.create((None, None, "button-multiple-refereed.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "button-multiple-refereed.push"))

	def test_no_val_attribute(self):
		
		"""
		raise "DBError" if no attribute "val" exist for <byte>-tag
		"""

		# signaldb.create((None, None, "button-no-value-defined.push"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "button-no-value-defined.push"))

	def test_no_val_attribute_for_refereed_byte(self):

		"""
		raise "DBError" if no attribute "val" exist for the refereed <byte>-tag
		"""

		# signaldb.create((None, None, "reference-missing-val-attr"))

		self.assertRaises(signaldb.DBError, signaldb.create, (None, None, "reference-missing-val-attr"))
