package ch.usi.dag.hprofviewer.parser;

import java.nio.ByteBuffer;
import java.util.HashMap;

import org.apache.log4j.Logger;

import ch.usi.dag.hprofviewer.model.Hprof;
import ch.usi.dag.hprofviewer.model.HprofHeapClassDump;
import ch.usi.dag.hprofviewer.model.HprofHeapInstance;
import ch.usi.dag.hprofviewer.model.HprofLoadedClass;

public class HprofParser {

	private final static Logger logger = Logger.getLogger(HprofParser.class);

	private static final int HPROF_UTF8 = 0x01;
	private static final int HPROF_LOAD_CLASS = 0x02;
	// private static final int HPROF_UNLOAD_CLASS = 0x03;
	private static final int HPROF_FRAME = 0x04;
	private static final int HPROF_TRACE = 0x05;
	// private static final int HPROF_ALLOC_SITES = 0x06;
	// private static final int HPROF_HEAP_SUMMARY = 0x07;
	// private static final int HPROF_START_THREAD = 0x0A;
	// private static final int HPROF_END_THREAD = 0x0B;
	private static final int HPROF_HEAP_DUMP = 0x0C;
	// private static final int HPROF_CPU_SAMPLES = 0x0D;
	// private static final int HPROF_CONTROL_SETTINGS = 0x0E;

	private static final int HPROF_GC_ROOT_UNKNOWN = 0xFF;
	private static final int HPROF_GC_ROOT_JNI_GLOBAL = 0x01;
	private static final int HPROF_GC_ROOT_JNI_LOCAL = 0x02;
	private static final int HPROF_GC_ROOT_JAVA_FRAME = 0x03;
	private static final int HPROF_GC_ROOT_NATIVE_STACK = 0x04;
	private static final int HPROF_GC_ROOT_STICKY_CLASS = 0x05;
	private static final int HPROF_GC_ROOT_THREAD_BLOCK = 0x06;
	private static final int HPROF_GC_ROOT_MONITOR_USED = 0x07;
	private static final int HPROF_GC_ROOT_THREAD_OBJ = 0x08;
	private static final int HPROF_GC_CLASS_DUMP = 0x20;
	private static final int HPROF_GC_INSTANCE_DUMP = 0x21;
	private static final int HPROF_GC_OBJ_ARRAY_DUMP = 0x22;
	private static final int HPROF_GC_PRIM_ARRAY_DUMP = 0x23;

	private static final int HPROF_ARRAY_OBJECT = 1;
	private static final int HPROF_NORMAL_OBJECT = 2;
	private static final int HPROF_BOOLEAN = 4;
	private static final int HPROF_CHAR = 5;
	private static final int HPROF_FLOAT = 6;
	private static final int HPROF_DOUBLE = 7;
	private static final int HPROF_BYTE = 8;
	private static final int HPROF_SHORT = 9;
	private static final int HPROF_INT = 10;
	private static final int HPROF_LONG = 11;

	private static int idSize;

	private static long readId(BufferReader reader) {
		byte[] r = reader.readBytes(idSize);
		long id = ByteBuffer.wrap(r).getLong();

		return id;
	}

	private static long readId(ByteBuffer bb) {
		return bb.getLong();
	}

	private static Object readValue(ByteBuffer bb) throws Exception {
		int basicType = bb.get();

		return readValuePrim(bb, basicType);
	}

	private static Object readValuePrim(ByteBuffer bb, int basicType) throws Exception {
		switch (basicType) {
			case HPROF_ARRAY_OBJECT:
			case HPROF_NORMAL_OBJECT:
				return readId(bb);
			case HPROF_BOOLEAN:
				return bb.get();
			case HPROF_CHAR:
				return bb.getChar();
			case HPROF_FLOAT:
				return bb.getFloat();
			case HPROF_DOUBLE:
				return bb.getDouble();
			case HPROF_BYTE:
				return bb.get();
			case HPROF_SHORT:
				return bb.getShort();
			case HPROF_INT:
				return bb.getInt();
			case HPROF_LONG:
				return bb.getLong();
			default:
				throw new InvalidHprofException("Unknown basic type '" + basicType
						+ "'. Unable to continue parsing file.");
		}
	}

	private static void readHeapDump(Hprof hprof, BufferReader reader, int length) throws Exception {
		ByteBuffer bb = ByteBuffer.wrap(reader.getBuffer(), reader._position, length);

		while (bb.hasRemaining()) {
			int type = bb.get();

			HashMap<String, Object> tag = new HashMap<String, Object>();

			tag.put("$recordType", type);

			switch (type) {
				case HPROF_GC_ROOT_UNKNOWN:
					tag.put("objectId", readId(bb));

					break;
				case HPROF_GC_ROOT_JNI_GLOBAL:
					tag.put("objectId", readId(bb));
					tag.put("jniGlobalRefId", readId(bb));

					break;
				case HPROF_GC_ROOT_JNI_LOCAL:
					tag.put("objectId", readId(bb));
					tag.put("threadSerialNumber", bb.getInt());
					tag.put("frameNumberInStackTrace", bb.getInt());

					break;
				case HPROF_GC_ROOT_JAVA_FRAME:
					tag.put("objectId", readId(bb));
					tag.put("threadSerialNumber", bb.getInt());
					tag.put("frameNumberInStackTrace", bb.getInt());

					break;
				case HPROF_GC_ROOT_NATIVE_STACK:
					tag.put("objectId", readId(bb));
					tag.put("threadSerialNumber", bb.getInt());

					break;
				case HPROF_GC_ROOT_STICKY_CLASS:
					tag.put("objectId", readId(bb));

					break;
				case HPROF_GC_ROOT_THREAD_BLOCK:
					tag.put("objectId", readId(bb));
					tag.put("threadSerialNumber", bb.getInt());

					break;
				case HPROF_GC_ROOT_MONITOR_USED:
					tag.put("objectId", readId(bb));

					break;
				case HPROF_GC_ROOT_THREAD_OBJ:
					tag.put("threadObjectId", readId(bb));
					tag.put("threadSerialNumber", bb.getInt());
					tag.put("stackTraceSerialNumber", bb.getInt());

					break;
				case HPROF_GC_CLASS_DUMP:
					HprofHeapClassDump c = new HprofHeapClassDump();

					c.classObjectId = readId(bb);
					tag.put("classObjectId", c.classObjectId);

					c.loadedClass = hprof.getLoadedClass(c.classObjectId);
					logger.trace(c.loadedClass.classNameString);

					tag.put("stackTraceSerialNumber", bb.getInt());

					c.superClassObjectId = readId(bb);
					tag.put("superClassObjectId", c.superClassObjectId);

					if (c.superClassObjectId != 0) {
						c.loadedSuperClass = hprof.getLoadedClass(c.superClassObjectId);
						logger.trace(c.loadedSuperClass.classNameString);
					}

					tag.put("classLoaderObjectId", readId(bb));
					tag.put("signersObjectId", readId(bb));
					tag.put("protectionDomainObjectId", readId(bb));
					tag.put("reserved1", readId(bb));
					tag.put("reserved2", readId(bb));
					tag.put("instanceSize", bb.getInt());

					short sizeOfConstantPool = bb.getShort();

					tag.put("sizeOfConstantPool", sizeOfConstantPool);

					for (short i = 0; i < sizeOfConstantPool; i++) {
						/* short index = */bb.getShort();
						readValue(bb);
					}

					short numberOfStaticFields = bb.getShort();

					tag.put("numberOfStaticFields", numberOfStaticFields);

					HashMap<Long, Object> staticFields = new HashMap<Long, Object>();
					tag.put("$staticFields", staticFields);

					for (int i = 0; i < numberOfStaticFields; i++) {
						long staticFieldId = readId(bb);

						Object value;
						try {
							value = readValue(bb);
							staticFields.put(staticFieldId, value);
						} catch (Exception e) {
							staticFields.put(staticFieldId, "EXCEPTION!!");

							logger.error(tag);
							throw e;
						}
					}

					short numberOfInstanceFields = bb.getShort();

					tag.put("numberOfInstanceFields", numberOfInstanceFields);

					for (int i = 0; i < numberOfInstanceFields; i++) {
						readId(bb);
						bb.get();
					}

					break;
				case HPROF_GC_INSTANCE_DUMP:
					HprofHeapInstance ins = new HprofHeapInstance();

					ins.objectId = readId(bb);
					ins.stackTraceSerialNumber = bb.getInt();
					ins.classObjectId = readId(bb);
					ins.loadedClassObjectId = hprof.getLoadedClass(ins.classObjectId);
					ins.instanceLength = bb.getInt();

					bb.position(bb.position() + ins.instanceLength);

					break;
				case HPROF_GC_OBJ_ARRAY_DUMP:
					tag.put("arrayObjectId", readId(bb));
					tag.put("stackTraceSerialNumber", bb.getInt());

					int numberOfElements = bb.getInt();

					tag.put("numberOfElements", numberOfElements);

					tag.put("arrayClassObjectId", readId(bb));

					bb.position(bb.position() + numberOfElements * idSize);

					break;
				case HPROF_GC_PRIM_ARRAY_DUMP:

					tag.put("arrayObjectId", readId(bb));
					tag.put("stackTraceSerialNumber", bb.getInt());

					int numberOfElementsPrim = bb.getInt();

					tag.put("numberOfElementsPrim", numberOfElementsPrim);

					byte elementType = bb.get();

					tag.put("elementType", elementType);

					for (int i = 0; i < numberOfElementsPrim; i++) {
						readValuePrim(bb, elementType);
					}

					break;
				default:
					logger.error("Unknown TYPE" + type);
			}

			logger.trace(tag);
		}

		reader.readBytes(length);
	}

	private static void readTag(Hprof hprof, BufferReader reader) throws Exception {
		byte tag = reader.readByte();

		int time = reader.readInt();

		int length = reader.readInt();

		String preffix = "TAG=" + tag + ", TIME=" + time + ", LENGTH: " + length + " | ";

		switch (tag) {
			case HPROF_UTF8:
				long stringId = readId(reader);
				String stringValue = reader.readString(length - idSize);

				hprof.strings().put(stringId, stringValue);

				break;
			case HPROF_LOAD_CLASS:
				if (length != 4 + 8 + 4 + 8) {
					throw new Exception("Invalid length for tag HPROF_LOAD_CLASS(2)");
				}

				HprofLoadedClass c = new HprofLoadedClass();

				c.classSerialNumber = reader.readInt();
				c.classObjectId = readId(reader);
				c.stackTraceSerialNumber = reader.readInt();
				c.classNameStringId = readId(reader);
				c.classNameString = hprof.getString(c.classNameStringId);

				hprof.loadedClasses().put(c.classObjectId, c);

				break;
			case HPROF_FRAME: {
				if (length != idSize + idSize + idSize + idSize + 4 + 4) {
					throw new Exception("Invalid length for tag STACK FRAME");
				}

				long stackFrameId = readId(reader);
				long methodNameStringId = readId(reader);
				long methodSignatureStringId = readId(reader);
				long sourceFileNameStringId = readId(reader);
				int classSerialNumber = reader.readInt();
				int lineInfo = reader.readInt();

				logger.trace(String
						.format(preffix
								+ "stackFrameId=%d, methodNameStringId=%d, methodSignatureStringId=%d, sourceFileNameStringId=%d, classSerialNumber=%d, lineInfo=%d",
								stackFrameId, methodNameStringId, methodSignatureStringId, sourceFileNameStringId,
								classSerialNumber, lineInfo));

				break;
			}

			case HPROF_TRACE: {
				int stackTraceSerialNumber = reader.readInt();
				int threadSerialNumber = reader.readInt();
				int numberOfFrames = reader.readInt();

				String ids = "[";
				for (int i = 0; i < numberOfFrames; i++) {
					long frameId = readId(reader);
					ids += frameId + " ";
				}
				ids += "]";

				logger.trace(String.format(preffix
						+ "stackTraceSerialNumber=%d, threadSerialNumber=%d, numberOfFrames=%d, IDs=%s",
						stackTraceSerialNumber, threadSerialNumber, numberOfFrames, ids));
				break;
			}

			case HPROF_HEAP_DUMP: {
				logger.trace(preffix + "BEGIN DUMP");

				readHeapDump(hprof, reader, length);

				logger.trace("END DUMP");

				break;
			}

			default: {
				reader.readBytes(length);
				logger.error("Unrecognized tag: " + tag);
			}
		}
	}

	public Hprof parse(byte[] buffer) throws Exception {
		Hprof hprof = new Hprof();

		BufferReader reader = new BufferReader(buffer);

		String version = reader.readNtString();

		logger.trace(version);

		idSize = reader.readInt();

		logger.debug("sizeOfIdentifiers: " + idSize);

		int highMilli = reader.readInt();

		int lowMilli = reader.readInt();

		logger.trace(highMilli + ":" + lowMilli);

		int t = 0;
		while (!reader.eob()) {
			readTag(hprof, reader);

			t++;
		}

		logger.debug(String.format("TAG count: %d", t));

		return hprof;
	}
}
