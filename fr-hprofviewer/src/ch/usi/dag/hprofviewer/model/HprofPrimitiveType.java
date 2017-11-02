package ch.usi.dag.hprofviewer.model;

import java.util.HashMap;
import java.util.Map;

import ch.usi.dag.hprofviewer.parser.InvalidHprofException;

public enum HprofPrimitiveType {
	HPROF_ARRAY_OBJECT(1),
	HPROF_NORMAL_OBJECT(2),
	HPROF_BOOLEAN(4),
	HPROF_CHAR(5),
	HPROF_FLOAT(6),
	HPROF_DOUBLE(7),
	HPROF_BYTE(8),
	HPROF_SHORT(9),
	HPROF_INT(10),
	HPROF_LONG(11);

	private int _primitiveType;

	private static Map<Integer, HprofPrimitiveType> _map = new HashMap<Integer, HprofPrimitiveType>();

	static {
		for (HprofPrimitiveType p : HprofPrimitiveType.values()) {
			_map.put(p._primitiveType, p);
		}
	}

	private HprofPrimitiveType(int primitiveType) {
		_primitiveType = primitiveType;
	}

	public static HprofPrimitiveType fromInt(int primitiveType) {
		if (_map.containsKey(primitiveType)) {
			return _map.get(primitiveType);
		}

		throw new InvalidHprofException("Unknown basic type '" + primitiveType + "'.");
	}
}
